# Known Bugs — User Management API

This report documents defects confirmed against the live deployment at
**`https://sdet-challenge-api.onrender.com`** on **2026-08-12**, using the automated
test suite in `tests/` run with:

```
pytest tests/ -v --junitxml=reports/full-run.xml
```

That run produced **98 tests collected, 78 passed, 20 failed**. Every failure below was
independently reproduced with a direct HTTP request outside the test framework
(exact status codes and response bodies are included as evidence). Expected behavior
is drawn from `sdet_challenge_api.yml`, which documents `dev` and `prod` as
functionally identical, isolated environments. All bug numbers below are the
irreducible, distinct defects behind those 20 failures — several test failures
share the same root cause and are grouped into a single entry, noted under each
bug's "Test that exposes it" / impact text.

One thing that is **not** a bug, despite touching a related area: dev/prod data
isolation itself holds correctly — a user created in one environment is never
returned by the other. The cross-environment lookups in
`tests/users/test_environment_isolation.py` fail only because they hit Bug 1 (GET on
a nonexistent email returns 500) at the isolation boundary, not because of any
data leak.

---

## Bug 1: GET on a nonexistent user returns 500 instead of 404

- **Endpoint:** `GET /{env}/users/{email}`
- **Expected (per spec):** `404` when no user exists for the given email (the spec documents only `200` and `404` for this endpoint).
- **Actual:** `500 {"error": "Internal server error"}` for any email that does not match an existing record — this includes a genuinely unknown email, a syntactically malformed email (e.g. `not-an-email`), an email just removed by a successful DELETE, and an email that exists only in the other environment. Reproduced directly on both `dev` and `prod`:
  ```
  GET /dev/users/qa-does-not-exist-verify@sdet-test.dev -> 500 {"error": "Internal server error"}
  GET /dev/users/not-an-email                           -> 500 {"error": "Internal server error"}
  ```
- **Test that exposes it:** `tests/users/test_read.py::test_get_user_returns_404_for_unknown_email` (also `test_get_user_handles_malformed_email_path_gracefully`, `test_delete.py::test_delete_user_with_valid_token_returns_204`, and both tests in `test_environment_isolation.py`, all of which fail for this same underlying reason).
- **Impact:** Any client that looks up a user by email and treats a non-2xx response as an error must special-case a 500 as "not found," which defeats the purpose of documented status codes and will surface as spurious server-error alerts/logging in any consumer of this API.

## Bug 2: POST with a duplicate email returns 500 instead of 409

- **Endpoint:** `POST /{env}/users`
- **Expected (per spec):** `409` when creating a user whose email already exists.
- **Actual:** `500 {"error": "Internal server error"}` on both `dev` and `prod`. Reproduced directly:
  ```
  POST /dev/users {email: X} -> 201 (first)
  POST /dev/users {email: X} -> 500 {"error": "Internal server error"} (duplicate)
  ```
- **Test that exposes it:** `tests/users/test_create.py::test_create_user_rejects_duplicate_email`
- **Impact:** Callers cannot distinguish a duplicate-email conflict from a genuine server failure, making it impossible to implement correct "create or handle existing user" logic without resorting to a follow-up GET.

## Bug 3: PUT with a different email in the body silently discards the update

- **Endpoint:** `PUT /{env}/users/{email}`
- **Expected (per spec):** A full replace of the user's fields (name, email, age all required); the spec documents a `409` for a duplicate email, implying an email change is a supported operation.
- **Actual:** The response is `200` and echoes the new email/name/age as if the update succeeded, but the underlying record is left completely unchanged under the original (path) email, and no record is created under the new email at all. Reproduced directly:
  ```
  create: {name: "Original Name", email: X, age: 20} -> 201
  PUT /dev/users/X {name: "CHANGED NAME", email: Y, age: 77} -> 200 {name: "CHANGED NAME", email: Y, age: 77}
  GET /dev/users/X -> 200 {name: "Original Name", email: X, age: 20}   # unchanged, update was dropped
  GET /dev/users/Y -> 500 {"error": "Internal server error"}            # no record created here (Bug 1)
  ```
- **Test that exposes it:** `tests/users/test_update.py::test_update_user_changing_email_in_body`
- **Impact:** This is a data-integrity bug, not just a wrong status code: the API reports success and returns a body describing a change that was never persisted, so a client has no reliable way to detect that its update was lost.

## Bug 4: DELETE on dev does not enforce authentication

- **Endpoint:** `DELETE /{env}/users/{email}`
- **Expected (per spec):** `401` unless the request carries the header `Authentication: mysecrettoken`.
- **Actual:** On `dev`, the delete succeeds (`204`) regardless of authentication — with no `Authentication` header at all, with an incorrect token value, and even with the conventional `Authorization: Bearer <token>` header instead of the spec's `Authentication` header. `prod` enforces the documented behavior correctly in all three cases (`401 {"error": "Authentication required"}`). Reproduced directly:
  ```
  dev:  DELETE with no auth header       -> 204 (deleted)
  dev:  DELETE with Authentication: wrong -> 204 (deleted)
  dev:  DELETE with Authorization: Bearer -> 204 (deleted)
  prod: same three cases                  -> 401 each time
  ```
- **Test that exposes it:** `tests/users/test_delete.py::test_delete_user_without_auth_header_returns_401[dev]` (also `test_delete_user_with_wrong_token_returns_401[dev]`)
- **Impact:** Anyone with network access to the dev environment can delete any user record without credentials of any kind. This is a security defect and an environment-parity gap (prod is correctly protected; dev is not).

## Bug 5: POST accepts syntactically invalid email addresses

- **Endpoint:** `POST /{env}/users`
- **Expected (per spec):** `400` when `email` is not a valid email (the shared User/CreateUserRequest schema declares `email` as `string, email format`).
- **Actual:** Only a fully empty string (`""`) is rejected with `400`. Every other malformed value tested is accepted with `201` and persisted, on both `dev` and `prod`:
  ```
  POST /dev/users {email: "not-an-email"}        -> 201 (persisted)
  POST /dev/users {email: "missing-at-sign.com"}  -> 201 (persisted)
  POST /dev/users {email: "   "}                  -> 201 (persisted)
  POST /dev/users {email: ""}                     -> 400 (correctly rejected)
  ```
- **Test that exposes it:** `tests/users/test_validation_boundaries.py::test_create_user_rejects_invalid_email_format`
- **Impact:** No real email-format validation is enforced; the API will store user records that cannot receive email, breaking any downstream feature (notifications, password reset, etc.) that assumes a valid address.
