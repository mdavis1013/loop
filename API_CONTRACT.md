# Loop API Contract
Base URL (local dev): `http://localhost:5001/api`

All request/response bodies are JSON. All authenticated requests send:

```
Authorization: Bearer <token>
```

---

## POST /api/auth/register

Create a new account.

**Request**
```json
{
  "email": "maria@example.com",
  "role": "member",
  "password": "correcthorsebattery"
}
```
`role` is optional (`member` or `business_owner`, default `member`). Anything else returns 400 `invalid_role`.

**Success — 201 Created**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "3f1b1e2a-...-uuid",
    "email": "maria@example.com",
    "role": "member",
    "created_at": "2026-09-26T14:00:00+00:00"
  }
}
```

**Errors**
| Status | error code | when |
|---|---|---|
| 400 | `invalid_email` | email missing or malformed |
| 400 | `weak_password` | password shorter than 8 characters |
| 409 | `email_taken` | an account with that email already exists |
| 400 | `invalid_role` | role is not `member` or `business_owner` |

```json
{ "error": "email_taken", "message": "An account with this email already exists." }
```

---

## POST /api/auth/login

**Request**
```json
{
  "email": "maria@example.com",
  "password": "correcthorsebattery"
}
```

**Success — 200 OK**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "3f1b1e2a-...-uuid",
    "email": "maria@example.com",
    "role": "member",
    "created_at": "2026-09-26T14:00:00+00:00"
  }
}
```

**Errors**
| Status | error code | when |
|---|---|---|
| 401 | `invalid_credentials` | wrong email OR wrong password (never distinguished — anti-enumeration) |

---

## Authenticated requests (every future protected route)

Any route wrapped in `@token_required` (bookmarks, reviews, upvotes, and
whatever Isabella/Kaylee build that needs to know who's asking) follows this
shape on auth failure — so the frontend can handle all of them with one
interceptor:

| Status | error code | when |
|---|---|---|
| 401 | `unauthorized` | missing/malformed `Authorization` header, or user was deleted |
| 401 | `token_expired` | token's `exp` has passed — frontend should redirect to login |
| 401 | `invalid_token` | token is malformed or signature doesn't match |

```json
{ "error": "token_expired", "message": "Token has expired." }
```

**Frontend integration note:** store the `token` (e.g. in memory + refresh
via a silent re-login, or localStorage if the team decides that's
acceptable for this project's threat model) and attach it to every request
to a protected route. Reviews and upvotes are documented below; saved lists
will be added when they land. All protected routes return the 401 shape above
when the token is bad.

---

## `GET /api/places/<google_place_id>/reviews`

List the reviews for a place. No login required. `<google_place_id>` is the
`id` returned by `/api/places/search`.

**Success: 200 OK**
```json
{
  "reviews": [
    {
      "id": "4e91d616-...-uuid",
      "rating": 5,
      "comment": "Great spot",
      "author_name": "maria",
      "upvote_count": 2,
      "created_at": "2026-11-13T16:33:27+00:00"
    }
  ],
  "review_count": 1,
  "average_rating": 5.0
}
```

Reviews are newest first. `comment` can be `null`. `author_name` is the part
of the reviewer's email before the `@` (the full email is never returned).
If nobody has reviewed the place yet (or it isn't in our database), the
response is still 200 with `"reviews": []`, `"review_count": 0`, and
`"average_rating": null`.

---

## `POST /api/places/<google_place_id>/reviews`

Post a review. **Login required.** One review per user per place.

**Request**
```json
{
  "rating": 5,
  "comment": "Great spot",
  "place": {
    "name": "Sample Coffee Shop",
    "address": "1 Main St",
    "location": { "lat": 29.65, "lng": -82.32 }
  }
}
```

- `rating` is required: a whole number from 1 to 5.
- `comment` is optional text, up to 2000 characters.
- `place` is required **only the first time a place is reviewed** (it is how
  we save the place). It can be sent every time. It needs `name` and
  `location`; `address` is optional. Use the same fields the search results return.

**Success: 201 Created**
```json
{
  "review": {
    "id": "4e91d616-...-uuid",
    "rating": 5,
    "comment": "Great spot",
    "author_name": "maria",
    "upvote_count": 0,
    "created_at": "2026-11-13T16:33:27+00:00"
  }
}
```

**Errors**
| Status | error code | when |
|---|---|---|
| 400 | `invalid_rating` | rating missing, not a whole number, or outside 1 to 5 |
| 400 | `invalid_comment` | comment is not text, or longer than 2000 characters |
| 400 | `place_required` | the place isn't saved yet and `place` is missing `name` or `location` |
| 401 | `unauthorized` / `token_expired` / `invalid_token` | see "Authenticated requests" |
| 409 | `already_reviewed` | this user already reviewed this place |

---

## `POST /api/reviews/<review_id>/upvote`

Upvote a review. **Login required.** No request body.

**Success: 200 OK**
```json
{ "upvote_count": 3 }
```

**Errors**
| Status | error code | when |
|---|---|---|
| 400 | `own_review` | the user is trying to upvote their own review |
| 401 | `unauthorized` / `token_expired` / `invalid_token` | see "Authenticated requests" |
| 404 | `not_found` | no review with that id |
| 409 | `already_upvoted` | this user already upvoted this review |

---

## General error shape

Every error response (from any endpoint, not just auth) follows:

```json
{ "error": "<snake_case_code>", "message": "<human readable>" }
```

Never assume `message` is stable for programmatic branching — branch on
`error` instead.
