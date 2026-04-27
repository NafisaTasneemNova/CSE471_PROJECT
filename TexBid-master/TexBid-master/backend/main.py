from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Depends, Header, Cookie, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import hashlib
import secrets

from database import connect_to_mongo, close_mongo_connection, db
from models import RoleEnum, OverallStatusEnum, CompanyModel, LegalAndCapacityModel, CertificationModel, CertTypeEnum, VerificationStatusEnum, RFQModel, RFQStatusEnum, BidModel, SubscriptionTierEnum, UserModel, NotificationModel, NotificationTypeEnum, ContractModel, ContractStatusEnum, EscrowStatusEnum, IncotermEnum, PaymentModel, ShippingCalculateRequest, ShippingMethodEnum, ShippingRateModel
from auth import (
    create_access_token, create_refresh_token, refresh_access_token,
    get_current_user_jwt, require_login_jwt, require_buyer, require_supplier, require_admin_jwt,
)
import io
import math
from colorthief import ColorThief
from datetime import datetime, timedelta


# ----------------------------------------
# PORT SEEDING
# ----------------------------------------

SEED_PORTS = [
    {"code": "BDCGP", "name": "Chittagong", "country": "Bangladesh", "region": "Asia", "distance_factor": 1.0},
    {"code": "BDMGL", "name": "Mongla", "country": "Bangladesh", "region": "Asia", "distance_factor": 1.0},
    {"code": "CNSHA", "name": "Shanghai", "country": "China", "region": "Asia", "distance_factor": 1.1},
    {"code": "CNTAO", "name": "Qingdao", "country": "China", "region": "Asia", "distance_factor": 1.1},
    {"code": "CNNGB", "name": "Ningbo", "country": "China", "region": "Asia", "distance_factor": 1.1},
    {"code": "CNSZX", "name": "Shenzhen", "country": "China", "region": "Asia", "distance_factor": 1.1},
    {"code": "INBOM", "name": "Mumbai", "country": "India", "region": "Asia", "distance_factor": 1.2},
    {"code": "INNSA", "name": "Nhava Sheva", "country": "India", "region": "Asia", "distance_factor": 1.2},
    {"code": "PKKAR", "name": "Karachi", "country": "Pakistan", "region": "Asia", "distance_factor": 1.2},
    {"code": "LKCMB", "name": "Colombo", "country": "Sri Lanka", "region": "Asia", "distance_factor": 1.15},
    {"code": "VNSGN", "name": "Ho Chi Minh City", "country": "Vietnam", "region": "Asia", "distance_factor": 1.05},
    {"code": "IDJKT", "name": "Jakarta", "country": "Indonesia", "region": "Asia", "distance_factor": 1.1},
    {"code": "MYPKG", "name": "Port Klang", "country": "Malaysia", "region": "Asia", "distance_factor": 1.1},
    {"code": "SGSIN", "name": "Singapore", "country": "Singapore", "region": "Asia", "distance_factor": 1.0},
    {"code": "TRIST", "name": "Istanbul", "country": "Turkey", "region": "Europe", "distance_factor": 2.0},
    {"code": "NLRTM", "name": "Rotterdam", "country": "Netherlands", "region": "Europe", "distance_factor": 2.5},
    {"code": "DEHAM", "name": "Hamburg", "country": "Germany", "region": "Europe", "distance_factor": 2.5},
    {"code": "GBFXT", "name": "Felixstowe", "country": "United Kingdom", "region": "Europe", "distance_factor": 2.6},
    {"code": "FRMRS", "name": "Marseille", "country": "France", "region": "Europe", "distance_factor": 2.4},
    {"code": "ITGOA", "name": "Genoa", "country": "Italy", "region": "Europe", "distance_factor": 2.4},
    {"code": "USNYC", "name": "New York", "country": "United States", "region": "Americas", "distance_factor": 3.5},
    {"code": "USLAX", "name": "Los Angeles", "country": "United States", "region": "Americas", "distance_factor": 3.2},
    {"code": "CAYVR", "name": "Vancouver", "country": "Canada", "region": "Americas", "distance_factor": 3.3},
    {"code": "BRSSZ", "name": "Santos", "country": "Brazil", "region": "Americas", "distance_factor": 3.8},
    {"code": "AUPOL", "name": "Port of Melbourne", "country": "Australia", "region": "Oceania", "distance_factor": 2.8},
    {"code": "ZASPE", "name": "Cape Town", "country": "South Africa", "region": "Africa", "distance_factor": 3.0},
    {"code": "EGPSD", "name": "Port Said", "country": "Egypt", "region": "Africa", "distance_factor": 2.2},
]

DEFAULT_RATES = [
    {"origin_region": "Asia", "dest_region": "Asia", "method": "SEA", "base_rate_per_kg": 0.80},
    {"origin_region": "Asia", "dest_region": "Asia", "method": "AIR", "base_rate_per_kg": 4.50},
    {"origin_region": "Asia", "dest_region": "Asia", "method": "ROAD", "base_rate_per_kg": 1.20},
    {"origin_region": "Asia", "dest_region": "Europe", "method": "SEA", "base_rate_per_kg": 1.80},
    {"origin_region": "Asia", "dest_region": "Europe", "method": "AIR", "base_rate_per_kg": 7.50},
    {"origin_region": "Asia", "dest_region": "Americas", "method": "SEA", "base_rate_per_kg": 2.20},
    {"origin_region": "Asia", "dest_region": "Americas", "method": "AIR", "base_rate_per_kg": 9.00},
    {"origin_region": "Asia", "dest_region": "Oceania", "method": "SEA", "base_rate_per_kg": 1.60},
    {"origin_region": "Asia", "dest_region": "Africa", "method": "SEA", "base_rate_per_kg": 2.00},
    {"origin_region": "Europe", "dest_region": "Europe", "method": "SEA", "base_rate_per_kg": 0.60},
    {"origin_region": "Europe", "dest_region": "Europe", "method": "ROAD", "base_rate_per_kg": 0.90},
    {"origin_region": "Europe", "dest_region": "Americas", "method": "SEA", "base_rate_per_kg": 1.50},
    {"origin_region": "Americas", "dest_region": "Americas", "method": "SEA", "base_rate_per_kg": 0.70},
    {"origin_region": "Americas", "dest_region": "Europe", "method": "SEA", "base_rate_per_kg": 1.50},
]

INCOTERMS_DATA = {
    "EXW": {
        "name": "Ex Works",
        "description": "The seller makes goods available at their premises. The buyer bears all costs and risks from that point.",
        "seller_pays": [],
        "buyer_pays": ["loading", "export_clearance", "main_carriage", "insurance", "import_duties", "last_mile"],
        "seller_cost_multiplier": 0.0,
        "includes_insurance": False,
        "includes_duties": False,
    },
    "FOB": {
        "name": "Free On Board",
        "description": "Seller delivers goods on board the vessel at the named port of shipment. Risk transfers when goods are on board.",
        "seller_pays": ["export_clearance", "loading", "port_charges"],
        "buyer_pays": ["main_carriage", "insurance", "import_duties", "last_mile"],
        "seller_cost_multiplier": 0.15,
        "includes_insurance": False,
        "includes_duties": False,
    },
    "CFR": {
        "name": "Cost and Freight",
        "description": "Seller pays freight to destination port. Risk transfers when goods are on board at origin.",
        "seller_pays": ["export_clearance", "loading", "port_charges", "main_carriage"],
        "buyer_pays": ["insurance", "import_duties", "last_mile"],
        "seller_cost_multiplier": 1.0,
        "includes_insurance": False,
        "includes_duties": False,
    },
    "CIF": {
        "name": "Cost, Insurance and Freight",
        "description": "Seller pays freight and insurance to destination port. Risk transfers when goods are on board at origin.",
        "seller_pays": ["export_clearance", "loading", "port_charges", "main_carriage", "insurance"],
        "buyer_pays": ["import_duties", "last_mile"],
        "seller_cost_multiplier": 1.0,
        "includes_insurance": True,
        "includes_duties": False,
    },
    "DAP": {
        "name": "Delivered at Place",
        "description": "Seller delivers goods to named destination, ready for unloading. Buyer pays import duties.",
        "seller_pays": ["export_clearance", "loading", "main_carriage", "insurance", "destination_charges"],
        "buyer_pays": ["import_duties", "unloading"],
        "seller_cost_multiplier": 1.0,
        "includes_insurance": True,
        "includes_duties": False,
    },
    "DDP": {
        "name": "Delivered Duty Paid",
        "description": "Seller bears all costs including import duties and taxes to the named destination. Maximum seller responsibility.",
        "seller_pays": ["export_clearance", "loading", "main_carriage", "insurance", "import_duties", "last_mile"],
        "buyer_pays": [],
        "seller_cost_multiplier": 1.0,
        "includes_insurance": True,
        "includes_duties": True,
    },
}

TRANSIT_DAYS = {
    ("Asia", "Asia", "SEA"): 14,
    ("Asia", "Asia", "AIR"): 3,
    ("Asia", "Asia", "ROAD"): 10,
    ("Asia", "Europe", "SEA"): 28,
    ("Asia", "Europe", "AIR"): 5,
    ("Asia", "Americas", "SEA"): 35,
    ("Asia", "Americas", "AIR"): 6,
    ("Asia", "Oceania", "SEA"): 21,
    ("Asia", "Africa", "SEA"): 25,
    ("Europe", "Europe", "SEA"): 7,
    ("Europe", "Europe", "ROAD"): 5,
    ("Europe", "Americas", "SEA"): 14,
    ("Americas", "Americas", "SEA"): 10,
    ("Americas", "Europe", "SEA"): 14,
}


async def seed_ports():
    """Seed the ports collection with major textile trade ports if empty."""
    from database import db
    if db is None:
        print("⚠️  Port seeding skipped: database not available")
        return

    count = await db["ports"].count_documents({})
    if count >= len(SEED_PORTS):
        print(f"✅ Ports already seeded ({count} ports)")
    else:
        await db["ports"].delete_many({})
        await db["ports"].insert_many(SEED_PORTS)
        print(f"✅ Seeded {len(SEED_PORTS)} ports")

    # Seed default rates if empty
    rate_count = await db["shipping_rates"].count_documents({})
    if rate_count == 0:
        import uuid as _uuid
        from datetime import datetime as _dt
        rates_to_insert = []
        for r in DEFAULT_RATES:
            rates_to_insert.append({
                "id": str(_uuid.uuid4()),
                "origin_region": r["origin_region"],
                "dest_region": r["dest_region"],
                "method": r["method"],
                "base_rate_per_kg": r["base_rate_per_kg"],
                "updated_at": _dt.utcnow(),
            })
        await db["shipping_rates"].insert_many(rates_to_insert)
        print(f"✅ Seeded {len(rates_to_insert)} default shipping rates")

    # Seed global shipping config if not present
    existing_config = await db["shipping_config"].find_one({"_id": "global"})
    if not existing_config:
        await db["shipping_config"].insert_one({
            "_id": "global",
            # Insurance
            "insurance_rate": 0.003,          # 0.3% of freight cost
            # Port / handling fees (flat USD per shipment)
            "port_fee_sea": 320.0,
            "port_fee_air": 180.0,
            "port_fee_road": 90.0,
            # Routing factors (multiplied onto base distance)
            "routing_factor_sea": 1.2,
            "routing_factor_air": 1.05,
            "routing_factor_road": 1.3,
            # Speed (km/h) for transit time estimation
            "speed_sea_kmh": 37.0,
            "speed_air_kmh": 800.0,
            "speed_road_kmh": 60.0,
            # Port handling days added to transit time
            "handling_days_sea": 4.0,
            "handling_days_air": 1.5,
            "handling_days_road": 2.0,
            # Min / max freight charge (USD) per shipment
            "min_freight_sea": 150.0,
            "max_freight_sea": 50000.0,
            "min_freight_air": 80.0,
            "max_freight_air": 30000.0,
            "min_freight_road": 50.0,
            "max_freight_road": 20000.0,
            # Air freight distance zone thresholds (km) and rate multipliers
            "air_zone_short_max_km": 3000.0,   # short-haul ≤ 3000 km
            "air_zone_mid_max_km": 8000.0,     # mid-haul ≤ 8000 km
            "air_zone_short_multiplier": 1.0,
            "air_zone_mid_multiplier": 1.2,
            "air_zone_long_multiplier": 1.5,
            # Import duty estimate rate (used for DDP)
            "import_duty_rate": 0.12,
            "updated_at": datetime.utcnow().isoformat(),
        })
        print("✅ Seeded default shipping_config")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await connect_to_mongo()
    await seed_ports()
    # Create TTL index on sessions collection so expired sessions auto-delete
    from database import db as _db
    if _db is not None:
        try:
            await _db["sessions"].create_index("expires_at", expireAfterSeconds=0)
            print("✅ Sessions TTL index ensured")
        except Exception:
            pass
    yield
    # Shutdown logic
    await close_mongo_connection()

app = FastAPI(title="TexBid API", lifespan=lifespan)

# Add CORS middleware to allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend/src/components"), name="static")

templates = Jinja2Templates(directory="../frontend/src/pages")

# ----------------------------------------
# AUTHENTICATION HELPERS
# ----------------------------------------

# MongoDB-backed session store — survives server restarts
# Sessions are stored in the 'sessions' collection with a 30-day TTL index

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash

async def create_session(user_id: str) -> str:
    """Create a new session token and persist it to MongoDB."""
    from database import db
    session_token = secrets.token_urlsafe(32)
    if db is not None:
        await db["sessions"].update_one(
            {"token": session_token},
            {"$set": {
                "token": session_token,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30),
            }},
            upsert=True
        )
    return session_token

async def get_user_from_session(session_token: Optional[str]) -> Optional[str]:
    """Get user ID from session token stored in MongoDB."""
    if not session_token:
        return None
    from database import db
    if db is None:
        return None
    session = await db["sessions"].find_one({"token": session_token})
    if not session:
        return None
    # Check expiry
    expires_at = session.get("expires_at")
    if expires_at and datetime.utcnow() > expires_at:
        await db["sessions"].delete_one({"token": session_token})
        return None
    return session.get("user_id")

async def get_current_user(session: Optional[str] = Cookie(None)):
    """Dependency to get current logged-in user."""
    if not session:
        return None

    user_id = await get_user_from_session(session)
    if not user_id:
        return None

    from database import db
    if db is None:
        return None

    user = await db["users"].find_one({"id": user_id})

    # Check and auto-downgrade expired PREMIUM subscriptions
    if user:
        await check_subscription_expiration(user)

    return user

