# API Reference — Workout Tracker API
 
**Brief version:** 1.1
**Document version:** 1.0
**Last updated:** 24 May 2026
 
This document specifies every HTTP endpoint exposed by the Workout Tracker API. It is the implementation contract: every endpoint listed here corresponds to a route in the application and at least one automated test.
 
## Conventions
 
- **Base path:** all endpoints are relative to the API root (e.g. `https://workout-tracker.example.com` in production, `http://localhost:8000` in development).
- **Auth:** "bearer" means a valid JWT must be supplied in the `Authorization: Bearer <token>` header. "none" means the endpoint is publicly accessible.
- **Content type:** all request and response bodies are `application/json` unless stated otherwise.
- **IDs:** all resource IDs are UUIDs (string-form in JSON).
- **Timestamps:** all timestamps are ISO 8601 with timezone (e.g. `2026-05-24T14:30:00Z`).
- **Pagination:** list endpoints return `{items, total, limit, offset}`. Default `limit=50`, maximum `limit=200`.
- **Errors:** non-2xx responses return `{"detail": "human-readable message"}`. Validation errors (422) return FastAPI's structured per-field error format.
---
 
## 1. Authentication
 
Implements **FR-1**, **FR-9**.
 
### POST `/auth/register`
 
Register a new user.
 
- **Auth:** none
- **Request body:**
  ```json
  {
    "email": "user@example.com",
    "password": "min 8 characters",
    "display_name": "Display Name"
  }
  ```
