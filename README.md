# SDET Home Challenge — User Management API

An automated end-to-end test framework for the User Management API, covering
CRUD operations, authentication, validation boundaries, and dev/prod
environment isolation. Tests run against the live API deployed on Render,
both locally and in CI.

The findings from this suite are written up in [`BUGS.md`](BUGS.md): 5
confirmed defects, each backed by reproduction steps and evidence captured
outside the test framework.

## Prerequisites

- Python 3.11+
- Access to the deployed API base URL and a valid auth token

## Install

```bash
pip install -e ".[dev]"
```

This installs the project itself plus the test/dev dependencies (`pytest`,
`pytest-html`, `Faker`) declared in `pyproject.toml`.

## Configuration

The suite reads its target environment from two environment variables:

| Variable               | Description                                                        |
|-------------------------|---------------------------------------------------------------------|
| `SDET_RENDER_BASE_URL`  | Base URL of the deployed API (e.g. `https://your-service.onrender.com`) |
| `SDET_AUTH_TOKEN`       | Token sent as the `Authentication` header for authenticated requests |

Copy `.env.example` to `.env` and fill in the real values:

```bash
cp .env.example .env
```

`src/config/settings.py` loads these via `pydantic-settings`, so a local
`.env` file is picked up automatically — no need to export the variables by
hand.

The API exposes two isolated environments, `dev` and `prod`, as path
prefixes under the same base URL (`{base_url}/dev/users`,
`{base_url}/prod/users`). By default the suite runs every test against both.
To restrict a run to one environment, set `TEST_ENVIRONMENTS`:

```bash
TEST_ENVIRONMENTS=dev pytest tests/ -v
```

## Test data

Parametrized values that used to be hardcoded in `@pytest.mark.parametrize`
(boundary ages, invalid emails, missing-field names) live in
[`tests/data/parametrize_data.json`](tests/data/parametrize_data.json),
loaded through `src.data.loader.load_dataset`. To add a new boundary value,
edit the JSON file — no test code changes needed.

## Running the suite locally

```bash
pytest tests/ -v
```

Useful variations:

```bash
# Run a single suite
pytest tests/users/test_delete.py -v

# Generate JUnit + self-contained HTML reports, same as CI
pytest tests/ --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html
```

A session-scoped, autouse fixture in `tests/conftest.py` sweeps both `dev`
and `prod` for leftover `qa-*` test users at the start of every run, so the
suite is safe to re-run without manual cleanup. Any invocation of pytest
against this repo needs `SDET_RENDER_BASE_URL`/`SDET_AUTH_TOKEN` set and
makes live requests to both environments before the first test executes.

Individual tests clean up whatever users they create — via the
`created_user_cleanup` fixture, an explicit `delete_user` call as part of
the test itself, or a `try`/`finally` block in the environment-isolation
suite — so a normal test run should not leave data behind in either
environment.

## Continuous integration

`.github/workflows/ci.yml` runs the full suite on every push and pull
request to `main` (and on manual dispatch). It uses a matrix of
`environment: [dev, prod]` so the two environments run as separate,
parallel jobs with `fail-fast: false` — a failure in one does not cancel the
other, and both report independently. Each job:

1. Waits for the Render service to become reachable (Render's free tier
   spins down on inactivity, so the first request can take a while).
2. Runs `pytest tests/` for its environment, producing a JUnit XML and a
   self-contained HTML report under `reports/`.
3. Uploads both reports as build artifacts via `actions/upload-artifact`,
   using `if: always()` so the reports are published even when tests fail.

There is deliberately no `continue-on-error` anywhere in the pipeline: the
API has confirmed bugs (see `BUGS.md`), and the pipeline is expected to
report red until those are fixed. Suppressing that failure would defeat the
purpose of the suite.

The workflow sets `SDET_RENDER_BASE_URL` and `SDET_AUTH_TOKEN` from a
repository variable and secret named `RENDER_BASE_URL` and `AUTH_TOKEN`
respectively (`vars.RENDER_BASE_URL`, `secrets.AUTH_TOKEN` in `ci.yml`) —
note these names do **not** carry the `SDET_` prefix used locally. Both must
be configured under the repository's Settings → Secrets and variables →
Actions for the workflow to run against a real deployment.

## Test case management

Test names read cleanly as TestRail case titles, grouped by capability
(Create / Read / Update / Delete & Authentication / Validation Boundaries /
Environment Isolation) rather than by environment. The 75 pytest instances
(parametrized by `dev`/`prod` and, for the data-driven suites, by value) roll
up to 28 TestRail cases — the catalog lives in
[`tests/data/testrail_cases.json`](tests/data/testrail_cases.json).

`src/reporting/case_sync.py` is a one-time (idempotent, re-runnable) script
that creates the sections/cases in TestRail from that catalog and writes the
resulting `function -> case_id` map to
[`tests/data/testrail_case_ids.json`](tests/data/testrail_case_ids.json).
Run it again only if the catalog changes:

```bash
python -m src.reporting.case_sync
```

`src/reporting/testrail_reporter.py` runs as the last step of every CI job
(`if: always()`, same as the artifact upload): it parses that job's JUnit XML,
rolls each function's `dev`/`prod`/data-driven variants up into one result per
case, creates a new TestRail Run, and posts the results — a case is Failed if
any of its variants failed, with a comment listing every variant's outcome.
Required env vars: `TESTRAIL_BASE_URL`, `TESTRAIL_USERNAME`,
`TESTRAIL_API_KEY`, `TESTRAIL_PROJECT_ID` (see `.env.example`).

## Known bugs

Bugs found while building and running this suite are documented in
[`BUGS.md`](BUGS.md), each with the affected endpoint, expected vs. actual
behavior, direct reproduction evidence, and the test that exposes it.

## Project structure

```
src/
  clients/
    base_client.py       # thin requests.Session wrapper (get/post/put/delete)
    users_client.py       # Users API surface built on top of base_client
  config/
    settings.py           # pydantic-settings config (SDET_ env vars, .env support)
    testrail_settings.py  # pydantic-settings config (TESTRAIL_ env vars)
  data/
    loader.py              # loads tests/data/parametrize_data.json (lru_cache'd)
  factories/
    user_factory.py       # UserFactory (random valid payloads) and
                           # UserPayloadBuilder (fluent builder for edge cases)
  models/
    user.py                # User / CreateUserRequest / UpdateUserRequest / ErrorResponse
  reporting/
    testrail_client.py     # thin TestRail API v2 client (sections/cases/runs)
    case_sync.py            # syncs tests/data/testrail_cases.json catalog to TestRail
    junit_parser.py         # parses JUnit XML, groups results by function
    testrail_reporter.py    # posts per-case results to TestRail after each CI job

tests/
  conftest.py              # env-parametrized users_client fixture, cleanup fixtures
  data/
    parametrize_data.json    # boundary/invalid values loaded by src.data.loader
    testrail_cases.json      # catalog of 28 TestRail cases (section + title per function)
    testrail_case_ids.json   # function -> case_id map, written by case_sync.py
  users/
    test_create.py                  # POST /users
    test_read.py                    # GET /users, GET /users/{email}
    test_update.py                  # PUT /users/{email}
    test_delete.py                  # DELETE /users/{email} and auth enforcement
    test_validation_boundaries.py   # field validation and boundary values
    test_environment_isolation.py   # dev/prod data isolation and parity

.github/workflows/ci.yml   # parallel dev/prod CI pipeline
BUGS.md                     # confirmed defects found by this suite
.env.example                 # template for required environment variables
pyproject.toml               # project metadata, dependencies, pytest config
```
