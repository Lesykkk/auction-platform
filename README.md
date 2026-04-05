# auction-platform

Online auction platform — from a monolithic REST API to a microservices system in Kubernetes.

## Tech Stack

- **Language:** Python 3.13
- **Framework:** FastAPI (async)
- **ORM:** SQLAlchemy 2.0 (async, declarative)
- **DB Driver:** Psycopg 3 (async)
- **Validation:** Pydantic 2
- **Database:** PostgreSQL 18 (native `uuidv7()`)
- **Migrations:** Alembic
- **Password hashing:** pwdlib (argon2)
- **JWT:** PyJWT

## Architecture Decisions

- All IDs are `UUID` with `DEFAULT uuidv7()` — globally unique, time-sortable, native in PostgreSQL 18
- SQLAlchemy relationships use `lazy="raise"` — all joins must be explicit, no implicit N+1 queries
- Async throughout — FastAPI, SQLAlchemy, Psycopg 3
- Dependency injection via FastAPI `Depends` and Annotated
- Auth: JWT access token in response body (stored in client memory) + refresh token in `httpOnly` cookie
- **Currently Stage 2:** PostgreSQL storage via SQLAlchemy 2.0.
- Repository pattern: `SQLAlchemyRepository` (in `repositories/base.py`) → specific repositories
- Repositories have two method types: paginated (`find_all`) for API, unpaginated domain-specific methods for internal business logic
- All business logic lives in services only — controllers are thin, repositories are dumb

## Layer Responsibilities

- **`controllers/`** — HTTP only: accept request schema, call service, return response schema. No logic.
- **`services/`** — all business logic: validation, status transitions, balance operations
- **`repositories/`** — data access only: CRUD operations via SQLAlchemy.
- **`schemas/`** — Pydantic request/response models (DTOs)
- **`models/`** — SQLAlchemy declarative models
- **`core/config.py`** — pydantic-settings, reads from environment variables
- **`core/security.py`** — JWT encode/decode, password hashing via pwdlib argon2
- **`api/router.py`** — main router, collects all sub-routers with prefixes and tags
- **`api/dependencies.py`** — FastAPI Annotated Depends - AuthServiceDep, CurrentUser, UserServiceDep..
- **`exceptions/handlers.py`** — custom exceptions + register_exception_handlers(app)
- **`core/database.py`** — SQLAlchemy engine and session configuration

## Custom Exceptions

Defined in `exceptions/handlers.py`:
- `NotFoundError` → 404
- `ConflictError` → 409
- `BusinessLogicError` → 400
- `UnauthorizedError` → 401
- `ForbiddenError` → 403

## Domain Model

### Relationships

```
Auction (1) ──< Lot (N)     one auction has many lots
Lot     (1) ──< Bid (N)     one lot has many bids
Lot     (1) ──< Payment (N) one lot has many payments (winner + refunds)
User    (1) ──< Bid (N)     one user places many bids
User    (1) ──< Payment (N) one user has many payments
User    (1) ──< Auction (N) one user creates many auctions
```

### Entity Fields

**User**
| Field | Type |
|-------|------|
| id | UUID |
| username | str |
| email | str |
| hashed_password | str |
| balance | Decimal |
| locked_balance | Decimal |
| created_at | datetime |

**Auction**
| Field | Type |
|-------|------|
| id | UUID |
| title | str |
| description | str |
| closes_at | datetime |
| status | AuctionStatus |
| user_id | UUID (User.id) |
| created_at | datetime |

**Lot**
| Field | Type |
|-------|------|
| id | UUID |
| auction_id | UUID (Auction.id) |
| title | str |
| description | str |
| starting_price | Decimal |
| min_bid_increment | Decimal |
| current_price | Decimal |
| status | LotStatus |
| created_at | datetime |

**Bid**
| Field | Type |
|-------|------|
| id | UUID |
| lot_id | UUID (Lot.id) |
| user_id | UUID (User.id) |
| amount | Decimal |
| created_at | datetime |

**Payment**
| Field | Type |
|-------|------|
| id | UUID |
| lot_id | UUID (Lot.id) |
| user_id | UUID (User.id) |
| amount | Decimal |
| status | PaymentStatus |
| created_at | datetime |

### Statuses

**Auction:** `PENDING` → `ACTIVE` → `CLOSED` / `CANCELLED`
**Lot:** `PENDING` → `ACTIVE` → `SOLD` / `UNSOLD` / `CANCELLED`
**Payment:** `COMPLETED` / `REFUNDED`

### System Flow

```
1. User registers → tops up balance
2. Organizer creates Auction (PENDING)
3. Organizer adds Lots to auction (each Lot: PENDING)
4. Organizer opens auction:
   → Auction: ACTIVE, all Lots: ACTIVE
5. Buyers place Bids on specific lots:
   - check: sufficient balance (balance - locked_balance >= bid amount)
   - check: bid > current_price + min_bid_increment
   - check: auction is ACTIVE
   - check: bidder ≠ auction creator
   - current_price updated; winner's funds blocked, previous leader's funds unblocked
6. Organizer closes auction → Auction: CLOSED
   → Lots with bids: SOLD
   → Lots without bids: UNSOLD
7. For each SOLD lot:
   Winner → Payment COMPLETED (locked funds charged)
   Other bidders → Payment REFUNDED (locked funds released)
```

### Balance Logic