async def check_subscription_expiration(user: dict):
    """Check if user's PREMIUM subscription has expired and auto-downgrade to FREE."""
    from database import db
    if db is None:
        return
    
    # Get user's company
    company = await db["companies"].find_one({"id": user.get("company_id")})
    
    if not company:
        return
    
    # Only check if currently on PREMIUM
    if company.get("subscription_tier") != "PREMIUM":
        return
    
    # Check if subscription has expired
    expires_at = company.get("subscription_expires_at")
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        now = datetime.utcnow()
        if now >= expires_at:
            # Subscription expired - downgrade to FREE
            await db["companies"].update_one(
                {"id": company.get("id")},
                {"$set": {
                    "subscription_tier": "FREE",
                    "subscription_expires_at": None,
                    "subscription_can_change_after": None  # Remove lock when auto-downgraded
                }}
            )
            print(f"Auto-downgraded company {company.get('name')} from PREMIUM to FREE (subscription expired)")

async def require_login(session: Optional[str] = Cookie(None)):
    """Dependency that requires user to be logged in."""
    user = await get_current_user(session)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in to access this feature")
    return user

# ----------------------------------------
# ACCESS CONTROL DEPENDENCY
# ----------------------------------------

async def check_premium_status(company_id: Optional[str] = Header(None, alias="X-Company-ID")):
    """
    Dependency to check if a company has PREMIUM subscription.
    Raises HTTPException if the company is on FREE tier.
    
    Usage: Add as dependency to protected routes
    Example: @app.get("/premium-feature", dependencies=[Depends(check_premium_status)])
    """
    if not company_id:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Authentication required",
                "message": "Company ID not provided",
                "upgrade_required": False
            }
        )
    
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    company = await db["companies"].find_one({"id": company_id})
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Company not found",
                "message": "Invalid company ID",
                "upgrade_required": False
            }
        )
    
    subscription_tier = company.get("subscription_tier", "FREE")
    
    if subscription_tier != "PREMIUM":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Premium subscription required",
                "message": "Upgrade to Premium to access this feature",
                "upgrade_required": True,
                "current_tier": subscription_tier
            }
        )
    
    return company

async def get_company_tier(company_id: str) -> str:
    """
    Helper function to get a company's subscription tier.
    Returns 'FREE' if company not found or no tier set.
    """
    from database import db
    
    if not company_id or db is None:
        return "FREE"
    
    company = await db["companies"].find_one({"id": company_id})
    
    if not company:
        return "FREE"
    
    return company.get("subscription_tier", "FREE")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user: Optional[dict] = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# ----------------------------------------
# AUTHENTICATION ROUTES
# ----------------------------------------

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Display registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request,
    company_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...)
):
    """Process user registration."""
    from database import db
    import random
    import string
    
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"
        })
    
    # Check if email already exists
    if db is not None:
        existing_user = await db["users"].find_one({"email": email})
        if existing_user:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Email already registered"
            })
        
        # Generate unique Supplier/Buyer ID
        role_prefix = "SUP" if role == "SUPPLIER" else "BUY"
        # Generate random 6-digit number
        random_number = ''.join(random.choices(string.digits, k=6))
        unique_id = f"{role_prefix}{random_number}"
        
        # Ensure uniqueness
        while await db["companies"].find_one({"unique_id": unique_id}):
            random_number = ''.join(random.choices(string.digits, k=6))
            unique_id = f"{role_prefix}{random_number}"
        
        # Create company - no subscription lock initially, user must choose plan
        company = CompanyModel(
            name=company_name,
            role=RoleEnum(role),
            overall_status=OverallStatusEnum.DRAFT,
            trust_score=0,
            subscription_tier=SubscriptionTierEnum.FREE,
            subscription_start_date=None,  # Not set until user selects a plan
            subscription_can_change_after=None  # No lock until user selects a plan
        )
        
        company_dict = company.model_dump()
        company_dict["unique_id"] = unique_id  # Add unique_id to company
        
        await db["companies"].insert_one(company_dict)
        
        # Create user
        user = UserModel(
            email=email,
            password_hash=hash_password(password),
            company_id=company.id
        )
        
        await db["users"].insert_one(user.model_dump())
        
        print(f"User registered: {email} with company: {company_name}, ID: {unique_id}")
    
    # Redirect to login with success message and show ID
    return RedirectResponse(url=f"/login?registered=true&id={unique_id}", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registered: Optional[str] = None, id: Optional[str] = None):
    """Display login page."""
    success = None
    if registered:
        if id:
            success = f"Registration successful! Your ID is: {id}. Please save this ID and log in."
        else:
            success = "Registration successful! Please log in."
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "success": success,
        "generated_id": id
    })

