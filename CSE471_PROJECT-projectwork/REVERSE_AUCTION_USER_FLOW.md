# Reverse Auction Access - Complete User Flow

## Overview
The Reverse Auction feature is a **PREMIUM feature** in TexBid. This document explains the complete user journey from attempting to access the feature to successfully using it after upgrading.

---

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  User clicks "Reverse Auction" in navbar dropdown            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │ Check User     │
            │ Subscription   │
            └────────┬───────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────┐
│ FREE User     │         │ PREMIUM User │
└───────┬───────┘         └──────┬───────┘
        │                        │
        ▼                        ▼
┌──────────────────────┐  ┌─────────────────────┐
│ Redirect to          │  │ Access Granted!     │
│ Premium Required     │  │ Show Auction Page   │
│ Page                 │  │ /rfq/auctions       │
└──────┬───────────────┘  └─────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Show Premium         │
│ Benefits & Pricing   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User clicks          │
│ "Upgrade to Premium" │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Redirect to          │
│ /pricing page        │
│ (with return_to URL) │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User selects         │
│ Payment Method       │
│ (bKash or BRAC Bank) │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User completes       │
│ Payment Form         │
│ ($99 for 30 days)    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Payment Processing   │
│ (Simulated)          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ API Call:            │
│ POST /api/           │
│ subscription/update  │
│ {tier: "PREMIUM"}    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Database Updated:    │
│ - subscription_tier  │
│   = "PREMIUM"        │
│ - expires_at =       │
│   now + 30 days      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Success Modal Shows: │
│ - Congratulations!   │
│ - Features Unlocked  │
│ - "Access Premium    │
│   Feature Now" btn   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User clicks button   │
│ to return to         │
│ Reverse Auction      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ ✅ SUCCESS!          │
│ User now has access  │
│ to Reverse Auctions  │
└──────────────────────┘
```

---

## Step-by-Step User Journey

### Step 1: User Attempts to Access Reverse Auction
- **Location**: Navbar → Auction dropdown → "Reverse Auction"
- **URL**: `/rfq/auctions`
- **What Happens**: Backend checks user's subscription tier

### Step 2: Subscription Check (Backend)
```python
# In backend/main.py - /rfq/auctions route
has_premium = False
if user and database.db is not None:
    company = await database.db["companies"].find_one({"id": user.get("company_id")})
    if company and company.get("subscription_tier") == "PREMIUM":
        has_premium = True

if not has_premium:
    # Redirect to premium_required.html
    return templates.TemplateResponse("premium_required.html", {...})
```

### Step 3A: FREE User - Premium Required Page
- **Template**: `frontend/src/pages/premium_required.html`
- **Shows**:
  - 🔒 Lock icon with "Premium Feature Locked" message
  - Current plan status (FREE)
  - List of premium benefits:
    - ⚡ Reverse Auction
    - 💡 AI Recommendations
    - 📊 Order Analytics
    - 📄 Automated Contracts
  - Pricing: **$99/30 days**
  - **"Upgrade to Premium Now"** button

### Step 3B: PREMIUM User - Direct Access
- **Template**: `frontend/src/pages/rfq_auctions.html`
- **Shows**: List of active reverse auction RFQs
- User can immediately participate in auctions

### Step 4: User Clicks "Upgrade to Premium"
- **From**: `premium_required.html`
- **To**: `/pricing?return_to=/rfq/auctions`
- **Note**: The `return_to` parameter remembers where the user wanted to go

### Step 5: Pricing Page
- **Template**: `frontend/src/pages/pricing.html`
- **Shows**:
  - Personalized greeting with current plan
  - Premium plan details ($99/month)
  - Feature comparison table
  - **"Upgrade to Premium"** button

### Step 6: Payment Method Selection
- **Triggered by**: Clicking "Upgrade to Premium"
- **Modal Shows**: Two payment options
  1. **bKash** - Mobile wallet payment
  2. **BRAC Bank** - Card payment

### Step 7: Payment Form
#### Option A: bKash Payment
- **Fields**:
  - bKash Account Number (01XXXXXXXXX)
  - PIN (4 digits)
- **Amount**: ৳7,920 ($99 × ৳80)

#### Option B: BRAC Bank Payment
- **Fields**:
  - Card Number
  - Expiry Date (MM/YY)
  - CVV
  - Cardholder Name
- **Amount**: ৳7,920 ($99 × ৳80)

### Step 8: Payment Processing
```javascript
// In pricing.html JavaScript
function updateSubscriptionToPremium() {
    fetch('/api/subscription/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({tier: 'PREMIUM'})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSubscriptionSuccess(companyName, 'Premium');
        }
    });
}
```

### Step 9: Database Update (Backend)
```python
# In backend/main.py - /api/subscription/update route
await database.db["companies"].update_one(
    {"id": company_id},
    {
        "$set": {
            "subscription_tier": "PREMIUM",
            "subscription_expires_at": datetime.utcnow() + timedelta(days=30),
            "subscription_start_date": datetime.utcnow()
        }
    }
)
```

### Step 10: Success Modal
- **Shows**:
  - ✅ Congratulations message
  - "You are now on the PREMIUM plan!"
  - Valid for 30 days
  - List of unlocked features
  - ⚠️ Expiry warning
  - **"Access Premium Feature Now"** button (if return_to exists)
  - "Continue" button

### Step 11: Return to Reverse Auction
- **User clicks**: "Access Premium Feature Now"
- **Redirects to**: `/rfq/auctions` (from return_to parameter)
- **Result**: ✅ User now has full access to Reverse Auctions!

---

## Key Features of the Flow

### 1. **Seamless Redirect Chain**
```
/rfq/auctions → /pricing?return_to=/rfq/auctions → /rfq/auctions
```
The user is automatically returned to the feature they wanted after upgrading.

### 2. **Clear Value Proposition**
At every step, users see:
- What they're missing (premium features)
- What they'll get (feature list)
- How much it costs ($99/30 days)
- How long it lasts (30 days)

### 3. **Multiple Payment Options**
- bKash (mobile wallet) - Popular in Bangladesh
- BRAC Bank (card payment) - Traditional banking

### 4. **Transparent Pricing**
- Shows both USD ($99) and local currency (৳7,920)
- Clear 30-day duration
- Auto-downgrade warning after expiry

### 5. **Immediate Access**
- After payment, users can immediately access the feature
- No waiting period or manual approval needed

---

## Testing the Flow

### Quick Test (Manual Database Update)
```bash
# Check current subscriptions
python check_subscription.py

