# TexBid — Garment Order Exchange Platform

## Quick Start

```bash
cd CSE471_PROJECT-Motiur/backend
pip install -r requirements.txt
python main.py
# Open http://localhost:8000
```

## Project Structure

```
CSE471_PROJECT-Motiur/
├── backend/
│   ├── main.py          # FastAPI app (all routes & logic)
│   ├── models.py        # Pydantic models
│   ├── database.py      # MongoDB connection
│   ├── requirements.txt
│   └── tools/
│       └── db_tools.py  # All DB maintenance utilities (admin, bids, subscriptions)
│
├── frontend/
│   └── src/
│       ├── pages/       # HTML templates (Jinja2)
│       └── components/  # CSS & JS
│
└── docs/                # All documentation
    ├── 01_SETUP.md
    ├── 02_RFQ.md
    ├── 03_AUCTION.md
    ├── 04_BID_TO_PAYMENT.md
    ├── 05_SUBSCRIPTION.md
    └── 06_NOTIFICATIONS.md
```

## Documentation

| File | Topic |
|------|-------|
| [docs/01_SETUP.md](docs/01_SETUP.md) | Installation, auth, roles, admin setup |
| [docs/02_RFQ.md](docs/02_RFQ.md) | Creating & managing RFQs, bid rules |
| [docs/03_AUCTION.md](docs/03_AUCTION.md) | Reverse auction, live leaderboard |
| [docs/04_BID_TO_PAYMENT.md](docs/04_BID_TO_PAYMENT.md) | Full bid → contract → payment flow |
| [docs/05_SUBSCRIPTION.md](docs/05_SUBSCRIPTION.md) | Free vs Premium, 30-day lock |
| [docs/06_NOTIFICATIONS.md](docs/06_NOTIFICATIONS.md) | All notification triggers |

## DB Maintenance

```bash
cd CSE471_PROJECT-Motiur/backend
python tools/db_tools.py
```

Options: make admin, reset subscription locks, list bids, remove buyer bids, list companies, and more.

## Tech Stack
- **Backend**: FastAPI + Python
- **Database**: MongoDB (Motor async driver)
- **Frontend**: HTML + TailwindCSS + Vanilla JS
- **Auth**: Session-based with bcrypt
- **Real-time**: WebSockets (auction room chat)