@app.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Process user login."""
    from database import db
    
    if db is None:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Database not available"
        })
    
    # Find user
    user = await db["users"].find_one({"email": email})
    
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        })
    
    # Update last login
    await db["users"].update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    # Create session (persisted to MongoDB)
    session_token = await create_session(user["id"])

    # Redirect to home with session cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        max_age=86400 * 30  # 30 days
    )

    return response

@app.get("/logout")
async def logout(session: Optional[str] = Cookie(None)):
    """Log out user — delete session from MongoDB."""
    from database import db
    if session and db is not None:
        await db["sessions"].delete_one({"token": session})

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session")
    return response


# ----------------------------------------
# JWT AUTH API ENDPOINTS
# ----------------------------------------

@app.post("/api/auth/login")
async def api_login(request: Request):
    """
    JWT login endpoint for API/mobile clients.
    Accepts JSON: { email, password }
    Returns: { access_token, refresh_token, token_type, user }
    """
    from database import db

    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)

    try:
        body = await request.json()
        email    = (body.get("email")    or "").strip().lower()
        password = (body.get("password") or "").strip()

        if not email or not password:
            return JSONResponse(
                {"success": False, "error": "Email and password are required"},
                status_code=422
            )

        user = await db["users"].find_one({"email": email})
        if not user or not verify_password(password, user["password_hash"]):
            return JSONResponse(
                {"success": False, "error": "Invalid email or password"},
                status_code=401
            )

        # Get company role
        company = await db["companies"].find_one({"id": user.get("company_id")})
        role = company.get("role", "BUYER") if company else "BUYER"

        # Update last login
        await db["users"].update_one(
            {"id": user["id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        access_token  = create_access_token(
            user_id=user["id"],
            email=user["email"],
            role=role,
            is_admin=user.get("is_admin", False),
            company_id=user.get("company_id"),
        )
        refresh_token = create_refresh_token(user_id=user["id"])

        return JSONResponse({
            "success":       True,
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "token_type":    "bearer",
            "expires_in":    60 * 24 * 60,  # seconds (24 hours)
            "user": {
                "id":         user["id"],
                "email":      user["email"],
                "role":       role,
                "is_admin":   user.get("is_admin", False),
                "company_id": user.get("company_id"),
            }
        })

    except Exception as e:
        print(f"JWT login error: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/auth/refresh")
async def api_refresh_token(request: Request):
    """
    Issue a new access token using a valid refresh token.
    Accepts JSON: { refresh_token }
    """
    try:
        body = await request.json()
        token = (body.get("refresh_token") or "").strip()
        if not token:
            return JSONResponse({"success": False, "error": "refresh_token is required"}, status_code=422)

        new_access_token = await refresh_access_token(token)
        return JSONResponse({
            "success":      True,
            "access_token": new_access_token,
            "token_type":   "bearer",
            "expires_in":   60 * 24 * 60,
        })

    except HTTPException as e:
        return JSONResponse({"success": False, "error": e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/auth/me")
async def api_me(user: dict = Depends(require_login_jwt)):
    """
    Return the current authenticated user's profile.
    Works with both JWT Bearer and session cookie.
    """
    from database import db
    company = None
    if db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})

    company_data = None
    if company:
        company_data = {
            "id":                company.get("id"),
            "name":              company.get("name"),
            "role":              company.get("role"),
            "unique_id":         company.get("unique_id"),
            "subscription_tier": company.get("subscription_tier", "FREE"),
            "trust_score":       company.get("trust_score", 0),
            "avg_rating":        company.get("avg_rating", 0),
            "total_reviews":     company.get("total_reviews", 0),
        }

    return JSONResponse({
        "success": True,
        "user": {
            "id":         user.get("id"),
            "email":      user.get("email"),
            "is_admin":   user.get("is_admin", False),
            "company_id": user.get("company_id"),
            "created_at": str(user.get("created_at", "")),
            "last_login": str(user.get("last_login", "")),
        },
        "company": company_data,
    })


@app.post("/api/auth/logout")
async def api_logout(request: Request, session: Optional[str] = Cookie(None)):
    """
    Logout endpoint for API clients.
    Clears session cookie and returns success.
    (JWT tokens are stateless — clients should discard them.)
    """
    if session and session in sessions:
        del sessions[session]

    response = JSONResponse({"success": True, "message": "Logged out successfully"})
    response.delete_cookie("session")
    return response


# ----------------------------------------
# ADMIN ROUTES
# ----------------------------------------

async def require_admin(user: dict = Depends(require_login)):
    """Dependency to require admin access."""
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Display admin login page."""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/api/admin/login")
async def admin_login(
    email: str = Body(...),
    password: str = Body(...)
):
    """Process admin login."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    # Find user
    user = await db["users"].find_one({"email": email})
    
    if not user or not verify_password(password, user["password_hash"]):
        return JSONResponse({"success": False, "error": "Invalid email or password"}, status_code=401)
    
    # Check if user is admin
    if not user.get("is_admin", False):
        return JSONResponse({"success": False, "error": "Insufficient permissions"}, status_code=403)
    
    # Update last login
    await db["users"].update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create session (persisted to MongoDB)
    session_token = await create_session(user["id"])
    
    # Return success with session cookie
    response = JSONResponse({"success": True, "message": "Login successful"})
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        max_age=86400 * 30  # 30 days
    )
    
    return response


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: dict = Depends(require_admin)):
    """Display admin dashboard."""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": admin})


@app.get("/api/admin/me")
async def get_admin_info(admin: dict = Depends(require_admin)):
    """Get current admin user info."""
    return {
        "success": True,
        "email": admin.get("email"),
        "id": admin.get("id")
    }


@app.get("/api/admin/stats")
async def get_admin_stats(admin: dict = Depends(require_admin)):
    """Get platform statistics for admin dashboard."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        # Count users
        total_users = await db["users"].count_documents({})
        
        # Count companies
        total_companies = await db["companies"].count_documents({})
        
        # Count RFQs
        total_rfqs = await db["rfqs"].count_documents({})
        
        # Count premium users (companies with PREMIUM subscription)
        premium_users = await db["companies"].count_documents({"subscription_tier": "PREMIUM"})
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_companies": total_companies,
                "total_rfqs": total_rfqs,
                "premium_users": premium_users
            }
        }
    except Exception as e:
        print(f"Error fetching admin stats: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, admin: dict = Depends(require_admin)):
    """Display admin users management page."""
    return templates.TemplateResponse("admin_users.html", {"request": request, "user": admin})


@app.get("/api/admin/users")
async def get_all_users(admin: dict = Depends(require_admin)):
    """Get all users for admin."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        users = await db["users"].find({}).to_list(length=1000)
        
        # Clean up users data
        clean_users = []
        for user in users:
            clean_users.append({
                "id": user.get("id"),
                "email": user.get("email"),
                "company_id": user.get("company_id"),
                "is_admin": user.get("is_admin", False),
                "created_at": user.get("created_at").isoformat() + 'Z' if isinstance(user.get("created_at"), datetime) else str(user.get("created_at")),
                "last_login": user.get("last_login").isoformat() + 'Z' if isinstance(user.get("last_login"), datetime) else None
            })
        
        return {
            "success": True,
            "users": clean_users
        }
    except Exception as e:
        print(f"Error fetching users: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/admin/companies", response_class=HTMLResponse)
async def admin_companies_page(request: Request, admin: dict = Depends(require_admin)):
    """Display admin companies management page."""
    return templates.TemplateResponse("admin_companies.html", {"request": request, "user": admin})


@app.get("/api/admin/companies")
async def get_all_companies(admin: dict = Depends(require_admin)):
    """Get all companies for admin."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        companies = await db["companies"].find({}).to_list(length=1000)
        
        # Clean up companies data
        clean_companies = []
        for company in companies:
            clean_companies.append({
                "id": company.get("id"),
                "name": company.get("name"),
                "role": company.get("role"),
                "overall_status": company.get("overall_status"),
                "trust_score": company.get("trust_score", 0),
                "subscription_tier": company.get("subscription_tier", "FREE"),
                "created_at": company.get("created_at").isoformat() + 'Z' if isinstance(company.get("created_at"), datetime) else str(company.get("created_at"))
            })
        
        return {
            "success": True,
            "companies": clean_companies
        }
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/admin/rfqs", response_class=HTMLResponse)
async def admin_rfqs_page(request: Request, admin: dict = Depends(require_admin)):
    """Display admin RFQs management page."""
    return templates.TemplateResponse("admin_rfqs.html", {"request": request, "user": admin})


@app.get("/api/admin/rfqs")
async def get_all_rfqs(admin: dict = Depends(require_admin)):
    """Get all RFQs for admin."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        rfqs = await db["rfqs"].find({}).to_list(length=1000)
        
        # Clean up RFQs data
        clean_rfqs = []
        for rfq in rfqs:
            clean_rfqs.append({
                "id": rfq.get("id"),
                "title": rfq.get("title", "Untitled"),
                "buyer_id": rfq.get("buyer_id"),
                "product_category": rfq.get("product_category"),
                "quantity": rfq.get("quantity", 0),
                "status": rfq.get("status", "DRAFT"),
                "is_reverse_auction": rfq.get("is_reverse_auction", False),
                "created_at": rfq.get("created_at").isoformat() + 'Z' if isinstance(rfq.get("created_at"), datetime) else str(rfq.get("created_at"))
            })
        
        return {
            "success": True,
            "rfqs": clean_rfqs
        }
    except Exception as e:
        print(f"Error fetching RFQs: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user: dict = Depends(require_login)):
    """Display user profile page with account information."""
    from database import db
    
    company = None
    if user and db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "company": company
    })


@app.post("/api/account/delete")
async def delete_account(request: Request, user: dict = Depends(require_login), session: Optional[str] = Cookie(None)):
    """Delete user account and all associated data."""
    from fastapi.responses import JSONResponse
    from database import db
    
    try:
        if db is None:
            return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
        company_id = user.get("company_id")
        user_id = user.get("id")
        
        # Delete all bids by this user's company
        await db["bids"].delete_many({"supplier_id": {"$regex": f".*"}})  # We'll need to match by company
        
        # Get company to find unique_id
        company = await db["companies"].find_one({"id": company_id})
        if company:
            unique_id = company.get("unique_id")
            # Delete all bids with this supplier_id
            await db["bids"].delete_many({"supplier_id": unique_id})
        
        # Delete all RFQs created by this user (if buyer)
        # Note: This assumes buyer_id matches company_id
        await db["rfqs"].delete_many({"buyer_id": company_id})
        
        # Delete legal capacity data
        await db["legal_capacity"].delete_many({"company_id": company_id})
        
        # Delete certifications
        await db["certifications"].delete_many({"company_id": company_id})
        
        # Delete company
        await db["companies"].delete_one({"id": company_id})
        
        # Delete user
        await db["users"].delete_one({"id": user_id})
        
        # Clear session from MongoDB
        if session:
            await db["sessions"].delete_one({"token": session})
        
        print(f"Account deleted: User={user.get('email')}, Company={company.get('name') if company else 'Unknown'}")
        
        return JSONResponse({
            "success": True,
            "message": "Account deleted successfully"
        })
    
    except Exception as e:
        print(f"Error deleting account: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display pricing plans page with user subscription status."""
    from database import db
    
    company = None
    subscription_locked = False
    days_until_change = 0
    days_until_expiration = 0
    subscription_expires = False
    
    if user and db is not None:
        # Get user's company
        company = await db["companies"].find_one({"id": user.get("company_id")})
        
        if company:
            # Check if subscription can be changed
            can_change_after = company.get("subscription_can_change_after")
            # Only lock if can_change_after is set AND is in the future
            if can_change_after is not None:
                if isinstance(can_change_after, str):
                    can_change_after = datetime.fromisoformat(can_change_after)
                
                now = datetime.utcnow()
                if now < can_change_after:
                    subscription_locked = True
                    days_until_change = (can_change_after - now).days + 1
            
            # Check subscription expiration for PREMIUM users
            if company.get("subscription_tier") == "PREMIUM":
                expires_at = company.get("subscription_expires_at")
                if expires_at:
                    if isinstance(expires_at, str):
                        expires_at = datetime.fromisoformat(expires_at)
                    
                    now = datetime.utcnow()
                    if now < expires_at:
                        subscription_expires = True
                        days_until_expiration = (expires_at - now).days + 1
    
    return templates.TemplateResponse("pricing.html", {
        "request": request,
        "user": user,
        "company": company,
        "subscription_locked": subscription_locked,
        "days_until_change": days_until_change,
        "subscription_expires": subscription_expires,
        "days_until_expiration": days_until_expiration
    })

@app.get("/subscription/edit", response_class=HTMLResponse)
async def subscription_edit_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display subscription edit page with locked visuals when within 30-day period."""
    from database import db
    
    # Redirect to login if not authenticated
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    company = None
    subscription_locked = False
    days_until_change = 0
    days_until_expiration = 0
    subscription_expires = False
    
    if db is not None:
        # Get user's company
        company = await db["companies"].find_one({"id": user.get("company_id")})
        
        if company:
            # Check if subscription can be changed
            can_change_after = company.get("subscription_can_change_after")
            # Only lock if can_change_after is set AND is in the future
            if can_change_after is not None:
                if isinstance(can_change_after, str):
                    can_change_after = datetime.fromisoformat(can_change_after)
                
                now = datetime.utcnow()
                if now < can_change_after:
                    subscription_locked = True
                    days_until_change = (can_change_after - now).days + 1
            
            # Check subscription expiration for PREMIUM users
            if company.get("subscription_tier") == "PREMIUM":
                expires_at = company.get("subscription_expires_at")
                if expires_at:
                    if isinstance(expires_at, str):
                        expires_at = datetime.fromisoformat(expires_at)
                    
                    now = datetime.utcnow()
                    if now < expires_at:
                        subscription_expires = True
                        days_until_expiration = (expires_at - now).days + 1
    
    return templates.TemplateResponse("subscription_edit.html", {
        "request": request,
        "user": user,
        "company": company,
        "subscription_locked": subscription_locked,
        "days_until_change": days_until_change,
        "subscription_expires": subscription_expires,
        "days_until_expiration": days_until_expiration
    })

@app.get("/analytics/dashboard", response_class=HTMLResponse)
async def analytics_dashboard_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display user analytics dashboard (PREMIUM feature) - Redirects to buyer or supplier dashboard."""
    import database
    
    # Check if user has PREMIUM subscription
    has_premium = False
    company = None
    
    if user and database.db is not None:
        company = await database.db["companies"].find_one({"id": user.get("company_id")})
        if company and company.get("subscription_tier") == "PREMIUM":
            has_premium = True
    
    # If user doesn't have PREMIUM, show access denied page
    if not has_premium:
        return templates.TemplateResponse("premium_required.html", {
            "request": request,
            "user": user,
            "company": company,
            "feature_name": "Order Analytics Dashboard",
            "feature_description": "Track your orders, costs, performance metrics, and identify business trends"
        })
    
    # Redirect to appropriate dashboard based on user role
    if company:
        role = company.get("role", "buyer").lower()
        if role == "supplier":
            return RedirectResponse(url="/analytics/supplier", status_code=303)
        else:
            return RedirectResponse(url="/analytics/buyer", status_code=303)
    
    # Default to buyer dashboard
    return RedirectResponse(url="/analytics/buyer", status_code=303)

@app.get("/analytics/buyer", response_class=HTMLResponse)
async def buyer_analytics_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display buyer analytics dashboard (PREMIUM feature)."""
    import database
    
    # Check if user has PREMIUM subscription
    has_premium = False
    company = None
    
    if user and database.db is not None:
        company = await database.db["companies"].find_one({"id": user.get("company_id")})
        if company and company.get("subscription_tier") == "PREMIUM":
            has_premium = True
    
    # If user doesn't have PREMIUM, show access denied page
    if not has_premium:
        return templates.TemplateResponse("premium_required.html", {
            "request": request,
            "user": user,
            "company": company,
            "feature_name": "Buyer Analytics Dashboard",
            "feature_description": "Track your procurement, spending, supplier performance, and sourcing trends"
        })
    
    # Generate buyer analytics data
    analytics = await generate_buyer_analytics(user, database.db)
    
    return templates.TemplateResponse("buyer_analytics.html", {
        "request": request,
        "user": user,
        "company": company,
        "analytics": analytics
    })

@app.get("/analytics/supplier", response_class=HTMLResponse)
async def supplier_analytics_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display supplier analytics dashboard (PREMIUM feature)."""
    import database
    
    # Check if user has PREMIUM subscription
    has_premium = False
    company = None
    
    if user and database.db is not None:
        company = await database.db["companies"].find_one({"id": user.get("company_id")})
        if company and company.get("subscription_tier") == "PREMIUM":
            has_premium = True
    
    # If user doesn't have PREMIUM, show access denied page
    if not has_premium:
        return templates.TemplateResponse("premium_required.html", {
            "request": request,
            "user": user,
            "company": company,
            "feature_name": "Supplier Analytics Dashboard",
            "feature_description": "Track your sales, revenue, customer satisfaction, and business growth"
        })
    
    # Generate supplier analytics data
    analytics = await generate_supplier_analytics(user, database.db)
    
    return templates.TemplateResponse("supplier_analytics.html", {
        "request": request,
        "user": user,
        "company": company,
        "analytics": analytics
    })

@app.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display admin analytics dashboard (ADMIN only)."""
    import database
    
    # Check if user is admin (you can add admin role check here)
    # For now, we'll just check if user is logged in
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Generate admin analytics data
    admin_analytics = await generate_admin_analytics(database.db)
    
    return templates.TemplateResponse("admin_analytics.html", {
        "request": request,
        "user": user,
        "admin_analytics": admin_analytics
    })

async def generate_buyer_analytics(user: dict, db):
    """Generate analytics data for buyer dashboard."""
    from datetime import datetime, timedelta
    
    if db is None:
        return {}
    
    try:
        company_id = user.get("company_id")
        company = await db["companies"].find_one({"id": company_id})
        
        if not company:
            return {}
        
        company_name = company.get("name", "")
        
        # Fetch RFQs created by this buyer
        rfqs_cursor = db["rfqs"].find({"buyer_company": company_name})
        rfqs = await rfqs_cursor.to_list(length=None)
        total_rfqs = len(rfqs)
        
        # Fetch all bids on buyer's RFQs
        rfq_ids = [rfq.get("id") for rfq in rfqs]
        bids_cursor = db["bids"].find({"rfq_id": {"$in": rfq_ids}})
        all_bids = await bids_cursor.to_list(length=None)
        
        # Calculate orders placed (accepted bids)
        accepted_bids = [bid for bid in all_bids if bid.get("status") == "ACCEPTED"]
        orders_placed = len(accepted_bids)
        
        # Calculate fulfilled orders (you can add a "fulfilled" status later)
        fulfilled_orders = len([bid for bid in accepted_bids if bid.get("delivery_status") == "DELIVERED"])
        fulfillment_rate = int((fulfilled_orders / orders_placed * 100)) if orders_placed > 0 else 0
        
        # Calculate total spent
        total_spent = sum([float(bid.get("bid_price", 0)) for bid in accepted_bids])
        avg_order_cost = int(total_spent / orders_placed) if orders_placed > 0 else 0
        
        # Supplier performance - on-time delivery
        delivered_orders = [bid for bid in accepted_bids if bid.get("delivery_status") == "DELIVERED"]
        on_time_deliveries = len([bid for bid in delivered_orders if bid.get("on_time", True)])
        total_deliveries = len(delivered_orders)
        supplier_on_time_rate = int((on_time_deliveries / total_deliveries * 100)) if total_deliveries > 0 else 0
        
        # Ratings given (you can add ratings collection later)
        total_ratings_given = len([bid for bid in accepted_bids if bid.get("rating")])
        avg_rating_given = 4.5  # Default for now
        rating_given_distribution = {5: 60, 4: 25, 3: 10, 2: 3, 1: 2}
        
        # Spending breakdown
        product_costs = int(total_spent * 0.75)
        shipping_costs = int(total_spent * 0.18)
        other_fees = int(total_spent * 0.07)
        
        # Top suppliers by order count
        supplier_counts = {}
        for bid in accepted_bids:
            supplier = bid.get("company_name", "Unknown")
            supplier_counts[supplier] = supplier_counts.get(supplier, 0) + 1
        
        top_suppliers = sorted(supplier_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_suppliers_labels = [s[0] for s in top_suppliers] if top_suppliers else ["No data"]
        top_suppliers_data = [s[1] for s in top_suppliers] if top_suppliers else [0]
        
        # Sourcing regions (you can add region field to companies later)
        sourcing_regions_labels = ["Asia", "Europe", "North America", "South America", "Africa"]
        sourcing_regions_data = [int(total_spent * 0.4), int(total_spent * 0.25), int(total_spent * 0.2), int(total_spent * 0.1), int(total_spent * 0.05)]
        
        # Spending trends over last 6 months
        spending_trends_labels = []
        spending_trends_data = []
        now = datetime.utcnow()
        
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_name = month_date.strftime("%b")
            spending_trends_labels.append(month_name)
            
            # Calculate spending for this month
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = now - timedelta(days=30*(i-1))
                month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_bids = [bid for bid in accepted_bids 
                         if bid.get("created_at") and 
                         month_start <= datetime.fromisoformat(str(bid.get("created_at"))) < month_end]
            month_spending = sum([float(bid.get("bid_price", 0)) for bid in month_bids])
            spending_trends_data.append(int(month_spending))
        
        # Recent orders
        recent_orders = []
        sorted_bids = sorted(accepted_bids, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
        
        for bid in sorted_bids:
            recent_orders.append({
                "rfq_id": bid.get("rfq_id", "N/A"),
                "supplier_name": bid.get("company_name", "Unknown"),
                "product_name": bid.get("product_name", "Product"),
                "date": datetime.fromisoformat(str(bid.get("created_at"))).strftime("%Y-%m-%d") if bid.get("created_at") else "N/A",
                "amount": f"{int(float(bid.get('bid_price', 0))):,}",
                "status": bid.get("delivery_status", "PENDING"),
                "rating": bid.get("rating")
            })
        
        analytics = {
            "total_rfqs": total_rfqs,
            "orders_placed": orders_placed,
            "fulfillment_rate": fulfillment_rate,
            "total_spent": f"{int(total_spent):,}",
            "avg_order_cost": f"{avg_order_cost:,}",
            
            "supplier_on_time_rate": supplier_on_time_rate,
            "on_time_deliveries": on_time_deliveries,
            "total_deliveries": total_deliveries,
            "avg_rating_given": avg_rating_given,
            "total_ratings_given": total_ratings_given,
            "rating_given_distribution": rating_given_distribution,
            
            "product_costs": f"{product_costs:,}",
            "shipping_costs": f"{shipping_costs:,}",
            "other_fees": f"{other_fees:,}",
            "product_percentage": 75,
            "shipping_percentage": 18,
            "other_percentage": 7,
            
            "top_suppliers_labels": top_suppliers_labels,
            "top_suppliers_data": top_suppliers_data,
            "sourcing_regions_labels": sourcing_regions_labels,
            "sourcing_regions_data": sourcing_regions_data,
            "spending_trends_labels": spending_trends_labels,
            "spending_trends_data": spending_trends_data,
            
            "recent_orders": recent_orders if recent_orders else [{
                "rfq_id": "N/A",
                "supplier_name": "No orders yet",
                "product_name": "-",
                "date": "-",
                "amount": "0",
                "status": "NONE",
                "rating": None
            }]
        }
        
        return analytics
        
    except Exception as e:
        print(f"Error generating buyer analytics: {e}")
        return {
            "total_rfqs": 0,
            "orders_placed": 0,
            "fulfillment_rate": 0,
            "total_spent": "0",
            "avg_order_cost": "0",
            "supplier_on_time_rate": 0,
            "on_time_deliveries": 0,
            "total_deliveries": 0,
            "avg_rating_given": 0,
            "total_ratings_given": 0,
            "rating_given_distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
            "product_costs": "0",
            "shipping_costs": "0",
            "other_fees": "0",
            "product_percentage": 0,
            "shipping_percentage": 0,
            "other_percentage": 0,
            "top_suppliers_labels": ["No data"],
            "top_suppliers_data": [0],
            "sourcing_regions_labels": ["No data"],
            "sourcing_regions_data": [0],
            "spending_trends_labels": ["No data"],
            "spending_trends_data": [0],
            "recent_orders": [{
                "rfq_id": "N/A",
                "supplier_name": "No orders yet",
                "product_name": "-",
                "date": "-",
                "amount": "0",
                "status": "NONE",
                "rating": None
            }]
        }

async def generate_supplier_analytics(user: dict, db):
    """Generate analytics data for supplier dashboard."""
    from datetime import datetime, timedelta
    
    if db is None:
        return {}
    
    try:
        company_id = user.get("company_id")
        company = await db["companies"].find_one({"id": company_id})
        
        if not company:
            return {}
        
        company_name = company.get("name", "")
        supplier_id = company.get("unique_id", "")
        
        # Fetch all bids submitted by this supplier
        bids_cursor = db["bids"].find({"company_name": company_name})
        all_bids = await bids_cursor.to_list(length=None)
        total_bids = len(all_bids)
        
        # Calculate orders won (accepted bids)
        won_bids = [bid for bid in all_bids if bid.get("status") == "ACCEPTED"]
        orders_won = len(won_bids)
        win_rate = int((orders_won / total_bids * 100)) if total_bids > 0 else 0
        
        # Calculate total revenue
        total_revenue = sum([float(bid.get("bid_price", 0)) for bid in won_bids])
        avg_deal_size = int(total_revenue / orders_won) if orders_won > 0 else 0
        
        # Delivery performance
        delivered_orders = [bid for bid in won_bids if bid.get("delivery_status") == "DELIVERED"]
        on_time_deliveries = len([bid for bid in delivered_orders if bid.get("on_time", True)])
        total_deliveries = len(delivered_orders)
        on_time_delivery_rate = int((on_time_deliveries / total_deliveries * 100)) if total_deliveries > 0 else 0
        
        # Customer ratings received
        rated_orders = [bid for bid in won_bids if bid.get("rating")]
        total_ratings_received = len(rated_orders)
        avg_rating_received = sum([float(bid.get("rating", 0)) for bid in rated_orders]) / total_ratings_received if total_ratings_received > 0 else 0
        avg_rating_received = round(avg_rating_received, 1)
        
        # Rating distribution
        rating_received_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for bid in rated_orders:
            rating = int(float(bid.get("rating", 0)))
            if rating in rating_received_distribution:
                rating_received_distribution[rating] += 1
        
        # Convert to percentages
        for rating in rating_received_distribution:
            rating_received_distribution[rating] = int((rating_received_distribution[rating] / total_ratings_received * 100)) if total_ratings_received > 0 else 0
        
        # Revenue breakdown
        product_revenue = int(total_revenue * 0.78)
        shipping_revenue = int(total_revenue * 0.15)
        other_revenue = int(total_revenue * 0.07)
        
        # Top buyers by order count
        buyer_counts = {}
        for bid in won_bids:
            # Get buyer from RFQ
            rfq = await db["rfqs"].find_one({"id": bid.get("rfq_id")})
            if rfq:
                buyer = rfq.get("buyer_company", "Unknown")
                buyer_counts[buyer] = buyer_counts.get(buyer, 0) + 1
        
        top_buyers = sorted(buyer_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_buyers_labels = [b[0] for b in top_buyers] if top_buyers else ["No data"]
        top_buyers_data = [b[1] for b in top_buyers] if top_buyers else [0]
        
        # Sales regions (you can add region field to companies later)
        sales_regions_labels = ["Asia", "Europe", "North America", "South America", "Africa"]
        sales_regions_data = [int(total_revenue * 0.45), int(total_revenue * 0.25), int(total_revenue * 0.18), int(total_revenue * 0.08), int(total_revenue * 0.04)]
        
        # Revenue trends over last 6 months
        revenue_trends_labels = []
        revenue_trends_data = []
        now = datetime.utcnow()
        
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_name = month_date.strftime("%b")
            revenue_trends_labels.append(month_name)
            
            # Calculate revenue for this month
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = now - timedelta(days=30*(i-1))
                month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_bids = [bid for bid in won_bids 
                         if bid.get("created_at") and 
                         month_start <= datetime.fromisoformat(str(bid.get("created_at"))) < month_end]
            month_revenue = sum([float(bid.get("bid_price", 0)) for bid in month_bids])
            revenue_trends_data.append(int(month_revenue))
        
        # Recent orders
        recent_orders = []
        sorted_bids = sorted(won_bids, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
        
        for bid in sorted_bids:
            # Get buyer name from RFQ
            rfq = await db["rfqs"].find_one({"id": bid.get("rfq_id")})
            buyer_name = rfq.get("buyer_company", "Unknown") if rfq else "Unknown"
            
            recent_orders.append({
                "order_id": bid.get("id", "N/A"),
                "buyer_name": buyer_name,
                "product_name": bid.get("product_name", "Product"),
                "date": datetime.fromisoformat(str(bid.get("created_at"))).strftime("%Y-%m-%d") if bid.get("created_at") else "N/A",
                "amount": f"{int(float(bid.get('bid_price', 0))):,}",
                "status": bid.get("delivery_status", "PROCESSING"),
                "rating": bid.get("rating")
            })
        
        analytics = {
            "total_bids": total_bids,
            "orders_won": orders_won,
            "win_rate": win_rate,
            "total_revenue": f"{int(total_revenue):,}",
            "avg_deal_size": f"{avg_deal_size:,}",
            
            "on_time_delivery_rate": on_time_delivery_rate,
            "on_time_deliveries": on_time_deliveries,
            "total_deliveries": total_deliveries,
            "avg_rating_received": avg_rating_received,
            "total_ratings_received": total_ratings_received,
            "rating_received_distribution": rating_received_distribution,
            
            "product_revenue": f"{product_revenue:,}",
            "shipping_revenue": f"{shipping_revenue:,}",
            "other_revenue": f"{other_revenue:,}",
            "product_percentage": 78,
            "shipping_percentage": 15,
            "other_percentage": 7,
            
            "top_buyers_labels": top_buyers_labels,
            "top_buyers_data": top_buyers_data,
            "sales_regions_labels": sales_regions_labels,
            "sales_regions_data": sales_regions_data,
            "revenue_trends_labels": revenue_trends_labels,
            "revenue_trends_data": revenue_trends_data,
            
            "recent_orders": recent_orders if recent_orders else [{
                "order_id": "N/A",
                "buyer_name": "No orders yet",
                "product_name": "-",
                "date": "-",
                "amount": "0",
                "status": "NONE",
                "rating": None
            }]
        }
        
        return analytics
        
    except Exception as e:
        print(f"Error generating supplier analytics: {e}")
        return {
            "total_bids": 0,
            "orders_won": 0,
            "win_rate": 0,
            "total_revenue": "0",
            "avg_deal_size": "0",
            "on_time_delivery_rate": 0,
            "on_time_deliveries": 0,
            "total_deliveries": 0,
            "avg_rating_received": 0,
            "total_ratings_received": 0,
            "rating_received_distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
            "product_revenue": "0",
            "shipping_revenue": "0",
            "other_revenue": "0",
            "product_percentage": 0,
            "shipping_percentage": 0,
            "other_percentage": 0,
            "top_buyers_labels": ["No data"],
            "top_buyers_data": [0],
            "sales_regions_labels": ["No data"],
            "sales_regions_data": [0],
            "revenue_trends_labels": ["No data"],
            "revenue_trends_data": [0],
            "recent_orders": [{
                "order_id": "N/A",
                "buyer_name": "No orders yet",
                "product_name": "-",
                "date": "-",
                "amount": "0",
                "status": "NONE",
                "rating": None
            }]
        }

async def generate_user_analytics(user: dict, db):
    """Generate analytics data for user dashboard."""
    from datetime import datetime, timedelta
    import random
    
    # In production, fetch real data from database
    # For now, generating sample data
    
    analytics = {
        "total_orders": random.randint(50, 200),
        "fulfilled_orders": random.randint(40, 180),
        "fulfillment_rate": random.randint(75, 95),
        "total_revenue": f"{random.randint(50000, 200000):,}",
        "avg_order_value": f"{random.randint(500, 2000):,}",
        
        # Performance metrics
        "on_time_delivery_rate": random.randint(85, 98),
        "on_time_deliveries": random.randint(80, 150),
        "total_deliveries": random.randint(90, 160),
        "avg_quality_rating": round(random.uniform(4.0, 4.9), 1),
        "total_ratings": random.randint(50, 150),
        "rating_distribution": {
            5: random.randint(50, 70),
            4: random.randint(20, 30),
            3: random.randint(5, 15),
            2: random.randint(2, 8),
            1: random.randint(0, 5)
        },
        
        # Cost breakdown
        "unit_price_costs": f"{random.randint(30000, 100000):,}",
        "shipping_costs": f"{random.randint(5000, 15000):,}",
        "escrow_payments": f"{random.randint(2000, 8000):,}",
        "unit_price_percentage": random.randint(65, 75),
        "shipping_percentage": random.randint(15, 25),
        "escrow_percentage": random.randint(5, 15),
        
        # Charts data
        "top_products_labels": ["T-Shirts", "Jeans", "Jackets", "Dresses", "Hoodies"],
        "top_products_data": [random.randint(20, 50) for _ in range(5)],
        "top_regions_labels": ["North America", "Europe", "Asia", "South America", "Africa"],
        "top_regions_data": [random.randint(10000, 50000) for _ in range(5)],
        "trends_labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "trends_data": [random.randint(10, 40) for _ in range(6)],
        
        # Recent orders
        "recent_orders": [
            {
                "id": f"ORD{random.randint(100000, 999999)}",
                "product_name": random.choice(["T-Shirts", "Jeans", "Jackets", "Dresses"]),
                "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "amount": f"{random.randint(500, 5000):,}",
                "status": random.choice(["FULFILLED", "PENDING", "IN_PROGRESS"]),
                "rating": random.choice([None, 4, 5, 4.5, 5])
            }
            for _ in range(10)
        ]
    }
    
    return analytics

async def generate_admin_analytics(db):
    """Generate analytics data for admin dashboard."""
    import random
    from datetime import datetime, timedelta
    
    # In production, fetch real data from database
    # For now, generating sample data
    
    admin_analytics = {
        "total_users": random.randint(500, 2000),
        "active_deals": random.randint(50, 200),
        "deals_growth": random.randint(5, 25),
        "total_revenue": f"{random.randint(500000, 2000000):,}",
        "revenue_growth": random.randint(10, 30),
        "dispute_rate": round(random.uniform(1.0, 5.0), 1),
        "dispute_trend": random.randint(-3, 2),
        "payment_flow": f"{random.randint(100000, 500000):,}",
        
        # User stats
        "active_rfqs": random.randint(100, 300),
        "total_bids": random.randint(500, 1500),
        "avg_response_time": random.randint(2, 12),
        
        # Charts data
        "user_distribution": [
            random.randint(200, 600),  # Buyers
            random.randint(200, 600),  # Suppliers
            random.randint(50, 200)    # Both
        ],
        "subscription_breakdown": [
            random.randint(400, 1500),  # FREE
            random.randint(100, 500)    # PREMIUM
        ],
        "revenue_labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "revenue_data": [random.randint(50000, 150000) for _ in range(4)],
        "payment_data": [random.randint(40000, 120000) for _ in range(4)],
        
        # Health metrics
        "health_score": random.randint(85, 98),
        "user_satisfaction": random.randint(85, 95),
        "system_uptime": round(random.uniform(99.0, 99.9), 1),
        "transaction_success": random.randint(95, 99),
        
        # Active disputes
        "active_disputes": [
            {
                "id": f"DIS{random.randint(100000, 999999)}",
                "priority": random.choice(["HIGH", "MEDIUM", "LOW"]),
                "description": random.choice([
                    "Quality issue with delivered goods",
                    "Payment not received after delivery",
                    "Delayed shipment beyond agreed date",
                    "Product specifications mismatch"
                ]),
                "date": (datetime.now() - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
                "amount": f"{random.randint(1000, 10000):,}"
            }
            for _ in range(3)
        ]
    }
    
    return admin_analytics

@app.get("/test-pricing", response_class=HTMLResponse)
async def test_pricing_page(request: Request):
    """Test pricing page."""
    return templates.TemplateResponse("test_pricing.html", {"request": request})

@app.get("/test-simple", response_class=HTMLResponse)
async def test_simple_page(request: Request):
    """Simple test page."""
    return templates.TemplateResponse("test_simple.html", {"request": request})

@app.get("/rfq/auctions", response_class=HTMLResponse)
async def rfq_auctions_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Display all active reverse auction RFQs."""
    import database
    
    # Check if user has PREMIUM subscription
    has_premium = False
    company = None
    
    if user and database.db is not None:
        company = await database.db["companies"].find_one({"id": user.get("company_id")})
        if company and company.get("subscription_tier") == "PREMIUM":
            has_premium = True
    
    # If user doesn't have PREMIUM, show access denied page
    if not has_premium:
        return templates.TemplateResponse("premium_required.html", {
            "request": request,
            "user": user,
            "company": company,
            "feature_name": "Reverse Auctions",
            "feature_description": "Access real-time competitive bidding and participate in reverse auctions"
        })
    
    active_auctions = []
    
    if database.db is not None:
        try:
            # Fetch all RFQs that are reverse auctions and open
            auctions_cursor = database.db["rfqs"].find({
                "is_reverse_auction": True,
                "status": "OPEN"
            }).sort("auction_end_time", 1)  # Soonest auctions first
            
            auctions = await auctions_cursor.to_list(length=None)
            
            for auction in auctions:
                # Get bid count for this auction
                bid_count = await database.db["bids"].count_documents({
                    "rfq_id": auction.get("id"),
                    "status": "ACTIVE"
                })
                
                # Calculate time remaining
                time_remaining = None
                if auction.get("auction_end_time"):
                    auction_end = auction.get("auction_end_time")
                    if isinstance(auction_end, str):
                        auction_end = datetime.fromisoformat(auction_end)
                    now = datetime.utcnow()
                    time_diff = auction_end - now
                    time_remaining = max(0, int(time_diff.total_seconds()))
                
                auction["bid_count"] = bid_count
                auction["time_remaining"] = time_remaining
                active_auctions.append(auction)
        
        except Exception as e:
            print(f"Error fetching auctions: {e}")
    
    return templates.TemplateResponse("rfq_auctions.html", {
        "request": request,
        "active_auctions": active_auctions,
        "user": user
    })

@app.get("/verify/buyer", response_class=HTMLResponse)
async def verify_buyer_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    return templates.TemplateResponse("buyer_verification.html", {"request": request, "user": user})

@app.post("/verify/buyer")
async def process_buyer_verification(request: Request):
    form_data = await request.form()
    print("Received buyer verification request:", form_data)
    return templates.TemplateResponse("buyer_verification.html", {"request": request, "success": True})

@app.get("/verify/supplier", response_class=HTMLResponse)
async def verify_supplier_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    return templates.TemplateResponse("supplier_verification.html", {"request": request, "user": user})

@app.post("/verify/supplier")
async def process_supplier_verification(request: Request):
    from fastapi.responses import JSONResponse
    import database
    
    is_ajax = "application/json" in request.headers.get("accept", "")
    
    try:
        form_data = await request.form()
        
        # --- Validate required fields ---
        company_name = form_data.get("company_name", "").strip()
        business_license_no = form_data.get("business_license_no", "").strip()
        trade_license_no = form_data.get("trade_license_no", "").strip()
        manufacturing_type = form_data.get("manufacturing_type", "").strip()
        
        errors = {}
        if not company_name:
            errors["company_name"] = "Company name is required"
        if not business_license_no:
            errors["business_license_no"] = "Business license number is required"
        if not trade_license_no:
            errors["trade_license_no"] = "Trade license number is required"
        if not manufacturing_type:
            errors["manufacturing_type"] = "Manufacturing type is required"
        
        total_workers = int(form_data.get("total_workers") or "0")
        total_machines = int(form_data.get("total_machines") or "0")
        annual_turnover = float(form_data.get("annual_turnover") or "0.0")
        
        if total_workers < 1:
            errors["total_workers"] = "Must have at least 1 worker"
        if total_machines < 1:
            errors["total_machines"] = "Must have at least 1 machine"
            
        if errors:
            if is_ajax:
                return JSONResponse({"success": False, "errors": errors}, status_code=422)
            return templates.TemplateResponse("supplier_verification.html", {"request": request, "errors": errors})
        
        # --- Build models ---
        company = CompanyModel(
            name=company_name,
            role=RoleEnum.SUPPLIER,
            overall_status=OverallStatusEnum.PENDING_REVIEW,
            trust_score=0
        )
        
        legal_cap = LegalAndCapacityModel(
            company_id=company.id,
            business_license_no=business_license_no,
            business_license_url=f"https://texbid-bucket.s3.amazonaws.com/{company.id}_license.pdf",
            trade_license_no=trade_license_no,
            manufacturing_type=manufacturing_type,
            total_workers=total_workers,
            total_machines=total_machines,
            annual_turnover=annual_turnover
        )
        
        # --- Handle multiple certifications ---
        cert_types = form_data.getlist("cert_types[]")
        cert_numbers = form_data.getlist("cert_numbers[]")
        certifications = []
        for i, (ct, cn) in enumerate(zip(cert_types, cert_numbers)):
            if cn and cn.strip():
                cert = CertificationModel(
                    company_id=company.id,
                    cert_type=CertTypeEnum(ct or "OTHER"),
                    cert_number=cn.strip(),
                    document_url=f"https://texbid-bucket.s3.amazonaws.com/{company.id}_cert_{i}.pdf",
                    verification_status=VerificationStatusEnum.PENDING
                )
                certifications.append(cert.model_dump())

            
        # --- MongoDB Insertion ---
        if database.db is not None:
            await database.db["companies"].insert_one(company.model_dump())
            await database.db["legal_capacity"].insert_one(legal_cap.model_dump())
            if certifications:
                await database.db["certifications"].insert_many(certifications)
            print(f"Company {company.name} saved successfully!")
        else:
            print("WARNING: db is None — MongoDB not connected. Data NOT saved.")
        
        if is_ajax:
            return JSONResponse({
                "success": True, 
                "company_name": company.name,
                "company_id": company.id,
                "certs_count": len(certifications)
            })
        
        return templates.TemplateResponse("supplier_verification.html", {"request": request, "success": True})
    
    except Exception as e:
        print(f"Error in supplier verification: {e}")
        if is_ajax:
            return JSONResponse({"success": False, "errors": {"_general": str(e)}}, status_code=500)
        return templates.TemplateResponse("supplier_verification.html", {"request": request, "errors": {"_general": str(e)}})


# ----------------------------------------
# SUPPLIER LIST (Admin View)
# ----------------------------------------

@app.get("/suppliers/list", response_class=HTMLResponse)
async def supplier_list(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Fetches all supplier submissions from the database."""
    import database
    companies = []
    if database.db is not None:
        async for company in database.db["companies"].find({"role": "SUPPLIER"}):
            company["_id"] = str(company["_id"])
            companies.append(company)
    return templates.TemplateResponse("suppliers_list.html", {"request": request, "companies": companies, "user": user})

# ----------------------------------------
# ADMIN SUBSCRIPTION MANAGEMENT
# ----------------------------------------

@app.get("/admin/subscriptions", response_class=HTMLResponse)
async def admin_subscriptions_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Admin dashboard for managing company subscriptions."""
    import database
    
    companies = []
    total_companies = 0
    free_count = 0
    premium_count = 0
    
    if database.db is not None:
        # Fetch all companies
        async for company in database.db["companies"].find().sort("created_at", -1):
            company["_id"] = str(company["_id"])
            companies.append(company)
            
            # Count by subscription tier
            tier = company.get("subscription_tier", "FREE")
            if tier == "PREMIUM":
                premium_count += 1
            else:
                free_count += 1
        
        total_companies = len(companies)
    
    # Calculate percentages
    free_percentage = round((free_count / total_companies * 100) if total_companies > 0 else 0, 1)
    premium_percentage = round((premium_count / total_companies * 100) if total_companies > 0 else 0, 1)
    
    return templates.TemplateResponse("admin_subscriptions.html", {
        "request": request,
        "companies": companies,
        "total_companies": total_companies,
        "free_count": free_count,
        "premium_count": premium_count,
        "free_percentage": free_percentage,
        "premium_percentage": premium_percentage,
        "user": user
    })

@app.post("/api/admin/toggle-subscription")
async def toggle_subscription(request: Request):
    """Admin endpoint to toggle a company's subscription tier."""
    from fastapi.responses import JSONResponse
    import database
    
    try:
        data = await request.json()
        company_id = data.get("company_id")
        new_tier = data.get("new_tier")
        
        if not company_id or not new_tier:
            return JSONResponse({
                "success": False,
                "error": "Missing company_id or new_tier"
            }, status_code=400)
        
        if new_tier not in ["FREE", "PREMIUM"]:
            return JSONResponse({
                "success": False,
                "error": "Invalid tier. Must be FREE or PREMIUM"
            }, status_code=400)
        
        if database.db is None:
            return JSONResponse({
                "success": False,
                "error": "Database not available"
            }, status_code=500)
        
        # Update the company's subscription tier
        result = await database.db["companies"].update_one(
            {"id": company_id},
            {"$set": {"subscription_tier": new_tier}}
        )
        
        if result.matched_count == 0:
            return JSONResponse({
                "success": False,
                "error": "Company not found"
            }, status_code=404)
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully updated subscription to {new_tier}",
            "new_tier": new_tier
        })
    
    except Exception as e:
        print(f"Error toggling subscription: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/subscription/update")
