# Loop API Contract — Auth (PBI-02)

Owner: Maria. This document is the source of truth for request/response
shapes so Eva (frontend auth UI) can build against it before the real
backend is deployed anywhere, and can mock these exact shapes locally.

Base URL (local dev): `http://localhost:5000/api`

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
  "password": "correcthorsebattery"
}
```

**Success — 201 Created**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "3f1b1e2a-...-uuid",
    "email": "maria@example.com",
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
to a route under `/api/lists`, `/api/reviews`, `/api/reviews/*/upvote`, etc.
Those routes don't exist yet — this contract will grow as PBI-03+ (bookmark
CRUD, review submission, upvoting) land, but they'll all return this same
401 shape when the token is bad, and their own 2xx shape otherwise.

---

## General error shape

Every error response (from any endpoint, not just auth) follows:

```json
{ "error": "<snake_case_code>", "message": "<human readable>" }
```

Never assume `message` is stable for programmatic branching — branch on
`error` instead.
