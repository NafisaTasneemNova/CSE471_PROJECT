# TexBid — Subscription System

## Plans

| Feature | Free | Premium |
|---------|------|---------|
| Browse RFQs | ✅ | ✅ |
| Submit bids | ✅ (1 per RFQ) | ✅ (unlimited) |
| Auction Room | ❌ | ✅ |
| Analytics Dashboard | ❌ | ✅ |
| AI Recommendations | ❌ | ✅ |

## Upgrading to Premium
1. Go to `http://localhost:8000/pricing`
2. Click **Upgrade to Premium**
3. Complete payment via bKash or card
4. Premium activates immediately for **30 days**

## 30-Day Lock
- Once you purchase Premium, your plan is **locked for 30 days**
- You cannot downgrade during this period
- After 30 days, plan auto-reverts to FREE unless renewed
- **Free users are never locked** — they can upgrade anytime

## Subscription Expiry
- Premium expires after 30 days
- You'll see a countdown on the pricing page: "Expires in X days"
- After expiry, access to premium features is removed automatically

## Admin Management
Admins can manually toggle subscriptions:
- `http://localhost:8000/admin/subscriptions`
- Or via API: `POST /api/admin/toggle-subscription`

## MongoDB Quick Commands

```javascript
// Check all subscription tiers
db.companies.find({}, { name: 1, subscription_tier: 1 })

// Manually upgrade a company
db.companies.updateOne(
  { name: "Company Name" },
  { $set: { subscription_tier: "PREMIUM", subscription_expires_at: new Date(Date.now() + 30*24*60*60*1000) } }
)

// Reset all to FREE
db.companies.updateMany({}, { $set: { subscription_tier: "FREE" } })
```
