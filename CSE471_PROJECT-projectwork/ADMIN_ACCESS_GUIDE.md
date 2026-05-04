# Admin Access Guide - TexBid

## Quick Start: Access Admin Panel

### Step 1: Check if You're an Admin
```bash
python check_admins.py
```

### Step 2: Make Yourself Admin (if needed)
```bash
python make_user_admin.py
```

### Step 3: Access Admin Panel
1. **Log out** from your current session
2. **Log back in** as the admin user
3. Navigate to any admin page (see list below)

---

## Available Admin Pages

### 🏠 Main Admin Pages

#### 1. **Admin Dashboard**
- **URL**: `http://localhost:8000/admin/dashboard`
- **Purpose**: Overview of system statistics
- **Features**:
  - Total users, companies, RFQs
  - Recent activity
  - System health

#### 2. **Subscription Management** ⭐ (MOST USEFUL FOR YOUR ISSUE)
- **URL**: `http://localhost:8000/admin/subscriptions`
- **Purpose**: Manage company subscriptions
- **Features**:
  - View all companies and their subscription tiers
  - **Toggle subscriptions** (FREE ↔ PREMIUM)
  - See subscription expiry dates
  - **This is where you can fix your premium access!**

#### 3. **User Management**
- **URL**: `http://localhost:8000/admin/users`
- **Purpose**: Manage user accounts
- **Features**:
  - View all users
  - Edit user details
  - Manage user roles

#### 4. **Company Management**
- **URL**: `http://localhost:8000/admin/companies`
- **Purpose**: Manage companies
- **Features**:
  - View all companies
  - See company details
  - View subscription status

#### 5. **RFQ Management**
- **URL**: `http://localhost:8000/admin/rfqs`
- **Purpose**: Manage all RFQs
- **Features**:
  - View all RFQs
  - Monitor RFQ status
  - Manage auctions

#### 6. **Analytics Dashboard**
- **URL**: `http://localhost:8000/admin/analytics`
- **Purpose**: View system analytics
- **Features**:
  - User statistics
  - Revenue metrics
  - Usage patterns

#### 7. **AI Configuration**
- **URL**: `http://localhost:8000/admin/ai`
- **Purpose**: Configure AI features
- **Features**:
  - AI model settings
  - Recommendation tuning
  - Performance monitoring

#### 8. **Capacity Monitor**
- **URL**: `http://localhost:8000/admin/capacity`
- **Purpose**: Monitor supplier capacity
- **Features**:
  - View capacity entries
  - Detect suspicious data
  - Manage supplier limits

#### 9. **Escrow Management**
- **URL**: `http://localhost:8000/admin/escrow`
- **Purpose**: Manage escrow transactions
- **Features**:
  - View all escrow accounts
  - Monitor transactions
  - Release funds

#### 10. **Contract Management**
- **URL**: `http://localhost:8000/admin/contracts`
- **Purpose**: View all contracts
- **Features**:
  - Contract list
  - Contract status
  - Document management

---

## How to Fix Your Premium Access Issue

### Option 1: Use Admin Panel (Recommended)

1. **Make yourself admin**:
   ```bash
   python make_user_admin.py
   ```

2. **Log out and log back in**

3. **Go to Subscription Management**:
   ```
   http://localhost:8000/admin/subscriptions
   ```

4. **Find your company** in the list

5. **Click the toggle button** to switch from FREE to PREMIUM

6. **Done!** You now have premium access

### Option 2: Use Command Line Script

```bash
python upgrade_to_premium.py
```

Then select your company from the list.

---

## Admin Login Process

### If Admin Login Page Exists:
1. Go to: `http://localhost:8000/admin/login`
2. Enter admin credentials
3. Access admin panel

### If Using Regular Login:
1. Make sure your user has `is_admin: true` in database
2. Log in normally at: `http://localhost:8000/login`
3. Access admin pages directly via URLs above

---

## Checking Admin Status

### Method 1: Use Script
```bash
python check_admins.py
```

### Method 2: MongoDB Query
```javascript
// Connect to MongoDB
use texbid_db

// Find all admins
db.users.find({ is_admin: true })

// Make a user admin
db.users.updateOne(
  { email: "your@email.com" },
  { $set: { is_admin: true } }
)
```

---

## Admin API Endpoints

### Toggle Subscription
```http
POST /api/admin/toggle-subscription
Content-Type: application/json

{
  "company_id": "company_123"
}

Response:
{
  "success": true,
  "new_tier": "PREMIUM",
  "message": "Subscription updated successfully"
}
```

### Get All Companies
```http
GET /api/admin/companies

Response:
{
  "companies": [
    {
      "id": "company_123",
      "name": "Example Company",
      "subscription_tier": "PREMIUM",
      "subscription_expires_at": "2026-06-03T10:00:00Z"
    }
  ]
}
```

---

## Security Notes

### Admin Access Control
- All admin routes use `Depends(require_admin)` or check `is_admin` flag
- Only users with `is_admin: true` can access admin pages
- Admin status is checked on every request

### Making Users Admin
- **Be careful** who you give admin access to
- Admins can:
  - View all user data
  - Modify subscriptions
  - Access sensitive information
  - Manage all system resources

---

## Troubleshooting

### Issue: "Access Denied" on Admin Pages
**Solution**: Make sure your user has `is_admin: true`
```bash
python make_user_admin.py
```

### Issue: Admin Pages Not Loading
**Solution**: 
1. Check if you're logged in
2. Clear browser cache
3. Try incognito mode

### Issue: Can't Toggle Subscription
**Solution**:
1. Check browser console (F12) for errors
2. Make sure you're an admin
3. Try using the command line script instead

---

## Quick Commands Reference

```bash
# Check who is admin
python check_admins.py

# Make a user admin
python make_user_admin.py

# Check subscription status
python check_subscription.py

# Upgrade to premium
python upgrade_to_premium.py

# Diagnose auction access
python diagnose_auction_access.py

# Verify premium access
python verify_premium_access.py
```

---

## Summary

To fix your Reverse Auction access issue using the admin panel:

1. ✅ Run: `python make_user_admin.py`
2. ✅ Select your user account
3. ✅ Log out and log back in
4. ✅ Go to: `http://localhost:8000/admin/subscriptions`
5. ✅ Find your company
6. ✅ Toggle subscription to PREMIUM
7. ✅ Try accessing Reverse Auction again
8. ✅ SUCCESS! 🎉

The admin panel gives you full control over subscriptions and makes it easy to fix access issues without touching the database directly.
