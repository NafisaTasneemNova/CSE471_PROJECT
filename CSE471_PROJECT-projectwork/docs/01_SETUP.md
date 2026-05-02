# TexBid — Setup & Authentication

## Prerequisites
- Python 3.8+
- MongoDB running on `localhost:27017`

## Installation

```bash
cd CSE471_PROJECT-Motiur/backend
pip install -r requirements.txt
python main.py
# Server runs at http://localhost:8000
```

## Authentication

- Registration: `http://localhost:8000/register` — choose BUYER or SUPPLIER
- Login: `http://localhost:8000/login` — session cookie valid for 30 days
- Logout: `http://localhost:8000/logout`

## User Roles

| Role | Can Do |
|------|--------|
| BUYER | Create RFQs, accept bids, initiate payment, sign contracts |
| SUPPLIER | Browse RFQs, submit bids, confirm orders, sign contracts |
| ADMIN | Everything + manage users, companies, subscriptions |

## Making a User Admin

```bash
cd CSE471_PROJECT-Motiur/backend
python tools/admin_tools.py
# Enter the user's email when prompted
```

Or directly in MongoDB:
```javascript
db.users.updateOne({ email: "you@example.com" }, { $set: { is_admin: true } })
```

## Admin URLs
- Login: `http://localhost:8000/admin/login`
- Dashboard: `http://localhost:8000/admin/dashboard`
- Users: `http://localhost:8000/admin/users`
- Companies: `http://localhost:8000/admin/companies`
- RFQs: `http://localhost:8000/admin/rfqs`
- Subscriptions: `http://localhost:8000/admin/subscriptions`

## Environment Variables

```bash
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=texbid_db
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Can't connect to MongoDB | Run `mongod`, check port 27017 |
| Login not working | Verify email/password, check DB |
| Session expired | Log in again, clear cookies |
| 403 on admin route | Run `admin_tools.py` to grant admin |