- **Response (201):**
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "Display Name",
    "created_at": "2026-05-24T14:30:00Z"
  }
  ```
- **Status codes:** 201, 400 (invalid input), 409 (email already exists)
### POST `/auth/login`
 
Exchange credentials for a JWT.
 
- **Auth:** none
- **Request body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response (200):**
  ```json
  {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
  ```
- **Status codes:** 200, 401 (invalid credentials)
- **Notes:** No refresh tokens in v1. Token expires in 30 minutes; client re-authenticates. No logout endpoint — JWT is stateless.
### GET `/auth/me`
 
Return the authenticated user's profile.
 
- **Auth:** bearer
- **Response (200):** same shape as `POST /auth/register` response.
- **Status codes:** 200, 401
---
 
## 2. Muscle Groups
 
Read-only catalogue. Seeded via the seed-data script (**FR-2a**). Never editable through the API.
 
### GET `/muscle-groups`
 
List all muscle groups, ordered by `display_order`.
 
- **Auth:** bearer
- **Response (200):**
  ```json
  [
    {"id": 1, "name": "chest", "display_order": 1},
    {"id": 2, "name": "back", "display_order": 2}
  ]
  ```
- **Status codes:** 200, 401
---
 
## 3. Exercises
 
Implements **FR-2** (hybrid catalogue). Some exercises are owned by the system (read-only for all users); others are custom and owned by individual users.
 
### GET `/exercises`
 
List exercises visible to the authenticated user.
 
- **Auth:** bearer
- **Query parameters:**
  - `muscle_group_id` (int, optional) — filter by associated muscle group
  - `owner` (string, optional, default `all`) — one of `system` | `me` | `all`
  - `q` (string, optional) — case-insensitive substring search on name
  - `limit` (int, optional, default 50, max 200)
  - `offset` (int, optional, default 0)
- **Response (200):** paginated list of exercise objects.
- **Status codes:** 200, 401
### GET `/exercises/{id}`
 
Retrieve a single exercise by ID.
 
- **Auth:** bearer
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "name": "Barbell Bench Press",
    "notes": "Optional notes",
    "is_system": true,
    "muscle_groups": [
      {"id": 1, "name": "chest", "is_primary": true},
      {"id": 5, "name": "triceps", "is_primary": false}
    ],
    "created_at": "2026-05-24T14:30:00Z"
  }
  ```
- **Status codes:** 200, 401, 404
### POST `/exercises`
 
Create a custom exercise.
 
- **Auth:** bearer
- **Request body:**
  ```json
  {
    "name": "My Custom Exercise",
    "notes": "Optional",
    "muscle_group_ids": [1, 5],
    "primary_muscle_group_id": 1
  }
  ```
- **Validation:** `primary_muscle_group_id` must be present in `muscle_group_ids`.
- **Response (201):** exercise object (as GET).
- **Status codes:** 201, 400, 401, 409 (user already has a custom exercise with this name)
### PUT `/exercises/{id}`
 
Update a custom exercise owned by the authenticated user.
 
- **Auth:** bearer
- **Request body:** same shape as POST.
- **Response (200):** updated exercise object.
- **Status codes:** 200, 400, 401, 403 (system exercise, or owned by another user), 404
### DELETE `/exercises/{id}`
 
Delete a custom exercise owned by the authenticated user.
 
- **Auth:** bearer
- **Response (204):** no content.
- **Status codes:** 204, 401, 403 (system exercise, or owned by another user), 404, 409 (exercise is referenced by existing sets — schema uses `ON DELETE RESTRICT`)
---
 
## 4. Workouts
 
Implements **FR-3**, **FR-5**.
 
### GET `/workouts`
 
List the authenticated user's workouts.
 
- **Auth:** bearer
- **Query parameters:**
  - `date_from` (ISO date, optional)
  - `date_to` (ISO date, optional)
  - `limit` (int, optional, default 50, max 200)
  - `offset` (int, optional, default 0)
- **Response (200):** paginated list. Workouts ordered by `performed_at` descending.
- **Status codes:** 200, 401
### GET `/workouts/{id}`
 
Retrieve a workout, including all its sets.
 
- **Auth:** bearer
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "name": "Push A",
    "performed_at": "2026-05-24T18:00:00Z",
    "notes": "Felt strong",
    "sets": [
      {
        "id": "uuid",
        "exercise_id": "uuid",
        "set_number": 1,
        "weight_kg": 100.00,
        "reps": 5,
        "rpe": 8.5,
        "estimated_1rm": 116.67,
        "created_at": "2026-05-24T18:05:00Z"
      }
    ],
    "created_at": "2026-05-24T18:00:00Z",
    "updated_at": "2026-05-24T18:30:00Z"
  }
  ```
- **Status codes:** 200, 401, 403, 404
### POST `/workouts`
 
Create a new workout.
 
- **Auth:** bearer
- **Request body:**
  ```json
  {
    "name": "Push A",
    "performed_at": "2026-05-24T18:00:00Z",
    "notes": "Optional"
  }
  ```
- **Response (201):** workout object (sets empty).
- **Status codes:** 201, 400, 401
### PUT `/workouts/{id}`
 
Update a workout's metadata (not its sets — those have their own endpoints).
 
- **Auth:** bearer
- **Request body:** same shape as POST.
- **Response (200):** updated workout object.
- **Status codes:** 200, 400, 401, 403, 404
### DELETE `/workouts/{id}`
 
Delete a workout. Cascades to all its sets (per schema). Triggers PR re-evaluation for any exercise that had a PR set within this workout.
 
- **Auth:** bearer
- **Response (204):** no content.
- **Status codes:** 204, 401, 403, 404
---
 
## 5. Sets
 
Implements **FR-4**, **FR-6**, **FR-7**.
 
### GET `/workouts/{workout_id}/sets`
 
List all sets in a workout, ordered by `set_number`.
 
- **Auth:** bearer
- **Response (200):** list of set objects (each includes computed `estimated_1rm`).
- **Status codes:** 200, 401, 403, 404
### POST `/workouts/{workout_id}/sets`
 
Add a set to a workout.
 
- **Auth:** bearer
- **Request body:**
  ```json
  {
    "exercise_id": "uuid",
    "set_number": 1,
    "weight_kg": 100.00,
    "reps": 5,
    "rpe": 8.5
  }
  ```
  - `set_number` is optional; if omitted, auto-assigned as max existing + 1 within this workout.
  - `rpe` is optional.
- **Response (201):**
  ```json
  {
    "id": "uuid",
    "workout_id": "uuid",
    "exercise_id": "uuid",
    "set_number": 1,
    "weight_kg": 100.00,
    "reps": 5,
    "rpe": 8.5,
    "estimated_1rm": 116.67,
    "is_pr": true,
    "created_at": "2026-05-24T18:05:00Z"
  }
  ```
- **Status codes:** 201, 400, 401, 403, 404
- **Notes:**
  - `estimated_1rm` is computed (Epley): `weight_kg * (1 + reps / 30)`. Per **FR-6**.
  - `is_pr` is `true` if this set is now the user's best estimated 1RM for this exercise. Per **FR-7**. Triggers creation of a `personal_records` row.
### PUT `/sets/{id}`
 
Update an existing set. Triggers PR re-evaluation for the affected exercise.
 
- **Auth:** bearer
- **Request body:** any subset of `{set_number, weight_kg, reps, rpe}`.
- **Response (200):** updated set object (with recomputed `estimated_1rm` and `is_pr`).
- **Status codes:** 200, 400, 401, 403, 404
- **Notes:** PR re-evaluation logic (see Appendix A) handles all transitions correctly.
### DELETE `/sets/{id}`
 
Delete a set. If the set was a PR, the next-best set for that exercise becomes the current PR.
 
- **Auth:** bearer
- **Response (204):** no content.
- **Status codes:** 204, 401, 403, 404
---
 
## 6. Personal Records
 
Implements **FR-8**. PRs are entirely derived — there are no write endpoints.
 
### GET `/personal-records`
 
List the authenticated user's personal records.
 
- **Auth:** bearer
- **Query parameters:**
  - `exercise_id` (uuid, optional) — filter to one exercise
  - `latest_only` (bool, optional, default `true`) — if `true`, returns one PR per exercise (the current best); if `false`, returns full history
- **Response (200):**
  ```json
  [
    {
      "id": "uuid",
      "exercise_id": "uuid",
      "exercise_name": "Barbell Bench Press",
      "set_id": "uuid",
      "estimated_1rm": 120.50,
      "achieved_at": "2026-05-24T18:05:00Z"
    }
  ]
  ```
- **Status codes:** 200, 401
### GET `/personal-records/{exercise_id}/history`
 
Full PR progression for one exercise, ordered chronologically. Showcase endpoint for the "PR over time" feature.
 
- **Auth:** bearer
- **Response (200):** list of PR objects, ascending by `achieved_at`.
- **Status codes:** 200, 401, 404 (exercise not visible to this user)
---
 
## 7. Health
 
### GET `/health`
 
Health probe for deployment platform (Railway, Fly.io).
 
- **Auth:** none
- **Response (200):**
  ```json
  {"status": "ok", "db": "ok"}
  ```
- **Response (503):**
  ```json
  {"status": "degraded", "db": "unreachable"}
  ```
- **Status codes:** 200, 503
---
 
## Appendix A — PR Re-evaluation Logic
 
The personal-record state must remain consistent under all set mutations. The following invariants hold at all times:
 
1. For each `(user, exercise)` pair, the `personal_records` rows form an ascending sequence by `achieved_at`, with strictly increasing `estimated_1rm`.
2. The "current PR" is the most recent row in that sequence.
3. PR history is preserved: rows are never silently rewritten when underlying sets are edited; instead, the affected sequence is recomputed.
A single service method, `PersonalRecordService.recompute_for_exercise(user_id, exercise_id)`, is called from:
 
- After `POST /workouts/{id}/sets` (set created)
- After `PUT /sets/{id}` (set updated)
- After `DELETE /sets/{id}` (set deleted)
- After `DELETE /workouts/{id}` (multiple sets deleted in cascade — called once per affected exercise)
The method:
 
1. Loads all sets for `(user, exercise)` ordered by `created_at` ascending.
2. Walks the sequence, tracking the running maximum `estimated_1rm`.
3. Replaces all existing PR rows for `(user, exercise)` with the new sequence in a single transaction.
This is simpler and more robust than attempting incremental updates from each mutation site.
 
---
 
## Appendix B — Authorisation Summary
 
Per **FR-9**:
 
| Resource | Read | Write |
|---|---|---|
| Own user (`/auth/me`) | self only | self only |
| Muscle groups | any authenticated user | nobody (read-only catalogue) |
| System exercises | any authenticated user | nobody via API |
| Custom exercises | owner only | owner only |
| Workouts | owner only | owner only |
| Sets | workout owner only | workout owner only |
| Personal records | owner only | derived (no direct writes) |
 
The ownership check is implemented as a FastAPI dependency, `require_ownership(model, id_param)`, applied to every route operating on a user-owned resource.
 
---
 
## Appendix C — Endpoint Count
 
| Section | Endpoints |
|---|---|
| Authentication | 3 |
| Muscle groups | 1 |
| Exercises | 5 |
| Workouts | 5 |
| Sets | 4 |
| Personal records | 2 |
| Health | 1 |
| **Total** | **21** |
 
Each endpoint corresponds to at least one automated test (per **NFR-4**).
