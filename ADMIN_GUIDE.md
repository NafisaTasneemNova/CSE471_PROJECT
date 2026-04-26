# Admin System - Complete Guide

## Overview
TexBid has a separate admin system for platform management. Only authorized administrators can access the admin panel.

---

## Quick Start

### Step 1: Register Your Admin Accounts
1. Go to `http://localhost:8000/register`
2. Register with your admin email addresses
3. Complete registration for all admin accounts

### Step 2: Make Users Administrators
```bash
cd TexBid-master/backend
python make_me_admin.py
# Enter your email when prompted
```

### Step 3: Access Admin Panel
1. Go to `http://localhost:8000/admin/login`
2. Log in with your admin credentials
3. You'll see the admin dashboard

---

## Admin Features

### 1. Admin Dashboard (`/admin/dashboard`)
- Platform statistics overview
- Quick access to all management pages
- Total users, companies, RFQs, premium users

### 2. User Management (`/admin/users`)
View all registered users:
- ✅ Email addresses
- ✅ Company IDs
- ✅ Admin vs Regular user badges
- ✅ Account creation dates
- ✅ Last login times
- ✅ Statistics: Total users, Admin users, Regular users

### 3. Company Management (`/admin/companies`)
View all companies (buyers & suppliers):
- ✅ Company names
- ✅ Role badges (Buyer/Supplier)
- ✅ Subscription tier (Free/Premium)
- ✅ Verification status
- ✅ Trust scores with progress bars
- ✅ Creation dates

### 4. RFQ Management (`/admin/rfqs`)
View all RFQs and reverse auctions:
- ✅ RFQ titles
- ✅ Buyer IDs
- ✅ Product categories
- ✅ Quantities
- ✅ Status badges (Open, Evaluating, Awarded)
- ✅ Type badges (Standard/Auction)

### 5. Analytics (`/admin_analytics`)
- Platform analytics dashboard
- User activity metrics
- Revenue tracking

### 6. Subscriptions (`/admin_subscriptions`)
- Manage user subscriptions
- View subscription history
- Handle upgrades/downgrades

---

## Admin URLs

### For Admins Only:
- **Admin Login**: `http://localhost:8000/admin/login`
- **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
- **User Management**: `http://localhost:8000/admin/users`
- **Company Management**: `http://localhost:8000/admin/companies`
- **RFQ Management**: `http://localhost:8000/admin/rfqs`
- **Analytics**: `http://localhost:8000/admin_analytics`
- **Subscriptions**: `http://localhost:8000/admin_subscriptions`

### Regular Users:
- Regular users use: `http://localhost:8000/login`
- They cannot access `/admin/*` URLs
- Admin links are NOT shown in regular navigation

---

## Security Features

1. **Separate Login**: Admins use a different login page
2. **Role Verification**: System checks `is_admin` flag on every admin request
3. **Hidden Access**: Admin URLs are not linked from regular user pages
4. **Session-Based**: Uses same secure session system as regular users

---

## Adding More Admins

### Option 1: Using Script
1. Edit `make_admin.py` and add their email
2. Run `python make_admin.py`

### Option 2: Using make_me_admin.py
```bash
python make_me_admin.py
# Enter the new admin's email
```

### Option 3: Manually in MongoDB
```javascript
db.users.updateOne(
  { email: "newemail@texbid.com" },
  { $set: { is_admin: true } }
)
```

---

## Removing Admin Access

```bash
cd TexBid-master/backend
python
```

```python
import asyncio
from database import db, connect_to_mongo

async def remove_admin():
    await connect_to_mongo()
    await db["users"].update_one(
        {"email": "user@texbid.com"},
        {"$set": {"is_admin": False}}
    )
    print("Admin access removed")

asyncio.run(remove_admin())
```

---

## Troubleshooting

### "Insufficient permissions" error:
- Make sure you ran `make_me_admin.py` after registering
- Check that the email matches exactly
- Verify in database: `db.users.find({email: "your@email.com"})`

### Can't access admin dashboard:
- Make sure you're logged in at `/admin/login` (not regular login)
- Clear browser cookies and try again
- Check backend logs for errors

### Regular users seeing admin links:
- They shouldn't! Admin links are only in admin pages
- If they try to access `/admin/*` URLs directly, they'll get 403 error

---

## Best Practices

1. **Keep Admin Emails Private**: Don't share admin login URL publicly
2. **Use Strong Passwords**: Admin accounts should have strong passwords
3. **Regular Audits**: Periodically review who has admin access
4. **Separate Accounts**: Don't use admin accounts for regular buying/selling
