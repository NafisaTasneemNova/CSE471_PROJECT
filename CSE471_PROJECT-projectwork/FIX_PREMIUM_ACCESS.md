# Fix Premium Access - Quick Guide

## Problem
You purchased premium but still can't access Reverse Auction.

## Solution (Choose One)

### 🚀 FASTEST: Use Admin Panel

```bash
# Step 1: Make yourself admin
python make_user_admin.py

# Step 2: Log out and log back in

# Step 3: Go to admin panel
# Open: http://localhost:8000/admin/subscriptions

# Step 4: Toggle your company to PREMIUM

# Step 5: Try Reverse Auction again
# Open: http://localhost:8000/rfq/auctions
```

### ⚡ QUICK: Use Command Line

```bash
# Run the upgrade script
python upgrade_to_premium.py

# Select your company from the list

# Log out and log back in

# Try Reverse Auction again
```

### 🔍 DIAGNOSTIC: Check What's Wrong

```bash
# Check if you're admin
python check_admins.py

# Check subscription status
python check_subscription.py

# Full diagnostic
python diagnose_auction_access.py

# Verify premium access
python verify_premium_access.py
```

---

## Step-by-Step: Admin Panel Method

### 1. Make Yourself Admin
```bash
python make_user_admin.py
```
- Select your user from the list
- Confirm with 'yes'

### 2. Log Out
```
http://localhost:8000/logout
```

### 3. Log Back In
```
http://localhost:8000/login
```

### 4. Open Admin Subscriptions Page
```
http://localhost:8000/admin/subscriptions
```

### 5. Find Your Company
- Look for your company name in the list
- Check current subscription tier

### 6. Toggle to PREMIUM
- Click the toggle button next to your company
- Should change from FREE to PREMIUM

### 7. Test Access
```
http://localhost:8000/rfq/auctions
```
- Should now see auction list instead of "Premium Required" page

---

## Why This Happens

### Possible Causes:
1. **Payment didn't update database** - Most common
2. **Session not refreshed** - Browser cached old data
3. **Wrong user logged in** - Different account than expected
4. **Database connection issue** - Payment processed but DB not updated

### The Fix:
- Admin panel directly updates the database
- Bypasses payment processing
- Gives immediate access
- No waiting or troubleshooting needed

---

## Verification

After fixing, verify you have access:

### Check 1: Pricing Page
```
http://localhost:8000/pricing
```
Should show:
- "You are currently on the PREMIUM plan"
- "Locked (30 days left)" button

### Check 2: Reverse Auction
```
http://localhost:8000/rfq/auctions
```
Should show:
- List of active auctions
- NOT "Premium Required" page

### Check 3: Database
```bash
python check_subscription.py
```
Should show:
- Your company with PREMIUM tier
- Expiry date 30 days in future

---

## All Admin Pages

Once you're admin, you can access:

- **Subscriptions**: `http://localhost:8000/admin/subscriptions` ⭐
- **Dashboard**: `http://localhost:8000/admin/dashboard`
- **Users**: `http://localhost:8000/admin/users`
- **Companies**: `http://localhost:8000/admin/companies`
- **RFQs**: `http://localhost:8000/admin/rfqs`
- **Analytics**: `http://localhost:8000/admin/analytics`
- **AI Config**: `http://localhost:8000/admin/ai`
- **Capacity**: `http://localhost:8000/admin/capacity`
- **Escrow**: `http://localhost:8000/admin/escrow`
- **Contracts**: `http://localhost:8000/admin/contracts`

---

## Need More Help?

### Check Documentation:
- `ADMIN_ACCESS_GUIDE.md` - Complete admin guide
- `REVERSE_AUCTION_USER_FLOW.md` - Full user flow
- `QUICK_START_PREMIUM.md` - Premium overview

### Run Diagnostics:
```bash
python diagnose_auction_access.py
```

### Manual Database Fix:
```javascript
// Connect to MongoDB
use texbid_db

// Update your company
db.companies.updateOne(
  { name: "YourCompanyName" },
  { 
    $set: { 
      subscription_tier: "PREMIUM",
      subscription_expires_at: new Date(Date.now() + 30*24*60*60*1000)
    } 
  }
)
```

---

## Summary

**Fastest Solution:**
1. `python make_user_admin.py` ← Make yourself admin
2. Log out and log back in
3. Go to `http://localhost:8000/admin/subscriptions`
4. Toggle your company to PREMIUM
5. Access Reverse Auction at `http://localhost:8000/rfq/auctions`
6. ✅ Done!

This bypasses any payment processing issues and gives you immediate access to premium features.