async def update_subscription(request: Request, user: dict = Depends(require_login)):
    """User endpoint to update their own subscription (with 30-day lock)."""
    from fastapi.responses import JSONResponse
    import database
    
    try:
        data = await request.json()
        new_tier = data.get("tier")
        
        if new_tier not in ["FREE", "PREMIUM"]:
            return JSONResponse({
                "success": False,
                "error": "Invalid tier. Must be FREE or PREMIUM"
            }, status_code=400)
        
        if database.db is None:
            return JSONResponse({
                "success": False,
                "error": "Database not available"
            }, status_code=500)
        
        # Get user's company
        company = await database.db["companies"].find_one({"id": user.get("company_id")})
        
        if not company:
            return JSONResponse({
                "success": False,
                "error": "Company not found"
            }, status_code=404)
        
        # Check if subscription can be changed
        can_change_after = company.get("subscription_can_change_after")
        if can_change_after:
            if isinstance(can_change_after, str):
                can_change_after = datetime.fromisoformat(can_change_after)
            
            if datetime.utcnow() < can_change_after:
                days_left = (can_change_after - datetime.utcnow()).days + 1
                return JSONResponse({
                    "success": False,
                    "error": f"Subscription locked. You can change in {days_left} days."
                }, status_code=403)
        
        # Update subscription with 30-day lock and expiration
        now = datetime.utcnow()
        update_data = {
            "subscription_tier": new_tier,
            "subscription_start_date": now,
            "subscription_can_change_after": now + timedelta(days=30)
        }
        
        # For PREMIUM, set expiration date to 30 days from now
        if new_tier == "PREMIUM":
            update_data["subscription_expires_at"] = now + timedelta(days=30)
        else:
            # For FREE, remove expiration date
            update_data["subscription_expires_at"] = None
        
        result = await database.db["companies"].update_one(
            {"id": user.get("company_id")},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return JSONResponse({
                "success": False,
                "error": "Failed to update subscription"
            }, status_code=500)
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully updated to {new_tier} plan",
            "tier": new_tier
        })
    
    except Exception as e:
        print(f"Error updating subscription: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/suppliers/detail/{company_name}", response_class=HTMLResponse)