# Upgrade a user to PREMIUM
python upgrade_to_premium.py
```

### Full Flow Test
1. **Start as FREE user**
   ```bash
   # Login as a FREE user
   # Navigate to: http://localhost:8000
   ```

2. **Try to access Reverse Auction**
   - Click: Navbar → Auction → Reverse Auction
   - Should see: Premium Required page

3. **Upgrade to Premium**
   - Click: "Upgrade to Premium Now"
   - Should redirect to: `/pricing?return_to=/rfq/auctions`

4. **Complete Payment**
   - Click: "Upgrade to Premium"
   - Select: bKash or BRAC Bank
   - Fill form and submit
   - Should see: Success modal

5. **Access Feature**
   - Click: "Access Premium Feature Now"
   - Should redirect to: `/rfq/auctions`
   - Should see: ✅ Auction list page

---

## API Endpoints

### Check Subscription
```http
GET /rfq/auctions
Authorization: Bearer <token>

Response (FREE user):
- Returns: premium_required.html template

Response (PREMIUM user):
- Returns: rfq_auctions.html template with auction list
```

### Update Subscription
```http
POST /api/subscription/update
Content-Type: application/json

{
  "tier": "PREMIUM"
}

Response:
{
  "success": true,
  "message": "Subscription updated successfully"
}
```

---

## Database Schema

### Company Document
```javascript
{
  "id": "company_123",
  "name": "Example Company",
  "subscription_tier": "PREMIUM",  // "FREE" or "PREMIUM"
  "subscription_start_date": ISODate("2026-05-04T10:00:00Z"),
  "subscription_expires_at": ISODate("2026-06-03T10:00:00Z"),
  "subscription_can_change_after": ISODate("2026-06-03T10:00:00Z")
}
```

---

## Premium Features

Once upgraded to PREMIUM, users get access to:

1. **⚡ Reverse Auction**
   - Real-time competitive bidding
   - Live leaderboards
   - Multiple bids per RFQ

2. **💡 AI Recommendations**
   - Smart supplier matching
   - Price predictions
   - Bid optimization

3. **📊 Order Analytics**
   - Advanced insights
   - Detailed reports
   - Performance metrics

4. **📄 Automated Contracts**
   - One-click generation
   - Template management
   - Digital signatures

5. **🎯 Additional Benefits**
   - Priority Support (24/7)
   - Unlimited RFQs & Auctions
   - Custom Branding Options

---

## Subscription Lifecycle

### Day 1-30: Active Premium
- Full access to all premium features
- Cannot downgrade (30-day lock)
- Can view expiry date on pricing page

### Day 30: Expiration
- Automatic downgrade to FREE
- Premium features become locked
- User receives notification
- Can re-subscribe anytime

### After Expiration
- User reverts to FREE plan
- Can upgrade again following the same flow
- No data loss - all history preserved

---

## Troubleshooting

### Issue: "Reverse Auction button not working"
**Cause**: User has FREE subscription
**Solution**: Follow the upgrade flow above

### Issue: "Payment completed but still can't access"
**Cause**: Database not updated or session not refreshed
**Solution**: 
1. Logout and login again
2. Check database: `python check_subscription.py`
3. Manually update if needed: `python upgrade_to_premium.py`

### Issue: "Already paid but subscription expired"
**Cause**: 30 days have passed
**Solution**: Subscribe again for another 30 days

---

## Summary

The Reverse Auction feature is working correctly! It's a premium feature that requires users to:

1. ✅ Click "Reverse Auction" → See premium required page
2. ✅ Click "Upgrade to Premium" → Go to pricing page
3. ✅ Select payment method → Complete payment form
4. ✅ Payment processed → Subscription updated to PREMIUM
5. ✅ Click "Access Feature" → Return to Reverse Auction
6. ✅ **SUCCESS!** → Full access to reverse auctions

The flow is designed to be seamless, transparent, and user-friendly, ensuring users understand the value they're getting and can easily upgrade when they want to access premium features.
