# Fix Password Reset Issue

## The Problem
You're getting an error because `bcrypt` is not installed.

## The Solution (2 Steps)

### Step 1: Install bcrypt
```bash
pip install bcrypt
```

### Step 2: Reset your password
```bash
cd backend
python reset_password.py
```

Then:
- Select user #1 (mdmotiurrahmanmim@gmail.com)
- Enter password: `admin1234`
- Confirm: `admin1234`
- Done!

---

## Complete Commands (Copy & Paste)

```bash
# Install bcrypt
pip install bcrypt

# Go to backend directory
cd D:\Cse471\CSE471_PROJECT\CSE471_PROJECT-projectwork\backend

# Reset password
python reset_password.py
```

---

## After Installing bcrypt

You'll see:
```
✅ SUCCESS! Password reset for mdmotiurrahmanmim@gmail.com

📋 NEW LOGIN CREDENTIALS:
   Email: mdmotiurrahmanmim@gmail.com
   Password: admin1234

🌐 LOGIN:
   Go to: http://localhost:8000/login
```

---

## Then Log In

1. Go to: `http://localhost:8000/login`
2. Email: `mdmotiurrahmanmim@gmail.com`
3. Password: `admin1234`
4. Click Login

---

## Access Admin Panel

After logging in:
1. Go to: `http://localhost:8000/admin/subscriptions`
2. Find your company
3. Toggle to PREMIUM
4. Access Reverse Auction: `http://localhost:8000/rfq/auctions`

---

## If pip install bcrypt fails

Try:
```bash
# Update pip first
python -m pip install --upgrade pip

# Then install bcrypt
pip install bcrypt

# Or install with specific version
pip install bcrypt==4.0.1
```

---

## Alternative: Use requirements.txt

```bash
# Install all backend requirements
cd backend
pip install -r requirements.txt
```

This will install bcrypt and all other dependencies.
