# TexBid - Garment Order Exchange Platform

## 📚 Documentation

All documentation has been organized into comprehensive guides:

### 🚀 Getting Started
- **[QUICK_START.md](QUICK_START.md)** - Quick setup and installation guide
- **[SETUP_AND_AUTH_GUIDE.md](SETUP_AND_AUTH_GUIDE.md)** - Complete setup, authentication, and security guide

### 👥 User Guides
- **[RFQ_GUIDE.md](RFQ_GUIDE.md)** - Everything about RFQs (create, browse, edit, delete)
- **[REVERSE_AUCTION_GUIDE.md](REVERSE_AUCTION_GUIDE.md)** - Reverse auction system guide
- **[SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md)** - Subscription tiers, upgrades, and 30-day lock system
- **[NOTIFICATION_GUIDE.md](NOTIFICATION_GUIDE.md)** - Notification system and troubleshooting

### 🔧 Admin Guides
- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Complete admin system guide (setup, features, management)

### 📊 Analytics & Features
- **[BUYER_SUPPLIER_ANALYTICS.md](BUYER_SUPPLIER_ANALYTICS.md)** - Analytics dashboard guide
- **[ORDER_ANALYTICS_DASHBOARD.md](ORDER_ANALYTICS_DASHBOARD.md)** - Order analytics features
- **[PAYMENT_FLOW_GUIDE.md](PAYMENT_FLOW_GUIDE.md)** - Payment and escrow system

---

## 🎯 Quick Links

### For Buyers:
- Create RFQ: Hover over "RFQ" → Click "Create RFQ"
- Browse RFQs: Hover over "RFQ" → Click "Browse RFQs"
- Reverse Auctions: Click "Reverse Auctions" (Premium only)
- Analytics: Click "Analytics" (Premium only)

### For Suppliers:
- Browse RFQs: Hover over "RFQ" → Click "Browse RFQs"
- Submit Bids: Click on any RFQ → Submit quote
- Reverse Auctions: Click "Reverse Auctions" (Premium only)
- Analytics: Click "Analytics" (Premium only)

### For Admins:
- Admin Login: `http://localhost:8000/admin/login`
- Admin Dashboard: `http://localhost:8000/admin/dashboard`

---

## 🏗️ Project Structure

```
TexBid-master/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # MongoDB connection
│   ├── requirements.txt     # Python dependencies
│   ├── make_admin.py        # Admin creation script
│   └── make_me_admin.py     # Quick admin script
│
├── frontend/
│   └── src/
│       ├── pages/           # HTML templates
│       └── components/      # CSS and JS
│
└── Documentation/
    ├── README.md            # This file
    ├── QUICK_START.md       # Quick start guide
    ├── ADMIN_GUIDE.md       # Admin guide
    ├── RFQ_GUIDE.md         # RFQ guide
    ├── REVERSE_AUCTION_GUIDE.md
    ├── SUBSCRIPTION_GUIDE.md
    ├── NOTIFICATION_GUIDE.md
    └── SETUP_AND_AUTH_GUIDE.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd TexBid-master/backend
pip install -r requirements.txt
```

### 2. Start MongoDB
Make sure MongoDB is running on `localhost:27017`

### 3. Start Backend
```bash
python main.py
```

### 4. Access Application
Open browser: `http://localhost:8000`

---

## 🔑 Key Features

### For All Users:
- ✅ Browse RFQs
- ✅ Company profiles
- ✅ Supplier directory
- ✅ Basic messaging

### For Buyers:
- ✅ Create RFQs
- ✅ Manage RFQs (edit/delete)
- ✅ Receive bids
- ✅ Create reverse auctions (Premium)
- ✅ Analytics dashboard (Premium)

### For Suppliers:
- ✅ Browse RFQs
- ✅ Submit bids
- ✅ Participate in auctions (Premium)
- ✅ Analytics dashboard (Premium)

### For Admins:
- ✅ View all users
- ✅ View all companies
- ✅ View all RFQs
- ✅ Manage subscriptions
- ✅ Platform analytics

---

## 📖 Documentation Index

### By Topic:

**Authentication & Setup:**
- [SETUP_AND_AUTH_GUIDE.md](SETUP_AND_AUTH_GUIDE.md)

**RFQs:**
- [RFQ_GUIDE.md](RFQ_GUIDE.md)

**Auctions:**
- [REVERSE_AUCTION_GUIDE.md](REVERSE_AUCTION_GUIDE.md)

**Subscriptions:**
- [SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md)

**Notifications:**
- [NOTIFICATION_GUIDE.md](NOTIFICATION_GUIDE.md)

**Admin:**
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md)

**Analytics:**
- [BUYER_SUPPLIER_ANALYTICS.md](BUYER_SUPPLIER_ANALYTICS.md)
- [ORDER_ANALYTICS_DASHBOARD.md](ORDER_ANALYTICS_DASHBOARD.md)

**Payments:**
- [PAYMENT_FLOW_GUIDE.md](PAYMENT_FLOW_GUIDE.md)

---

## 🆘 Need Help?

1. **Check the relevant guide** from the list above
2. **Search the documentation** for your specific issue
3. **Check troubleshooting sections** in each guide
4. **Review the Quick Start** if you're just getting started

---

## 🔧 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Frontend**: HTML, TailwindCSS, JavaScript
- **Authentication**: Session-based with bcrypt
- **Real-time**: Auto-refresh notifications

---

## 📝 Notes

- All guides are comprehensive and include troubleshooting
- Each guide is self-contained and can be read independently
- Code examples and API endpoints included where relevant
- Best practices and tips included in each guide

---

## 🎉 Getting Started

New to TexBid? Start here:
1. Read [QUICK_START.md](QUICK_START.md)
2. Follow [SETUP_AND_AUTH_GUIDE.md](SETUP_AND_AUTH_GUIDE.md)
3. Explore feature-specific guides as needed

Happy bidding! 🚀