async def supplier_detail(request: Request, company_name: str, user: Optional[dict] = Depends(get_current_user)):
    """Fetches a single supplier's full profile — company + legal capacity + certifications."""
    import database

    company = None
    legal = None
    certifications = []

    if database.db is not None:
        # 1. Find the company by its name
        company = await database.db["companies"].find_one({"name": company_name})
        
        if company:
            # Convert the MongoDB _id to string for the HTML template
            company["_id"] = str(company["_id"])
            
            # 2. Extract the Pydantic 'id' (no underscore) to use as the foreign key
            actual_company_id = company.get("id")
            
            # 3. Use actual_company_id to find the matching legal data
            legal = await database.db["legal_capacity"].find_one({"company_id": actual_company_id})
            if legal:
                legal["_id"] = str(legal["_id"])
                
            # 4. Use actual_company_id to find matching certifications
            async for cert in database.db["certifications"].find({"company_id": actual_company_id}):
                cert["_id"] = str(cert["_id"])
                certifications.append(cert)

    if not company:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/suppliers/list")

    return templates.TemplateResponse("supplier_detail.html", {
        "request": request,
        "company": company,
        "legal": legal,
        "certifications": certifications,
        "user": user
    })
    

from fastapi import Body

@app.get("/getSupplierRaw")
async def get_supplier_raw(payload: dict = Body(...)):
    """A GET method that reads a JSON body and returns a simple list."""
    import database
    
    # Extract the name from the JSON body you type in Postman
    company_name = payload.get("name")
    
    if database.db is not None:
        # Find the exact company in the database
        company = await database.db["companies"].find_one({"name": company_name})
        
        if company:
            # Return a simple list just like the screenshot!
            return [
                str(company["_id"]),
                company.get("name"),
                company.get("role"),
                company.get("overall_status")
            ]
            
    return ["Supplier not found"]
# ----------------------------------------
# SMART RFQ BUILDER MODULE
# ----------------------------------------

@app.get("/rfq/create", response_class=HTMLResponse)
async def rfq_builder_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """RFQ creation page - Only for logged-in buyers."""
    from database import db

    # Not logged in — redirect to login with a friendly message
    if not user:
        return RedirectResponse(url="/login?next=/rfq/create&msg=login_required", status_code=303)

    # Check if user has a company and if it's a buyer
    if user.get("company_id"):
        company = await db["companies"].find_one({"id": user["company_id"]})
        if company and company.get("role") != "BUYER":
            # User is a supplier, not a buyer
            return templates.TemplateResponse("error.html", {
                "request": request,
                "user": user,
                "error_title": "Access Denied",
                "error_message": "Only buyers can create RFQs. Suppliers can browse and bid on RFQs."
            })
    
    return templates.TemplateResponse("rfq_builder.html", {"request": request, "user": user})

