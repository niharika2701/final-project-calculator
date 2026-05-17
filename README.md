# Final Project — Calculation History & Reports

**IS 601 | Python for Web API | NJIT**

Extends Module 14 with a **Reports & History** feature: a `/reports/summary`
API endpoint, a visual stats dashboard, and comprehensive unit, integration,
and E2E test coverage.

---

## New Feature: Reports & History

| | |
|---|---|
| `GET /reports/summary` | Per-user stats: total calculations, per-operation counts, averages, 5 most recent |
| `/reports` page | Visual dashboard with stat cards, operation bar chart, and recent history list |
| Nav link | `/calculations` page links to `/reports` |

### Architecture highlight
Business logic lives in `app/report_service.py` — a pure function with zero
database or HTTP dependencies. This lets unit tests run in milliseconds with
no fixtures, while the route in `app/routers/reports.py` stays thin.

---

## Full Stack

FastAPI · SQLAlchemy · PostgreSQL · bcrypt · JWT · Jinja2 · Docker · GitHub Actions · Playwright

---

## Docker Hub

```bash
docker pull niharika2701/final-project-calculator:latest
```

🔗 https://hub.docker.com/r/niharika2701/final-project-calculator

---

## Project Structure
Final Project/
├── app/
│   ├── routers/
│   │   ├── auth.py             # Register + login endpoints
│   │   ├── calculations.py     # Full BREAD for calculations
│   │   ├── reports.py          # NEW: /reports/summary
│   │   └── users.py
│   ├── report_service.py       # NEW: pure stats logic
│   ├── calculations.py         # OperationType enum + factory
│   ├── models.py               # User + Calculation ORM models
│   ├── schemas.py              # Pydantic schemas (+ ReportRead)
│   ├── auth.py                 # JWT helpers + get_current_user
│   └── database.py
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── calculations.html
│   └── reports.html            # NEW: stats dashboard
├── tests/
│   ├── conftest.py                     # Smart server fixture (E2E only)
│   ├── test_calculations_e2e.py        # Existing E2E tests
│   ├── test_reports_unit.py            # NEW: pure logic unit tests
│   ├── test_reports_integration.py     # NEW: route integration tests
│   └── test_e2e_reports.py             # NEW: Playwright E2E for reports
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
---

## Running the App Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start with SQLite (no Docker needed for dev)
DATABASE_URL="sqlite:///./local.db" python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000 → register → login → use the calculator → view reports.

---

## Running Tests Locally

### Unit tests (no server or DB needed)
```bash
python -m pytest tests/test_reports_unit.py -v
```

### Integration tests
```bash
DATABASE_URL="sqlite:///./test_integration.db" python -m pytest tests/test_reports_integration.py -v
```

### E2E tests
```bash
DATABASE_URL="sqlite:///./test_e2e.db" python -m pytest tests/test_calculations_e2e.py tests/test_e2e_reports.py -v
```

### All tests
```bash
DATABASE_URL="sqlite:///./test_e2e.db" python -m pytest tests/ -v
```

---

## API Reference

### Auth
| Method | Route | Description |
|---|---|---|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login, returns JWT |

### Calculations (JWT required)
| Method | Route | Description |
|---|---|---|
| POST | /calculations/ | Add calculation |
| GET | /calculations/ | Browse all (user-scoped) |
| GET | /calculations/{id} | Read one |
| PUT | /calculations/{id} | Edit |
| DELETE | /calculations/{id} | Delete |

### Reports (JWT required) — NEW
| Method | Route | Description |
|---|---|---|
| GET | /reports/summary | Usage stats + recent history |

### Pages
| Route | Description |
|---|---|
| / | Home |
| /register | Register |
| /login | Login |
| /calculations | Calculator BREAD UI |
| /reports | Stats dashboard (NEW) |

---

## CI/CD Pipeline

Three parallel jobs run on every push. Docker image is pushed only when all three pass.

| Job | Tests | Needs DB? | Needs server? |
|---|---|---|---|
| unit-tests | `test_reports_unit.py` | No | No |
| integration-tests | `test_reports_integration.py` | SQLite in-memory | No |
| e2e-tests | `test_calculations_e2e.py` + `test_e2e_reports.py` | SQLite file | Yes |
| deploy | builds + pushes Docker image | — | — |