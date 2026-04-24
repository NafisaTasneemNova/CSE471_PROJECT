# 🚀 Subscription System - Quick Start

## 1️⃣ Test the Setup (30 seconds)

```bash
cd TexBid-master/backend
python test_subscription_system.py
```

## 2️⃣ Start the Server

```bash
uvicorn main:app --reload
```

## 3️⃣ Visit These URLs

### 👀 View Pricing
```
http://localhost:8000/pricing
```

### 🔧 Admin Dashboard
```
http://localhost:8000/admin/subscriptions
```

### 🏠 Home Page
```
http://localhost:8000/
```

## 4️⃣ Test the Flow

### Create a Company (if needed)
1. Go to: `http://localhost:8000/verify/supplier`
2. Fill out the form
3. Submit → Company created with **FREE** tier

### Upgrade to Premium
1. Go to: `http://localhost:8000/admin/subscriptions`
2. Find your company
3. Click **"Upgrade to Premium"**
4. ✅ Done!

### Test Premium Features
1. Try accessing: `http://localhost:8000/rfq/auctions`
2. FREE users → See upgrade prompt
3. PREMIUM users → Full access

## 📋 Key Features

| Feature | URL | Access |
|---------|-----|--------|
| Pricing Page | `/pricing` | Everyone |
| Admin Dashboard | `/admin/subscriptions` | Admin |
| Reverse Auction | `/rfq/auctions` | PREMIUM |
| AI Price Prediction | `/api/predict-price` | PREMIUM |

## 🎯 Quick Commands

### Check Subscription Status (MongoDB)
```javascript
use texbid_db
db.companies.find({}, {name: 1, subscription_tier: 1})
```

### Upgrade a Company (MongoDB)
```javascript
db.companies.updateOne(
    {name: "Company Name"},
    {$set: {subscription_tier: "PREMIUM"}}
)
```

### Set All to FREE (Reset)
```javascript
db.companies.updateMany(
    {},
    {$set: {subscription_tier: "FREE"}}
)
```

## 💡 Usage in Code

### Protect a Route
```python
@app.get("/premium-feature", dependencies=[Depends(check_premium_status)])
async def my_feature():
    return {"message": "Premium only!"}
```

### Check Tier in Template
```html
{% if tier == 'PREMIUM' %}
    <a href="/premium-feature">Access Feature</a>
{% else %}
    <button onclick="showPremiumModal('Feature Name')">
        🔒 Upgrade Required
    </button>
{% endif %}
```

### Show Premium Modal
```html
<script src="/static/js/premium_modal.js"></script>
<script>
    showPremiumModal('Reverse Auction');
</script>
```

## ✅ Checklist

- [ ] Run test script
- [ ] Start server
- [ ] View pricing page
- [ ] Access admin dashboard
- [ ] Create/find a FREE company
- [ ] Upgrade to PREMIUM
- [ ] Test premium feature access
- [ ] Downgrade back to FREE

## 📚 Full Documentation

- `SUBSCRIPTION_SYSTEM_README.md` - Complete overview
- `backend/SUBSCRIPTION_SYSTEM_GUIDE.md` - Technical details
- `backend/test_subscription_system.py` - Test script

## 🎉 You're Ready!

The subscription system is fully implemented and ready to use!

**Need help?** Check the documentation files above.