@app.post("/rfq/create")
async def process_rfq_creation(request: Request, user: dict = Depends(require_login)):
    """Process RFQ creation - Only for logged-in buyers."""
    from fastapi.responses import JSONResponse
    from database import db
    from datetime import datetime
    
    # Check if user is a buyer
    if user.get("company_id"):
        company = await db["companies"].find_one({"id": user["company_id"]})
        if company and company.get("role") != "BUYER":
            return JSONResponse({
                "success": False,
                "error": "Only buyers can create RFQs"
            }, status_code=403)
    
    is_ajax = "application/json" in request.headers.get("accept", "")
    
    try:
        form_data = await request.form()
        
        # --- Validate required fields ---
        title = (form_data.get("title") or "").strip()
        product_category = (form_data.get("product_category") or "").strip()
        
        errors = {}
        if not title:
            errors["title"] = "RFQ title is required"
        if not product_category:
            errors["product_category"] = "Product category is required"
            
        if errors:
            if is_ajax:
                return JSONResponse({"success": False, "errors": errors}, status_code=422)
            return templates.TemplateResponse("rfq_builder.html", {"request": request, "errors": errors})
        
        # Get buyer_id from logged-in user (or use simulated ID if not logged in)
        buyer_id = "SIMULATED_BUYER_123"  # Default fallback
        if user:
            # Use the user's ID as buyer_id for ownership tracking
            buyer_id = user.get("id")
            # Alternative: use company_id if you want company-level ownership
            # buyer_id = user.get("company_id") or user.get("id")
        
        # Process certifications from multiple checkbox inputs
        cert_reqs = form_data.getlist("compliance[]")
        mapped_certs = [CertTypeEnum(c) for c in cert_reqs if c in [e.value for e in CertTypeEnum]]
        
        # Process dynamic Quantity Breakdown (Array of Inputs)
        sizes = form_data.getlist("b_size[]")
        colors = form_data.getlist("b_color[]")
        qtys = form_data.getlist("b_qty[]")
        
        quantity_breakdown = []
        for s, c, q in zip(sizes, colors, qtys):
            if s and c and q:
                quantity_breakdown.append({"size": s, "color": c, "quantity": int(q)})
                
        total_qty = int(form_data.get("total_quantity") or 0)
        
        # Safe date parser
        def parse_date(date_str):
            if not date_str: return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return None

        def parse_auction_end(date_str):
            """Parse HTML datetime-local (YYYY-MM-DDTHH:MM) as naive UTC for auction end."""
            if not date_str:
                return None
            s = str(date_str).strip()
            if len(s) == 16 and "T" in s:
                s = s + ":00"
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        is_reverse_auction = form_data.get("is_reverse_auction") in ("true", "on", "1")
        auction_end_time = parse_auction_end(form_data.get("auction_end_time") or "")
        is_draft = form_data.get("status") == "DRAFT"

        errors = {}
        if is_reverse_auction and not is_draft:
            if not auction_end_time:
                errors["auction_end_time"] = "Auction end date and time is required for reverse auctions"
            elif auction_end_time <= datetime.utcnow():
                errors["auction_end_time"] = "Auction end time must be in the future"

        if errors:
            if is_ajax:
                return JSONResponse({"success": False, "errors": errors}, status_code=422)
            return templates.TemplateResponse("rfq_builder.html", {"request": request, "errors": errors})
                
        rfq = RFQModel(
            buyer_id=buyer_id,  # Use actual user ID instead of hardcoded value
            title=title,
            product_category=product_category,
            urgency_level=form_data.get("urgency_level", "MEDIUM"),
            quantity=total_qty,
            quantity_breakdown=quantity_breakdown,
            target_price=None,
            fabric_type=form_data.get("fabric_type", "Unknown"),
            fabric_gsm=form_data.get("custom_gsm") if form_data.get("gsm_range") == "Custom" else form_data.get("gsm_range"),
            certifications_required=mapped_certs,
            
            # --- Step 2: Specifications ---
            bom_buttons=form_data.get("bom_buttons"),
            bom_zippers=form_data.get("bom_zippers"),
            bom_thread=form_data.get("bom_thread"),
            labeling_reqs=form_data.getlist("labeling_reqs[]"),
            packaging_type=form_data.get("packaging_type"),
            measurement_tolerance=form_data.get("measurement_tolerance"),
            
            # --- Step 3: Timeline & Logistics ---
            target_delivery_date=parse_date(form_data.get("target_delivery_date")),
            proto_sample_req=(form_data.get("proto_sample_req") == "true"),
            proto_sample_date=parse_date(form_data.get("proto_sample_date")),
            pp_sample_req=(form_data.get("pp_sample_req") == "true"),
            pp_sample_date=parse_date(form_data.get("pp_sample_date")),
            incoterms=form_data.get("incoterm", "FOB"),
            incoterm=form_data.get("incoterm", "FOB"), 
            shipping_method=form_data.get("shipping_method"),
            destination_port=form_data.get("destination_port"),
            
            status=RFQStatusEnum.DRAFT if form_data.get("status") == "DRAFT" else RFQStatusEnum.OPEN,
            deadline=None,
            special_instructions="",
            tech_pack_url=None,
            pantone_colors=form_data.getlist("pantone_colors[]") or ["PANTONE 19-4052 TCX"],
            is_reverse_auction=is_reverse_auction,
            auction_end_time=auction_end_time if is_reverse_auction else None,
        )
        
        # Async Insert
        if db is not None:
            await db["rfqs"].insert_one(rfq.model_dump())
            print(f"RFQ Created: {rfq.title} - {rfq.product_category} ({rfq.quantity} units)")
            
            # Send notifications to suppliers if RFQ is OPEN (not draft)
            if rfq.status == RFQStatusEnum.OPEN:
                if rfq.is_reverse_auction:
                    # Notify about new reverse auction
                    await notify_new_auction(rfq.id, rfq.title, rfq.auction_end_time)
                else:
                    # Notify about new RFQ
                    await notify_new_rfq(rfq.id, rfq.title, rfq.product_category)
        
        if is_ajax:
            return JSONResponse({
                "success": True,
                "rfq_title": rfq.title,
                "rfq_id": rfq.id,
                "quantity": rfq.quantity,
                "is_reverse_auction": bool(rfq.is_reverse_auction),
            })
            
        return templates.TemplateResponse("rfq_builder.html", {"request": request, "success": True})
    
    except Exception as e:
        print(f"Error creating RFQ: {e}")
        if is_ajax:
            return JSONResponse({"success": False, "errors": {"_general": str(e)}}, status_code=500)
        return templates.TemplateResponse("rfq_builder.html", {"request": request, "errors": {"_general": str(e)}})


@app.delete("/api/rfq/{rfq_id}")
async def delete_rfq(rfq_id: str, user: dict = Depends(require_login)):
    """Delete an RFQ. Only the RFQ creator can delete their RFQ."""
    from fastapi.responses import JSONResponse
    from database import db
    
    try:
        if db is None:
            return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
        # Find the RFQ
        rfq = await db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            return JSONResponse({"success": False, "error": "RFQ not found"}, status_code=404)
        
        # Check ownership with improved logic
        user_company = await db["companies"].find_one({"id": user.get("company_id")})
        
        is_owner = (
            rfq.get("buyer_id") == user.get("id") or  # Direct user ID match
            rfq.get("buyer_id") == user.get("company_id") or  # Company ID match
            (user_company and rfq.get("buyer_id") == user_company.get("id")) or  # Company doc ID match
            (user_company and rfq.get("buyer_id") == user_company.get("unique_id")) or  # Company unique_id match
            rfq.get("buyer_id") == "SIMULATED_BUYER_123"  # Legacy: treat all simulated RFQs as deletable
        )
        
        if not is_owner:
            return JSONResponse({"success": False, "error": "You can only delete your own RFQs"}, status_code=403)
        
        # Delete all bids associated with this RFQ
        await db["bids"].delete_many({"rfq_id": rfq_id})
        
        # Delete the RFQ
        result = await db["rfqs"].delete_one({"id": rfq_id})
        
        if result.deleted_count == 0:
            return JSONResponse({"success": False, "error": "Failed to delete RFQ"}, status_code=500)
        
        print(f"RFQ deleted: ID={rfq_id}, Title={rfq.get('title')}")
        
        return JSONResponse({
            "success": True,
            "message": "RFQ and all associated bids deleted successfully"
        })
    
    except Exception as e:
        print(f"Error deleting RFQ: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/dashboard", response_class=HTMLResponse)
