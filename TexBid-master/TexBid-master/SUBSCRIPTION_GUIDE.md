# Subscription System - Complete Guide

## Overview
TexBid offers two subscription tiers: FREE and PREMIUM. Premium unlocks advanced features like reverse auctions and analytics.

---

## Subscription Tiers

### FREE Plan
**Cost**: $0/month

**Features:**
- ✅ Create and browse RFQs
- ✅ Basic supplier directory
- ✅ Submit quotes
- ✅ Basic messaging
- ✅ Profile management
- ❌ No reverse auctions
- ❌ No analytics dashboard
- ❌ Limited features

### PREMIUM Plan
**Cost**: See pricing page

**Features:**
- ✅ Everything in FREE
- ✅ **Reverse auctions** (create & participate)
- ✅ **Analytics dashboard** (insights & reports)
- ✅ Priority support
- ✅ Advanced search filters
- ✅ Unlimited RFQs
- ✅ Premium badge
- ✅ Early access to new features

---

## 30-Day Lock System

### How It Works:
When you change your subscription (upgrade or downgrade), you're **locked for 30 days**.

```
Day 1: Upgrade to Premium
    ↓
Days 1-30: Cannot change subscription (locked)
    ↓
Day 31+: Can change subscription again
```

### Why 30 Days?
- Prevents subscription abuse
- Ensures fair pricing
- Protects platform integrity
- Industry standard practice

### Lock Rules:
- ✅ Can use all features during lock period
- ✅ Subscription remains active
- ❌ Cannot upgrade/downgrade
- ❌ Cannot cancel (must wait 30 days)
- ✅ Lock expires automatically after 30 days

---

## Upgrading to Premium

### Step 1: Access Subscription Page
1. Log in to your account
2. Click your profile dropdown
3. Select "Subscription"
   
   **OR**
   
   Click "Subscription Plan" in navigation

### Step 2: Choose Premium
1. See plan comparison
2. Click "Upgrade to Premium"
3. Review features and pricing

### Step 3: Confirm Upgrade
1. Confirm subscription change
2. System processes upgrade
3. **30-day lock starts**
4. Instant access to premium features

### Step 4: Enjoy Premium
- Access reverse auctions immediately
- View analytics dashboard
- Premium badge on profile
- All features unlocked

---

## Downgrading to Free

### Step 1: Access Subscription Page
1. Go to "Subscription" page
2. See current plan (Premium)

### Step 2: Downgrade
1. Click "Downgrade to Free"
2. Confirm downgrade
3. **30-day lock starts**
4. Premium features remain active for 30 days

### Step 3: After 30 Days
- Premium features disabled
- Reverse auctions locked
- Analytics dashboard locked
- Back to FREE features only

---

## Subscription Status

### Check Your Status:
1. Go to profile page
2. See subscription tier badge
3. View lock status
4. Check next change date

### Status Indicators:
```
🟢 FREE - Active
🟡 PREMIUM - Active
🔒 LOCKED - Cannot change (X days remaining)
✅ UNLOCKED - Can change subscription
```

---

## Premium Feature Access Control

### How It Works:
System checks subscription before allowing access to premium features.

```
User tries to access premium feature
    ↓
Is user logged in?
    ├─ No → Redirect to login
    └─ Yes → Continue
        ↓
    Is subscription PREMIUM?
        ├─ No → Show "Premium Required" page
        └─ Yes → Allow access
```

### Protected Features:
- `/rfq/auctions` - Reverse auctions
- `/analytics/dashboard` - Analytics
- Bid submission in auctions
- Advanced search filters
- Premium-only pages

---

## Subscription Management

### View Subscription Details:
- Current tier (FREE/PREMIUM)
- Start date
- Lock status
- Next change available date
- Features included

### Change Subscription:
**If Unlocked:**
1. Go to subscription page
2. Click upgrade/downgrade button
3. Confirm change
4. 30-day lock starts

**If Locked:**
- See lock message
- View days remaining
- Wait for lock to expire
- Cannot change until unlocked

---

## Admin Subscription Management

### Admins Can:
- View all subscriptions
- See subscription history
- Override locks (if needed)
- Grant premium access
- Handle special cases

### Admin Page:
`/admin_subscriptions`

**Features:**
- List all companies
- Filter by subscription tier
- See lock status
- Modify subscriptions
- View revenue metrics

---

## Subscription Database

### Company Model:
```python
{
    "id": "company_id",
    "name": "Company Name",
    "subscription_tier": "FREE" or "PREMIUM",
    "subscription_start_date": "2024-01-01",
    "subscription_can_change_after": "2024-01-31",
    "created_at": "2024-01-01"
}
```

### Lock Calculation:
```python
can_change_after = start_date + 30 days
is_locked = current_date < can_change_after
```

---

## Pricing Page

### Features:
- Side-by-side plan comparison
- Feature checklist
- Clear pricing
- Upgrade/downgrade buttons
- FAQ section

### Access:
`/pricing` or click "Subscription Plan" in navigation

---

## Notifications

### Subscription Changes:
- ✅ Upgrade confirmed
- ✅ Downgrade scheduled
- ✅ Lock period started
- ✅ Lock period ending soon (3 days before)
- ✅ Lock period ended

---

## Troubleshooting

### Can't Access Premium Features
- **Not premium**: Upgrade subscription
- **Subscription expired**: Renew subscription
- **Not logged in**: Log in first
- **Wrong account**: Check you're on right account

### Can't Change Subscription
- **Locked**: Wait for 30-day lock to expire
- **Check lock date**: See when you can change
- **Contact admin**: For special circumstances

### Premium Features Not Working
- **Just upgraded**: Refresh page
- **Cache issue**: Clear browser cache
- **Session expired**: Log out and log back in
- **Check subscription**: Verify it's PREMIUM

---

## Best Practices

### For Users:
1. **Choose Wisely**: Consider your needs before upgrading
2. **Use Trial Period**: Test premium features
3. **Plan Ahead**: Remember the 30-day lock
4. **Track Usage**: Monitor if premium is worth it
5. **Renew On Time**: Don't lose access

### For Admins:
1. **Monitor Subscriptions**: Track upgrades/downgrades
2. **Handle Disputes**: Fair resolution process
3. **Communicate Clearly**: Explain lock system
4. **Offer Support**: Help users choose right plan
5. **Track Metrics**: Revenue and conversion rates

---

## API Endpoints

### For Developers:
- `GET /pricing` - Pricing page
- `GET /subscription/edit` - Subscription management
- `POST /api/subscription/upgrade` - Upgrade to premium
- `POST /api/subscription/downgrade` - Downgrade to free
- `GET /api/subscription/status` - Check subscription status

---

## Payment Integration

### Current Status:
- Subscription changes are instant
- No payment gateway integrated yet
- Manual payment tracking
- Admin can grant premium access

### Future Integration:
- Stripe payment gateway
- Automatic billing
- Invoice generation
- Payment history
- Refund processing

---

## Tips

### For Buyers:
💡 Upgrade to Premium for reverse auctions
💡 Use analytics to track spending
💡 Premium badge increases trust
💡 Plan subscription changes around busy periods

### For Suppliers:
💡 Premium access to all auctions
💡 Analytics show win rates
💡 Premium badge attracts buyers
💡 Competitive advantage in bidding