```
available_balance = balance - locked_balance

Place bid:    locked_balance += bid_amount
Re-bid:       locked_balance -= user's previous bid on this lot, locked_balance += new_bid_amount
Win:          balance -= bid_amount, locked_balance -= bid_amount
Lose/Refund:  locked_balance -= bid_amount (highest bid of the user on this lot)
```

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/auth/login` | ❌ | Login, returns access token + sets refresh cookie |
| POST | `/auth/refresh` | 🍪 | Refresh access token |
| POST | `/auth/logout` | ✅ | Logout, clears refresh cookie |
| POST | `/users/register` | ❌ | Register new user |
| GET | `/users/me` | ✅ | Get current user |
| PATCH | `/users/me` | ✅ | Update current user |
| POST | `/users/me/top-up` | ✅ | Top up balance |
| GET | `/auctions` | ❌ | Get all auctions |
| GET | `/auctions/{id}` | ❌ | Get auction by id |
| POST | `/auctions` | ✅ | Create auction (PENDING) |
| PATCH | `/auctions/{id}` | ✅ | Update auction (owner only, PENDING only) |
| DELETE | `/auctions/{id}` | ✅ | Delete auction (owner only, PENDING only, cascades to lots) |
| POST | `/auctions/{id}/open` | ✅ | Open auction (owner only) → ACTIVE |
| POST | `/auctions/{id}/close` | ✅ | Close auction (owner only) → CLOSED |
| GET | `/lots?auction_id={id}` | ❌ | Get all lots in auction |
| POST | `/lots` | ✅ | Add lot to auction (owner only, PENDING auction only) |
| GET | `/lots/{id}` | ❌ | Get lot by id |
| PATCH | `/lots/{id}` | ✅ | Update lot (owner only, PENDING auction only) |
| DELETE | `/lots/{id}` | ✅ | Delete lot (owner only, PENDING auction only) |
| GET | `/bids?lot_id={lot_id}` | ❌ | Get bids for lot |
| POST | `/bids` | ✅ | Place a bid on a lot |
| GET | `/payments` | ✅ | Get current user's payments |

## Code Conventions

- All route handlers and service methods are `async`
- Services receive Pydantic schemas as input, return domain models or Pydantic schemas
- Repositories work with domain models internally
- Never raise HTTPException directly — use custom exceptions from `exceptions/handlers.py`
- Controllers never contain `if` statements for business logic
- Service collection methods follow the signature: `(context_id, filters, pagination)` — filters always before pagination
- `BaseFilterParams` uses `extra="forbid"`
- `PaginatedResponse` uses `items` (not `data`) + `meta` with auto-computed `total_pages`

Repositories inherit from `SQLAlchemyRepository[ModelType, FilterType]` which uses `AsyncSession`:

```python
class SQLAlchemyRepository(Generic[ModelType, FilterType]):
    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model

# Standard methods:
# find_by_id(id) -> model
# find_all(filters, pagination) -> (list, total)
# save(entity) -> model
# delete(id) -> None
```

## Current Implementation Status

- ✅ REST API (FastAPI)
- ✅ PostgreSQL 18 integration
- ✅ SQLAlchemy 2.0 (Async)
- ✅ Alembic Migrations
- ✅ Business Logic (Auctions, Lots, Bids, Payments)
- ✅ Authentication (JWT + Refresh Tokens)

## Project Structure

```
auction-platform/
├── server/
│   ├── src/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py              ← DB Engine/Session
│   │   │   ├── security.py
│   │   │   └── seed.py                  ← DB Seeding
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── dependencies.py
│   │   ├── controllers/                 ← HTTP Handlers
│   │   ├── services/                    ← Business Logic
│   │   ├── repositories/
│   │   │   ├── base.py                  ← SQLAlchemyRepository
│   │   │   ├── user.py
│   │   │   ├── auction.py
│   │   │   ├── lot.py
│   │   │   ├── bid.py
│   │   │   └── payment.py
│   │   ├── models/                      ← SQLAlchemy Models
│   │   ├── schemas/                     ← Pydantic DTOs
│   │   ├── exceptions/
│   │   │   └── handlers.py
│   │   └── migrations/                  ← Alembic Migrations
│   ├── alembic.ini
│   └── requirements.txt
├── .env
├── compose.yaml
└── README.md
```

## Development Stages

| Stage | Status | Architecture | Storage | What's added |
|-------|--------|-------------|---------|--------------|
| 1 | ✅ Done | Monolith | In-memory | REST API, CRUD, business logic, auth |
| 2 | ✅ Done | Monolith | PostgreSQL 18 | SQLAlchemy 2, Alembic, transactions |
| 3 | ⏳ Planned | Microservices | PostgreSQL (separate DBs) | REST inter-service communication |
| 4 | ⏳ Planned | Microservices | PostgreSQL + Redis | Docker, docker-compose, caching |
| 5 | ⏳ Planned | Microservices | PostgreSQL + Redis | Kubernetes, scaling, rolling update |

## Running the Project

### Prerequisites

- Docker + Docker Compose

### Setup

```bash
# 1. Copy environment file and fill in the values
cp .env.example .env

# 2. Start all services
docker compose up --build
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | — | PostgreSQL username |
| `POSTGRES_PASSWORD` | — | PostgreSQL password |
| `POSTGRES_DB` | `auction_platform` | PostgreSQL database name |
| `SECRET_KEY` | — | JWT secret key |