async def smart_dashboard(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Redirect to the correct dashboard based on the user's role."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    from database import db
    if db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            role = company.get("role", "").upper()
            if role == "SUPPLIER":
                return RedirectResponse(url="/dashboard/supplier", status_code=303)
            elif role == "BUYER":
                return RedirectResponse(url="/dashboard/buyer", status_code=303)

    return RedirectResponse(url="/dashboard/buyer", status_code=303)


@app.get("/rfq/browse", response_class=HTMLResponse)
async def rfq_browse_redirect(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Smart Browse RFQs redirect — buyers see their dashboard, suppliers see the RFQ feed."""
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    from database import db
    if db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            role = company.get("role", "").upper()
            if role == "SUPPLIER":
                return RedirectResponse(url="/dashboard/supplier", status_code=303)
            elif role == "BUYER":
                return RedirectResponse(url="/dashboard/buyer", status_code=303)

    return RedirectResponse(url="/dashboard/buyer", status_code=303)


@app.get("/dashboard/buyer", response_class=HTMLResponse)
async def buyer_dashboard(request: Request, user: dict = Depends(require_login)):
    """Buyer dashboard — shows their RFQs, bids received, and payment statuses."""
    from database import db
    rfqs = []
    payments = []
    if db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        buyer_id = user.get("id")
        company_id = user.get("company_id")

        # Fetch buyer's RFQs (match by multiple buyer_id formats)
        async for rfq in db["rfqs"].find({
            "$or": [
                {"buyer_id": buyer_id},
                {"buyer_id": company_id},
                {"buyer_id": company.get("id") if company else None},
                {"buyer_id": company.get("unique_id") if company else None},
            ]
        }).sort("created_at", -1):
            rfq["_id"] = str(rfq["_id"])
            # Count bids for this RFQ
            rfq["bid_count"] = await db["bids"].count_documents({"rfq_id": rfq["id"]})
            # Check if paid
            payment = await db["payments"].find_one({
                "order_id": rfq["id"],
                "status": {"$in": ["PAID_IN_ESCROW", "RELEASED"]}
            })
            rfq["payment_status"] = payment.get("status") if payment else None
            rfq["payment_id"] = payment.get("payment_id") if payment else None
            rfqs.append(rfq)

        # Fetch buyer's payments
        async for p in db["payments"].find({"buyer_id": buyer_id}).sort("created_at", -1).limit(5):
            p["_id"] = str(p["_id"])
            payments.append(p)

    return templates.TemplateResponse("buyer_dashboard.html", {
        "request": request,
        "user": user,
        "rfqs": rfqs,
        "payments": payments,
    })


@app.get("/dashboard/supplier", response_class=HTMLResponse)
async def supplier_dashboard_feed(request: Request, user: Optional[dict] = Depends(get_current_user)):
    from database import db

    rfqs = []
    orders = []  # accepted bids + paid orders

    if db is not None:
        # Open RFQs for browsing
        async for document in db["rfqs"].find({"status": "OPEN"}).sort("created_at", -1):
            document['_id'] = str(document['_id'])
            rfqs.append(document)

        if user:
            company = await db["companies"].find_one({"id": user.get("company_id")})
            company_role = company.get("role", "").upper() if company else ""

            # Only show orders/bids section for SUPPLIER accounts
            if company_role == "SUPPLIER":
                supplier_id = company.get("unique_id") or company.get("id") if company else user.get("id")

                # Fetch all bids by this supplier (accepted, confirmed, or with payments)
                async for bid in db["bids"].find({
                    "supplier_id": supplier_id,
                    "status": {"$in": ["ACCEPTED", "CONFIRMED", "ACTIVE"]}
                }):
                    rfq = await db["rfqs"].find_one({"id": bid.get("rfq_id")})
                    if not rfq:
                        continue

                    # Check for payment linked to this specific bid
                    payment = await db["payments"].find_one({
                        "order_id": bid.get("rfq_id"),
                        "bid_id": bid.get("id"),
                        "status": {"$in": [
                            "PAID_IN_ESCROW", "WORK_IN_PROGRESS",
                            "SENT_FOR_DELIVERY", "RELEASED"
                        ]}
                    })

                    if bid.get("status") in ("ACCEPTED", "CONFIRMED") or payment:
                        if payment:
                            payment["_id"] = str(payment["_id"])
                        orders.append({
                            "bid": bid,
                            "payment": payment,
                            "rfq": rfq,
                        })
                
                # Also fetch bids that have payments but might not be in ACCEPTED/CONFIRMED status anymore
                async for payment in db["payments"].find({
                    "supplier_id": supplier_id,
                    "status": {"$in": [
                        "PAID_IN_ESCROW", "WORK_IN_PROGRESS",
                        "SENT_FOR_DELIVERY", "RELEASED"
                    ]}
                }):
                    # Check if we already have this order
                    bid_id = payment.get("bid_id")
                    if bid_id and not any(o["bid"].get("id") == bid_id for o in orders):
                        bid = await db["bids"].find_one({"id": bid_id})
                        if bid:
                            rfq = await db["rfqs"].find_one({"id": bid.get("rfq_id")})
                            if rfq:
                                payment["_id"] = str(payment["_id"])
                                orders.append({
                                    "bid": bid,
                                    "payment": payment,
                                    "rfq": rfq,
                                })

    return templates.TemplateResponse("supplier_dashboard.html", {
        "request": request,
        "rfqs": rfqs,
        "orders": orders,
        "user": user,
    })


@app.get("/rfq/feed", response_class=HTMLResponse)
async def rfq_feed_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Browse all open RFQs - accessible to both buyers and suppliers."""
    from database import db

    rfqs = []
    if db is not None:
        # Fetch all open RFQs
        async for document in db["rfqs"].find({"status": "OPEN"}).sort("created_at", -1):
            document['_id'] = str(document['_id'])
            rfqs.append(document)

    return templates.TemplateResponse("rfq_feed.html", {
        "request": request,
        "rfqs": rfqs,
        "user": user,
    })


@app.post("/quote/submit")
async def submit_quote(request: Request):
    form_data = await request.form()
    # In a real app we'd save this to a 'quotes' collection
    # Here, we'll just log and mock a success return to the dashboard
    print("New Quote Submitted:", form_data)
    
    # Redirect back to dashboard (or show a success message)
    # Re-fetch RFQs to render dashboard properly
    from database import db
    rfqs = []
    if db is not None:
        cursor = db["rfqs"].find({"status": "OPEN"}).sort("created_at", -1)
        async for document in cursor:
            document['_id'] = str(document['_id']) 
            rfqs.append(document)
            
    return templates.TemplateResponse("supplier_dashboard.html", {
        "request": request, 
        "rfqs": rfqs,
        "success": True,
        "message": "Your quote was successfully sent to the buyer!"
    })

# ----------------------------------------
# AI TOOLS MODULE
# ----------------------------------------

BASE_RATES = {
    "Cotton": 3.50,
    "Polyester": 2.20,
    "Linen": 5.00,
    "Blend": 3.00,
    "Silk": 8.50,
    "Unknown": 3.00
}

def calculate_predicted_price(category: str, fabric: str, quantity: int, urgency: str, certifications: list) -> dict:
    base = BASE_RATES.get(fabric, 3.00)
    
    # Volume discount
    if quantity > 10000:
        base *= 0.90
    elif quantity > 5000:
        base *= 0.95
        
    # Urgency premium
    if urgency == "HIGH":
        base *= 1.15
    elif urgency == "LOW":
        base *= 0.95
        
    # Certification costs
    base += len(certifications) * 0.20
    
    estimated_min = base * 0.92
    estimated_max = base * 1.08
    
    return {
        "estimated_min": round(estimated_min, 2),
        "estimated_max": round(estimated_max, 2)
    }

from pydantic import BaseModel
class PredictPriceRequest(BaseModel):
    category: str
    fabric: str
    quantity: int
    urgency: str
    certifications: list

@app.post("/api/predict-price")
async def predict_price(payload: PredictPriceRequest):
    result = calculate_predicted_price(
        payload.category, 
        payload.fabric, 
        payload.quantity, 
        payload.urgency, 
        payload.certifications
    )
    return result

PANTONE_COLORS = [
    ((19, 42, 63), "PANTONE 19-4052 TCX", "Classic Blue", "#1b4478"),
    ((65, 64, 60), "PANTONE 19-4033 TCX", "Classic Grey", "#41403c"),
    ((240, 240, 240), "PANTONE 19-4006 TCX", "White Navy", "#f0f0f0"),
    ((194, 156, 105), "PANTONE 16-1144 TCX", "Oxford Tan", "#c29c69"),
    ((155, 126, 86), "PANTONE 17-1044 TCX", "Rawhide", "#9b7e56"),
    ((44, 64, 89), "PANTONE 19-4035 TCX", "Salute", "#2c4059"),
    ((138, 30, 65), "PANTONE 19-1536 TCX", "Red", "#8a1e41"),
    ((71, 105, 48), "PANTONE 18-0527 TCX", "Olive", "#476930"),
]

def closest_pantone(rgb):
    min_dist = float('inf')
    best_match = None
    for p_rgb, p_name, p_friendly, p_hex in PANTONE_COLORS:
        dist = math.sqrt((rgb[0] - p_rgb[0])**2 + (rgb[1] - p_rgb[1])**2 + (rgb[2] - p_rgb[2])**2)
        if dist < min_dist:
            min_dist = dist
            best_match = {"pantone": p_name, "name": p_friendly, "hex": p_hex}
    return best_match

@app.post("/api/extract-palette")
async def extract_palette(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")
    
    contents = await file.read()
    try:
        color_thief = ColorThief(io.BytesIO(contents))
        # Get a larger palette to find distinct colors, ColorThief extracts dominant colors
        palette = color_thief.get_palette(color_count=5)
        
        results = []
        for rgb in palette:
            match = closest_pantone(rgb)
            if match not in results:
                results.append(match)
                if len(results) == 3: # Limit to top 3 distinct
                    break
                    
        return {"colors": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------
# REVERSE AUCTION SYSTEM
# ----------------------------------------

@app.get("/auction/{rfq_id}", response_class=HTMLResponse)
async def auction_room(request: Request, rfq_id: str, user: Optional[dict] = Depends(get_current_user)):
    """Display the reverse auction room for a specific RFQ."""
    import database
    
    rfq = None
    bids = []
    time_remaining = None
    auction_active = False
    company = None
    
    # Get user's company data if logged in
    if user and database.db is not None:
        company = await database.db["companies"].find_one({"id": user.get("company_id")})
        
        # ✅ CHECK PREMIUM SUBSCRIPTION - Reverse auctions are PREMIUM only
        if company:
            subscription_tier = company.get("subscription_tier", "FREE")
            if subscription_tier != "PREMIUM":
                # Show premium required page
                return templates.TemplateResponse("premium_required.html", {
                    "request": request,
                    "user": user,
                    "feature_name": "Reverse Auctions",
                    "feature_description": "Participate in live reverse auctions and submit competitive bids to win contracts."
                })
    else:
        # Not logged in - redirect to login
        if not user:
            return RedirectResponse(url="/login?next=/auction/" + rfq_id, status_code=303)
    
    if database.db is not None:
        try:
            rfq = await database.db["rfqs"].find_one({"id": rfq_id})
            
            if rfq:
                # Convert ObjectId to string to avoid serialization errors
                rfq["_id"] = str(rfq["_id"])
                
                if rfq.get("is_reverse_auction"):
                    auction_active = True
                    
                    # Fetch only the latest bid from each supplier using aggregation
                    # This ensures each supplier appears only once with their most recent bid
                    pipeline = [
                        {"$match": {"rfq_id": rfq_id, "status": "ACTIVE"}},
                        {"$sort": {"timestamp": -1}},  # Sort by timestamp descending (newest first)
                        {"$group": {
                            "_id": "$supplier_id",  # Group by supplier_id
                            "latest_bid": {"$first": "$$ROOT"}  # Take the first (most recent) bid
                        }},
                        {"$replaceRoot": {"newRoot": "$latest_bid"}},  # Replace root with the bid document
                        {"$sort": {"bid_price": -1}}  # Sort by price descending (highest first)
                    ]
                    
                    raw_bids = await database.db["bids"].aggregate(pipeline).to_list(length=None)
                    
                    # Convert ObjectIds in bids
                    for bid in raw_bids:
                        bid["_id"] = str(bid["_id"])
                        bids.append(bid)
                    
                    # Calculate time remaining
                    if rfq.get("auction_end_time"):
                        auction_end = rfq.get("auction_end_time")
                        if isinstance(auction_end, str):
                            auction_end = datetime.fromisoformat(auction_end)
                        now = datetime.utcnow()
                        time_diff = auction_end - now
                        time_remaining = max(0, int(time_diff.total_seconds()))
                        
                        # Auto-close if time expired
                        if time_remaining == 0 and rfq.get("status") == "OPEN":
                            await database.db["rfqs"].update_one(
                                {"id": rfq_id},
                                {"$set": {"status": "EVALUATING"}}
                            )
                            auction_active = False
        except Exception as e:
            print(f"Error fetching auction data: {e}")
            import traceback
            traceback.print_exc()
    
    return templates.TemplateResponse("auction_room.html", {
        "request": request,
        "rfq": rfq,
        "bids": bids,
        "time_remaining": time_remaining,
        "auction_active": auction_active,
        "rfq_id": rfq_id,
        "user": user,
        "company": company
    })


@app.post("/api/auction/bid")
async def place_bid(request: Request, user: dict = Depends(require_login)):
    """Place a bid in a reverse auction. Requires login and PREMIUM subscription. Validates supplier role, auction time, and bid amount."""
    from fastapi.responses import JSONResponse
    import database
    import uuid
    
    try:
        form_data = await request.form()
        rfq_id = form_data.get("rfq_id", "").strip()
        supplier_id = form_data.get("supplier_id", "").strip()
        supplier_name = form_data.get("supplier_name", "").strip()
        bid_price = float(form_data.get("bid_price", 0))
        
        errors = {}
        
        if not rfq_id:
            errors["rfq_id"] = "RFQ ID is required"
        if not supplier_id:
            errors["supplier_id"] = "Supplier ID is required"
        if bid_price <= 0:
            errors["bid_price"] = "Bid price must be greater than 0"
        
        if errors:
            return JSONResponse({"success": False, "errors": errors}, status_code=422)
        
        if database.db is None:
            return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
        # Get logged-in user's company to validate ID and name
        user_company = await database.db["companies"].find_one({"id": user.get("company_id")})
        
        if not user_company:
            return JSONResponse({"success": False, "error": "Company not found for logged-in user"}, status_code=404)
        
        # ✅ CHECK PREMIUM SUBSCRIPTION - Reverse auctions are PREMIUM only
        subscription_tier = user_company.get("subscription_tier", "FREE")
        if subscription_tier != "PREMIUM":
            return JSONResponse({
                "success": False,
                "error": "Premium subscription required",
                "message": "Reverse auction bidding is only available for PREMIUM subscribers. Upgrade your plan to participate in reverse auctions.",
                "upgrade_required": True,
                "current_tier": subscription_tier
            }, status_code=403)
        
        # Validate that submitted supplier_id matches user's company unique_id
        if user_company.get("unique_id") != supplier_id:
            return JSONResponse({
                "success": False, 
                "error": f"Company ID does not match your account. Your ID is: {user_company.get('unique_id')}"
            }, status_code=403)
        
        # Validate that submitted supplier_name matches user's company name
        if user_company.get("name") != supplier_name:
            return JSONResponse({
                "success": False, 
                "error": f"Company name does not match your account. Your company name is: {user_company.get('name')}"
            }, status_code=403)
        
        # Fetch RFQ
        rfq = await database.db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            return JSONResponse({"success": False, "error": "RFQ not found"}, status_code=404)
        
        if not rfq.get("is_reverse_auction"):
            return JSONResponse({"success": False, "error": "This RFQ is not a reverse auction"}, status_code=400)
        
        # Check auction status
        if rfq.get("status") != "OPEN":
            return JSONResponse({"success": False, "error": "Auction is not open"}, status_code=400)
        
        # Check auction time
        if rfq.get("auction_end_time"):
            auction_end = rfq.get("auction_end_time")
            if isinstance(auction_end, str):
                auction_end = datetime.fromisoformat(auction_end)
            if datetime.utcnow() > auction_end:
                return JSONResponse({"success": False, "error": "Auction has ended"}, status_code=400)
        
        # Create bid record with a unique ID to ensure each bid is stored separately
        bid = BidModel(
            id=str(uuid.uuid4()),  # Explicitly generate a new unique ID for each bid
            rfq_id=rfq_id,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            bid_price=bid_price,
            timestamp=datetime.utcnow()  # Explicitly set timestamp
        )
        
        # Convert to dict for MongoDB insertion
        bid_dict = bid.model_dump()
        
        # Save bid to database - each bid is a separate document
        result = await database.db["bids"].insert_one(bid_dict)
        
        print(f"New bid inserted: ID={bid.id}, Supplier={supplier_name}, Price=${bid_price:.2f}, MongoDB _id={result.inserted_id}")
        
        # Send notification to buyer about new bid
        await notify_bid_submitted(rfq_id, supplier_name, bid_price)
        
        return JSONResponse({
            "success": True,
            "message": f"Bid placed successfully at ${bid_price:.2f}!",
            "bid_id": bid.id,
            "bid_price": bid_price
        })
    
    except Exception as e:
        print(f"Error placing bid: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.delete("/api/auction/bid/{bid_id}")
async def delete_bid(bid_id: str, user: dict = Depends(require_login)):
    """Delete a bid. Only the bid owner can delete their bid."""
    from fastapi.responses import JSONResponse
    import database
    
    try:
        if database.db is None:
            return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
        # Get user's company
        user_company = await database.db["companies"].find_one({"id": user.get("company_id")})
        
        if not user_company:
            return JSONResponse({"success": False, "error": "Company not found"}, status_code=404)
        
        # Find the bid
        bid = await database.db["bids"].find_one({"id": bid_id})
        
        if not bid:
            return JSONResponse({"success": False, "error": "Bid not found"}, status_code=404)
        
        # Verify the bid belongs to the logged-in user
        if bid.get("supplier_id") != user_company.get("unique_id"):
            return JSONResponse({
                "success": False, 
                "error": "You can only delete your own bids"
            }, status_code=403)
        
        # Delete the bid
        result = await database.db["bids"].delete_one({"id": bid_id})
        
        if result.deleted_count == 0:
            return JSONResponse({"success": False, "error": "Failed to delete bid"}, status_code=500)
        
        print(f"Bid deleted: ID={bid_id}, Supplier={bid.get('supplier_name')}")
        
        return JSONResponse({
            "success": True,
            "message": "Bid deleted successfully"
        })
    
    except Exception as e:
        print(f"Error deleting bid: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/auction/{rfq_id}/status")
async def get_auction_status(rfq_id: str):
    """Get real-time auction status including current lowest bid and all bids."""
    from fastapi.responses import JSONResponse
    import database
    
    try:
        if database.db is None:
            return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
        rfq = await database.db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            return JSONResponse({"success": False, "error": "RFQ not found"}, status_code=404)
        
        if not rfq.get("is_reverse_auction"):
            return JSONResponse({"success": False, "error": "This RFQ is not a reverse auction"}, status_code=400)
        
        # Fetch only the latest bid from each supplier using aggregation
        # This ensures each supplier appears only once with their most recent bid
        pipeline = [
            {"$match": {"rfq_id": rfq_id, "status": "ACTIVE"}},
            {"$sort": {"timestamp": -1}},  # Sort by timestamp descending (newest first)
            {"$group": {
                "_id": "$supplier_id",  # Group by supplier_id
                "latest_bid": {"$first": "$$ROOT"}  # Take the first (most recent) bid
            }},
            {"$replaceRoot": {"newRoot": "$latest_bid"}},  # Replace root with the bid document
            {"$sort": {"bid_price": -1}}  # Sort by price descending (highest first)
        ]
        
        bids = await database.db["bids"].aggregate(pipeline).to_list(length=None)
        
        # Format bids for JSON response
        formatted_bids = []
        for bid in bids:
            ts = bid.get("timestamp")
            if ts and hasattr(ts, "isoformat"):
                ts_str = ts.isoformat()
            elif ts:
                ts_str = str(ts)
            else:
                ts_str = ""
            formatted_bids.append({
                "supplier_id": bid.get("supplier_id"),
                "supplier_name": bid.get("supplier_name"),
                "bid_price": bid.get("bid_price"),
                "timestamp": ts_str
            })
        
        # Calculate time remaining
        time_remaining = None
        if rfq.get("auction_end_time"):
            auction_end = rfq.get("auction_end_time")
            if isinstance(auction_end, str):
                auction_end = datetime.fromisoformat(auction_end)
            now = datetime.utcnow()
            time_diff = auction_end - now
            time_remaining = max(0, int(time_diff.total_seconds()))
        
        return {
            "success": True,
            "rfq_id": rfq_id,
            "current_lowest_bid": rfq.get("current_lowest_bid"),
            "lowest_bidder": rfq.get("lowest_bidder_id"),
            "auction_status": rfq.get("status"),
            "bid_count": len(bids),
            "bids": formatted_bids,
            "time_remaining": time_remaining
        }
    
    except Exception as e:
        print(f"Error fetching auction status: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/auction/{rfq_id}/close")
async def close_auction(rfq_id: str):
    """Admin endpoint to manually close an auction."""
    from fastapi.responses import JSONResponse
    import database
    
    try:
        if database.db is None:
            return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
        rfq = await database.db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            return JSONResponse({"success": False, "error": "RFQ not found"}, status_code=404)
        
        if not rfq.get("is_reverse_auction"):
            return JSONResponse({"success": False, "error": "This RFQ is not a reverse auction"}, status_code=400)
        
        # Update RFQ status
        await database.db["rfqs"].update_one(
            {"id": rfq_id},
            {"$set": {"status": "EVALUATING"}}
        )
        
        return JSONResponse({
            "success": True,
            "message": "Auction closed successfully",
            "winning_bid_price": rfq.get("current_lowest_bid"),
            "winning_supplier_id": rfq.get("lowest_bidder_id")
        })
    
    except Exception as e:
        print(f"Error closing auction: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ----------------------------------------
# NOTIFICATION SYSTEM
# ----------------------------------------

async def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    related_id: Optional[str] = None
):
    """
    Helper function to create a notification for a user.
    This simulates external API integration for notifications.
    """
    from models import NotificationModel
    from database import db
    
    if db is None:
        print("Database not available - cannot create notification")
        return
    
    notification = NotificationModel(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id
    )
    
    try:
        await db["notifications"].insert_one(notification.dict())
        print(f"✅ Notification created for user {user_id}: {title}")
    except Exception as e:
        print(f"❌ Error creating notification: {e}")


@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request, user: dict = Depends(require_login)):
    """Display notifications page."""
    return templates.TemplateResponse("notifications.html", {"request": request, "user": user})


@app.get("/api/notifications")
async def get_notifications(
    limit: int = 20,
    user: dict = Depends(require_login)
):
    """Get user notifications with pagination."""
    from database import db
    from bson import ObjectId
    
    if db is None:
        print("⚠️  Database not available")
        return {"notifications": [], "unread_count": 0}
    
    try:
        print(f"🔍 Fetching notifications for user: {user.get('email', 'unknown')} (ID: {user.get('id')})")
        
        # Get notifications for the user
        notifications = await db["notifications"].find(
            {"user_id": user["id"]}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        print(f"📦 Found {len(notifications)} notifications in database")
        
        # Convert to JSON-serializable format
        serialized_notifications = []
        for idx, notif in enumerate(notifications):
            try:
                # Get created_at and ensure it's properly formatted as UTC
                created_at = notif.get("created_at")
                if isinstance(created_at, datetime):
                    # Convert to ISO format with 'Z' suffix to indicate UTC
                    created_at_str = created_at.isoformat() + 'Z' if not created_at.isoformat().endswith('Z') else created_at.isoformat()
                else:
                    created_at_str = str(created_at)
                
                # Create a clean dict without MongoDB-specific fields
                clean_notif = {
                    "id": str(notif.get("id", notif.get("_id", f"notif_{idx}"))),
                    "user_id": str(notif.get("user_id", "")),
                    "type": str(notif.get("type", "unknown")),
                    "title": str(notif.get("title", "Notification")),
                    "message": str(notif.get("message", "")),
                    "is_read": bool(notif.get("is_read", False)),
                    "created_at": created_at_str,
                    "related_id": str(notif.get("related_id")) if notif.get("related_id") else None
                }
                serialized_notifications.append(clean_notif)
            except Exception as notif_error:
                print(f"⚠️  Error serializing notification {idx}: {notif_error}")
                # Skip problematic notification but continue processing others
                continue
        
        # Count unread notifications
        unread_count = await db["notifications"].count_documents({
            "user_id": user["id"],
            "is_read": False
        })
        
        print(f"✅ Returning {len(serialized_notifications)} notifications ({unread_count} unread)")
        
        return {
            "notifications": serialized_notifications,
            "unread_count": unread_count
        }
    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        import traceback
        traceback.print_exc()
        return {"notifications": [], "unread_count": 0}


@app.get("/api/notifications/count")
async def get_notification_count(user: dict = Depends(require_login)):
    """Get unread notification count."""
    from database import db
    
    if db is None:
        return {"unread_count": 0}
    
    try:
        unread_count = await db["notifications"].count_documents({
            "user_id": user["id"],
            "is_read": False
        })
        
        return {"unread_count": unread_count}
        return JSONResponse({"unread_count": unread_count})
    except Exception as e:
        print(f"Error counting notifications: {e}")
        return JSONResponse({"unread_count": 0})


@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user: dict = Depends(require_login)
):
    """Mark a notification as read."""
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        result = await db["notifications"].update_one(
            {"id": notification_id, "user_id": user["id"]},
            {"$set": {"is_read": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return JSONResponse({"success": True, "message": "Notification marked as read"})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")


@app.post("/api/notifications/mark-all-read")
async def mark_all_notifications_read(user: dict = Depends(require_login)):
    """Mark all notifications as read for the current user."""
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        result = await db["notifications"].update_many(
            {"user_id": user["id"], "is_read": False},
            {"$set": {"is_read": True}}
        )
        
        return JSONResponse({
            "success": True,
            "message": f"Marked {result.modified_count} notifications as read"
        })
    except Exception as e:
        print(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")


# ----------------------------------------
# NOTIFICATION TRIGGERS
# ----------------------------------------

# Modify the place_bid endpoint to send notifications
# This is an example - you would add similar triggers to other endpoints

async def notify_bid_submitted(rfq_id: str, supplier_name: str, bid_price: float):
    """Send notification when a new bid is submitted."""
    from database import db
    
    if db is None:
        return
    
    # Get RFQ to find buyer
    rfq = await db["rfqs"].find_one({"id": rfq_id})
    if not rfq:
        return
    
    buyer_id = rfq.get("buyer_id")
    if not buyer_id:
        return
    
    # Find user associated with buyer
    user = await db["users"].find_one({"company_id": buyer_id})
    if not user:
        return
    
    # Create notification for buyer
    await create_notification(
        user_id=user["id"],
        notification_type="bid_submitted",
        title="New Bid Received",
        message=f"{supplier_name} submitted a bid of ${bid_price:.2f} per unit on your RFQ: {rfq.get('title', 'Untitled')}",
        related_id=rfq_id
    )


async def notify_new_rfq(rfq_id: str, rfq_title: str, product_category: str):
    """Send notification to all suppliers when a new RFQ is posted."""
    from database import db
    
    if db is None:
        print("❌ Notification: Database not available")
        return
    
    try:
        # Get all supplier companies
        suppliers = await db["companies"].find({"role": "SUPPLIER"}).to_list(length=1000)
        
        print(f"📢 Sending RFQ notifications to {len(suppliers)} suppliers")
        
        notification_count = 0
        for supplier in suppliers:
            # Find user associated with supplier
            user = await db["users"].find_one({"company_id": supplier["id"]})
            if user:
                await create_notification(
                    user_id=user["id"],
                    notification_type="new_rfq",
                    title="New RFQ Posted",
                    message=f"A new RFQ has been posted: {rfq_title} ({product_category}). Check it out and submit your bid!",
                    related_id=rfq_id
                )
                notification_count += 1
            else:
                print(f"⚠️  No user found for supplier company: {supplier.get('name', 'Unknown')} (ID: {supplier['id']})")
        
        print(f"✅ Sent {notification_count} notifications for new RFQ: {rfq_title}")
        
    except Exception as e:
        print(f"❌ Error sending RFQ notifications: {e}")
        import traceback
        traceback.print_exc()


async def notify_new_auction(rfq_id: str, rfq_title: str, auction_end_time: datetime):
    """Send notification to all suppliers when a new reverse auction starts."""
    from database import db
    
    if db is None:
        print("❌ Notification: Database not available")
        return
    
    try:
        # Get all supplier companies
        suppliers = await db["companies"].find({"role": "SUPPLIER"}).to_list(length=1000)
        
        print(f"📢 Sending auction notifications to {len(suppliers)} suppliers")
        
        # Format end time
        time_str = auction_end_time.strftime("%B %d, %Y at %I:%M %p UTC")
        
        notification_count = 0
        for supplier in suppliers:
            # Find user associated with supplier
            user = await db["users"].find_one({"company_id": supplier["id"]})
            if user:
                await create_notification(
                    user_id=user["id"],
                    notification_type="new_auction",
                    title="New Reverse Auction Started",
                    message=f"A new reverse auction has started: {rfq_title}. Auction ends on {time_str}. Place your bid now!",
                    related_id=rfq_id
                )
                notification_count += 1
            else:
                print(f"⚠️  No user found for supplier company: {supplier.get('name', 'Unknown')} (ID: {supplier['id']})")
        
        print(f"✅ Sent {notification_count} notifications for new auction: {rfq_title}")
        
    except Exception as e:
        print(f"❌ Error sending auction notifications: {e}")
        import traceback
        traceback.print_exc()


async def notify_auction_deadline(rfq_id: str, rfq_title: str, hours_remaining: int):
    """Send notification reminder about auction deadline."""
    from database import db
    
    if db is None:
        return
    
    # Get all bidders for this auction
    bids = await db["bids"].find({"rfq_id": rfq_id, "status": "ACTIVE"}).to_list(length=1000)
    
    # Get unique supplier IDs
    supplier_ids = list(set([bid["supplier_id"] for bid in bids]))
    
    for supplier_id in supplier_ids:
        # Find user associated with supplier
        user = await db["users"].find_one({"company_id": supplier_id})
        if user:
            await create_notification(
                user_id=user["id"],
                notification_type="auction_deadline",
                title="Auction Ending Soon",
                message=f"The auction for '{rfq_title}' ends in {hours_remaining} hours. Update your bid to stay competitive!",
                related_id=rfq_id
            )


# ----------------------------------------
# RFQ DETAIL VIEW
# ----------------------------------------

@app.get("/rfq/{rfq_id}", response_class=HTMLResponse)
async def rfq_detail_page(request: Request, rfq_id: str, user: Optional[dict] = Depends(get_current_user)):
    """Display detailed view of a specific RFQ with edit/delete options for owner."""
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Get RFQ
        rfq = await db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        # Check if current user is the owner
        is_owner = False
        if user:
            user_company = await db["companies"].find_one({"id": user.get("company_id")})

            is_owner = (
                rfq.get("buyer_id") == user.get("id") or
                rfq.get("buyer_id") == user.get("company_id") or
                (user_company and rfq.get("buyer_id") == user_company.get("id")) or
                (user_company and rfq.get("buyer_id") == user_company.get("unique_id")) or
                rfq.get("buyer_id") == "SIMULATED_BUYER_123"
            )

            # Also treat as owner if user accepted a bid on this RFQ
            # (handles case where buyer_id format doesn't match)
            if not is_owner:
                accepted_bid = await db["bids"].find_one({
                    "rfq_id": rfq_id,
                    "status": {"$in": ["ACCEPTED", "CONFIRMED"]}
                })
                if accepted_bid:
                    # Check if current user is NOT the bidder (i.e. they are the acceptor/buyer)
                    bidder_ids = {accepted_bid.get("supplier_id")}
                    if user_company:
                        bidder_ids.add(user_company.get("unique_id"))
                        bidder_ids.add(user_company.get("id"))
                    bidder_ids.discard(None)
                    # If user is not the bidder, they must be the one who accepted = buyer
                    user_all_ids = {user.get("id"), user.get("company_id")}
                    if user_company:
                        user_all_ids.add(user_company.get("id"))
                        user_all_ids.add(user_company.get("unique_id"))
                    user_all_ids.discard(None)
                    if not (user_all_ids & bidder_ids):
                        is_owner = True  # user is the acceptor = buyer
        
        # Fetch all bids for this RFQ
        # Determine current user's company role and IDs for bid ownership checks
        user_company_role = user_company.get("role", "").upper() if user_company else ""
        user_company_ids = set()
        if user:
            user_company_ids.add(user.get("id"))
            user_company_ids.add(user.get("company_id"))
            if user_company:
                user_company_ids.add(user_company.get("id"))
                user_company_ids.add(user_company.get("unique_id"))
        user_company_ids.discard(None)

        bids = []
        async for bid in db["bids"].find({"rfq_id": rfq_id}).sort("bid_price", 1):
            bid["_id"] = str(bid["_id"])
            
            # First, clean up any old PENDING payments for this bid (older than 30 minutes)
            from datetime import timedelta
            thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
            await db["payments"].delete_many({
                "order_id": rfq_id,
                "bid_id": bid.get("id"),
                "status": EscrowStatusEnum.PENDING,
                "created_at": {"$lt": thirty_minutes_ago}
            })
            
            # Check if THIS specific bid has been paid (only PAID_IN_ESCROW or RELEASED)
            existing_payment = await db["payments"].find_one({
                "order_id": rfq_id,
                "bid_id": bid.get("id"),
                "status": {"$in": ["PAID_IN_ESCROW", "RELEASED"]}
            })
            bid["already_paid"] = existing_payment is not None
            
            # Check if contract exists for this bid
            contract = await db["contracts"].find_one({
                "rfq_id": rfq_id,
                "bid_id": bid.get("id")
            })
            if contract:
                bid["contract_id"] = contract.get("contract_id")
                bid["contract_status"] = contract.get("status")
            else:
                bid["contract_id"] = None
                bid["contract_status"] = None
            
            # Flag if this bid was placed by the current user (so they can't accept their own)
            bid["is_own_bid"] = bid.get("supplier_id") in user_company_ids
            bids.append(bid)

        return templates.TemplateResponse("rfq_detail.html", {
            "request": request,
            "user": user,
            "rfq": rfq,
            "is_owner": is_owner,
            "bids": bids,
            "user_company_role": user_company_role,
            "is_buyer_role": user_company_role == "BUYER",
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading RFQ detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to load RFQ details")


@app.get("/rfq/{rfq_id}/edit", response_class=HTMLResponse)
async def rfq_edit_page(request: Request, rfq_id: str, user: dict = Depends(require_login)):
    """Display RFQ edit page (only for owner)."""
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Get RFQ
        rfq = await db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        # Check ownership with improved logic
        user_company = await db["companies"].find_one({"id": user.get("company_id")})
        
        is_owner = (
            rfq.get("buyer_id") == user.get("id") or  # Direct user ID match
            rfq.get("buyer_id") == user.get("company_id") or  # Company ID match
            (user_company and rfq.get("buyer_id") == user_company.get("id")) or  # Company doc ID match
            (user_company and rfq.get("buyer_id") == user_company.get("unique_id")) or  # Company unique_id match
            rfq.get("buyer_id") == "SIMULATED_BUYER_123"  # Legacy: treat all simulated RFQs as editable
        )
        
        if not is_owner:
            raise HTTPException(status_code=403, detail="You can only edit your own RFQs")
        
        # Return the RFQ builder page with pre-filled data
        return templates.TemplateResponse("rfq_builder.html", {
            "request": request,
            "user": user,
            "rfq": rfq,
            "edit_mode": True
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading RFQ edit page: {e}")
        raise HTTPException(status_code=500, detail="Failed to load RFQ edit page")


@app.put("/api/rfq/{rfq_id}")
async def update_rfq(rfq_id: str, request: Request, user: dict = Depends(require_login)):
    """Update an existing RFQ. Only the RFQ creator can update their RFQ."""
    from database import db
    from fastapi.responses import JSONResponse
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        # Get RFQ
        rfq = await db["rfqs"].find_one({"id": rfq_id})
        
        if not rfq:
            return JSONResponse({"success": False, "error": "RFQ not found"}, status_code=404)
        
        # Check ownership with improved logic
        user_company = await db["companies"].find_one({"id": user.get("company_id")})
        
        is_owner = (
            rfq.get("buyer_id") == user.get("id") or  # Direct user ID match
            rfq.get("buyer_id") == user.get("company_id") or  # Company ID match
            (user_company and rfq.get("buyer_id") == user_company.get("id")) or  # Company doc ID match
            (user_company and rfq.get("buyer_id") == user_company.get("unique_id")) or  # Company unique_id match
            rfq.get("buyer_id") == "SIMULATED_BUYER_123"  # Legacy: treat all simulated RFQs as editable
        )
        
        if not is_owner:
            return JSONResponse({"success": False, "error": "You can only update your own RFQs"}, status_code=403)
        
        # Get update data from request
        form_data = await request.form()
        
        # Build update dict (similar to create, but updating existing)
        update_data = {}
        
        # Basic fields
        if form_data.get("title"):
            update_data["title"] = form_data.get("title").strip()
        if form_data.get("product_category"):
            update_data["product_category"] = form_data.get("product_category").strip()
        if form_data.get("urgency_level"):
            update_data["urgency_level"] = form_data.get("urgency_level")
        if form_data.get("quantity"):
            update_data["quantity"] = int(form_data.get("quantity"))
        if form_data.get("fabric_type"):
            update_data["fabric_type"] = form_data.get("fabric_type")
        if form_data.get("fabric_gsm"):
            update_data["fabric_gsm"] = form_data.get("fabric_gsm")
        
        # Update in database
        result = await db["rfqs"].update_one(
            {"id": rfq_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return JSONResponse({"success": False, "error": "No changes made"}, status_code=400)
        
        return JSONResponse({
            "success": True,
            "message": "RFQ updated successfully",
            "rfq_id": rfq_id
        })
    
    except Exception as e:
        print(f"Error updating RFQ: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# =====================================================    })
