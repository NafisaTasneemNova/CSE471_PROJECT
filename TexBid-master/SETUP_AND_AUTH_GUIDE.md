# Setup & Authentication Guide

## Quick Start

### Prerequisites:
- Python 3.8+
- MongoDB running on localhost:27017
- Node.js (for frontend, if needed)

### Installation:

```bash
# 1. Navigate to backend
cd TexBid-master/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start MongoDB (if not running)
# Windows: mongod
# Mac/Linux: sudo systemctl start mongod

# 4. Start backend server
python main.py

# Server runs on: http://localhost:8000
```

---

## Authentication System

### User Registration

**Step 1: Access Registration**
- Go to `http://localhost:8000/register`
- Choose role: BUYER or SUPPLIER

**Step 2: Fill Information**
- Email (unique)
- Password (hashed with bcrypt)
- Company name
- Company details

**Step 3: Account Created**
- User account created
- Company profile created
- Automatic login
- Redirect to home

### User Login

**Step 1: Access Login**
- Go to `http://localhost:8000/login`

**Step 2: Enter Credentials**
- Email
- Password

**Step 3: Authentication**
- Password verified with bcrypt
- Session token created
- Cookie set (30-day expiry)
- Redirect to home

### Session Management

**How It Works:**
```python
# Login creates session
session_token = secrets.token_urlsafe(32)
sessions[session_token] = user_id

# Cookie stores token
response.set_cookie("session", session_token, httponly=True, max_age=86400*30)

# Protected routes check session
user = sessions.get(session_token)
if not user:
    redirect_to_login()
```

**Session Duration:**
- 30 days by default
- Extends on activity
- Cleared on logout
- Stored in memory (not database)

---

## User Roles

### BUYER
**Can:**
- ✅ Create RFQs
- ✅ Browse RFQs
- ✅ Create reverse auctions (Premium)
- ✅ View analytics (Premium)
- ✅ Manage subscriptions
- ❌ Cannot bid on RFQs

### SUPPLIER
**Can:**
- ✅ Browse RFQs
- ✅ Submit bids
- ✅ Participate in auctions (Premium)
- ✅ View analytics (Premium)
- ✅ Manage subscriptions
- ❌ Cannot create RFQs

### ADMIN
**Can:**
- ✅ Everything buyers/suppliers can do
- ✅ Access admin panel
- ✅ View all users
- ✅ View all companies
- ✅ View all RFQs
- ✅ Manage subscriptions
- ✅ Override restrictions

---

## Protected Routes

### Login Required:
```python
@app.get("/protected")
async def protected_route(user: dict = Depends(require_login)):
    # User must be logged in
    pass
```

**Routes:**
- `/profile`
- `/rfq/create`
- `/rfq/auctions`
- `/analytics/dashboard`
- `/subscription/edit`
- All `/api/*` endpoints

### Admin Only:
```python
@app.get("/admin/dashboard")
async def admin_route(admin: dict = Depends(require_admin)):
    # User must be admin
    pass
```

**Routes:**
- `/admin/login`
- `/admin/dashboard`
- `/admin/users`
- `/admin/companies`
- `/admin/rfqs`
- All `/api/admin/*` endpoints

### Premium Only:
```python
# Check in route handler
if company.subscription_tier != "PREMIUM":
    redirect_to_premium_required()
```

**Routes:**
- `/rfq/auctions` (view & participate)
- `/analytics/dashboard`
- Bid submission in auctions

---

## Password Security

### Hashing:
```python
import bcrypt

# Hash password on registration
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verify on login
is_valid = bcrypt.checkpw(password.encode(), stored_hash)
```

### Best Practices:
- ✅ Passwords never stored in plain text
- ✅ Bcrypt with salt
- ✅ Minimum 8 characters (recommended)
- ✅ Hash comparison in constant time
- ❌ Never log passwords
- ❌ Never send passwords in URLs

---

## Database Structure

### Users Collection:
```python
{
    "id": "uuid",
    "email": "user@example.com",
    "password_hash": "bcrypt_hash",
    "company_id": "company_uuid",
    "is_admin": false,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
}
```

### Companies Collection:
```python
{
    "id": "uuid",
    "name": "Company Name",
    "role": "BUYER" or "SUPPLIER",
    "overall_status": "VERIFIED",
    "trust_score": 85,
    "subscription_tier": "PREMIUM",
    "subscription_start_date": "2024-01-01",
    "subscription_can_change_after": "2024-01-31",
    "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Environment Variables

### Configuration:
```bash
# MongoDB connection
MONGO_URL=mongodb://localhost:27017

# Database name
DATABASE_NAME=texbid_db

# Session secret (optional)
SESSION_SECRET=your_secret_key_here
```

### Setting Variables:
```bash
# Windows
set MONGO_URL=mongodb://localhost:27017

# Mac/Linux
export MONGO_URL=mongodb://localhost:27017
```

---

## Troubleshooting

### Can't Connect to MongoDB
**Error**: `Could not connect to MongoDB`

**Solutions:**
1. Check if MongoDB is running: `mongod --version`
2. Start MongoDB service
3. Check connection string in `database.py`
4. Verify port 27017 is open

### Login Not Working
**Error**: `Invalid email or password`

**Solutions:**
1. Check email is correct
2. Check password is correct
3. Verify user exists in database
4. Check password hash is valid

### Session Expired
**Error**: `Please log in to continue`

**Solutions:**
1. Log in again
2. Check cookie settings
3. Clear browser cookies
4. Check session storage

### Can't Access Protected Route
**Error**: `403 Forbidden` or redirect to login

**Solutions:**
1. Make sure you're logged in
2. Check user role (buyer/supplier/admin)
3. Verify subscription tier (for premium features)
4. Clear cache and try again

---

## Security Best Practices

### For Developers:
1. ✅ Always use `require_login` for protected routes
2. ✅ Check user roles before allowing actions
3. ✅ Validate all input data
4. ✅ Use HTTPS in production
5. ✅ Set secure cookie flags
6. ✅ Implement rate limiting
7. ✅ Log security events
8. ❌ Never expose sensitive data in errors
9. ❌ Never trust client-side validation alone
10. ❌ Never store passwords in plain text

### For Users:
1. ✅ Use strong passwords
2. ✅ Don't share credentials
3. ✅ Log out on shared computers
4. ✅ Keep email secure
5. ❌ Don't reuse passwords
6. ❌ Don't save passwords in browser (on shared computers)

---

## API Authentication

### Session Cookie:
```javascript
// Frontend automatically sends cookie
fetch('/api/protected', {
    credentials: 'include'  // Include cookies
})
```

### Checking Auth Status:
```javascript
// Check if logged in
const response = await fetch('/api/user/me');
if (response.ok) {
    const user = await response.json();
    // User is logged in
} else {
    // User is not logged in
}
```

---

## Logout

### Process:
1. User clicks "Log Out"
2. POST request to `/logout`
3. Session deleted from server
4. Cookie deleted from browser
5. Redirect to home page

### Implementation:
```python
@app.get("/logout")
async def logout(session: Optional[str] = Cookie(None)):
    if session and session in sessions:
        del sessions[session]
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session")
    return response
```

---

## Tips

### For Development:
💡 Use MongoDB Compass to view database
💡 Check browser console for errors
💡 Use Postman to test API endpoints
💡 Enable debug logging in development
💡 Test with different user roles

### For Production:
💡 Use environment variables for secrets
💡 Enable HTTPS
💡 Set secure cookie flags
💡 Implement rate limiting
💡 Monitor authentication logs
💡 Regular security audits
💡 Keep dependencies updated
