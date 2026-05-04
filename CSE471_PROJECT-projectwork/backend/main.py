from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Depends, Header, Cookie, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import hashlib
import secrets

from database import connect_to_mongo, close_mongo_connection, db
from models import RoleEnum, OverallStatusEnum, CompanyModel, LegalAndCapacityModel, CertificationModel, CertTypeEnum, VerificationStatusEnum, RFQModel, RFQStatusEnum, BidModel, BidStatusEnum, SubscriptionTierEnum, UserModel, NotificationModel, NotificationTypeEnum, EscrowStatusEnum, PaymentModel, ShippingCalculateRequest, ShippingRateModel, ShippingMethodEnum, IncotermEnum, ContractModel, ContractStatusEnum, MessageModel
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
        
        # Create indexes for buyer queries (Task 13.1)
        try:
            await _db["rfqs"].create_index("buyer_id")
            await _db["rfqs"].create_index("status")
            await _db["payments"].create_index("buyer_id")
            await _db["payments"].create_index("status")
            print("✅ Buyer query indexes ensured")
        except Exception as e:
            print(f"⚠️ Failed to create buyer indexes: {e}")
        
        # Create indexes for supplier queries (Task 13.2)
        try:
            await _db["bids"].create_index("supplier_id")
            await _db["bids"].create_index("status")
            await _db["payments"].create_index("supplier_id")
            await _db["rfqs"].create_index([("status", 1), ("created_at", -1)])  # Compound index
            print("✅ Supplier query indexes ensured")
        except Exception as e:
            print(f"⚠️ Failed to create supplier indexes: {e}")
        
        # Create indexes for chat messages
        try:
            await _db["messages"].create_index("rfq_id")
            await _db["messages"].create_index([("rfq_id", 1), ("timestamp", 1)])
            print("✅ Messages indexes ensured")
        except Exception as e:
            print(f"⚠️ Failed to create messages indexes: {e}")
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

# Serve uploaded files (chat images, etc.)
import os as _os
_uploads_dir = _os.path.join(_os.path.dirname(__file__), "..", "frontend", "src", "uploads")
_os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

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
# ACCESS CONTROL DEPENDENCY (RBAC Engine)
# ----------------------------------------
from models import UserRole

async def get_current_user_with_mock_role(
    x_user_role: Optional[str] = Header(None),
    user: Optional[dict] = Depends(get_current_user)
):
    """Retrieves user and their effective role, supporting a mock header for testing."""
    role = "GUEST"
    
    if x_user_role:
        role = x_user_role.upper()
    elif user:
        from database import db
        if db is not None:
            company = await db["companies"].find_one({"id": user.get("company_id")})
            if company:
                db_role = company.get("role", "").upper()
                # Map platform's SUPPLIER to the requested SELLER role
                role = UserRole.SELLER.value if db_role == "SUPPLIER" else db_role
                
    return user, role

async def require_buyer(user_and_role: tuple = Depends(get_current_user_with_mock_role)):
    user, role = user_and_role
    if role != UserRole.BUYER.value:
        raise HTTPException(status_code=403, detail="Access denied. BUYER privileges required.")
    return user or {"mock": True, "role": role}

async def require_seller(user_and_role: tuple = Depends(get_current_user_with_mock_role)):
    user, role = user_and_role
    if role != UserRole.SELLER.value:
        raise HTTPException(status_code=403, detail="Access denied. SELLER privileges required.")
    return user or {"mock": True, "role": role}

# Alias for existing routes that use require_supplier
require_supplier = require_seller

async def require_active_participant(user_and_role: tuple = Depends(get_current_user_with_mock_role)):
    user, role = user_and_role
    if role not in [UserRole.BUYER.value, UserRole.SELLER.value]:
        raise HTTPException(status_code=403, detail="Access denied. Active participant privileges required.")
    return user or {"mock": True, "role": role}

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

# ----------------------------------------
# ADMIN VERIFICATIONS
# ----------------------------------------

@app.get("/admin/verifications", response_class=HTMLResponse)
async def admin_verifications_page(request: Request, admin: dict = Depends(require_admin)):
    """Display admin profile verification queue page."""
    return templates.TemplateResponse("admin_verifications.html", {"request": request, "user": admin})


@app.get("/api/admin/verifications")
async def get_pending_verifications(admin: dict = Depends(require_admin)):
    """Get all companies pending verification."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        companies = await db["companies"].find({"overall_status": OverallStatusEnum.PENDING_REVIEW}).to_list(length=1000)
        
        # Hydrate with legal docs and certifications
        full_companies = []
        for company in companies:
            c_id = company.get("id")
            
            # Fetch legal
            legal = await db["legal_capacity"].find_one({"company_id": c_id})
            if legal:
                legal.pop("_id", None)
                
            # Fetch certifications
            certs = await db["certifications"].find({"company_id": c_id}).to_list(length=100)
            for cert in certs:
                cert.pop("_id", None)
                if isinstance(cert.get("issue_date"), datetime):
                    cert["issue_date"] = cert["issue_date"].isoformat() + 'Z'
                if isinstance(cert.get("expiry_date"), datetime):
                    cert["expiry_date"] = cert["expiry_date"].isoformat() + 'Z'
                    
            full_companies.append({
                "id": c_id,
                "name": company.get("name"),
                "role": company.get("role"),
                "overall_status": company.get("overall_status"),
                "created_at": company.get("created_at").isoformat() + 'Z' if isinstance(company.get("created_at"), datetime) else str(company.get("created_at")),
                "legal_capacity": legal,
                "certifications": certs
            })
            
        return {
            "success": True,
            "companies": full_companies
        }
    except Exception as e:
        print(f"Error fetching verifications: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/admin/verify/{company_id}")
async def approve_verification(company_id: str, admin: dict = Depends(require_admin)):
    """Approve a company profile verification."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
    try:
        company = await db["companies"].find_one({"id": company_id})
        if not company:
            return JSONResponse({"success": False, "error": "Company not found"}, status_code=404)
            
        # Update company status and default trust score to 50
        await db["companies"].update_one(
            {"id": company_id},
            {"$set": {
                "overall_status": OverallStatusEnum.VERIFIED,
                "trust_score": 50
            }}
        )
        
        # Update all pending certs to VERIFIED
        await db["certifications"].update_many(
            {"company_id": company_id, "verification_status": VerificationStatusEnum.PENDING},
            {"$set": {"verification_status": VerificationStatusEnum.VERIFIED}}
        )
        
        # Find the user belonging to this company to notify them
        user = await db["users"].find_one({"company_id": company_id})
        if user:
            notification = NotificationModel(
                user_id=user["id"],
                type=NotificationTypeEnum.SAMPLE_APPROVED, # Reusing this for general approval
                title="Profile Verified",
                message="Your company profile and documents have been successfully verified by an administrator! You now have a starting Trust Score of 50.",
                related_id=company_id
            )
            await db["notifications"].insert_one(notification.model_dump())
            
        return {"success": True, "message": "Company verified successfully"}
    except Exception as e:
        print(f"Error approving verification: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/admin/reject/{company_id}")
async def reject_verification(company_id: str, admin: dict = Depends(require_admin)):
    """Reject a company profile verification."""
    from database import db
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
    try:
        company = await db["companies"].find_one({"id": company_id})
        if not company:
            return JSONResponse({"success": False, "error": "Company not found"}, status_code=404)
            
        # Update company status to REJECTED
        await db["companies"].update_one(
            {"id": company_id},
            {"$set": {"overall_status": OverallStatusEnum.REJECTED}}
        )
        
        # Update all pending certs to INVALID
        await db["certifications"].update_many(
            {"company_id": company_id, "verification_status": VerificationStatusEnum.PENDING},
            {"$set": {"verification_status": VerificationStatusEnum.INVALID}}
        )
        
        # Find the user belonging to this company to notify them
        user = await db["users"].find_one({"company_id": company_id})
        if user:
            notification = NotificationModel(
                user_id=user["id"],
                type=NotificationTypeEnum.SAMPLE_REJECTED, # Reusing this for general rejection
                title="Profile Rejected",
                message="Your company profile verification was rejected. Please review your documents and try again or contact support.",
                related_id=company_id
            )
            await db["notifications"].insert_one(notification.model_dump())
            
        return {"success": True, "message": "Company rejected successfully"}
    except Exception as e:
        print(f"Error rejecting verification: {e}")
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
            # Only lock if user is on PREMIUM plan (they paid for it). Free users are never locked.
            can_change_after = company.get("subscription_can_change_after")
            if can_change_after is not None and company.get("subscription_tier") == "PREMIUM":
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
            # Only lock if user is on PREMIUM plan (they paid for it). Free users are never locked.
            can_change_after = company.get("subscription_can_change_after")
            if can_change_after is not None and company.get("subscription_tier") == "PREMIUM":
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
        user_id = user.get("id")
        company = await db["companies"].find_one({"id": company_id})
        
        if not company:
            return {}
        
        company_name = company.get("name", "")
        buyer_ids = [user_id, company_id]
        if company.get("unique_id"):
            buyer_ids.append(company.get("unique_id"))
        
        # Fetch RFQs created by this buyer (using multiple ID formats)
        rfqs_cursor = db["rfqs"].find({"$or": [
            {"buyer_company": company_name},
            {"buyer_id": {"$in": buyer_ids}}
        ]})
        rfqs = await rfqs_cursor.to_list(length=None)
        total_rfqs = len(rfqs)
        rfq_ids = [rfq.get("id") for rfq in rfqs]
        
        # Count RFQs by status
        open_rfqs = len([r for r in rfqs if r.get("status") == "OPEN"])
        evaluating_rfqs = len([r for r in rfqs if r.get("status") == "EVALUATING"])
        awarded_rfqs = len([r for r in rfqs if r.get("status") == "AWARDED"])
        
        # Fetch all bids on buyer's RFQs
        bids_cursor = db["bids"].find({"rfq_id": {"$in": rfq_ids}})
        all_bids = await bids_cursor.to_list(length=None)
        total_bids_received = len(all_bids)
        
        # Fetch all payments made by this buyer
        payments_cursor = db["payments"].find({"buyer_id": {"$in": buyer_ids}})
        all_payments = await payments_cursor.to_list(length=None)
        
        # Fetch all FULLY_EXECUTED contracts for this buyer (awaiting payment)
        # Use the same query as the contracts page to ensure consistency
        contracts_cursor = db["contracts"].find({
            "$or": [
                {"buyer_id": user_id},
                {"buyer_id": {"$in": buyer_ids}}
            ],
            "status": "FULLY_EXECUTED"
        })
        all_contracts = await contracts_cursor.to_list(length=None)
        orders_awaiting_payment = len(all_contracts)
        
        print(f"DEBUG: Found {orders_awaiting_payment} FULLY_EXECUTED contracts (awaiting payment)")
        
        # Separate payments by status
        paid_payments = [p for p in all_payments if p.get("status") in ["PAID_IN_ESCROW", "WORK_IN_PROGRESS", "SENT_FOR_DELIVERY", "RELEASED"]]
        completed_payments = [p for p in all_payments if p.get("status") == "RELEASED"]
        
        orders_placed = len(paid_payments)
        orders_completed = len(completed_payments)
        
        # Calculate fulfillment rate
        fulfillment_rate = int((orders_completed / orders_placed * 100)) if orders_placed > 0 else 0
        
        # Calculate total spent
        total_spent = sum([float(p.get("base_amount_usd", 0)) for p in paid_payments])
        avg_order_cost = int(total_spent / orders_placed) if orders_placed > 0 else 0
        
        # Analyze product categories from RFQs
        category_counts = {}
        for rfq in rfqs:
            category = rfq.get("product_category", "Other")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        category_labels = [c[0] for c in top_categories] if top_categories else ["No data"]
        category_data = [c[1] for c in top_categories] if top_categories else [0]
        
        # Analyze fabric types from RFQs
        fabric_counts = {}
        for rfq in rfqs:
            fabric = rfq.get("fabric_type", "Not specified")
            if fabric and fabric != "Not specified":
                fabric_counts[fabric] = fabric_counts.get(fabric, 0) + 1
        
        top_fabrics = sorted(fabric_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        fabric_labels = [f[0] for f in top_fabrics] if top_fabrics else ["No data"]
        fabric_data = [f[1] for f in top_fabrics] if top_fabrics else [0]
        
        # Analyze incoterms preferences
        incoterm_counts = {}
        for rfq in rfqs:
            incoterm = rfq.get("incoterms", "FOB")
            incoterm_counts[incoterm] = incoterm_counts.get(incoterm, 0) + 1
        
        incoterm_labels = list(incoterm_counts.keys()) if incoterm_counts else ["No data"]
        incoterm_data = list(incoterm_counts.values()) if incoterm_counts else [0]
        
        # Top suppliers by order count
        supplier_counts = {}
        for payment in paid_payments:
            bid = await db["bids"].find_one({"id": payment.get("bid_id")})
            if bid:
                supplier = bid.get("company_name", "Unknown")
                supplier_counts[supplier] = supplier_counts.get(supplier, 0) + 1
        
        top_suppliers = sorted(supplier_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_suppliers_labels = [s[0] for s in top_suppliers] if top_suppliers else ["No data"]
        top_suppliers_data = [s[1] for s in top_suppliers] if top_suppliers else [0]
        
        # Spending trends over last 6 months
        spending_trends_labels = []
        spending_trends_data = []
        now = datetime.utcnow()
        
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_name = month_date.strftime("%b %y")
            spending_trends_labels.append(month_name)
            
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = now - timedelta(days=30*(i-1))
                month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_payments = [p for p in paid_payments 
                         if p.get("created_at") and 
                         month_start <= p.get("created_at") < month_end]
            month_spending = sum([float(p.get("base_amount_usd", 0)) for p in month_payments])
            spending_trends_data.append(int(month_spending))
        
        # RFQ creation trends
        rfq_trends_labels = []
        rfq_trends_data = []
        
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_name = month_date.strftime("%b %y")
            rfq_trends_labels.append(month_name)
            
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = now - timedelta(days=30*(i-1))
                month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_rfqs = [r for r in rfqs 
                         if r.get("created_at") and 
                         month_start <= r.get("created_at") < month_end]
            rfq_trends_data.append(len(month_rfqs))
        
        # Recent orders
        recent_orders = []
        sorted_payments = sorted(
            paid_payments, 
            key=lambda x: x.get("created_at") if x.get("created_at") else datetime.min, 
            reverse=True
        )[:10]
        
        for payment in sorted_payments:
            bid = await db["bids"].find_one({"id": payment.get("bid_id")})
            rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
            
            # Get supplier company name
            supplier_name = "Unknown"
            if bid:
                # Try to get from bid first
                supplier_name = bid.get("company_name") or bid.get("supplier_name")
                # If still not found, get from companies collection
                if not supplier_name or supplier_name == "Unknown":
                    supplier_company = await db["companies"].find_one({"unique_id": bid.get("supplier_id")})
                    if supplier_company:
                        supplier_name = supplier_company.get("name", "Unknown")
            
            recent_orders.append({
                "rfq_id": payment.get("order_id", "N/A"),
                "supplier_name": supplier_name,
                "product_name": rfq.get("title", "Product") if rfq else "Product",
                "date": payment.get("created_at").strftime("%Y-%m-%d") if payment.get("created_at") else "N/A",
                "amount": f"${int(float(payment.get('base_amount_usd', 0))):,}",
                "status": payment.get("status", "PENDING")
            })
        
        analytics = {
            "total_rfqs": total_rfqs,
            "evaluating_rfqs": evaluating_rfqs,
            "awarded_rfqs": awarded_rfqs,
            "total_bids_received": total_bids_received,
            "orders_placed": orders_placed,
            "orders_awaiting_payment": orders_awaiting_payment,
            "orders_completed": orders_completed,
            "fulfillment_rate": fulfillment_rate,
            "total_spent": f"${int(total_spent):,}",
            "avg_order_cost": f"${avg_order_cost:,}",
            
            "category_labels": category_labels,
            "category_data": category_data,
            "fabric_labels": fabric_labels,
            "fabric_data": fabric_data,
            "incoterm_labels": incoterm_labels,
            "incoterm_data": incoterm_data,
            
            "top_suppliers_labels": top_suppliers_labels,
            "top_suppliers_data": top_suppliers_data,
            "spending_trends_labels": spending_trends_labels,
            "spending_trends_data": spending_trends_data,
            "rfq_trends_labels": rfq_trends_labels,
            "rfq_trends_data": rfq_trends_data,
            
            "recent_orders": recent_orders if recent_orders else [{
                "rfq_id": "N/A",
                "supplier_name": "No orders yet",
                "product_name": "-",
                "date": "-",
                "amount": "$0",
                "status": "NONE"
            }]
        }
        
        return analytics
        
    except Exception as e:
        print(f"Error generating buyer analytics: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "total_rfqs": 0,
            "evaluating_rfqs": 0,
            "awarded_rfqs": 0,
            "total_bids_received": 0,
            "orders_placed": 0,
            "orders_awaiting_payment": 0,
            "orders_completed": 0,
            "fulfillment_rate": 0,
            "total_spent": "$0",
            "avg_order_cost": "$0",
            "category_labels": ["No data"],
            "category_data": [0],
            "fabric_labels": ["No data"],
            "fabric_data": [0],
            "incoterm_labels": ["No data"],
            "incoterm_data": [0],
            "top_suppliers_labels": ["No data"],
            "top_suppliers_data": [0],
            "spending_trends_labels": ["No data"],
            "spending_trends_data": [0],
            "rfq_trends_labels": ["No data"],
            "rfq_trends_data": [0],
            "recent_orders": [{
                "rfq_id": "N/A",
                "supplier_name": "No orders yet",
                "product_name": "-",
                "date": "-",
                "amount": "$0",
                "status": "NONE"
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
        supplier_id = company.get("unique_id") or company.get("id")
        
        # Fetch all bids submitted by this supplier
        bids_cursor = db["bids"].find({"supplier_id": supplier_id})
        all_bids = await bids_cursor.to_list(length=None)
        total_bids = len(all_bids)
        
        # Count bids by status
        pending_bids = len([b for b in all_bids if b.get("status") in ["PENDING", None]])
        accepted_bids = len([b for b in all_bids if b.get("status") == "ACCEPTED"])
        confirmed_bids = len([b for b in all_bids if b.get("status") == "CONFIRMED"])
        rejected_bids = len([b for b in all_bids if b.get("status") == "REJECTED"])
        
        # Calculate orders won (accepted + confirmed)
        won_bids = [b for b in all_bids if b.get("status") in ["ACCEPTED", "CONFIRMED"]]
        orders_won = len(won_bids)
        win_rate = int((orders_won / total_bids * 100)) if total_bids > 0 else 0
        
        # Fetch all payments received by this supplier
        payments_cursor = db["payments"].find({"supplier_id": supplier_id})
        all_payments = await payments_cursor.to_list(length=None)
        
        # Fetch all FULLY_EXECUTED contracts for this supplier to find orders awaiting payment
        contracts_cursor = db["contracts"].find({
            "supplier_id": supplier_id,
            "status": "FULLY_EXECUTED"
        })
        all_contracts = await contracts_cursor.to_list(length=None)
        
        # Find contracts that don't have payments yet (awaiting payment)
        paid_rfq_ids = [p.get("order_id") for p in all_payments]
        awaiting_payment_contracts = [c for c in all_contracts if c.get("rfq_id") not in paid_rfq_ids]
        
        # Separate payments by status
        paid_payments = [p for p in all_payments if p.get("status") in ["PAID_IN_ESCROW", "WORK_IN_PROGRESS", "SENT_FOR_DELIVERY", "RELEASED"]]
        completed_payments = [p for p in all_payments if p.get("status") == "RELEASED"]
        in_progress_payments = [p for p in all_payments if p.get("status") in ["PAID_IN_ESCROW", "WORK_IN_PROGRESS", "SENT_FOR_DELIVERY"]]
        
        orders_in_progress = len(in_progress_payments)
        orders_completed = len(completed_payments)
        orders_awaiting_payment = len(awaiting_payment_contracts)
        
        # Calculate total revenue from actual payments
        total_revenue = sum([float(p.get("base_amount_usd", 0)) for p in paid_payments])
        revenue_released = sum([float(p.get("base_amount_usd", 0)) for p in completed_payments])
        revenue_pending = sum([float(p.get("base_amount_usd", 0)) for p in in_progress_payments])
        
        avg_deal_size = int(total_revenue / len(paid_payments)) if paid_payments else 0
        
        # Analyze product categories from won bids
        category_counts = {}
        for bid in won_bids:
            rfq = await db["rfqs"].find_one({"id": bid.get("rfq_id")})
            if rfq:
                category = rfq.get("product_category", "Other")
                category_counts[category] = category_counts.get(category, 0) + 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        category_labels = [c[0] for c in top_categories] if top_categories else ["No data"]
        category_data = [c[1] for c in top_categories] if top_categories else [0]
        
        # Top buyers by order count
        buyer_counts = {}
        for payment in paid_payments:
            bid = await db["bids"].find_one({"id": payment.get("bid_id")})
            if bid:
                rfq = await db["rfqs"].find_one({"id": bid.get("rfq_id")})
                if rfq:
                    buyer = rfq.get("buyer_company", "Unknown")
                    buyer_counts[buyer] = buyer_counts.get(buyer, 0) + 1
        
        top_buyers = sorted(buyer_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_buyers_labels = [b[0] for b in top_buyers] if top_buyers else ["No data"]
        top_buyers_data = [b[1] for b in top_buyers] if top_buyers else [0]
        
        # Revenue trends over last 6 months
        revenue_trends_labels = []
        revenue_trends_data = []
        now = datetime.utcnow()
        
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_name = month_date.strftime("%b %y")
            revenue_trends_labels.append(month_name)
            
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = now - timedelta(days=30*(i-1))
                month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_payments = [p for p in paid_payments 
                         if p.get("created_at") and 
                         month_start <= p.get("created_at") < month_end]
            month_revenue = sum([float(p.get("base_amount_usd", 0)) for p in month_payments])
            revenue_trends_data.append(int(month_revenue))
        
        # Bid trends over last 6 months
        bid_trends_labels = []
        bid_trends_data = []
        
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_name = month_date.strftime("%b %y")
            bid_trends_labels.append(month_name)
            
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                next_month = now - timedelta(days=30*(i-1))
                month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_bids = [b for b in all_bids 
                         if b.get("timestamp") and 
                         month_start <= b.get("timestamp") < month_end]
            bid_trends_data.append(len(month_bids))
        
        # Recent contracts - include both paid and awaiting payment
        recent_contracts = []
        
        # Combine paid orders and awaiting payment contracts
        all_recent_items = []
        
        # Add paid orders
        for payment in paid_payments:
            bid = await db["bids"].find_one({"id": payment.get("bid_id")})
            rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
            
            # Get buyer company name - try multiple methods
            buyer_name = "Unknown"
            if rfq:
                # Method 1: Try buyer_company field
                buyer_name = rfq.get("buyer_company")
                
                # Method 2: If not found, try to get company by buyer_id
                if not buyer_name:
                    buyer_id = rfq.get("buyer_id")
                    if buyer_id:
                        # Try finding company where user is associated
                        user = await db["users"].find_one({"id": buyer_id})
                        if user and user.get("company_id"):
                            buyer_company = await db["companies"].find_one({"id": user.get("company_id")})
                            if buyer_company:
                                buyer_name = buyer_company.get("name")
                        
                        # If still not found, try direct company lookup
                        if not buyer_name:
                            buyer_company = await db["companies"].find_one({"id": buyer_id})
                            if buyer_company:
                                buyer_name = buyer_company.get("name")
            
            if not buyer_name:
                buyer_name = "Unknown"
            
            all_recent_items.append({
                "contract_id": payment.get("order_id", "N/A"),
                "buyer_name": buyer_name,
                "product_name": rfq.get("title", "Product") if rfq else "Product",
                "date": payment.get("created_at") if payment.get("created_at") else datetime.min,
                "date_str": payment.get("created_at").strftime("%Y-%m-%d") if payment.get("created_at") else "N/A",
                "amount": f"${int(float(payment.get('base_amount_usd', 0))):,}",
                "status": payment.get("status", "PENDING")
            })
        
        # Add awaiting payment contracts
        for contract in awaiting_payment_contracts:
            bid = await db["bids"].find_one({"id": contract.get("bid_id")})
            rfq = await db["rfqs"].find_one({"id": contract.get("rfq_id")})
            
            # Get buyer company name - try multiple methods
            buyer_name = "Unknown"
            if rfq:
                # Method 1: Try buyer_company field
                buyer_name = rfq.get("buyer_company")
                
                # Method 2: If not found, try to get company by buyer_id
                if not buyer_name:
                    buyer_id = rfq.get("buyer_id")
                    if buyer_id:
                        # Try finding company where user is associated
                        user = await db["users"].find_one({"id": buyer_id})
                        if user and user.get("company_id"):
                            buyer_company = await db["companies"].find_one({"id": user.get("company_id")})
                            if buyer_company:
                                buyer_name = buyer_company.get("name")
                        
                        # If still not found, try direct company lookup
                        if not buyer_name:
                            buyer_company = await db["companies"].find_one({"id": buyer_id})
                            if buyer_company:
                                buyer_name = buyer_company.get("name")
            
            if not buyer_name:
                buyer_name = "Unknown"
            
            all_recent_items.append({
                "contract_id": contract.get("rfq_id", "N/A"),
                "buyer_name": buyer_name,
                "product_name": rfq.get("title", "Product") if rfq else "Product",
                "date": contract.get("created_at") if contract.get("created_at") else datetime.min,
                "date_str": contract.get("created_at").strftime("%Y-%m-%d") if contract.get("created_at") else "N/A",
                "amount": f"${int(float(bid.get('total_price', 0))):,}" if bid else "$0",
                "status": "AWAITING_PAYMENT"
            })
        
        # Sort by date and take top 10
        all_recent_items.sort(key=lambda x: x["date"], reverse=True)
        recent_contracts = [{
            "contract_id": item["contract_id"],
            "buyer_name": item["buyer_name"],
            "product_name": item["product_name"],
            "date": item["date_str"],
            "amount": item["amount"],
            "status": item["status"]
        } for item in all_recent_items[:10]]
        
        analytics = {
            "total_bids": total_bids,
            "pending_bids": pending_bids,
            "accepted_bids": accepted_bids,
            "confirmed_bids": confirmed_bids,
            "rejected_bids": rejected_bids,
            "orders_won": orders_won,
            "orders_in_progress": orders_in_progress,
            "orders_completed": orders_completed,
            "orders_awaiting_payment": orders_awaiting_payment,
            "win_rate": win_rate,
            "total_revenue": f"${int(total_revenue):,}",
            "revenue_released": f"${int(revenue_released):,}",
            "revenue_pending": f"${int(revenue_pending):,}",
            "avg_deal_size": f"${avg_deal_size:,}",
            
            "category_labels": category_labels,
            "category_data": category_data,
            "top_buyers_labels": top_buyers_labels,
            "top_buyers_data": top_buyers_data,
            "revenue_trends_labels": revenue_trends_labels,
            "revenue_trends_data": revenue_trends_data,
            "bid_trends_labels": bid_trends_labels,
            "bid_trends_data": bid_trends_data,
            
            "recent_contracts": recent_contracts if recent_contracts else [{
                "contract_id": "N/A",
                "buyer_name": "No contracts yet",
                "product_name": "-",
                "date": "-",
                "amount": "$0",
                "status": "NONE"
            }]
        }
        
        return analytics
        
    except Exception as e:
        print(f"Error generating supplier analytics: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "total_bids": 0,
            "pending_bids": 0,
            "accepted_bids": 0,
            "confirmed_bids": 0,
            "rejected_bids": 0,
            "orders_won": 0,
            "orders_in_progress": 0,
            "orders_completed": 0,
            "orders_awaiting_payment": 0,
            "win_rate": 0,
            "total_revenue": "$0",
            "revenue_released": "$0",
            "revenue_pending": "$0",
            "avg_deal_size": "$0",
            "category_labels": ["No data"],
            "category_data": [0],
            "top_buyers_labels": ["No data"],
            "top_buyers_data": [0],
            "revenue_trends_labels": ["No data"],
            "revenue_trends_data": [0],
            "bid_trends_labels": ["No data"],
            "bid_trends_data": [0],
            "recent_contracts": [{
                "contract_id": "N/A",
                "buyer_name": "No contracts yet",
                "product_name": "-",
                "date": "-",
                "amount": "$0",
                "status": "NONE"
            }]
        }


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
        
        # Check if subscription can be changed (only applies to PREMIUM users)
        can_change_after = company.get("subscription_can_change_after")
        if can_change_after and company.get("subscription_tier") == "PREMIUM":
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
async def rfq_builder_page(request: Request, user: dict = Depends(require_login)):
    """RFQ creation page - Only for logged-in buyers."""
    from database import db
    
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
                print(f"🔔 RFQ is OPEN, sending notifications...")
                
                # Always notify about new RFQ
                print(f"📧 Sending 'New RFQ' notification...")
                await notify_new_rfq(rfq.id, rfq.title, rfq.product_category)
                
                # Additionally notify about reverse auction if enabled
                if rfq.is_reverse_auction:
                    print(f"🏆 Sending 'Reverse Auction' notification...")
                    await notify_new_auction(rfq.id, rfq.title, rfq.auction_end_time)
                
                print(f"✅ All notifications sent for RFQ: {rfq.id}")
        
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
    def no_cache_redirect(url: str):
        response = RedirectResponse(url=url, status_code=303)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    if not user:
        return no_cache_redirect("/login")
        
    if user.get("is_admin"):
        return no_cache_redirect("/admin/dashboard")

    from database import db
    if db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            role = company.get("role", "").upper()
            if role == "SUPPLIER":
                return no_cache_redirect("/dashboard/supplier")
            elif role == "BUYER":
                return no_cache_redirect("/dashboard/buyer")

    return no_cache_redirect("/dashboard/buyer")

@app.get("/rfq/browse", response_class=HTMLResponse)
async def rfq_browse_redirect(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Browse RFQs — redirects to the open RFQ marketplace feed."""
    return RedirectResponse(url="/rfq/feed", status_code=303)


@app.get("/dashboard/buyer", response_class=HTMLResponse)
async def buyer_dashboard(request: Request, user: dict = Depends(require_buyer)):
    """Buyer dashboard — serves the HTML shell. All data is fetched client-side via /api/dashboard/buyer/* endpoints."""
    return templates.TemplateResponse("buyer_dashboard.html", {
        "request": request,
        "user": user,
    })


def build_buyer_query(user: dict, company: dict) -> dict:
    """Build a MongoDB $or query that matches buyer_id across all known ID formats."""
    return {
        "$or": [
            {"buyer_id": user.get("id")},
            {"buyer_id": user.get("company_id")},
            {"buyer_id": company.get("id")},
            {"buyer_id": company.get("unique_id")},
        ]
    }


@app.get("/api/dashboard/buyer/stats")
async def get_buyer_stats(user: dict = Depends(require_buyer)):
    """
    Get buyer dashboard statistics.
    Security Matrix: Only returns spending data.
    """
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
        
    buyer_id = user.get("id")
    
    # Calculate spending_data: sum of all released/paid amounts
    spending_data = 0.0
    async for payment in db["payments"].find({
        "buyer_id": buyer_id,
        "status": "RELEASED"
    }):
        spending_data += payment.get("amount", 0.0)
        
    return {
        "success": True,
        "stats": {
            "spending_data": spending_data,
        }
    }


@app.get("/api/dashboard/buyer/recent-rfqs")
async def get_buyer_recent_rfqs(
    limit: int = 10,
    user: dict = Depends(require_buyer)
):
    """
    Get buyer's recent RFQs with enriched data.
    Returns RFQs with bid_count, payment_status, and payment_id.
    """
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    buyer_query = build_buyer_query(user, company)
    
    # Fetch RFQs sorted by created_at descending
    rfqs = []
    async for rfq in db["rfqs"].find(buyer_query).sort("created_at", -1).limit(limit):
        # Convert ObjectId to string if present
        if "_id" in rfq:
            rfq["_id"] = str(rfq["_id"])
        
        # Count bids for this RFQ
        bid_count = await db["bids"].count_documents({"rfq_id": rfq.get("id")})
        
        # Find payment for this RFQ
        payment = await db["payments"].find_one({"order_id": rfq.get("id")})
        
        # Enrich RFQ with additional data
        rfq["bid_count"] = bid_count
        rfq["payment_status"] = payment.get("status") if payment else None
        rfq["payment_id"] = payment.get("payment_id") if payment else None
        
        rfqs.append(rfq)
    
    return {
        "success": True,
        "rfqs": rfqs
    }


@app.get("/api/dashboard/buyer/action-required")
async def get_buyer_action_required(user: dict = Depends(require_buyer)):
    """
    Get buyer's action-required items from escrow system.
    Returns payments with status SENT_FOR_DELIVERY that need buyer confirmation.
    """
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    buyer_id = user.get("id")
    
    # Query payments with status SENT_FOR_DELIVERY
    actions = []
    async for payment in db["payments"].find({
        "buyer_id": buyer_id,
        "status": "SENT_FOR_DELIVERY"
    }):
        # Fetch associated RFQ to get title
        rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
        rfq_title = rfq.get("title", "Unknown RFQ") if rfq else "Unknown RFQ"
        
        # Build action object
        action = {
            "payment_id": payment.get("payment_id"),
            "transaction_id": payment.get("transaction_id"),
            "action": "confirm_delivery",
            "description": "Supplier has marked order as delivered. Please confirm receipt.",
            "amount": payment.get("amount", 0.0),
            "rfq_title": rfq_title
        }
        actions.append(action)
    
    return {
        "success": True,
        "actions": actions
    }


@app.get("/supplier/bids", response_class=HTMLResponse)
async def supplier_bids_page(request: Request, user: dict = Depends(require_seller)):
    """Serve the 'My Bids' page for a supplier."""
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
        
    try:
        user_company = await db["companies"].find_one({"id": user.get("company_id")})
        bidder_ids = [user.get("id"), user.get("company_id")]
        if user_company:
            bidder_ids.append(user_company.get("id"))
            bidder_ids.append(user_company.get("unique_id"))
            
        bids_cursor = db["bids"].find({"supplier_id": {"$in": [id for id in bidder_ids if id]}}).sort("timestamp", -1)
        bids = await bids_cursor.to_list(length=100)
        
        print(f"DEBUG SUPPLIER BIDS: Total bids before filter: {len(bids)}")
        for bid in bids:
            print(f"  - Bid {bid.get('id')}: status={bid.get('status')}, bid_status={bid.get('bid_status')}, rfq={bid.get('rfq_id')}")
        
        # Filter out rejected bids - suppliers should only see their accepted or pending bids
        bids = [bid for bid in bids if bid.get("status") != "REJECTED" and bid.get("bid_status") != "REJECTED"]
        
        print(f"DEBUG SUPPLIER BIDS: Total bids after filter: {len(bids)}")
        
        # Enrich bids with RFQ and Buyer data
        rfq_ids = list(set([bid.get("rfq_id") for bid in bids if bid.get("rfq_id")]))
        rfqs_cursor = db["rfqs"].find({"id": {"$in": rfq_ids}})
        rfqs_list = await rfqs_cursor.to_list(length=len(rfq_ids))
        rfqs_map = {rfq.get("id"): rfq for rfq in rfqs_list}
        
        # Fetch buyer users
        buyer_ids = list(set([rfq.get("buyer_id") for rfq in rfqs_list if rfq.get("buyer_id")]))
        buyers_cursor = db["users"].find({"id": {"$in": buyer_ids}})
        buyers_list = await buyers_cursor.to_list(length=len(buyer_ids))
        buyers_map = {b.get("id"): b for b in buyers_list}

        # Fetch companies for these buyers
        buyer_company_ids = list(set([b.get("company_id") for b in buyers_list if b.get("company_id")]))
        buyer_companies_cursor = db["companies"].find({"id": {"$in": buyer_company_ids}})
        buyer_companies_list = await buyer_companies_cursor.to_list(length=len(buyer_company_ids))
        buyer_companies_map = {c.get("id"): c for c in buyer_companies_list}
        
        enriched_bids = []
        for bid in bids:
            # Add a string representation of ID for Jinja compatibility if needed
            bid["id_str"] = str(bid.get("id", ""))
            rfq = rfqs_map.get(bid.get("rfq_id"), {})
            
            buyer_user = buyers_map.get(rfq.get("buyer_id"), {})
            buyer_company = buyer_companies_map.get(buyer_user.get("company_id"), {})
            buyer_name = buyer_company.get("name") or buyer_user.get("email") or "Buyer"
            
            enriched_bids.append({
                "bid": bid,
                "rfq": rfq,
                "buyer_name": buyer_name
            })
            
        return templates.TemplateResponse("supplier_bids.html", {
            "request": request,
            "user": user,
            "company": user_company,
            "bids_data": enriched_bids
        })
        
    except Exception as e:
        print(f"Error loading supplier bids: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to load bids")


@app.get("/api/dashboard/supplier/stats")
async def get_supplier_stats(user: dict = Depends(require_supplier)):
    """
    Get supplier dashboard statistics.
    Security Matrix: Only returns win rate and revenue.
    """
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
        
    company = await db["companies"].find_one({"id": user.get("company_id")})
    supplier_id = company.get("unique_id") or company.get("id") if company else user.get("id")
    
    # Calculate win rate
    total_bids = await db["bids"].count_documents({"supplier_id": supplier_id})
    accepted_bids = await db["bids"].count_documents({"supplier_id": supplier_id, "status": "ACCEPTED"})
    win_rate = (accepted_bids / total_bids * 100) if total_bids > 0 else 0.0
    
    # Calculate revenue (released payments)
    revenue = 0.0
    async for payment in db["payments"].find({
        "supplier_id": supplier_id,
        "status": "RELEASED"
    }):
        revenue += payment.get("amount", 0.0)
        
    return {
        "success": True,
        "stats": {
            "win_rate": round(win_rate, 2),
            "revenue": revenue
        }
    }


@app.get("/api/bids/recommendations")
async def get_bid_recommendations(user: dict = Depends(require_seller)):
    """Returns open RFQs that match the supplier's profile — used on supplier dashboard."""
    from database import db
    if db is None:
        return {"success": True, "recommendations": []}
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        return {"success": True, "recommendations": []}
    # Return open RFQs the supplier hasn't bid on yet
    supplier_id = company.get("unique_id") or company.get("id")
    bid_rfq_ids = set()
    async for b in db["bids"].find({"supplier_id": supplier_id}, {"rfq_id": 1}):
        bid_rfq_ids.add(b.get("rfq_id"))
    recs = []
    async for rfq in db["rfqs"].find({"status": "OPEN"}).sort("created_at", -1).limit(10):
        rfq.pop("_id", None)
        if rfq.get("id") not in bid_rfq_ids:
            recs.append({"id": rfq.get("id"), "title": rfq.get("title"), "quantity": rfq.get("quantity"), "fabric_type": rfq.get("fabric_type"), "target_price": rfq.get("target_price")})
    return {"success": True, "recommendations": recs}


@app.post("/escrow/deposit")
async def escrow_deposit(user: dict = Depends(require_buyer)):
    """Buyer deposits funds into escrow."""
    return {"success": True, "status": "deposited"}


@app.post("/escrow/release")
async def escrow_release(user: dict = Depends(require_admin)):
    """Admin releases funds from escrow."""
    return {"success": True, "status": "released"}


@app.get("/api/dashboard/supplier/open-rfqs")
async def get_supplier_open_rfqs(
    user: dict = Depends(require_supplier),
    limit: int = 20,
    category: Optional[str] = None,
    urgency: Optional[str] = None
):
    """
    Get open RFQs available for bidding.
    Returns list of open RFQs with optional filtering by category and urgency.
    
    Requirements: 4.5
    """
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    # Build query filter
    query_filter = {"status": "OPEN"}
    
    # Apply category filter if provided
    if category:
        query_filter["product_category"] = category
    
    # Apply urgency filter if provided
    if urgency:
        query_filter["urgency_level"] = urgency
    
    # Query RFQs collection with filters
    rfqs = []
    async for rfq in db["rfqs"].find(query_filter).sort("created_at", -1).limit(limit):
        # Convert ObjectId to string for JSON serialization
        rfq["_id"] = str(rfq["_id"])
        
        # Build response object with required fields
        rfq_data = {
            "id": rfq.get("id"),
            "title": rfq.get("title"),
            "product_category": rfq.get("product_category"),
            "quantity": rfq.get("quantity"),
            "urgency_level": rfq.get("urgency_level"),
            "target_delivery_date": rfq.get("target_delivery_date").isoformat() if rfq.get("target_delivery_date") else None,
            "created_at": rfq.get("created_at").isoformat() if rfq.get("created_at") else None
        }
        
        rfqs.append(rfq_data)
    
    return {
        "success": True,
        "rfqs": rfqs
    }


@app.get("/api/dashboard/supplier/verification-status")
async def get_supplier_verification_status(user: dict = Depends(require_supplier)):
    """
    Get supplier verification status and trust metrics.
    Returns verification status, average rating, total reviews, and trust score.
    
    Requirements: 4.6, 12.1, 12.2, 12.3, 12.4, 12.5
    """
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    # Query companies collection for supplier's company record
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Extract overall_status as verification_status
    verification_status = company.get("overall_status", "DRAFT")
    
    # Extract trust_score from company record
    trust_score = company.get("trust_score", 0)
    
    # Calculate average_rating from reviews (if reviews system exists, otherwise return 0)
    # Since reviews system doesn't exist yet, return 0
    average_rating = 0.0
    
    # Count total_reviews (if reviews system exists, otherwise return 0)
    # Since reviews system doesn't exist yet, return 0
    total_reviews = 0
    
    return {
        "success": True,
        "verification": {
            "status": verification_status,
            "average_rating": average_rating,
            "total_reviews": total_reviews,
            "trust_score": trust_score
        }
    }


@app.get("/api/dashboard/supplier/active-production")
async def get_supplier_active_production(user: dict = Depends(require_supplier)):
    """
    Get supplier's active production orders.
    Returns orders currently in production with milestone tracking.
    
    Requirements: 4.7, 11.3, 11.4
    """
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    supplier_id = company.get("unique_id") or company.get("id")
    
    # Query payments collection for supplier's payments with status WORK_IN_PROGRESS
    orders = []
    async for payment in db["payments"].find({
        "supplier_id": supplier_id,
        "status": "WORK_IN_PROGRESS"
    }):
        # For each payment, fetch associated bid and RFQ data
        bid = await db["bids"].find_one({"id": payment.get("bid_id")})
        rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
        
        if rfq:
            # Build order objects with payment_id, order_id, bid_id, amount, rfq_title, quantity, current_milestone, started_at
            order = {
                "payment_id": payment.get("payment_id"),
                "order_id": payment.get("order_id"),
                "bid_id": payment.get("bid_id"),
                "amount": payment.get("amount", 0.0),
                "rfq_title": rfq.get("title", "Unknown RFQ"),
                "quantity": rfq.get("quantity", 0),
                "current_milestone": payment.get("status", "WORK_IN_PROGRESS"),
                "started_at": payment.get("created_at").isoformat() if payment.get("created_at") else None
            }
            
            orders.append(order)
    
    return {
        "success": True,
        "orders": orders
    }


@app.get("/dashboard/supplier", response_class=HTMLResponse)
async def supplier_dashboard_feed(request: Request, user: dict = Depends(require_supplier)):
    """
    Supplier dashboard page route — serves the HTML shell.
    All data is fetched client-side via /api/dashboard/supplier/* endpoints.
    Requirements: 3.1, 9.1, 11.3
    """
    return templates.TemplateResponse("supplier_dashboard.html", {
        "request": request,
        "user": user,
    })


@app.get("/supplier/capacity", response_class=HTMLResponse)
async def supplier_capacity_page(request: Request, user: dict = Depends(require_supplier)):
    """Supplier capacity management page."""
    return templates.TemplateResponse("supplier_capacity.html", {
        "request": request,
        "user": user,
    })


@app.get("/bid/submit", response_class=HTMLResponse)
async def bid_submit_page(request: Request, rfq_id: Optional[str] = None, user: dict = Depends(require_login)):
    """Submit a single bid on an RFQ - available for all suppliers."""
    from database import db
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    rfq = None
    user_has_bid = False
    is_premium = False
    
    # Get user's company
    user_company = await db["companies"].find_one({"id": user.get("company_id")})
    
    if not user_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if user is a supplier
    user_role = user_company.get("role", "").upper()
    if user_role != "SUPPLIER":
        raise HTTPException(status_code=403, detail="Only suppliers can submit bids")
    
    # Check subscription status from company
    subscription_tier = user_company.get("subscription_tier", "FREE")
    is_premium = subscription_tier == "PREMIUM"
    
    # Get RFQ if rfq_id is provided
    if rfq_id:
        rfq = await db["rfqs"].find_one({"id": rfq_id})
        
        if rfq:
            # Check if user has already bid on this RFQ
            existing_bid = await db["bids"].find_one({
                "rfq_id": rfq_id,
                "supplier_id": user_company.get("unique_id")
            })
            user_has_bid = existing_bid is not None
    
    return templates.TemplateResponse("bid_submit.html", {
        "request": request,
        "user": user,
        "rfq": rfq,
        "user_has_bid": user_has_bid,
        "is_premium": is_premium
    })


@app.get("/rfq/feed", response_class=HTMLResponse)
async def rfq_feed_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Browse all open RFQs - accessible to both buyers and suppliers."""
    from database import db

    rfqs = []
    user_role = "GUEST"
    if db is not None:
        # Fetch all open and evaluating RFQs (so accepted bids still show)
        async for document in db["rfqs"].find({"status": {"$in": ["OPEN", "EVALUATING"]}}).sort("created_at", -1):
            document['_id'] = str(document['_id'])
            rfqs.append(document)

        # Determine the logged-in user's role
        if user:
            company = await db["companies"].find_one({"id": user.get("company_id")})
            if company:
                user_role = company.get("role", "GUEST").upper()

    return templates.TemplateResponse("rfq_feed.html", {
        "request": request,
        "rfqs": rfqs,
        "user": user,
        "user_role": user_role,
    })


@app.get("/rfq/my", response_class=HTMLResponse)
async def my_rfqs_page(request: Request, user: dict = Depends(require_buyer)):
    """My RFQs — shows only the RFQs created by the logged-in buyer."""
    from database import db

    rfqs = []
    if db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        # Build a query that matches buyer_id across all known ID formats
        buyer_ids = [user.get("id"), user.get("company_id")]
        if company:
            buyer_ids.append(company.get("id"))
            buyer_ids.append(company.get("unique_id"))
        buyer_ids = [bid for bid in buyer_ids if bid]  # remove None values

        async for document in db["rfqs"].find(
            {"buyer_id": {"$in": buyer_ids}}
        ).sort("created_at", -1):
            document['_id'] = str(document['_id'])
            rfqs.append(document)

    return templates.TemplateResponse("my_rfqs.html", {
        "request": request,
        "rfqs": rfqs,
        "user": user,
        "user_role": "BUYER",
        "page_title": "My RFQs",
        "page_description": "Manage the requests for quotation you have posted."
    })


@app.post("/quote/submit")
async def submit_quote(request: Request, user: dict = Depends(require_login)):
    form_data = await request.form()
    # In a real app we'd save this to a 'quotes' collection
    # Here, we'll just log and mock a success return to the dashboard
    print("New Quote Submitted:", form_data)
    
    # Redirect to supplier dashboard (client-side fetches all data)
    return RedirectResponse(url="/dashboard/supplier", status_code=303)

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


# ============================================================
# AI-BASED BID RECOMMENDATIONS
# ============================================================
# Collection: bid_recommendations
# Fields: supplier_id, input_costs, suggested_price,
#         price_range, confidence, market_adjustment,
#         historical_avg, created_at
# Collection: ai_config
# Fields: min_profit_margin_pct, max_discount_pct,
#         market_adjustment_pct, updated_by, updated_at
# ============================================================

DEFAULT_AI_CONFIG = {
    "min_profit_margin_pct": 15.0,   # Minimum profit margin (%)
    "max_discount_pct": 30.0,        # Max allowed discount vs market avg (%)
    "market_adjustment_pct": 8.0,    # Market premium/discount factor (%)
}


async def get_ai_config() -> dict:
    """Fetch AI config from DB, fall back to defaults."""
    from database import db
    if db is None:
        return DEFAULT_AI_CONFIG.copy()
    cfg = await db["ai_config"].find_one({})
    if cfg:
        cfg.pop("_id", None)
        return cfg
    return DEFAULT_AI_CONFIG.copy()


async def get_historical_avg(fabric: str, category: str, quantity: int) -> dict:
    """Analyse historical accepted bids to get market average price."""
    from database import db
    if db is None:
        return {"avg": None, "count": 0}
    # Find accepted/confirmed bids on similar RFQs
    pipeline = [
        {"$lookup": {
            "from": "rfqs",
            "localField": "rfq_id",
            "foreignField": "id",
            "as": "rfq"
        }},
        {"$unwind": "$rfq"},
        {"$match": {
            "status": {"$in": ["ACCEPTED", "CONFIRMED"]},
            "$or": [
                {"rfq.fabric_type": {"$regex": fabric, "$options": "i"}},
                {"rfq.product_category": {"$regex": category, "$options": "i"}},
            ]
        }},
        {"$group": {
            "_id": None,
            "avg_price": {"$avg": "$bid_price"},
            "min_price": {"$min": "$bid_price"},
            "max_price": {"$max": "$bid_price"},
            "count": {"$sum": 1}
        }}
    ]
    try:
        results = await db["bids"].aggregate(pipeline).to_list(length=1)
        if results:
            r = results[0]
            return {
                "avg": round(r.get("avg_price", 0), 2),
                "min": round(r.get("min_price", 0), 2),
                "max": round(r.get("max_price", 0), 2),
                "count": r.get("count", 0),
            }
    except Exception:
        pass
    return {"avg": None, "count": 0}


def calculate_ai_bid(
    material_cost: float,
    labor_cost: float,
    shipping_cost: float,
    quantity: int,
    fabric: str,
    category: str,
    urgency: str,
    historical: dict,
    config: dict,
) -> dict:
    """
    Core AI bid calculation logic.
    base_cost = material + labor + shipping
    suggested = base_cost + profit_margin + market_adjustment
    """
    base_cost = material_cost + labor_cost + shipping_cost

    # Profit margin (admin-controlled minimum)
    min_margin_pct = config.get("min_profit_margin_pct", 15.0)
    profit = base_cost * (min_margin_pct / 100)

    # Market adjustment based on historical data
    market_adj = 0.0
    confidence = "LOW"
    historical_avg = historical.get("avg")

    if historical_avg and historical_avg > 0:
        market_adj_pct = config.get("market_adjustment_pct", 8.0)
        # If market avg is higher than our cost+margin, add a market premium
        cost_with_margin = base_cost + profit
        if historical_avg > cost_with_margin:
            market_adj = (historical_avg - cost_with_margin) * (market_adj_pct / 100)
        confidence = "HIGH" if historical.get("count", 0) >= 5 else "MEDIUM"
    else:
        # No historical data — use fabric base rate as reference
        fabric_base = BASE_RATES.get(fabric, 3.00)
        market_adj = fabric_base * quantity * (config.get("market_adjustment_pct", 8.0) / 100)
        confidence = "LOW"

    # Volume discount
    volume_discount = 0.0
    if quantity > 10000:
        volume_discount = base_cost * 0.05
    elif quantity > 5000:
        volume_discount = base_cost * 0.02

    # Urgency premium
    urgency_premium = 0.0
    if urgency == "HIGH":
        urgency_premium = base_cost * 0.10
    elif urgency == "LOW":
        urgency_premium = -(base_cost * 0.03)

    suggested = base_cost + profit + market_adj - volume_discount + urgency_premium

    # Anti-underbidding: enforce minimum margin
    min_allowed = base_cost * (1 + min_margin_pct / 100)
    max_discount_pct = config.get("max_discount_pct", 30.0)
    if historical_avg:
        min_allowed = max(min_allowed, historical_avg * (1 - max_discount_pct / 100))

    suggested = max(suggested, min_allowed)

    # Price range: ±8%
    price_min = round(suggested * 0.92, 2)
    price_max = round(suggested * 1.08, 2)
    suggested = round(suggested, 2)

    return {
        "base_cost": round(base_cost, 2),
        "profit_margin": round(profit, 2),
        "market_adjustment": round(market_adj, 2),
        "volume_discount": round(volume_discount, 2),
        "urgency_premium": round(urgency_premium, 2),
        "suggested_price": suggested,
        "price_range": {"min": price_min, "max": price_max},
        "confidence": confidence,
        "historical_avg": historical_avg,
        "historical_count": historical.get("count", 0),
        "min_allowed": round(min_allowed, 2),
    }


class AiBidRequest(BaseModel):
    material_cost: float
    labor_cost: float
    shipping_cost: float
    quantity: int
    fabric: str = "Unknown"
    category: str = "General"
    urgency: str = "MEDIUM"
    rfq_id: str = ""


@app.post("/ai/recommend-bid")
async def ai_recommend_bid(payload: AiBidRequest, user: dict = Depends(require_login)):
    """
    AI Bid Recommendation — supplier enters costs, gets suggested price.
    Requires PREMIUM subscription.
    """
    from database import db
    import uuid as _uuid
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Check premium
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company or company.get("role", "").upper() != "SUPPLIER":
        raise HTTPException(status_code=403, detail="Only suppliers can use AI bid recommendations")
    if company.get("subscription_tier", "FREE").upper() != "PREMIUM":
        raise HTTPException(status_code=403, detail="AI Bid Recommendations require a Premium subscription")

    # Validate inputs
    if payload.material_cost < 0 or payload.labor_cost < 0 or payload.shipping_cost < 0:
        raise HTTPException(status_code=400, detail="Costs cannot be negative")
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    config = await get_ai_config()
    historical = await get_historical_avg(payload.fabric, payload.category, payload.quantity)

    result = calculate_ai_bid(
        material_cost=payload.material_cost,
        labor_cost=payload.labor_cost,
        shipping_cost=payload.shipping_cost,
        quantity=payload.quantity,
        fabric=payload.fabric,
        category=payload.category,
        urgency=payload.urgency,
        historical=historical,
        config=config,
    )

    # Store in bid_recommendations collection
    supplier_id = company.get("unique_id") or company.get("id")
    rec_doc = {
        "id": str(_uuid.uuid4()),
        "supplier_id": supplier_id,
        "input_costs": {
            "material_cost": payload.material_cost,
            "labor_cost": payload.labor_cost,
            "shipping_cost": payload.shipping_cost,
            "quantity": payload.quantity,
            "fabric": payload.fabric,
            "category": payload.category,
            "urgency": payload.urgency,
        },
        "suggested_price": result["suggested_price"],
        "price_range": result["price_range"],
        "confidence": result["confidence"],
        "market_adjustment": result["market_adjustment"],
        "historical_avg": result["historical_avg"],
        "rfq_id": payload.rfq_id or None,
        "created_at": datetime.utcnow(),
    }
    await db["bid_recommendations"].insert_one(rec_doc)

    return {
        "success": True,
        "result": result,
        "recommendation_id": rec_doc["id"],
    }


@app.get("/ai/history/{supplier_id}")
async def ai_recommendation_history(supplier_id: str, user: dict = Depends(require_login)):
    """Get AI recommendation history for a supplier."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Only the supplier themselves or admin can view
    company = await db["companies"].find_one({"id": user.get("company_id")})
    user_supplier_id = company.get("unique_id") or company.get("id") if company else None
    if supplier_id != user_supplier_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    history = []
    async for doc in db["bid_recommendations"].find(
        {"supplier_id": supplier_id}
    ).sort("created_at", -1).limit(20):
        doc.pop("_id", None)
        if isinstance(doc.get("created_at"), datetime):
            doc["created_at"] = doc["created_at"].isoformat() + "Z"
        history.append(doc)

    return {"success": True, "history": history, "count": len(history)}


@app.get("/admin/ai-config")
async def get_admin_ai_config(user: dict = Depends(require_admin)):
    """Get current AI configuration."""
    config = await get_ai_config()
    config.pop("_id", None)
    return {"success": True, "config": config}


class AiConfigUpdateRequest(BaseModel):
    min_profit_margin_pct: float
    max_discount_pct: float
    market_adjustment_pct: float


@app.post("/admin/ai-config")
async def update_admin_ai_config(payload: AiConfigUpdateRequest, user: dict = Depends(require_admin)):
    """Admin updates AI bid recommendation limits."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    if payload.min_profit_margin_pct < 0 or payload.min_profit_margin_pct > 100:
        raise HTTPException(status_code=400, detail="Min profit margin must be 0-100%")
    if payload.max_discount_pct < 0 or payload.max_discount_pct > 80:
        raise HTTPException(status_code=400, detail="Max discount must be 0-80%")
    if payload.market_adjustment_pct < 0 or payload.market_adjustment_pct > 50:
        raise HTTPException(status_code=400, detail="Market adjustment must be 0-50%")

    now = datetime.utcnow()
    await db["ai_config"].update_one(
        {},
        {"$set": {
            "min_profit_margin_pct": payload.min_profit_margin_pct,
            "max_discount_pct": payload.max_discount_pct,
            "market_adjustment_pct": payload.market_adjustment_pct,
            "updated_by": user.get("id"),
            "updated_at": now,
        }},
        upsert=True
    )
    return {"success": True, "message": "AI configuration updated", "updated_at": now.isoformat() + "Z"}


@app.get("/admin/ai", response_class=HTMLResponse)
async def admin_ai_page(request: Request, admin: dict = Depends(require_admin)):
    """Admin AI monitoring and configuration page."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    config = await get_ai_config()
    config.pop("_id", None)

    # Stats
    total_recs = await db["bid_recommendations"].count_documents({})
    recent = []
    async for doc in db["bid_recommendations"].find().sort("created_at", -1).limit(10):
        doc.pop("_id", None)
        sid = doc.get("supplier_id")
        company = await db["companies"].find_one({"$or": [{"id": sid}, {"unique_id": sid}]})
        doc["company_name"] = company.get("name", "Unknown") if company else "Unknown"
        if isinstance(doc.get("created_at"), datetime):
            doc["created_at"] = doc["created_at"].isoformat() + "Z"
        recent.append(doc)

    return templates.TemplateResponse("admin_ai.html", {
        "request": request,
        "user": admin,
        "config": config,
        "total_recs": total_recs,
        "recent": recent,
    })


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
    else:
        # Not logged in - redirect to login
        if not user:
            return RedirectResponse(url="/login?next=/auction/" + rfq_id, status_code=303)
    
    # Check subscription status from company
    is_premium = False
    user_has_bid = False
    if company:
        subscription_tier = company.get("subscription_tier", "FREE")
        is_premium = subscription_tier == "PREMIUM"
    
    # Restrict auction room access to premium users only
    if not is_premium:
        return templates.TemplateResponse("premium_required.html", {
            "request": request,
            "user": user,
            "company": company,
            "feature_name": "Auction Room",
            "feature_description": "Real-time bidding in the Auction Room is exclusive to Premium members. Free users can submit bids through the 'Submit a Bid' page.",
            "redirect_url": f"/rfq/{rfq_id}"
        })
    
    if database.db is not None:
        try:
            rfq = await database.db["rfqs"].find_one({"id": rfq_id})
            
            if rfq:
                # Convert ObjectId to string to avoid serialization errors
                rfq["_id"] = str(rfq["_id"])
                
                # Check if current user has already bid on this RFQ
                if company and company.get("role", "").upper() == "SUPPLIER":
                    existing_bid = await database.db["bids"].find_one({
                        "rfq_id": rfq_id,
                        "supplier_id": company.get("unique_id")
                    })
                    user_has_bid = existing_bid is not None
                
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
        "company": company,
        "is_premium": is_premium,
        "user_has_bid": user_has_bid
    })


@app.post("/api/auction/bid")
async def place_bid(request: Request, user: dict = Depends(require_login)):
    """Place a bid in a reverse auction. Free users can bid once, Premium users can bid multiple times."""
    from fastapi.responses import JSONResponse
    import database
    import uuid
    
    try:
        form_data = await request.form()
        rfq_id = form_data.get("rfq_id", "").strip()
        supplier_id = form_data.get("supplier_id", "").strip()
        supplier_name = form_data.get("supplier_name", "").strip()
        bid_price = float(form_data.get("bid_price", 0))
        currency = form_data.get("currency", "BDT").strip().upper()
        if currency not in ["BDT", "USD", "EUR", "GBP", "INR", "CNY"]:
            currency = "BDT"
        
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
        
        # Check if user is a buyer - buyers cannot bid
        user_role = user_company.get("role", "").upper()
        if user_role == "BUYER":
            return JSONResponse({
                "success": False,
                "error": "Buyers cannot place bids. Only suppliers can bid on RFQs."
            }, status_code=403)
        
        # Check subscription status from company
        subscription_tier = user_company.get("subscription_tier", "FREE")
        is_premium = subscription_tier == "PREMIUM"
        
        # For free users, check if they already have a bid on this RFQ
        if not is_premium:
            existing_bid = await database.db["bids"].find_one({
                "rfq_id": rfq_id,
                "supplier_id": supplier_id
            })
            if existing_bid:
                return JSONResponse({
                    "success": False,
                    "error": "Free plan users can only submit one bid per RFQ. Upgrade to Premium to submit multiple bids.",
                    "upgrade_required": True
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
            id=str(uuid.uuid4()),
            rfq_id=rfq_id,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            bid_price=bid_price,
            currency=currency,
            timestamp=datetime.utcnow()
        )
        
        # Convert to dict for MongoDB insertion
        bid_dict = bid.model_dump()
        
        # Save bid to database - each bid is a separate document
        result = await database.db["bids"].insert_one(bid_dict)
        
        print(f"New bid inserted: ID={bid.id}, Supplier={supplier_name}, Price=${bid_price:.2f}, MongoDB _id={result.inserted_id}")
        
        # Send notification to buyer about new bid
        await notify_bid_submitted(rfq_id, supplier_name, bid_price, currency)
        
        bid_count_msg = ""
        if is_premium:
            # Count total bids from this supplier
            total_bids = await database.db["bids"].count_documents({
                "rfq_id": rfq_id,
                "supplier_id": supplier_id
            })
            bid_count_msg = f" (Bid #{total_bids} - Premium)"
        else:
            bid_count_msg = " (Free plan - 1 bid limit)"
        
        return JSONResponse({
            "success": True,
            "message": f"Bid placed successfully at ${bid_price:.2f}!{bid_count_msg}",
            "bid_id": bid.id,
            "bid_price": bid_price,
            "is_premium": is_premium
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
            {"$sort": {"timestamp": -1}}  # Sort by latest bid at top
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
                "id": bid.get("id", ""),
                "supplier_id": bid.get("supplier_id"),
                "supplier_name": bid.get("supplier_name"),
                "bid_price": bid.get("bid_price"),
                "currency": bid.get("currency", "BDT"),
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


# ----------------------------------------
# NOTIFICATION HELPER
# ----------------------------------------

async def create_notification(user_id: str, notification_type: str, title: str, message: str, related_id: str = None, link: str = None):
    """Create a notification for a user and persist to the database."""
    from database import db
    import uuid as _uuid

    if db is None:
        return None

    notif = {
        "id": str(_uuid.uuid4()),
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "is_read": False,
        "created_at": datetime.utcnow(),
        "related_id": related_id,
        "link": link,
    }
    await db["notifications"].insert_one(notif)
    return notif


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
                    "related_id": str(notif.get("related_id")) if notif.get("related_id") else None,
                    "link": str(notif.get("link")) if notif.get("link") else None
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

async def notify_bid_submitted(rfq_id: str, supplier_name: str, bid_price: float, currency: str = "BDT"):
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
    
    # buyer_id is the user's ID, so look up user directly
    user = await db["users"].find_one({
        "$or": [
            {"id": buyer_id},
            {"unique_id": buyer_id}
        ]
    })
    if not user:
        print(f"DEBUG NOTIFICATION: Buyer user not found for buyer_id={buyer_id}")
        return
    
    # Currency symbols
    currency_symbols = {
        "BDT": "৳",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹",
        "CNY": "¥"
    }
    symbol = currency_symbols.get(currency, currency)
    
    # Create notification for buyer
    await create_notification(
        user_id=user["id"],
        notification_type="bid_submitted",
        title="New Bid Received",
        message=f"{supplier_name} submitted a bid of {symbol}{bid_price:.2f} per unit on your RFQ: {rfq.get('title', 'Untitled')}",
        related_id=rfq_id
    )
    print(f"✅ Notification sent to buyer {user.get('email')} for new bid from {supplier_name}")


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
        user_company = None
        user_company_role = ""
        
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
        if user_company:
            user_company_role = user_company.get("role", "").upper()
        
        user_company_ids = set()
        if user:
            user_company_ids.add(user.get("id"))
            user_company_ids.add(user.get("company_id"))
            if user_company:
                user_company_ids.add(user_company.get("id"))
                user_company_ids.add(user_company.get("unique_id"))
        user_company_ids.discard(None)

        # Fetch only the latest bid from each supplier using aggregation
        # This ensures each supplier appears only once with their most recent bid
        pipeline = [
            {"$match": {"rfq_id": rfq_id}},
            {"$sort": {"timestamp": -1}},  # Sort by timestamp descending (newest first)
            {"$group": {
                "_id": "$supplier_id",  # Group by supplier_id
                "latest_bid": {"$first": "$$ROOT"}  # Take the first (most recent) bid
            }},
            {"$replaceRoot": {"newRoot": "$latest_bid"}},  # Replace root with the bid document
            {"$sort": {"bid_price": 1}}  # Sort by price ascending (lowest first)
        ]
        
        raw_bids = await db["bids"].aggregate(pipeline).to_list(length=None)
        
        bids = []
        for bid in raw_bids:
            bid["_id"] = str(bid["_id"])
            
            # Normalize status field (handle both 'status' and 'bid_status')
            if "status" not in bid and "bid_status" in bid:
                bid["status"] = bid["bid_status"]
            elif "status" not in bid:
                bid["status"] = "PENDING"
            
            # Hide rejected bids from non-owners
            # Check BOTH status fields - if either is REJECTED, hide from non-owners
            is_rejected = bid.get("status") == "REJECTED" or bid.get("bid_status") == "REJECTED"
            if is_rejected and not is_owner:
                continue
            
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

        # Check if current user has already bid on this RFQ (for suppliers)
        user_has_bid = False
        is_premium = False
        
        # Check subscription status for all users (both buyers and suppliers)
        # Try both user-level and company-level subscriptions
        if user:
            # First, try user-level subscription
            user_subscription = await db["subscriptions"].find_one({"user_id": user.get("id")})
            print(f"DEBUG PREMIUM CHECK: user_id={user.get('id')}, user_subscription={user_subscription}")
            
            if user_subscription:
                plan_tier = user_subscription.get("plan_tier", "FREE").upper()
                is_premium = plan_tier in ["PREMIUM", "ENTERPRISE"]
                print(f"DEBUG PREMIUM CHECK: plan_tier from user subscription={plan_tier}, is_premium={is_premium}")
            else:
                print(f"DEBUG PREMIUM CHECK: No user subscription found, checking company subscription")
                # If no user subscription, check company-level subscription
                user_company_id = user.get("company_id")
                if user_company_id:
                    company = await db["companies"].find_one({
                        "$or": [
                            {"id": user_company_id},
                            {"unique_id": user_company_id}
                        ]
                    })
                    if company:
                        subscription_tier = company.get("subscription_tier", "FREE").upper()
                        is_premium = subscription_tier in ["PREMIUM", "ENTERPRISE"]
                        print(f"DEBUG PREMIUM CHECK: company subscription_tier={subscription_tier}, is_premium={is_premium}")
                    else:
                        print(f"DEBUG PREMIUM CHECK: No company found for company_id={user_company_id}")
        
        if user and user_company_role == "SUPPLIER":
            # Check if user already has a bid
            existing_user_bid = await db["bids"].find_one({
                "rfq_id": rfq_id,
                "supplier_id": {"$in": list(user_company_ids)}
            })
            user_has_bid = existing_user_bid is not None

        # Fetch buyer company name for display
        buyer_company_name = None
        buyer_user_id = rfq.get("buyer_id")
        print(f"DEBUG: Looking up buyer company. buyer_id from RFQ: {buyer_user_id}")
        
        if buyer_user_id:
            # First, look up the buyer user to get their company_id
            buyer_user = await db["users"].find_one({
                "$or": [
                    {"id": buyer_user_id},
                    {"unique_id": buyer_user_id}
                ]
            })
            print(f"DEBUG: Buyer user lookup result: {buyer_user.get('email') if buyer_user else 'NOT FOUND'}")
            
            if buyer_user:
                buyer_company_id = buyer_user.get("company_id")
                print(f"DEBUG: Buyer user's company_id: {buyer_company_id}")
                
                if buyer_company_id:
                    # Now look up the company
                    buyer_company = await db["companies"].find_one({
                        "$or": [
                            {"id": buyer_company_id},
                            {"unique_id": buyer_company_id}
                        ]
                    })
                    print(f"DEBUG: Buyer company lookup result: {buyer_company.get('name') if buyer_company else 'NOT FOUND'}")
                    if buyer_company:
                        buyer_company_name = buyer_company.get("name")
                else:
                    print("DEBUG: Buyer user has no company_id")
            else:
                print("DEBUG: Buyer user not found")
        else:
            print("DEBUG: No buyer_id found in RFQ")

        print(f"DEBUG TEMPLATE VARS: is_premium={is_premium}, user_company_role={user_company_role}, user_id={user.get('id') if user else None}")

        return templates.TemplateResponse("rfq_detail.html", {
            "request": request,
            "user": user,
            "rfq": rfq,
            "is_owner": is_owner,
            "bids": bids,
            "user_company_role": user_company_role,
            "user_role": user_company_role,  # Add user_role for template
            "is_buyer_role": user_company_role == "BUYER",
            "user_has_bid": user_has_bid,
            "is_premium": is_premium,
            "buyer_company_name": buyer_company_name,
        })
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error loading RFQ detail: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to load RFQ details: {str(e)}")


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
        
        # Return the simplified RFQ edit page
        return templates.TemplateResponse("rfq_edit.html", {
            "request": request,
            "user": user,
            "rfq": rfq
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

# ----------------------------------------
# MULTI-CURRENCY ESCROW PAYMENT SYSTEM
# ----------------------------------------
import httpx
from pydantic import BaseModel
import uuid

# In-memory cache for exchange rates
exchange_rates_cache = {}
CACHE_TTL_HOURS = 1

async def get_exchange_rates():
    now = datetime.utcnow()
    if "USD" in exchange_rates_cache:
        cached_data = exchange_rates_cache["USD"]
        if now - cached_data["timestamp"] < timedelta(hours=CACHE_TTL_HOURS):
            return cached_data["rates"]

    try:
        async with httpx.AsyncClient() as client:
            # Using Open Exchange Rates API
            response = await client.get("https://open.er-api.com/v6/latest/USD")
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                exchange_rates_cache["USD"] = {
                    "rates": rates,
                    "timestamp": now
                }
                return rates
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
    
    # Fallback rates if API fails
    return {"USD": 1.0, "BDT": 110.0, "EUR": 0.92, "GBP": 0.79}

async def convert_to_base(amount: float, from_currency: str):
    """Convert any supported currency to base USD."""
    rates = await get_exchange_rates()
    rate = rates.get(from_currency, 1.0)
    # Conversion: USD = amount / rate_of_currency_per_usd
    base_usd = amount / rate if rate else amount
    return {
        "original_amount": amount,
        "original_currency": from_currency,
        "base_amount_usd": base_usd,
        "exchange_rate": rate
    }

@app.get("/api/currency/convert")
async def api_convert_currency(amount: float, currency: str):
    conversion = await convert_to_base(amount, currency)
    return conversion


class BidSubmitRequest(BaseModel):
    rfq_id: str
    bid_price: float
    currency: str = "BDT"  # Default to BDT


@app.post("/api/bid/submit")
async def submit_bid(payload: BidSubmitRequest, user: dict = Depends(require_login)):
    """Any logged-in user can place a bid on an RFQ (reverse bidding system)."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    company = await db["companies"].find_one({"id": user.get("company_id")})
    rfq = await db["rfqs"].find_one({"id": payload.rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Prevent bidding on your own RFQ
    buyer_ids = {rfq.get("buyer_id"), user.get("id"), user.get("company_id")}
    if company:
        buyer_ids.add(company.get("id"))
        buyer_ids.add(company.get("unique_id"))
    buyer_ids.discard(None)
    if rfq.get("buyer_id") in buyer_ids and rfq.get("buyer_id") == (company.get("id") if company else user.get("id")):
        raise HTTPException(status_code=403, detail="You cannot bid on your own RFQ")

    bidder_name = company.get("name", user.get("email", "Unknown")) if company else user.get("email", "Unknown")
    bidder_id = company.get("unique_id") or company.get("id") if company else user.get("id")
    bidder_role = company.get("role", "SUPPLIER").upper() if company else "SUPPLIER"

    # Check if user is a buyer - buyers cannot bid
    if bidder_role == "BUYER":
        raise HTTPException(status_code=403, detail="Buyers cannot place bids. Only suppliers can bid on RFQs.")

    # Check subscription status from company
    subscription_tier = company.get("subscription_tier", "FREE")
    is_premium = subscription_tier == "PREMIUM"
    
    # For free users, check if they already have a bid on this RFQ
    if not is_premium:
        existing_bid = await db["bids"].find_one({
            "rfq_id": payload.rfq_id,
            "supplier_id": bidder_id
        })
        if existing_bid:
            raise HTTPException(
                status_code=403, 
                detail="Free plan users can only submit one bid per RFQ. Upgrade to Premium to submit multiple bids."
            )

    # ── Factory Capacity Check (warning only — does not block submission) ──
    capacity_warning = None
    rfq_quantity = rfq.get("quantity", 0)
    if rfq_quantity > 0:
        cap = await get_supplier_capacity(bidder_id)
        if cap.get("has_data"):
            available = cap.get("available_capacity", cap.get("estimated_monthly_units", 0))
            if available < rfq_quantity:
                shortfall = rfq_quantity - available
                capacity_warning = (
                    f"Your available production capacity ({available:,} units/month) is below "
                    f"the RFQ quantity ({rfq_quantity:,} units). Shortfall: {shortfall:,} units. "
                    f"The buyer will be informed of this when reviewing bids."
                )

    bid = BidModel(
        rfq_id=payload.rfq_id,
        supplier_id=bidder_id,
        supplier_name=bidder_name,
        bid_price=payload.bid_price,
        currency=payload.currency,
    )
    bid_dict = bid.model_dump()
    bid_dict["bidder_role"] = bidder_role  # track who placed the bid
    await db["bids"].insert_one(bid_dict)
    
    # Send notification to buyer about new bid
    await notify_bid_submitted(payload.rfq_id, bidder_name, payload.bid_price, payload.currency)

    return {
        "success": True,
        "bid_id": bid.id,
        "message": "Bid submitted successfully",
        "is_premium": is_premium,
        "capacity_warning": capacity_warning,
    }


@app.put("/api/bid/{bid_id}")
async def update_bid(bid_id: str, request: Request, user: dict = Depends(require_login)):
    """Update a submitted bid."""
    from database import db
    from fastapi.responses import JSONResponse
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
    bid = await db["bids"].find_one({"id": bid_id})
    if not bid:
        return JSONResponse({"success": False, "error": "Bid not found"}, status_code=404)
        
    # Check ownership
    user_company = await db["companies"].find_one({"id": user.get("company_id")})
    bidder_ids = {user.get("id"), user.get("company_id")}
    if user_company:
        bidder_ids.add(user_company.get("id"))
        bidder_ids.add(user_company.get("unique_id"))
    bidder_ids.discard(None)
    
    if bid.get("supplier_id") not in bidder_ids:
        return JSONResponse({"success": False, "error": "Unauthorized to update this bid"}, status_code=403)
        
    # Ensure bid hasn't been accepted
    if bid.get("bid_status") in ["ACCEPTED", "REJECTED"]:
        return JSONResponse({"success": False, "error": f"Cannot edit an {bid.get('bid_status').lower()} bid"}, status_code=400)
        
    form_data = await request.form()
    update_data = {}
    
    if form_data.get("bid_price"):
        update_data["bid_price"] = float(form_data.get("bid_price"))
    if form_data.get("delivery_time_days"):
        update_data["delivery_time_days"] = int(form_data.get("delivery_time_days"))
    if form_data.get("incoterms"):
        update_data["incoterms"] = form_data.get("incoterms")
    if form_data.get("quality_notes") is not None:
        update_data["quality_notes"] = form_data.get("quality_notes")
        
    if not update_data:
        return JSONResponse({"success": False, "error": "No data provided"}, status_code=400)
        
    await db["bids"].update_one({"id": bid_id}, {"$set": update_data})
    
    return JSONResponse({"success": True, "message": "Bid updated successfully"})


@app.delete("/api/bid/{bid_id}")
async def withdraw_bid(bid_id: str, user: dict = Depends(require_login)):
    """Withdraw/delete a submitted bid."""
    from database import db
    from fastapi.responses import JSONResponse
    
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
        
    bid = await db["bids"].find_one({"id": bid_id})
    if not bid:
        return JSONResponse({"success": False, "error": "Bid not found"}, status_code=404)
        
    # Check ownership
    user_company = await db["companies"].find_one({"id": user.get("company_id")})
    bidder_ids = {user.get("id"), user.get("company_id")}
    if user_company:
        bidder_ids.add(user_company.get("id"))
        bidder_ids.add(user_company.get("unique_id"))
    bidder_ids.discard(None)
    
    if bid.get("supplier_id") not in bidder_ids:
        return JSONResponse({"success": False, "error": "Unauthorized to withdraw this bid"}, status_code=403)
        
    # Ensure bid hasn't been accepted
    if bid.get("bid_status") in ["ACCEPTED", "REJECTED"]:
        return JSONResponse({"success": False, "error": f"Cannot withdraw an {bid.get('bid_status').lower()} bid"}, status_code=400)
        
    await db["bids"].delete_one({"id": bid_id})
    
    return JSONResponse({"success": True, "message": "Bid withdrawn successfully"})


# ----------------------------------------

# ----------------------------------------
# FACTORY CAPACITY MANAGEMENT
# ----------------------------------------
# Collection: supplier_capacity
# Fields: supplier_id, total_capacity, available_capacity, last_updated
# Logic:
#   - Supplier declares total & available capacity via PUT /capacity/update
#   - Deducted when bid is confirmed (order locked in)
#   - Restored when payment is cancelled, disputed, or refunded
# ─────────────────────────────────────────

def estimate_capacity_units(total_workers: int, total_machines: int) -> int:
    """Estimate monthly production capacity from workforce/machine data."""
    if total_workers <= 0 and total_machines <= 0:
        return 0
    worker_capacity = total_workers * 550        # ~550 units/worker/month
    machine_capacity = total_machines * 200 * 22 # ~200 units/machine/day × 22 days
    return min(worker_capacity, machine_capacity) if total_machines > 0 else worker_capacity


async def get_supplier_capacity(supplier_id: str) -> dict:
    """
    Fetch supplier capacity. Checks supplier_capacity collection first,
    falls back to estimating from legal_capacity if no explicit record.
    """
    from database import db
    if db is None:
        return {"has_data": False}

    company = await db["companies"].find_one({
        "$or": [{"id": supplier_id}, {"unique_id": supplier_id}]
    })
    if not company:
        return {"has_data": False}

    company_id = company.get("id")

    # 1. Dedicated supplier_capacity record (most accurate)
    cap_doc = await db["supplier_capacity"].find_one({"supplier_id": company_id})
    if cap_doc:
        total = cap_doc.get("total_capacity", 0)
        available = cap_doc.get("available_capacity", 0)
        last = cap_doc.get("last_updated")
        return {
            "has_data": True,
            "source": "supplier_capacity",
            "company_id": company_id,
            "total_capacity": total,
            "available_capacity": available,
            "estimated_monthly_units": total,
            "last_updated": last,
        }

    # 2. Estimate from legal_capacity (fallback)
    legal = await db["legal_capacity"].find_one({"company_id": company_id})
    if not legal:
        return {"has_data": False, "company_id": company_id}

    workers = legal.get("total_workers", 0)
    machines = legal.get("total_machines", 0)
    estimated = estimate_capacity_units(workers, machines)
    return {
        "has_data": True,
        "source": "legal_capacity",
        "company_id": company_id,
        "total_workers": workers,
        "total_machines": machines,
        "total_capacity": estimated,
        "available_capacity": estimated,
        "estimated_monthly_units": estimated,
        "last_updated": None,
    }


async def deduct_capacity(supplier_id: str, quantity: int):
    """Deduct quantity from available_capacity when an order is confirmed."""
    from database import db
    if db is None:
        return
    company = await db["companies"].find_one({
        "$or": [{"id": supplier_id}, {"unique_id": supplier_id}]
    })
    if not company:
        return
    company_id = company.get("id")
    cap_doc = await db["supplier_capacity"].find_one({"supplier_id": company_id})
    if cap_doc:
        new_avail = max(0, cap_doc.get("available_capacity", 0) - quantity)
        await db["supplier_capacity"].update_one(
            {"supplier_id": company_id},
            {"$set": {"available_capacity": new_avail, "last_updated": datetime.utcnow()}}
        )


async def restore_capacity(supplier_id: str, quantity: int):
    """Restore quantity to available_capacity when an order is cancelled/refunded."""
    from database import db
    if db is None:
        return
    company = await db["companies"].find_one({
        "$or": [{"id": supplier_id}, {"unique_id": supplier_id}]
    })
    if not company:
        return
    company_id = company.get("id")
    cap_doc = await db["supplier_capacity"].find_one({"supplier_id": company_id})
    if cap_doc:
        new_avail = min(
            cap_doc.get("total_capacity", 0),
            cap_doc.get("available_capacity", 0) + quantity
        )
        await db["supplier_capacity"].update_one(
            {"supplier_id": company_id},
            {"$set": {"available_capacity": new_avail, "last_updated": datetime.utcnow()}}
        )


# ── PUT /capacity/update ──────────────────────────────────────────────────────

class CapacityUpdateRequest(BaseModel):
    total_capacity: int
    available_capacity: int


@app.put("/capacity/update")
async def update_capacity(payload: CapacityUpdateRequest, user: dict = Depends(require_login)):
    """Supplier sets their declared production capacity."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company or company.get("role", "").upper() != "SUPPLIER":
        raise HTTPException(status_code=403, detail="Only suppliers can update capacity")

    if payload.total_capacity <= 0:
        raise HTTPException(status_code=400, detail="Total capacity must be greater than 0")
    if payload.available_capacity < 0:
        raise HTTPException(status_code=400, detail="Available capacity cannot be negative")
    if payload.available_capacity > payload.total_capacity:
        raise HTTPException(status_code=400, detail="Available capacity cannot exceed total capacity")

    company_id = company.get("id")
    now = datetime.utcnow()
    await db["supplier_capacity"].update_one(
        {"supplier_id": company_id},
        {"$set": {
            "supplier_id": company_id,
            "total_capacity": payload.total_capacity,
            "available_capacity": payload.available_capacity,
            "last_updated": now,
        }},
        upsert=True
    )
    return {
        "success": True,
        "message": "Capacity updated successfully",
        "total_capacity": payload.total_capacity,
        "available_capacity": payload.available_capacity,
        "last_updated": now.isoformat() + "Z",
    }


# ── GET /capacity/{supplier_id} ───────────────────────────────────────────────

@app.get("/capacity/{supplier_id}")
async def get_capacity_endpoint(supplier_id: str, user: dict = Depends(require_login)):
    """Get a supplier's capacity. Accessible to buyers, suppliers, and admins."""
    cap = await get_supplier_capacity(supplier_id)
    if not cap.get("has_data"):
        return {
            "success": True,
            "has_data": False,
            "supplier_id": supplier_id,
            "message": "No capacity data available for this supplier.",
        }
    last = cap.get("last_updated")
    total = cap.get("total_capacity", 0)
    available = cap.get("available_capacity", 0)
    return {
        "success": True,
        "has_data": True,
        "supplier_id": supplier_id,
        "source": cap.get("source"),
        "total_capacity": total,
        "available_capacity": available,
        "utilization_pct": round((1 - available / max(total, 1)) * 100, 1),
        "last_updated": last.isoformat() + "Z" if last else None,
    }


# ── POST /capacity/check ──────────────────────────────────────────────────────

class CapacityCheckRequest(BaseModel):
    supplier_id: str
    quantity: int


@app.post("/capacity/check")
async def check_capacity_post(payload: CapacityCheckRequest, user: dict = Depends(require_login)):
    """
    Check if a supplier has enough available capacity for a given quantity.
    Returns can_fulfill, shortfall, and split suggestion.
    """
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    cap = await get_supplier_capacity(payload.supplier_id)
    if not cap.get("has_data"):
        return {
            "success": True,
            "has_capacity_data": False,
            "quantity_required": payload.quantity,
            "message": "Supplier has not submitted capacity details yet.",
        }

    available = cap.get("available_capacity", 0)
    total = cap.get("total_capacity", 0)
    can_fulfill = available >= payload.quantity
    shortfall = max(0, payload.quantity - available)
    split_count = math.ceil(payload.quantity / available) if available > 0 and not can_fulfill else None

    return {
        "success": True,
        "has_capacity_data": True,
        "quantity_required": payload.quantity,
        "total_capacity": total,
        "available_capacity": available,
        "utilization_pct": round((1 - available / max(total, 1)) * 100, 1),
        "can_fulfill": can_fulfill,
        "shortfall": shortfall,
        "split_suggestion": split_count,
        "message": (
            f"Supplier can fulfill this order ({available:,} units available)."
            if can_fulfill
            else f"Supplier only has {available:,} units available but {payload.quantity:,} required. "
                 f"Shortfall: {shortfall:,} units. Consider splitting across {split_count} suppliers."
        ),
    }


# ── GET /api/capacity/check (RFQ-based) ──────────────────────────────────────

@app.get("/api/capacity/check")
async def check_capacity_get(supplier_id: str, rfq_id: str, user: dict = Depends(require_login)):
    """Check capacity for a specific RFQ (GET convenience endpoint)."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    rfq = await db["rfqs"].find_one({"id": rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    result = await check_capacity_post(
        CapacityCheckRequest(supplier_id=supplier_id, quantity=rfq.get("quantity", 0)), user
    )
    result["rfq_id"] = rfq_id
    return result


# ── GET /admin/capacity ───────────────────────────────────────────────────────

@app.get("/admin/capacity", response_class=HTMLResponse)
async def admin_capacity_monitor(request: Request, admin: dict = Depends(require_admin)):
    """Admin: monitor all supplier capacity entries for suspicious/fake data."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    entries = []
    async for doc in db["supplier_capacity"].find().sort("last_updated", -1):
        doc.pop("_id", None)
        sid = doc.get("supplier_id")
        company = await db["companies"].find_one({"id": sid})
        total = doc.get("total_capacity", 0)
        available = doc.get("available_capacity", 0)
        legal = await db["legal_capacity"].find_one({"company_id": sid})
        est_legal = 0
        if legal:
            est_legal = estimate_capacity_units(
                legal.get("total_workers", 0), legal.get("total_machines", 0)
            )
        # Flag suspicious: declared capacity > 3x legal estimate
        suspicious = est_legal > 0 and total > est_legal * 3
        last = doc.get("last_updated")
        entries.append({
            "supplier_id": sid,
            "company_name": company.get("name", "Unknown") if company else "Unknown",
            "total_capacity": total,
            "available_capacity": available,
            "utilization_pct": round((1 - available / max(total, 1)) * 100, 1),
            "estimated_from_legal": est_legal,
            "suspicious": suspicious,
            "last_updated": last.isoformat() + "Z" if last else None,
        })

    return templates.TemplateResponse("admin_capacity.html", {
        "request": request,
        "user": admin,
        "entries": entries,
        "total_suppliers": len(entries),
        "suspicious_count": sum(1 for e in entries if e["suspicious"]),
    })


class BidAcceptRequest(BaseModel):
    bid_id: str
    rfq_id: str


@app.post("/api/bid/accept")
async def accept_bid(payload: BidAcceptRequest, user: dict = Depends(require_login)):
    """Accept a bid. Only the buyer who created the RFQ can accept a bid."""
    from database import db
    import uuid as _uuid
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    rfq = await db["rfqs"].find_one({"id": payload.rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    bid = await db["bids"].find_one({"id": payload.bid_id, "rfq_id": payload.rfq_id})
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Get current user's company
    user_company = await db["companies"].find_one({"id": user.get("company_id")})

    # Only buyers can accept bids
    if not user_company or user_company.get("role", "").upper() != "BUYER":
        raise HTTPException(status_code=403, detail="Only buyers can accept bids.")

    # Only the buyer who created this RFQ can accept bids on it
    rfq_buyer_id = rfq.get("buyer_id")
    user_id = user.get("id")
    user_company_id = user.get("company_id")
    
    # Check if current user is the RFQ owner (buyer_id is the user's ID)
    if rfq_buyer_id != user_id:
        raise HTTPException(status_code=403, detail="You can only accept bids on RFQs you created.")

    # ── Factory Capacity Check (hard warning — returns capacity info to frontend) ──
    rfq_quantity = rfq.get("quantity", 0)
    capacity_info = None
    if rfq_quantity > 0:
        cap = await get_supplier_capacity(bid.get("supplier_id", ""))
        if cap.get("has_data"):
            estimated = cap["estimated_monthly_units"]
            available = cap.get("available_capacity", estimated)
            can_fulfill = available >= rfq_quantity
            capacity_info = {
                "has_data": True,
                "can_fulfill": can_fulfill,
                "estimated_monthly_units": estimated,
                "available_capacity": available,
                "total_capacity": cap.get("total_capacity", estimated),
                "total_workers": cap.get("total_workers"),
                "total_machines": cap.get("total_machines"),
                "quantity_required": rfq_quantity,
                "shortfall": max(0, rfq_quantity - available),
            }
        else:
            capacity_info = {"has_data": False}

    # Mark this bid ACCEPTED, reject all others on this RFQ
    await db["bids"].update_one({"id": payload.bid_id}, {"$set": {"status": "ACCEPTED"}})
    await db["bids"].update_many(
        {"rfq_id": payload.rfq_id, "id": {"$ne": payload.bid_id}},
        {"$set": {"status": "REJECTED"}}
    )

    # Update RFQ to EVALUATING
    await db["rfqs"].update_one({"id": payload.rfq_id}, {"$set": {"status": "EVALUATING"}})

    # Notify the bid owner
    bid_owner_company = await db["companies"].find_one({
        "$or": [{"unique_id": bid.get("supplier_id")}, {"id": bid.get("supplier_id")}]
    })
    if bid_owner_company:
        bid_owner_user = await db["users"].find_one({"company_id": bid_owner_company.get("id")})
        if bid_owner_user:
            acceptor_name = user_company.get("name", user.get("email", "")) if user_company else user.get("email", "")
            await db["notifications"].insert_one({
                "id": str(_uuid.uuid4()),
                "user_id": bid_owner_user.get("id"),
                "type": "bid_submitted",
                "title": "Your Bid Was Accepted!",
                "message": f"{acceptor_name} accepted your bid of BDT {bid.get('bid_price'):,.2f}/unit for '{rfq.get('title')}'. Please confirm you can fulfill this order.",
                "is_read": False,
                "created_at": datetime.utcnow(),
                "related_id": payload.rfq_id,
            })

    return {
        "success": True,
        "message": "Bid accepted. The other party must now confirm.",
        "capacity_info": capacity_info,
    }


class BidConfirmRequest(BaseModel):
    bid_id: str
    rfq_id: str


@app.post("/api/bid/confirm")
async def confirm_bid(payload: BidConfirmRequest, user: dict = Depends(require_login)):
    """Supplier confirms they can fulfill the accepted bid. Unlocks Pay Now for the buyer."""
    from database import db
    import uuid as _uuid
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    bid = await db["bids"].find_one({"id": payload.bid_id, "rfq_id": payload.rfq_id})
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    if bid.get("status") != "ACCEPTED":
        raise HTTPException(status_code=400, detail="Bid must be ACCEPTED by buyer before supplier can confirm")

    # Verify caller is the supplier of this bid
    company = await db["companies"].find_one({"id": user.get("company_id")})
    supplier_ids = [user.get("id")]
    if company:
        if company.get("unique_id"):
            supplier_ids.append(company.get("unique_id"))
        supplier_ids.append(company.get("id"))

    if bid.get("supplier_id") not in supplier_ids:
        raise HTTPException(status_code=403, detail="Only the supplier of this bid can confirm it")

    # Mark bid as CONFIRMED
    await db["bids"].update_one(
        {"id": payload.bid_id},
        {"$set": {"status": "CONFIRMED", "confirmed_at": datetime.utcnow()}}
    )

    # ── Deduct capacity from supplier when order is confirmed ──
    rfq_for_cap = await db["rfqs"].find_one({"id": payload.rfq_id})
    if rfq_for_cap:
        await deduct_capacity(bid.get("supplier_id", ""), rfq_for_cap.get("quantity", 0))

    # Notify the buyer
    rfq = await db["rfqs"].find_one({"id": payload.rfq_id})
    buyer_user = None
    if rfq:
        buyer_user = await db["users"].find_one({"id": rfq.get("buyer_id")})
        if not buyer_user:
            # Try by company_id
            buyer_company = await db["companies"].find_one({
                "$or": [
                    {"id": rfq.get("buyer_id")},
                    {"unique_id": rfq.get("buyer_id")},
                ]
            })
            if buyer_company:
                buyer_user = await db["users"].find_one({"company_id": buyer_company.get("id")})

    if buyer_user:
        await db["notifications"].insert_one({
            "id": str(_uuid.uuid4()),
            "user_id": buyer_user.get("id"),
            "type": "bid_submitted",
            "title": "Supplier Confirmed — Ready to Pay",
            "message": f"The supplier has confirmed your accepted bid for '{rfq.get('title') if rfq else ''}'. You can now proceed to payment.",
            "is_read": False,
            "created_at": datetime.utcnow(),
            "related_id": payload.rfq_id,
        })

    return {"success": True, "message": "Order confirmed. Buyer can now proceed to payment."}

class InitiatePaymentRequest(BaseModel):
    order_id: str
    bid_id: str
    amount: float
    currency: str
    supplier_id: str

@app.post("/api/payment/initiate")
@app.post("/escrow/deposit")
async def initiate_payment(payload: InitiatePaymentRequest, user: dict = Depends(require_buyer)):
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    # Clean up any existing PENDING payments for this bid (user might have cancelled before)
    await db["payments"].delete_many({
        "order_id": payload.order_id,
        "bid_id": payload.bid_id,
        "status": EscrowStatusEnum.PENDING
    })
        
    buyer_id = user.get("id")
    conversion = await convert_to_base(payload.amount, payload.currency)
    
    # Normally, integrate with SSLCommerz here for gateway initiation.
    # We will simulate a successful SSLCommerz redirect logic.
    payment_id = str(uuid.uuid4())
    transaction_id = f"TXN-{secrets.token_hex(8).upper()}"
    
    payment = PaymentModel(
        payment_id=payment_id,
        transaction_id=transaction_id,
        order_id=payload.order_id,
        bid_id=payload.bid_id,
        buyer_id=buyer_id,
        supplier_id=payload.supplier_id,
        amount=payload.amount,
        original_amount=conversion["original_amount"],
        original_currency=conversion["original_currency"],
        base_amount_usd=conversion["base_amount_usd"],
        exchange_rate=conversion["exchange_rate"],
        status=EscrowStatusEnum.PENDING
    )
    
    await db["payments"].insert_one(payment.model_dump())
    
    # Provide a redirect URL to our simulated SSLCommerz gateway
    redirect_url = f"/payment/sslcommerz/checkout?txn={transaction_id}"
    return {"success": True, "transaction_id": transaction_id, "redirect_url": redirect_url}

@app.get("/payment/gateway", response_class=HTMLResponse)
async def payment_gateway_page(
    request: Request,
    rfq_id: str,
    bid_id: str,
    user: dict = Depends(require_login)
):
    """Payment gateway page: shows currency conversion and 'Pay by Card' button."""
    from database import db
    rfq = await db["rfqs"].find_one({"id": rfq_id}) if db is not None else None
    bid = await db["bids"].find_one({"id": bid_id}) if db is not None else None

    if not rfq or not bid:
        raise HTTPException(status_code=404, detail="RFQ or Bid not found")

    # Pre-fetch conversion for BDT so the page can render the preview
    bid_price = bid.get("bid_price", 0)
    quantity = rfq.get("quantity", 1)
    total_bdt = bid_price * quantity
    conversion = await convert_to_base(total_bdt, "BDT")

    return templates.TemplateResponse("payment_gateway.html", {
        "request": request,
        "user": user,
        "rfq": rfq,
        "bid": bid,
        "total_local": total_bdt,
        "local_currency": "BDT",
        "usd_amount": round(conversion["base_amount_usd"], 2),
        "exchange_rate": round(conversion["exchange_rate"], 4),
    })


@app.get("/payment/sslcommerz/checkout", response_class=HTMLResponse)
async def sslcommerz_mock_checkout(request: Request, txn: str):
    """Simulated SSLCommerz Hosted Checkout page (Strictly Card Only)."""
    from database import db
    payment = None
    if db is not None:
        payment = await db["payments"].find_one({"transaction_id": txn})
    return templates.TemplateResponse("mock_sslcommerz.html", {
        "request": request,
        "txn": txn,
        "payment": payment,
    })


@app.post("/api/payment/success")
async def payment_success(request: Request, transaction_id: str = Form(...)):
    """
    SSLCommerz IPN / redirect callback.
    Marks the payment as HELD_IN_ESCROW and logs the exact exchange rate
    that was captured at initiation time (already stored in the document).
    Also marks the linked RFQ as AWARDED so it leaves the open feed.
    """
    from database import db
    if db is not None:
        payment = await db["payments"].find_one({"transaction_id": transaction_id})
        if payment:
            confirmed_at = datetime.utcnow()
            print(
                f"[ESCROW] Payment confirmed | txn={transaction_id} | "
                f"local={payment.get('original_amount')} {payment.get('original_currency')} | "
                f"usd={payment.get('base_amount_usd')} | "
                f"rate_at_payment={payment.get('exchange_rate')} | "
                f"confirmed_at={confirmed_at.isoformat()}"
            )
            await db["payments"].update_one(
                {"transaction_id": transaction_id},
                {
                    "$set": {
                        "status": EscrowStatusEnum.PAID_IN_ESCROW,
                        "updated_at": confirmed_at,
                        "confirmed_at": confirmed_at,
                        "rate_locked_at_payment": payment.get("exchange_rate"),
                    }
                }
            )
            # Mark the linked RFQ as AWARDED so it no longer appears in the open feed
            order_id = payment.get("order_id")
            if order_id:
                result = await db["rfqs"].update_one(
                    {"id": order_id},
                    {"$set": {"status": "AWARDED"}}
                )
                print(f"[ESCROW] RFQ {order_id} status → AWARDED (matched={result.matched_count}, modified={result.modified_count})")

            # ── Auto-create milestone record on payment success ──
            milestone_order_id = payment.get("order_id")
            milestone_payment_id = payment.get("payment_id")
            if milestone_order_id and milestone_payment_id:
                existing_ms = await db["order_milestones"].find_one({"order_id": milestone_order_id})
                if not existing_ms:
                    ms_doc = build_initial_milestones(
                        order_id=milestone_order_id,
                        payment_id=milestone_payment_id,
                        supplier_id=payment.get("supplier_id", ""),
                        buyer_id=payment.get("buyer_id", ""),
                    )
                    await db["order_milestones"].insert_one(ms_doc)
                    print(f"[MILESTONE] Created milestone for order {milestone_order_id}")

            # Notify supplier that payment has been completed
            supplier_id = payment.get("supplier_id")
            if supplier_id:
                import uuid as _uuid
                # Find supplier user
                supplier_user = await db["users"].find_one({
                    "$or": [
                        {"id": supplier_id},
                        {"company_id": supplier_id},
                    ]
                })
                if not supplier_user:
                    supplier_company = await db["companies"].find_one({
                        "$or": [
                            {"id": supplier_id},
                            {"unique_id": supplier_id},
                        ]
                    })
                    if supplier_company:
                        supplier_user = await db["users"].find_one({"company_id": supplier_company.get("id")})

                if supplier_user:
                    rfq_title = ""
                    if order_id:
                        rfq_doc = await db["rfqs"].find_one({"id": order_id})
                        rfq_title = rfq_doc.get("title", "") if rfq_doc else ""

                    amount = payment.get("original_amount", payment.get("base_amount_usd", 0))
                    currency = payment.get("original_currency", "BDT")
                    currency_symbols = {"BDT": "৳", "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "CNY": "¥"}
                    symbol = currency_symbols.get(currency, currency)

                    await db["notifications"].insert_one({
                        "id": str(_uuid.uuid4()),
                        "user_id": supplier_user.get("id"),
                        "type": "payment_received",
                        "title": "Payment Completed — Funds in Escrow",
                        "message": f"The buyer has completed payment of {symbol}{amount:.2f} for '{rfq_title}'. Funds are held in escrow and will be released upon order completion.",
                        "is_read": False,
                        "created_at": datetime.utcnow(),
                        "related_id": order_id or payment.get("id", ""),
                    })
                    print(f"[NOTIFICATION] Payment notification sent to supplier {supplier_user.get('email')}")
    return RedirectResponse(url="/buyer/orders", status_code=303)


@app.post("/api/payment/fail")
async def payment_fail(request: Request, transaction_id: str = Form(...)):
    """SSLCommerz failure callback — deletes the pending payment."""
    from database import db
    if db is not None:
        # Delete the failed payment record
        await db["payments"].delete_one({
            "transaction_id": transaction_id,
            "status": EscrowStatusEnum.PENDING
        })
    return RedirectResponse(url=f"/buyer/orders?failed={transaction_id}", status_code=303)


@app.post("/api/payment/cancel")
async def payment_cancel(request: Request, transaction_id: str = Form(...)):
    """SSLCommerz cancel callback - deletes the pending payment and restores capacity."""
    from database import db
    if db is not None:
        payment = await db["payments"].find_one({
            "transaction_id": transaction_id,
            "status": EscrowStatusEnum.PENDING
        })
        if payment:
            # Restore supplier capacity before deleting
            bid = await db["bids"].find_one({"id": payment.get("bid_id")})
            rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
            if bid and rfq:
                await restore_capacity(bid.get("supplier_id", ""), rfq.get("quantity", 0))
            await db["payments"].delete_one({"transaction_id": transaction_id, "status": EscrowStatusEnum.PENDING})
    return RedirectResponse(url=f"/buyer/orders?cancelled={transaction_id}", status_code=303)


@app.get("/api/payment/list")
async def get_all_payments(admin: dict = Depends(require_admin)):
    """Admin endpoint to list all escrow payments."""
    from database import db
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    try:
        payments = await db["payments"].find({}).sort("created_at", -1).to_list(length=1000)
        clean_payments = []
        for p in payments:
            clean_p = {
                "payment_id": p.get("payment_id"),
                "transaction_id": p.get("transaction_id"),
                "order_id": p.get("order_id"),
                "bid_id": p.get("bid_id"),
                "buyer_id": p.get("buyer_id"),
                "supplier_id": p.get("supplier_id"),
                "amount": p.get("amount", 0.0),
                "original_amount": p.get("original_amount", 0.0),
                "original_currency": p.get("original_currency", "BDT"),
                "base_amount_usd": p.get("base_amount_usd", 0.0),
                "exchange_rate": p.get("exchange_rate", 1.0),
                "status": p.get("status"),
                "created_at": p.get("created_at").isoformat() + 'Z' if isinstance(p.get("created_at"), datetime) else str(p.get("created_at"))
            }
            clean_payments.append(clean_p)
            
        return {"success": True, "payments": clean_payments}
    except Exception as e:
        print(f"Error fetching payments: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


class ReleasePaymentRequest(BaseModel):
    payment_id: str


@app.post("/api/payment/release")
@app.post("/escrow/release")
async def release_escrow(payload: ReleasePaymentRequest, user: dict = Depends(require_admin)):
    """Admin releases escrowed funds to the supplier."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    payment = await db["payments"].find_one({"payment_id": payload.payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can release escrow funds")

    if payment.get("status") not in [EscrowStatusEnum.PAID_IN_ESCROW, "WORK_IN_PROGRESS", "SENT_FOR_DELIVERY"]:
        raise HTTPException(status_code=400, detail="Payment must be in escrow to release")

    await db["payments"].update_one(
        {"payment_id": payload.payment_id},
        {"$set": {"status": EscrowStatusEnum.RELEASED, "updated_at": datetime.utcnow()}}
    )
    return {"success": True, "message": "Funds released to supplier"}


class DisputePaymentRequest(BaseModel):
    payment_id: str
    reason: str


@app.post("/api/payment/dispute")
async def dispute_escrow(payload: DisputePaymentRequest, user: dict = Depends(require_login)):
    """Admin places a payment on hold (DISPUTED) to block release."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can file disputes")

    payment = await db["payments"].find_one({"payment_id": payload.payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.get("status") not in [EscrowStatusEnum.PAID_IN_ESCROW, EscrowStatusEnum.RELEASED]:
        raise HTTPException(status_code=400, detail="Cannot dispute a payment in its current state")

    # Restore supplier capacity when payment is disputed (order blocked)
    dispute_bid = await db["bids"].find_one({"id": payment.get("bid_id")})
    dispute_rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
    if dispute_bid and dispute_rfq:
        await restore_capacity(dispute_bid.get("supplier_id", ""), dispute_rfq.get("quantity", 0))

        await db["payments"].update_one(
        {"payment_id": payload.payment_id},
        {
            "$set": {
                "status": EscrowStatusEnum.DISPUTED,
                "dispute_reason": payload.reason,
                "updated_at": datetime.utcnow(),
            }
        }
    )
    return {"success": True, "message": "Payment marked as DISPUTED"}


class SupplierOrderActionRequest(BaseModel):
    payment_id: str


@app.post("/api/order/start-work")
async def supplier_start_work(payload: SupplierOrderActionRequest, user: dict = Depends(require_login)):
    """Supplier marks order as Work In Progress."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    payment = await db["payments"].find_one({"payment_id": payload.payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")

    if payment.get("status") != "PAID_IN_ESCROW":
        raise HTTPException(status_code=400, detail="Order must be in escrow to start work")

    await db["payments"].update_one(
        {"payment_id": payload.payment_id},
        {"$set": {"status": "WORK_IN_PROGRESS", "updated_at": datetime.utcnow(), "work_started_at": datetime.utcnow()}}
    )
    return {"success": True, "message": "Order marked as Work In Progress"}


@app.post("/api/order/send-delivery")
async def supplier_send_delivery(payload: SupplierOrderActionRequest, user: dict = Depends(require_login)):
    """Supplier marks order as Sent for Delivery — triggers admin to release escrow."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    payment = await db["payments"].find_one({"payment_id": payload.payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")

    if payment.get("status") not in ["PAID_IN_ESCROW", "WORK_IN_PROGRESS"]:
        raise HTTPException(status_code=400, detail="Cannot mark delivery in current state")

    await db["payments"].update_one(
        {"payment_id": payload.payment_id},
        {"$set": {"status": "SENT_FOR_DELIVERY", "updated_at": datetime.utcnow(), "delivered_at": datetime.utcnow()}}
    )
    return {"success": True, "message": "Order marked as Sent for Delivery. Admin will release funds."}


# ----------------------------------------
# REVIEW SYSTEM ROUTES
# ----------------------------------------

class ReviewSubmissionRequest(BaseModel):
    transaction_id: str
    selected_tags: List[str]
    comment: Optional[str] = None


@app.post("/api/review/submit")
async def submit_review(payload: ReviewSubmissionRequest, user: dict = Depends(require_login)):
    """Submit a review for a completed transaction."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Get user's company to determine role
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        raise HTTPException(status_code=404, detail="User company not found")

    # Find the payment/transaction
    payment = await db["payments"].find_one({"transaction_id": payload.transaction_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Check if transaction is in a reviewable state (RELEASED)
    if payment.get("status") != "RELEASED":
        raise HTTPException(status_code=400, detail="Reviews can only be submitted for released transactions")

    # Get user role and determine reviewer/reviewee
    reviewer_id = user.get("id")
    reviewer_role = company.get("role", "").upper()
    
    # Get RFQ details to fetch company information
    rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    if reviewer_role == "BUYER":
        if payment.get("buyer_id") != reviewer_id:
            raise HTTPException(status_code=403, detail="You can only review your own transactions")
        reviewee_id = payment.get("supplier_id")
        # Get supplier company name from RFQ
        reviewee_company = rfq.get("supplier_company", "Unknown Supplier")
    elif reviewer_role == "SUPPLIER":
        # Check if supplier owns this transaction - supplier_id can be company unique_id or company id
        is_supplier_transaction = payment.get("supplier_id") == reviewer_id
        if not is_supplier_transaction:
            # Also check against company unique_id and company id
            is_supplier_transaction = (
                payment.get("supplier_id") == company.get("unique_id") or
                payment.get("supplier_id") == company.get("id")
            )
        
        if not is_supplier_transaction:
            raise HTTPException(status_code=403, detail="You can only review your own transactions")
        reviewee_id = payment.get("buyer_id")
        # Get buyer company name from RFQ
        reviewee_company = rfq.get("buyer_company", "Unknown Buyer")
    else:
        raise HTTPException(status_code=403, detail="Invalid user role for reviews")

    # Check if review already exists
    existing_review = await db["reviews"].find_one({
        "transaction_id": payload.transaction_id,
        "reviewer_id": reviewer_id
    })
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this transaction")

    # Validate tags based on reviewer role
    from models import ReviewTagEnum
    valid_tags = []
    if reviewer_role == "BUYER":
        buyer_tags = [ReviewTagEnum.ON_TIME_DELIVERY, ReviewTagEnum.GOOD_QUALITY, 
                     ReviewTagEnum.CLEAR_COMMUNICATION, ReviewTagEnum.LATE_DELIVERY, 
                     ReviewTagEnum.POOR_QUALITY]
        valid_tags = [tag.value for tag in buyer_tags]
    elif reviewer_role == "SUPPLIER":
        supplier_tags = [ReviewTagEnum.FAST_PAYMENT, ReviewTagEnum.CLEAR_REQUIREMENTS,
                        ReviewTagEnum.PROFESSIONAL_BEHAVIOR, ReviewTagEnum.LATE_PAYMENT,
                        ReviewTagEnum.UNCLEAR_INSTRUCTIONS]
        valid_tags = [tag.value for tag in supplier_tags]

    # Validate submitted tags
    for tag in payload.selected_tags:
        if tag not in valid_tags:
            raise HTTPException(status_code=400, detail=f"Invalid tag for {reviewer_role}: {tag}")

    # Create review
    from models import ReviewModel
    review = ReviewModel(
        transaction_id=payload.transaction_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        reviewer_role=reviewer_role,
        reviewee_company=reviewee_company,
        selected_tags=payload.selected_tags,
        comment=payload.comment
    )

    # Insert into database
    await db["reviews"].insert_one(review.dict())
    
    return {"success": True, "message": "Review submitted successfully"}


@app.get("/api/review/check/{transaction_id}")
async def check_review_status(transaction_id: str, user: dict = Depends(require_login)):
    """Check if user can review this transaction and get company info."""
    from database import db
    if db is None:
        return {"can_review": False, "reason": "Database not available"}

    # Get user's company to determine role
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        return {"can_review": False, "reason": "User company not found"}

    # Find the payment/transaction
    payment = await db["payments"].find_one({"transaction_id": transaction_id})
    if not payment:
        return {"can_review": False, "reason": "Transaction not found"}

    # Check if transaction is reviewable (RELEASED)
    if payment.get("status") != "RELEASED":
        return {"can_review": False, "reason": "Transaction not released"}

    # Check if user is part of this transaction
    user_id = user.get("id")
    user_role = company.get("role", "").upper()
    
    if user_role == "BUYER" and payment.get("buyer_id") != user_id:
        return {"can_review": False, "reason": "Not your transaction"}
    elif user_role == "SUPPLIER":
        # Check if supplier owns this transaction - supplier_id can be company unique_id or company id
        is_supplier_transaction = payment.get("supplier_id") == user_id
        if not is_supplier_transaction:
            # Also check against company unique_id and company id
            is_supplier_transaction = (
                payment.get("supplier_id") == company.get("unique_id") or
                payment.get("supplier_id") == company.get("id")
            )
        
        if not is_supplier_transaction:
            return {"can_review": False, "reason": "Not your transaction"}
    elif user_role not in ["BUYER", "SUPPLIER"]:
        return {"can_review": False, "reason": "Invalid role"}

    # Check if already reviewed
    existing_review = await db["reviews"].find_one({
        "transaction_id": transaction_id,
        "reviewer_id": user_id
    })
    
    if existing_review:
        return {"can_review": False, "reason": "Already reviewed"}

    # Get company information from RFQ
    rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
    company_name = "Unknown Company"
    if rfq:
        if user_role == "BUYER":
            company_name = rfq.get("supplier_company", "Unknown Supplier")
        else:
            company_name = rfq.get("buyer_company", "Unknown Buyer")

    return {
        "can_review": True, 
        "user_role": user_role,
        "company_name": company_name
    }


@app.get("/api/reviews/given")
async def get_given_reviews(user: dict = Depends(require_login)):
    """Get all reviews given by the current user."""
    from database import db
    if db is None:
        return {"reviews": []}

    user_id = user.get("id")
    reviews = []
    
    async for review in db["reviews"].find({"reviewer_id": user_id}).sort("created_at", -1):
        review["_id"] = str(review["_id"])
        # Convert datetime to string if needed
        if isinstance(review.get("created_at"), datetime):
            review["created_at"] = review["created_at"].isoformat()
        reviews.append(review)
    
    return {"reviews": reviews}


@app.get("/api/reviews/received")
async def get_received_reviews(user: dict = Depends(require_login)):
    """Get all reviews received by the current user."""
    from database import db
    if db is None:
        return {"reviews": []}

    # Get user's company to determine how to find received reviews
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        return {"reviews": []}

    user_id = user.get("id")
    user_role = company.get("role", "").upper()
    
    # Find reviews where this user is the reviewee
    # Need to check both user_id and company identifiers
    query = {"$or": [
        {"reviewee_id": user_id},
        {"reviewee_id": company.get("unique_id")},
        {"reviewee_id": company.get("id")}
    ]}
    
    reviews = []
    async for review in db["reviews"].find(query).sort("created_at", -1):
        review["_id"] = str(review["_id"])
        # Convert datetime to string if needed
        if isinstance(review.get("created_at"), datetime):
            review["created_at"] = review["created_at"].isoformat()
        
        # Get reviewer company name by looking up the reviewer's company
        reviewer_company_name = "Unknown Company"
        reviewer_user = await db["users"].find_one({"id": review.get("reviewer_id")})
        if reviewer_user:
            reviewer_company = await db["companies"].find_one({"id": reviewer_user.get("company_id")})
            if reviewer_company:
                reviewer_company_name = reviewer_company.get("name", "Unknown Company")
        
        review["reviewer_company"] = reviewer_company_name
        reviews.append(review)
    
    return {"reviews": reviews}


@app.get("/api/reviews/summary")
async def get_review_summary(user: dict = Depends(require_login)):
    """Get review summary statistics for the current user."""
    from database import db
    if db is None:
        return {"given_count": 0, "received_count": 0, "avg_rating": 0}

    # Get user's company
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        return {"given_count": 0, "received_count": 0, "avg_rating": 0}

    user_id = user.get("id")
    
    # Count given reviews
    given_count = await db["reviews"].count_documents({"reviewer_id": user_id})
    
    # Count received reviews
    received_query = {"$or": [
        {"reviewee_id": user_id},
        {"reviewee_id": company.get("unique_id")},
        {"reviewee_id": company.get("id")}
    ]}
    received_count = await db["reviews"].count_documents(received_query)
    
    # Calculate positive review percentage (as a simple rating metric)
    received_reviews = await db["reviews"].find(received_query).to_list(length=None)
    positive_tags = ["On-time Delivery", "Good Quality", "Clear Communication", 
                    "Fast Payment", "Clear Requirements", "Professional Behavior"]
    
    total_tags = 0
    positive_tag_count = 0
    
    for review in received_reviews:
        tags = review.get("selected_tags", [])
        total_tags += len(tags)
        positive_tag_count += len([tag for tag in tags if tag in positive_tags])
    
    avg_rating = (positive_tag_count / total_tags * 100) if total_tags > 0 else 0
    
    return {
        "given_count": given_count,
        "received_count": received_count,
        "avg_rating": round(avg_rating, 1)
    }


@app.get("/reviews", response_class=HTMLResponse)
async def reviews_page(request: Request, user: dict = Depends(require_login)):
    """Display user's review tracking page."""
    return templates.TemplateResponse("reviews.html", {"request": request, "user": user})
async def list_payments(user: dict = Depends(require_login)):
    """List payments — admins see all, buyers see their own."""
    from database import db
    if db is None:
        return {"payments": []}

    query = {} if user.get("is_admin") else {"buyer_id": user.get("id")}
    payments = []
    async for payment in db["payments"].find(query).sort("created_at", -1):
        payment["_id"] = str(payment["_id"])
        # Serialize datetimes
        for key in ("created_at", "updated_at", "confirmed_at"):
            if isinstance(payment.get(key), datetime):
                payment[key] = payment[key].isoformat() + "Z"
        payments.append(payment)
    return {"payments": payments}



# ============================================================
# MILESTONE TRACKING TIMELINE
# ============================================================
# Collection: order_milestones
# Fields: order_id, payment_id, supplier_id, buyer_id,
#         current_stage, stages: [{name, status, timestamp}]
# ============================================================

MILESTONE_STAGES = [
    "Order Placed",
    "Fabric Sourcing",
    "Cutting",
    "Sewing",
    "Finishing",
    "Shipping",
]


def build_initial_milestones(order_id: str, payment_id: str, supplier_id: str, buyer_id: str) -> dict:
    """Create a fresh milestone document with all stages pending."""
    import uuid as _uuid
    now = datetime.utcnow()
    stages = []
    for i, name in enumerate(MILESTONE_STAGES):
        stages.append({
            "name": name,
            "status": "completed" if i == 0 else "pending",
            "timestamp": now.isoformat() + "Z" if i == 0 else None,
        })
    return {
        "id": str(_uuid.uuid4()),
        "order_id": order_id,
        "payment_id": payment_id,
        "supplier_id": supplier_id,
        "buyer_id": buyer_id,
        "current_stage": "Order Placed",
        "stages": stages,
        "created_at": now,
        "updated_at": now,
    }


@app.post("/milestones/create")
async def create_milestone(order_id: str, payment_id: str, user: dict = Depends(require_login)):
    """Manually create a milestone record for an order (auto-created on payment success)."""
    from database import db
    import uuid as _uuid
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    existing = await db["order_milestones"].find_one({"order_id": order_id})
    if existing:
        existing.pop("_id", None)
        if isinstance(existing.get("created_at"), datetime):
            existing["created_at"] = existing["created_at"].isoformat() + "Z"
        if isinstance(existing.get("updated_at"), datetime):
            existing["updated_at"] = existing["updated_at"].isoformat() + "Z"
        return {"success": True, "milestone": existing, "created": False}

    payment = await db["payments"].find_one({"payment_id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    doc = build_initial_milestones(
        order_id=order_id,
        payment_id=payment_id,
        supplier_id=payment.get("supplier_id", ""),
        buyer_id=payment.get("buyer_id", ""),
    )
    await db["order_milestones"].insert_one(doc)
    doc.pop("_id", None)
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat() + "Z"
    if isinstance(doc.get("updated_at"), datetime):
        doc["updated_at"] = doc["updated_at"].isoformat() + "Z"
    return {"success": True, "milestone": doc, "created": True}


class MilestoneUpdateRequest(BaseModel):
    order_id: str
    stage_name: str  # Must be one of MILESTONE_STAGES


@app.put("/milestones/update")
async def update_milestone(payload: MilestoneUpdateRequest, user: dict = Depends(require_login)):
    """
    Supplier updates the current production stage.
    Marks the stage as in-progress, previous stages as completed.
    """
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    if payload.stage_name not in MILESTONE_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {MILESTONE_STAGES}")

    doc = await db["order_milestones"].find_one({"order_id": payload.order_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Milestone record not found for this order")

    # Verify caller is the supplier
    company = await db["companies"].find_one({"id": user.get("company_id")})
    supplier_ids = {user.get("id"), user.get("company_id")}
    if company:
        supplier_ids.add(company.get("id"))
        supplier_ids.add(company.get("unique_id"))
    supplier_ids.discard(None)

    if doc.get("supplier_id") not in supplier_ids and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only the supplier of this order can update milestones")

    stage_idx = MILESTONE_STAGES.index(payload.stage_name)
    now = datetime.utcnow()
    updated_stages = []
    for i, stage in enumerate(doc.get("stages", [])):
        s = dict(stage)
        if i < stage_idx:
            s["status"] = "completed"
            if not s.get("timestamp"):
                s["timestamp"] = now.isoformat() + "Z"
        elif i == stage_idx:
            s["status"] = "in-progress"
            s["timestamp"] = now.isoformat() + "Z"
        else:
            s["status"] = "pending"
            s["timestamp"] = None
        updated_stages.append(s)

    await db["order_milestones"].update_one(
        {"order_id": payload.order_id},
        {"$set": {
            "current_stage": payload.stage_name,
            "stages": updated_stages,
            "updated_at": now,
        }}
    )

    # Notify buyer of stage update
    import uuid as _uuid
    buyer_user = await db["users"].find_one({"id": doc.get("buyer_id")})
    if buyer_user:
        await db["notifications"].insert_one({
            "id": str(_uuid.uuid4()),
            "user_id": buyer_user.get("id"),
            "type": "bid_submitted",
            "title": f"Order Update: {payload.stage_name}",
            "message": f"Your order has reached the '{payload.stage_name}' stage.",
            "is_read": False,
            "created_at": now,
            "related_id": payload.order_id,
        })

    return {"success": True, "current_stage": payload.stage_name, "updated_at": now.isoformat() + "Z"}


@app.get("/milestones/{order_id}")
async def get_milestone(order_id: str, user: dict = Depends(require_login)):
    """Get milestone data for an order."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    doc = await db["order_milestones"].find_one({"order_id": order_id})
    if not doc:
        return {"success": True, "found": False, "order_id": order_id}

    doc.pop("_id", None)
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat() + "Z"
    if isinstance(doc.get("updated_at"), datetime):
        doc["updated_at"] = doc["updated_at"].isoformat() + "Z"

    return {"success": True, "found": True, "milestone": doc}


@app.get("/escrow/tracker/{payment_id}", response_class=HTMLResponse)
async def escrow_tracker_page(request: Request, payment_id: str, user: dict = Depends(require_login)):
    """Visual escrow progress tracker for a specific payment."""
    from database import db
    payment = None
    rfq = None
    if db is not None:
        payment = await db["payments"].find_one({"payment_id": payment_id})
        if payment:
            rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Only the buyer, supplier, or admin can view the tracker
    # supplier_id in payment may be company unique_id or company id — check all
    is_buyer = payment.get("buyer_id") == user.get("id")
    is_supplier = payment.get("supplier_id") == user.get("id")
    if not is_supplier and db is not None:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            is_supplier = (
                payment.get("supplier_id") == company.get("unique_id") or
                payment.get("supplier_id") == company.get("id")
            )
    if not (is_buyer or is_supplier or user.get("is_admin")):
        raise HTTPException(status_code=403, detail="Access denied")

    # Fetch milestone data
    milestone = None
    if db is not None and payment:
        ms_doc = await db["order_milestones"].find_one({"order_id": payment.get("order_id")})
        if ms_doc:
            ms_doc.pop("_id", None)
            if isinstance(ms_doc.get("created_at"), datetime):
                ms_doc["created_at"] = ms_doc["created_at"].isoformat() + "Z"
            if isinstance(ms_doc.get("updated_at"), datetime):
                ms_doc["updated_at"] = ms_doc["updated_at"].isoformat() + "Z"
            milestone = ms_doc

    return templates.TemplateResponse("escrow_tracker.html", {
        "request": request,
        "user": user,
        "payment": payment,
        "rfq": rfq,
        "is_buyer": is_buyer,
        "is_supplier": is_supplier,
        "milestone": milestone,
        "milestone_stages": MILESTONE_STAGES,
    })


# New frontend routes for dashboards
@app.get("/buyer/checkout/{rfq_id}/{bid_id}", response_class=HTMLResponse)
async def buyer_checkout_page(request: Request, rfq_id: str, bid_id: str, user: dict = Depends(require_login)):
    """Redirect to the new payment gateway page."""
    return RedirectResponse(url=f"/payment/gateway?rfq_id={rfq_id}&bid_id={bid_id}", status_code=303)


@app.get("/api/user/role")
async def get_user_role(user: dict = Depends(require_login)):
    """Get the current user's company role."""
    from database import db
    
    if db is None:
        return {"role": "BUYER"}  # Default
    
    company = await db["companies"].find_one({"id": user.get("company_id")})
    if company:
        return {"role": company.get("role", "BUYER").upper()}
    
    return {"role": "BUYER"}  # Default


@app.get("/supplier/orders", response_class=HTMLResponse)
async def supplier_orders_page(request: Request, user: dict = Depends(require_login)):
    """Supplier orders page - shows all orders/payments for the supplier."""
    from database import db
    
    orders = []
    if db is not None:
        # Get supplier's company
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            supplier_id = company.get("unique_id") or company.get("id")
            
            # Fetch all payments where this supplier is the recipient
            async for payment in db["payments"].find({"supplier_id": supplier_id}).sort("created_at", -1):
                payment["_id"] = str(payment["_id"])
                
                # Fetch associated bid and RFQ for additional details
                bid = await db["bids"].find_one({"id": payment.get("bid_id")})
                rfq = await db["rfqs"].find_one({"id": payment.get("order_id")})
                
                # Add additional context to payment
                if bid:
                    payment["bid_price"] = bid.get("bid_price")
                    payment["delivery_time_days"] = bid.get("delivery_time_days")
                if rfq:
                    payment["rfq_title"] = rfq.get("title")
                    payment["quantity"] = rfq.get("quantity")
                    payment["buyer_company"] = rfq.get("buyer_company")
                
                payment["source"] = "payment"
                orders.append(payment)
            
            # Also fetch ALL contracts where supplier is involved (regardless of bid status)
            async for contract in db["contracts"].find({
                "supplier_id": supplier_id,
                "status": "FULLY_EXECUTED"
            }).sort("executed_at", -1):
                # Check if we already have this as a payment
                payment_exists = await db["payments"].find_one({
                    "bid_id": contract.get("bid_id"),
                    "supplier_id": supplier_id
                })
                
                # Only add if no payment exists yet
                if not payment_exists:
                    bid = await db["bids"].find_one({"id": contract.get("bid_id")})
                    rfq = await db["rfqs"].find_one({"id": contract.get("rfq_id")})
                    
                    if bid and rfq:
                        # Create an order object from the bid and contract
                        order = {
                            "_id": str(contract.get("_id")),
                            "contract_id": contract.get("contract_id"),
                            "order_id": contract.get("rfq_id"),
                            "bid_id": contract.get("bid_id"),
                            "transaction_id": f"CONTRACT-{contract.get('contract_id')[:8]}",
                            "bid_price": bid.get("bid_price"),
                            "delivery_time_days": bid.get("delivery_time_days"),
                            "original_amount": bid.get("bid_price") * rfq.get("quantity", 1),
                            "original_currency": "BDT",
                            "base_amount_usd": bid.get("bid_price") * rfq.get("quantity", 1) / 110,  # Approximate conversion
                            "exchange_rate": 110.0,
                            "status": "AWAITING_PAYMENT",
                            "created_at": contract.get("executed_at") or contract.get("created_at"),
                            "rfq_title": rfq.get("title"),
                            "quantity": rfq.get("quantity"),
                            "buyer_company": rfq.get("buyer_company"),
                            "source": "contract"
                        }
                        orders.append(order)
            
            # Sort all orders by created_at
            orders.sort(key=lambda x: x.get("created_at") or datetime.min, reverse=True)
    
    return templates.TemplateResponse("supplier_orders.html", {
        "request": request,
        "user": user,
        "orders": orders
    })


@app.get("/buyer/orders", response_class=HTMLResponse)
async def buyer_orders_page(request: Request, user: dict = Depends(require_login)):
    from database import db
    orders = []
    if db is not None:
        async for order in db["payments"].find({"buyer_id": user.get("id")}).sort("created_at", -1):
            order["_id"] = str(order["_id"])
            orders.append(order)
    return templates.TemplateResponse("buyer_orders.html", {"request": request, "user": user, "orders": orders})


@app.get("/admin/escrow", response_class=HTMLResponse)
async def admin_escrow_page(request: Request, admin: dict = Depends(require_admin)):
    return templates.TemplateResponse("admin_escrow.html", {"request": request, "user": admin})


# ----------------------------------------
# SHIPPING & INCOTERMS CALCULATOR ROUTES
# ----------------------------------------

@app.get("/api/shipping/ports")
async def get_ports():
    """Return all seeded ports for the shipping calculator dropdowns."""
    from database import db
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=500)
    
    ports = await db["ports"].find({}).sort("name", 1).to_list(length=500)
    for p in ports:
        p.pop("_id", None)
    return {"success": True, "ports": ports}


@app.get("/api/shipping/incoterms")
async def get_incoterms():
    """Return all supported Incoterms with descriptions and responsibility breakdowns."""
    result = []
    for code, data in INCOTERMS_DATA.items():
        result.append({
            "code": code,
            "name": data["name"],
            "description": data["description"],
            "seller_pays": data["seller_pays"],
            "buyer_pays": data["buyer_pays"],
        })
    return {"success": True, "incoterms": result}


@app.get("/api/shipping/rfq/{rfq_id}")
async def calculate_shipping_for_rfq(
    rfq_id: str,
    origin_port_code: str,
    user: dict = Depends(require_login)
):
    """
    Calculate shipping for a specific RFQ using its locked parameters.
    Only the origin port (supplier's loading port) is variable.
    Everything else — incoterm, shipping method, destination, quantity — is fixed from the RFQ.
    """
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    rfq = await db["rfqs"].find_one({"id": rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Map RFQ shipping method to calculator enum
    raw_method = (rfq.get("shipping_method") or "Sea").upper()
    method_map = {
        "SEA": "SEA", "SEA FREIGHT": "SEA", "OCEAN": "SEA",
        "AIR": "AIR", "AIR FREIGHT": "AIR",
        "LAND": "ROAD", "LAND/RAIL": "ROAD", "ROAD": "ROAD", "RAIL": "ROAD",
    }
    shipping_method = method_map.get(raw_method, "SEA")

    # Map incoterm
    incoterm_raw = (rfq.get("incoterm") or rfq.get("incoterms") or "FOB").upper()
    incoterm_map = {"FOB": "FOB", "CIF": "CIF", "CFR": "CFR", "EXW": "EXW", "DAP": "DAP", "DDP": "DDP"}
    incoterm = incoterm_map.get(incoterm_raw, "FOB")

    # Build a ShippingCalculateRequest using RFQ locked params
    try:
        payload = ShippingCalculateRequest(
            rfq_id=rfq_id,
            origin_port_code=origin_port_code.upper(),
            dest_port_code=rfq.get("destination_port", "NLRTM"),
            shipping_method=ShippingMethodEnum(shipping_method),
            incoterm=IncotermEnum(incoterm),
            quantity=rfq.get("quantity", 1),
            goods_value_usd=0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid parameters: {e}")

    # Reuse the main calculate function logic inline
    cfg = await db["shipping_config"].find_one({"_id": "global"}) or {}
    insurance_rate   = float(cfg.get("insurance_rate", 0.003))
    import_duty_rate = float(cfg.get("import_duty_rate", 0.12))
    port_fees = {"SEA": float(cfg.get("port_fee_sea", 320.0)), "AIR": float(cfg.get("port_fee_air", 180.0)), "ROAD": float(cfg.get("port_fee_road", 90.0))}
    routing_factors = {"SEA": float(cfg.get("routing_factor_sea", 1.2)), "AIR": float(cfg.get("routing_factor_air", 1.05)), "ROAD": float(cfg.get("routing_factor_road", 1.3))}
    speeds = {"SEA": float(cfg.get("speed_sea_kmh", 37.0)), "AIR": float(cfg.get("speed_air_kmh", 800.0)), "ROAD": float(cfg.get("speed_road_kmh", 60.0))}
    handling_days = {"SEA": float(cfg.get("handling_days_sea", 4.0)), "AIR": float(cfg.get("handling_days_air", 1.5)), "ROAD": float(cfg.get("handling_days_road", 2.0))}
    min_freight = {"SEA": float(cfg.get("min_freight_sea", 150.0)), "AIR": float(cfg.get("min_freight_air", 80.0)), "ROAD": float(cfg.get("min_freight_road", 50.0))}
    max_freight = {"SEA": float(cfg.get("max_freight_sea", 50000.0)), "AIR": float(cfg.get("max_freight_air", 30000.0)), "ROAD": float(cfg.get("max_freight_road", 20000.0))}

    origin = await db["ports"].find_one({"code": payload.origin_port_code})
    if not origin:
        # Try name match
        origin = await db["ports"].find_one({"name": {"$regex": payload.origin_port_code, "$options": "i"}})
    if not origin:
        raise HTTPException(status_code=404, detail=f"Origin port '{payload.origin_port_code}' not found. Please select from the dropdown.")

    dest_code = payload.dest_port_code.upper()
    dest = await db["ports"].find_one({"code": dest_code})
    if not dest:
        # Try name match for destination
        dest_name = rfq.get("destination_port", "")
        dest = await db["ports"].find_one({"name": {"$regex": dest_name[:6], "$options": "i"}}) if dest_name else None
    if not dest:
        raise HTTPException(status_code=404, detail=f"Destination port '{payload.dest_port_code}' not found in port database.")

    incoterm_info = INCOTERMS_DATA.get(incoterm)
    if not incoterm_info:
        raise HTTPException(status_code=422, detail=f"Unsupported Incoterm: {incoterm}")

    origin_region = origin["region"]
    dest_region   = dest["region"]
    method        = shipping_method

    rate_doc = await db["shipping_rates"].find_one({"origin_region": origin_region, "dest_region": dest_region, "method": method})
    base_rate_per_kg = float(rate_doc["base_rate_per_kg"]) if rate_doc else next(
        (float(r["base_rate_per_kg"]) for r in DEFAULT_RATES if r["origin_region"] == origin_region and r["method"] == method), 2.0
    )

    weight_kg = payload.quantity * 0.3
    distance_factor = float(dest.get("distance_factor", 1.0))
    effective_factor = distance_factor * routing_factors.get(method, 1.0)
    raw_freight = base_rate_per_kg * weight_kg * effective_factor
    base_freight = max(min_freight.get(method, 0), min(max_freight.get(method, 999999), raw_freight))
    insurance_cost = base_freight * insurance_rate
    port_fee = port_fees.get(method, 320.0)
    duties_cost = 0.0

    if incoterm == "EXW":
        total_seller = 0.0; total_buyer = base_freight + insurance_cost + port_fee + duties_cost
    elif incoterm == "FOB":
        total_seller = base_freight * 0.15 + port_fee; total_buyer = base_freight * 0.85 + insurance_cost + duties_cost
    elif incoterm == "CFR":
        total_seller = base_freight + port_fee; total_buyer = insurance_cost + duties_cost
    elif incoterm == "CIF":
        total_seller = base_freight + insurance_cost + port_fee; total_buyer = duties_cost
    elif incoterm == "DAP":
        total_seller = base_freight + insurance_cost + port_fee; total_buyer = duties_cost
    elif incoterm == "DDP":
        total_seller = base_freight + insurance_cost + port_fee + duties_cost; total_buyer = 0.0
    else:
        total_seller = base_freight + insurance_cost + port_fee; total_buyer = 0.0

    grand_total = total_seller + total_buyer
    approx_km = distance_factor * 2500
    transit_time = (approx_km / speeds.get(method, 37.0)) / 24 + handling_days.get(method, 4.0)
    estimated_days = max(1, math.ceil(transit_time))

    return {
        "success": True,
        "rfq_id": rfq_id,
        "rfq_title": rfq.get("title", ""),
        "locked_params": {
            "incoterm": incoterm,
            "shipping_method": method,
            "destination_port": rfq.get("destination_port", ""),
            "quantity": payload.quantity,
        },
        "incoterm": incoterm,
        "incoterm_name": incoterm_info["name"],
        "incoterm_description": incoterm_info["description"],
        "seller_pays": incoterm_info["seller_pays"],
        "buyer_pays": incoterm_info["buyer_pays"],
        "breakdown": {
            "base_freight_usd": round(base_freight, 2),
            "insurance_usd": round(insurance_cost, 2),
            "handling_usd": round(port_fee, 2),
            "duties_usd": round(duties_cost, 2),
            "total_seller_usd": round(total_seller, 2),
            "total_buyer_usd": round(total_buyer, 2),
            "grand_total_usd": round(grand_total, 2),
        },
        "origin_port": f"{origin['name']}, {origin['country']}",
        "dest_port": f"{dest['name']}, {dest['country']}",
        "shipping_method": method,
        "weight_kg": round(weight_kg, 1),
        "estimated_days": estimated_days,
    }


@app.post("/api/shipping/calculate")
async def calculate_shipping(
    payload: ShippingCalculateRequest,
    user: dict = Depends(require_login)
):
    """Calculate estimated shipping cost using admin-managed config from DB."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Load global config (admin-managed)
    cfg = await db["shipping_config"].find_one({"_id": "global"}) or {}

    # Config values with fallbacks to defaults
    insurance_rate      = float(cfg.get("insurance_rate", 0.003))
    import_duty_rate    = float(cfg.get("import_duty_rate", 0.12))

    port_fees = {
        "SEA":  float(cfg.get("port_fee_sea", 320.0)),
        "AIR":  float(cfg.get("port_fee_air", 180.0)),
        "ROAD": float(cfg.get("port_fee_road", 90.0)),
    }
    routing_factors = {
        "SEA":  float(cfg.get("routing_factor_sea", 1.2)),
        "AIR":  float(cfg.get("routing_factor_air", 1.05)),
        "ROAD": float(cfg.get("routing_factor_road", 1.3)),
    }
    speeds = {
        "SEA":  float(cfg.get("speed_sea_kmh", 37.0)),
        "AIR":  float(cfg.get("speed_air_kmh", 800.0)),
        "ROAD": float(cfg.get("speed_road_kmh", 60.0)),
    }
    handling_days = {
        "SEA":  float(cfg.get("handling_days_sea", 4.0)),
        "AIR":  float(cfg.get("handling_days_air", 1.5)),
        "ROAD": float(cfg.get("handling_days_road", 2.0)),
    }
    min_freight = {
        "SEA":  float(cfg.get("min_freight_sea", 150.0)),
        "AIR":  float(cfg.get("min_freight_air", 80.0)),
        "ROAD": float(cfg.get("min_freight_road", 50.0)),
    }
    max_freight = {
        "SEA":  float(cfg.get("max_freight_sea", 50000.0)),
        "AIR":  float(cfg.get("max_freight_air", 30000.0)),
        "ROAD": float(cfg.get("max_freight_road", 20000.0)),
    }
    air_zone_short_km   = float(cfg.get("air_zone_short_max_km", 3000.0))
    air_zone_mid_km     = float(cfg.get("air_zone_mid_max_km", 8000.0))
    air_short_mult      = float(cfg.get("air_zone_short_multiplier", 1.0))
    air_mid_mult        = float(cfg.get("air_zone_mid_multiplier", 1.2))
    air_long_mult       = float(cfg.get("air_zone_long_multiplier", 1.5))

    # Look up ports
    origin = await db["ports"].find_one({"code": payload.origin_port_code.upper()})
    if not origin:
        raise HTTPException(status_code=404, detail=f"Origin port '{payload.origin_port_code}' not found")
    dest = await db["ports"].find_one({"code": payload.dest_port_code.upper()})
    if not dest:
        raise HTTPException(status_code=404, detail=f"Destination port '{payload.dest_port_code}' not found")

    incoterm_code = payload.incoterm.value
    incoterm_info = INCOTERMS_DATA.get(incoterm_code)
    if not incoterm_info:
        raise HTTPException(status_code=422, detail=f"Unsupported Incoterm: {incoterm_code}")

    origin_region = origin["region"]
    dest_region   = dest["region"]
    method        = payload.shipping_method.value

    # Look up base rate from DB
    rate_doc = await db["shipping_rates"].find_one({
        "origin_region": origin_region,
        "dest_region": dest_region,
        "method": method,
    })
    if rate_doc:
        base_rate_per_kg = float(rate_doc["base_rate_per_kg"])
    else:
        fallback = next(
            (r for r in DEFAULT_RATES if r["origin_region"] == origin_region and r["method"] == method),
            None
        )
        base_rate_per_kg = float(fallback["base_rate_per_kg"]) if fallback else 2.0

    # Weight estimation (avg garment = 0.3 kg)
    weight_kg = payload.quantity * 0.3

    # Distance factor from port document
    distance_factor = float(dest.get("distance_factor", 1.0))

    # Apply routing factor (admin-configurable)
    effective_factor = distance_factor * routing_factors.get(method, 1.0)

    # Air freight zone multiplier based on distance factor proxy
    air_zone_mult = 1.0
    if method == "AIR":
        # Use distance_factor as a proxy for distance (1.0=short, 2.5=mid, 3.5+=long)
        approx_km = distance_factor * 2500  # rough km estimate
        if approx_km <= air_zone_short_km:
            air_zone_mult = air_short_mult
        elif approx_km <= air_zone_mid_km:
            air_zone_mult = air_mid_mult
        else:
            air_zone_mult = air_long_mult
        effective_factor *= air_zone_mult

    # Base freight calculation
    raw_freight = base_rate_per_kg * weight_kg * effective_factor

    # Apply min/max thresholds (admin-configurable)
    base_freight = max(min_freight.get(method, 0), min(max_freight.get(method, 999999), raw_freight))

    # Insurance and port fees from config
    insurance_cost = base_freight * insurance_rate
    port_fee       = port_fees.get(method, 320.0)

    # Duties estimate (only for DDP)
    goods_value  = payload.goods_value_usd or 0.0
    duties_cost  = 0.0
    if incoterm_info["includes_duties"] and goods_value > 0:
        duties_cost = goods_value * import_duty_rate

    # Incoterm cost split
    if incoterm_code == "EXW":
        total_seller = 0.0
        total_buyer  = base_freight + insurance_cost + port_fee + duties_cost
    elif incoterm_code == "FOB":
        total_seller = base_freight * 0.15 + port_fee
        total_buyer  = base_freight * 0.85 + insurance_cost + duties_cost
    elif incoterm_code == "CFR":
        total_seller = base_freight + port_fee
        total_buyer  = insurance_cost + duties_cost
    elif incoterm_code == "CIF":
        total_seller = base_freight + insurance_cost + port_fee
        total_buyer  = duties_cost
    elif incoterm_code == "DAP":
        total_seller = base_freight + insurance_cost + port_fee
        total_buyer  = duties_cost
    elif incoterm_code == "DDP":
        total_seller = base_freight + insurance_cost + port_fee + duties_cost
        total_buyer  = 0.0
    else:
        total_seller = base_freight + insurance_cost + port_fee
        total_buyer  = 0.0

    grand_total = total_seller + total_buyer

    # Transit time using admin-configurable speeds and handling days
    speed        = speeds.get(method, 37.0)
    h_days       = handling_days.get(method, 4.0)
    approx_km    = distance_factor * 2500
    transit_time = (approx_km / speed) / 24 + h_days  # hours → days
    estimated_days = max(1, math.ceil(transit_time))

    return {
        "success": True,
        "incoterm": incoterm_code,
        "incoterm_name": incoterm_info["name"],
        "incoterm_description": incoterm_info["description"],
        "seller_pays": incoterm_info["seller_pays"],
        "buyer_pays": incoterm_info["buyer_pays"],
        "breakdown": {
            "base_freight_usd": round(base_freight, 2),
            "insurance_usd": round(insurance_cost, 2),
            "handling_usd": round(port_fee, 2),
            "duties_usd": round(duties_cost, 2),
            "total_seller_usd": round(total_seller, 2),
            "total_buyer_usd": round(total_buyer, 2),
            "grand_total_usd": round(grand_total, 2),
        },
        "origin_port": f"{origin['name']}, {origin['country']}",
        "dest_port": f"{dest['name']}, {dest['country']}",
        "shipping_method": method,
        "weight_kg": round(weight_kg, 1),
        "estimated_days": estimated_days,
        # Expose config used so admin can verify
        "config_used": {
            "insurance_rate_pct": round(insurance_rate * 100, 2),
            "port_fee_usd": round(port_fee, 2),
            "routing_factor": routing_factors.get(method, 1.0),
            "min_freight_usd": min_freight.get(method, 0),
            "max_freight_usd": max_freight.get(method, 999999),
        },
    }






# ----------------------------------------
# CONTRACT GENERATOR ROUTES
# ----------------------------------------
import hashlib as _hashlib


def _build_contract_text(c: dict) -> str:
    """Build the plain-text contract body used for hashing and display."""
    lines = [
        f"CONTRACT AGREEMENT",
        f"Contract No: {c['contract_id']}",
        f"Date: {c['created_at']}",
        "",
        "1. PARTIES",
        f"Buyer:    {c['buyer_legal_name']} ({c['buyer_email']})",
        f"Supplier: {c['supplier_legal_name']} ({c['supplier_email']})",
        "",
        "2. ORDER DETAILS",
        f"Product:     {c['rfq_title']} — {c['rfq_product_category']}",
        f"Fabric:      {c['rfq_fabric_type']}",
        f"Quantity:    {c['rfq_quantity']:,} units",
        f"Unit Price:  BDT {c['bid_price']:,.2f}",
        f"Total Value: BDT {c['bid_total_value']:,.2f}",
        "",
        "3. DELIVERY TERMS",
        f"Incoterm:         {c['rfq_incoterm']}",
        f"Shipping Method:  {c['rfq_shipping_method'] or 'TBD'}",
        f"Destination Port: {c['rfq_destination_port'] or 'TBD'}",
        "",
        "4. SAMPLE REQUIREMENTS",
        f"Proto Sample Required:      {'Yes' if c['rfq_proto_sample_req'] else 'No'}",
        f"Pre-Production Sample Req:  {'Yes' if c['rfq_pp_sample_req'] else 'No'}",
        "Sample Approval Process:    Digital approval/rejection via TexBid platform",
        "",
        "5. PAYMENT & ESCROW CONDITIONS",
        "- Buyer deposits full order value into TexBid escrow before production begins.",
        "- Funds are held by TexBid and released to supplier only after:",
        "  a) Buyer confirms receipt of goods, OR",
        "  b) Admin verifies delivery completion in case of dispute.",
        "- Partial payment release is permitted at milestone completion.",
        "",
        "6. DISPUTE RESOLUTION",
        "6.1 Refund Clause: If the supplier fails to deliver within the agreed deadline,",
        "    the buyer is entitled to a full or partial refund from escrow.",
        "6.2 Partial Payment Clause: If goods are partially delivered or defective,",
        "    escrow is split proportionally based on evidence submitted by both parties.",
        "6.3 Re-shipment Clause: If goods are rejected due to quality failure, the supplier",
        "    must re-ship conforming goods at their own cost, or a refund is triggered.",
        "6.4 Contract Enforcement Clause: Both parties agree this contract is legally binding.",
        "    TexBid reserves the right to freeze escrow funds and escalate to legal enforcement.",
        "",
        "7. CONFIDENTIALITY",
        "Both parties agree to keep pricing, product specifications, and communication",
        "confidential and not disclose to third parties without written consent.",
        "",
        "8. FORCE MAJEURE",
        "Neither party is liable for delays caused by events beyond reasonable control",
        "including natural disasters, pandemics, port strikes, or government restrictions.",
        "",
        "9. SPECIAL INSTRUCTIONS",
        c.get("rfq_special_instructions") or "None",
        "",
        "10. SIGNATURES",
        f"Buyer Signature:    {'[SIGNED]' if c.get('buyer_signed_at') else '[PENDING]'}",
        f"  Signed by: {c.get('buyer_legal_name', '')}",
        f"  Date: {c.get('buyer_signed_at') or '___________'}",
        "",
        f"Supplier Signature: {'[SIGNED]' if c.get('supplier_signed_at') else '[PENDING]'}",
        f"  Signed by: {c.get('supplier_legal_name', '')}",
        f"  Date: {c.get('supplier_signed_at') or '___________'}",
        "",
        f"Platform Verified: TexBid  |  Contract ID: {c['contract_id']}",
    ]
    return "\n".join(lines)


class GenerateContractRequest(BaseModel):
    rfq_id: str
    bid_id: str
    payment_id: Optional[str] = None


@app.post("/api/contracts/generate")
async def generate_contract(payload: GenerateContractRequest, user: dict = Depends(require_login)):
    """Generate a contract from an accepted bid. Only the buyer of the RFQ can generate."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Load RFQ
    rfq = await db["rfqs"].find_one({"id": payload.rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Load bid
    bid = await db["bids"].find_one({"id": payload.bid_id})
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Verify caller is the buyer
    buyer_company = await db["companies"].find_one({"id": user.get("company_id")})
    is_buyer = (
        rfq.get("buyer_id") == user.get("id") or
        rfq.get("buyer_id") == user.get("company_id") or
        (buyer_company and rfq.get("buyer_id") == buyer_company.get("id")) or
        (buyer_company and rfq.get("buyer_id") == buyer_company.get("unique_id"))
    )
    if not is_buyer:
        raise HTTPException(status_code=403, detail="Only the buyer of this RFQ can generate a contract")

    # Check if contract already exists for this bid
    existing = await db["contracts"].find_one({"rfq_id": payload.rfq_id, "bid_id": payload.bid_id})
    if existing:
        existing.pop("_id", None)
        return {"success": True, "contract_id": existing["contract_id"], "already_exists": True}

    # Load supplier company
    supplier_company = await db["companies"].find_one({
        "$or": [
            {"unique_id": bid.get("supplier_id")},
            {"id": bid.get("supplier_id")},
        ]
    })
    supplier_user = await db["users"].find_one({"company_id": supplier_company.get("id")}) if supplier_company else None

    # Build contract document
    quantity = rfq.get("quantity", 0)
    bid_price = bid.get("bid_price", 0.0)
    total_value = bid_price * quantity

    contract_data = {
        "rfq_id": payload.rfq_id,
        "bid_id": payload.bid_id,
        "payment_id": payload.payment_id,
        "buyer_id": user.get("id"),
        "supplier_id": bid.get("supplier_id"),
        "rfq_title": rfq.get("title", "Untitled RFQ"),
        "rfq_product_category": rfq.get("product_category", ""),
        "rfq_quantity": quantity,
        "rfq_incoterm": rfq.get("incoterm") or rfq.get("incoterms") or "FOB",
        "rfq_shipping_method": rfq.get("shipping_method") or "",
        "rfq_destination_port": rfq.get("destination_port") or "",
        "rfq_proto_sample_req": rfq.get("proto_sample_req", False),
        "rfq_pp_sample_req": rfq.get("pp_sample_req", False),
        "rfq_fabric_type": rfq.get("fabric_type", ""),
        "rfq_special_instructions": rfq.get("special_instructions") or "",
        "bid_price": bid_price,
        "bid_total_value": total_value,
        "bid_supplier_name": bid.get("supplier_name", ""),
        "buyer_legal_name": buyer_company.get("name", user.get("email", "")) if buyer_company else user.get("email", ""),
        "buyer_email": user.get("email", ""),
        "supplier_legal_name": supplier_company.get("name", bid.get("supplier_name", "")) if supplier_company else bid.get("supplier_name", ""),
        "supplier_email": supplier_user.get("email", "") if supplier_user else "",
        "buyer_signed_at": None,
        "buyer_signed_by": None,
        "supplier_signed_at": None,
        "supplier_signed_by": None,
        "status": ContractStatusEnum.PENDING_BUYER_SIGNATURE,
        "created_at": datetime.utcnow(),
        "executed_at": None,
    }

    # Generate contract ID
    import uuid as _uuid
    contract_id = f"TXB-{_uuid.uuid4().hex[:8].upper()}"
    contract_data["contract_id"] = contract_id

    # Hash the contract content for tamper detection
    contract_text = _build_contract_text(contract_data)
    content_hash = _hashlib.sha256(contract_text.encode()).hexdigest()
    contract_data["content_hash"] = content_hash

    await db["contracts"].insert_one(contract_data)

    # Notify buyer that contract is ready to sign
    await db["notifications"].insert_one({
        "id": str(_uuid.uuid4()),
        "user_id": user.get("id"),
        "type": "contract_signoff",
        "title": "Contract Ready to Sign",
        "message": f"Contract {contract_id} for '{rfq.get('title')}' is ready. Please review and sign.",
        "is_read": False,
        "created_at": datetime.utcnow(),
        "related_id": contract_id,
    })

    # Notify supplier that a contract has been generated and is awaiting signatures
    if supplier_user:
        await db["notifications"].insert_one({
            "id": str(_uuid.uuid4()),
            "user_id": supplier_user.get("id"),
            "type": "contract_signoff",
            "title": "Contract Generated — Awaiting Signatures",
            "message": f"A contract ({contract_id}) has been generated for your bid on '{rfq.get('title')}'. The buyer will sign first, then it will be sent to you.",
            "is_read": False,
            "created_at": datetime.utcnow(),
            "related_id": contract_id,
        })

    return {"success": True, "contract_id": contract_id, "already_exists": False}


@app.post("/api/contracts/{contract_id}/sign")
async def sign_contract(contract_id: str, request: Request, user: dict = Depends(require_login)):
    """Record a drawn digital signature for the authenticated user on the given contract."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    body = await request.json()
    signature_image = body.get("signature_image", "")  # base64 PNG data URL
    if not signature_image or not signature_image.startswith("data:image/png;base64,"):
        raise HTTPException(status_code=400, detail="A drawn signature is required")

    contract = await db["contracts"].find_one({"contract_id": contract_id})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    user_id = user.get("id")
    now = datetime.utcnow()
    import uuid as _uuid

    is_buyer    = contract.get("buyer_id") == user_id
    is_supplier = contract.get("supplier_id") == user_id

    if not is_supplier:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            is_supplier = (
                contract.get("supplier_id") == company.get("unique_id") or
                contract.get("supplier_id") == company.get("id")
            )

    if not is_buyer and not is_supplier:
        raise HTTPException(status_code=403, detail="You are not a party to this contract")

    updates = {}
    new_status = contract.get("status")

    if is_buyer:
        if contract.get("buyer_signed_at"):
            return {"success": True, "message": "Already signed by buyer", "status": new_status}
        updates["buyer_signed_at"] = now
        updates["buyer_signed_by"] = user_id
        updates["buyer_signature_image"] = signature_image
        new_status = ContractStatusEnum.PENDING_SUPPLIER_SIGNATURE

        supplier_user = await db["users"].find_one({
            "$or": [
                {"id": contract.get("supplier_id")},
                {"company_id": contract.get("supplier_id")},
            ]
        })
        if supplier_user:
            await db["notifications"].insert_one({
                "id": str(_uuid.uuid4()),
                "user_id": supplier_user.get("id"),
                "type": "contract_signoff",
                "title": "Contract Awaiting Your Signature",
                "message": f"The buyer has signed contract {contract_id}. Please review and sign.",
                "is_read": False,
                "created_at": now,
                "related_id": contract_id,
            })

    elif is_supplier:
        if contract.get("supplier_signed_at"):
            return {"success": True, "message": "Already signed by supplier", "status": new_status}
        if not contract.get("buyer_signed_at"):
            raise HTTPException(status_code=400, detail="Buyer must sign first")
        updates["supplier_signed_at"] = now
        updates["supplier_signed_by"] = user_id
        updates["supplier_signature_image"] = signature_image
        new_status = ContractStatusEnum.FULLY_EXECUTED
        updates["executed_at"] = now

        buyer_user = await db["users"].find_one({"id": contract.get("buyer_id")})
        if buyer_user:
            await db["notifications"].insert_one({
                "id": str(_uuid.uuid4()),
                "user_id": buyer_user.get("id"),
                "type": "contract_signoff",
                "title": "Contract Fully Executed",
                "message": f"Contract {contract_id} has been signed by both parties. Production can begin.",
                "is_read": False,
                "created_at": now,
                "related_id": contract_id,
            })

    updates["status"] = new_status

    # Recompute hash after signatures
    updated_contract = {**contract, **updates}
    updated_contract.pop("_id", None)
    contract_text = _build_contract_text(updated_contract)
    updates["content_hash"] = _hashlib.sha256(contract_text.encode()).hexdigest()

    await db["contracts"].update_one(
        {"contract_id": contract_id},
        {"$set": updates}
    )

    return {"success": True, "message": "Contract signed successfully", "status": new_status}


@app.get("/contracts/{contract_id}", response_class=HTMLResponse)
async def contract_view_page(request: Request, contract_id: str, user: dict = Depends(require_login)):
    """View and sign a contract."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    contract = await db["contracts"].find_one({"contract_id": contract_id})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract.pop("_id", None)

    # Determine viewer role
    user_id = user.get("id")
    is_buyer = contract.get("buyer_id") == user_id
    is_supplier = contract.get("supplier_id") == user_id
    if not is_supplier:
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company:
            is_supplier = (
                contract.get("supplier_id") == company.get("unique_id") or
                contract.get("supplier_id") == company.get("id")
            )

    if not is_buyer and not is_supplier and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify hash integrity
    contract_text = _build_contract_text(contract)
    current_hash = _hashlib.sha256(contract_text.encode()).hexdigest()
    hash_valid = current_hash == contract.get("content_hash", "")

    return templates.TemplateResponse("contract_view.html", {
        "request": request,
        "user": user,
        "contract": contract,
        "is_buyer": is_buyer,
        "is_supplier": is_supplier,
        "hash_valid": hash_valid,
        "contract_text": contract_text,
    })


@app.get("/contracts", response_class=HTMLResponse)
async def contracts_list_page(request: Request, user: dict = Depends(require_login)):
    """List all contracts for the current user."""
    from database import db
    contracts = []
    if db is not None:
        user_id = user.get("id")
        company = await db["companies"].find_one({"id": user.get("company_id")})
        supplier_ids = [user_id]
        if company:
            if company.get("unique_id"):
                supplier_ids.append(company.get("unique_id"))
            supplier_ids.append(company.get("id"))

        async for c in db["contracts"].find({
            "$or": [
                {"buyer_id": user_id},
                {"supplier_id": {"$in": supplier_ids}},
            ]
        }).sort("created_at", -1):
            c.pop("_id", None)
            contracts.append(c)

    return templates.TemplateResponse("contracts_list.html", {
        "request": request,
        "user": user,
        "contracts": contracts,
    })


@app.get("/api/contracts/{contract_id}")
async def get_contract_api(contract_id: str, user: dict = Depends(require_login)):
    """API endpoint to get contract data."""
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    contract = await db["contracts"].find_one({"contract_id": contract_id})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract.pop("_id", None)
    # Serialize datetimes
    for key in ("created_at", "executed_at", "buyer_signed_at", "supplier_signed_at"):
        if isinstance(contract.get(key), datetime):
            contract[key] = contract[key].isoformat() + "Z"

    return {"success": True, "contract": contract}


@app.get("/admin/contracts", response_class=HTMLResponse)
async def admin_contracts_page(request: Request, admin: dict = Depends(require_admin)):
    """Admin view of all contracts."""
    from database import db
    contracts = []
    if db is not None:
        async for c in db["contracts"].find({}).sort("created_at", -1):
            c.pop("_id", None)
            contracts.append(c)
    return templates.TemplateResponse("admin_contracts.html", {
        "request": request,
        "user": admin,
        "contracts": contracts,
    })


# ----------------------------------------
# BID COMPARISON MATRIX
# ----------------------------------------

@app.get("/rfq/{rfq_id}/bids", response_class=HTMLResponse)
async def bid_comparison_page(request: Request, rfq_id: str, user: dict = Depends(require_buyer)):
    """Serve the Bid Comparison Matrix page for a buyer's RFQ."""
    from database import db

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Fetch the RFQ and verify ownership
    rfq = await db["rfqs"].find_one({"id": rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Check if current user owns this RFQ
    rfq_buyer_id = rfq.get("buyer_id") or rfq.get("company_id")
    user_company_id = user.get("company_id")
    is_owner = rfq_buyer_id == user_company_id

    return templates.TemplateResponse("bid_comparison.html", {
        "request": request,
        "user": user,
        "rfq_id": rfq_id,
        "is_owner": is_owner,
    })


@app.get("/api/bids/recommendations")
async def get_bid_recommendations(user: dict = Depends(require_seller)):
    """
    AI Bid Recommendations API
    Strictly for Sellers.
    """
    return {"success": True, "recommendations": []}


@app.get("/rfq/{rfq_id}/compare-bids")
async def compare_bids(rfq_id: str, user: dict = Depends(require_buyer)):
    """
    Bid Comparison Matrix API — Strictly for Buyers.
    Fetches all bids for a given RFQ, enriched with supplier company details
    (company name, trust score, average rating) for side-by-side comparison.
    """
    from database import db

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Verify the RFQ exists and check ownership
    rfq = await db["rfqs"].find_one({"id": rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Check if current user owns this RFQ
    rfq_buyer_id = rfq.get("buyer_id") or rfq.get("company_id")
    user_company_id = user.get("company_id")
    is_owner = rfq_buyer_id == user_company_id
    
    rfq.pop("_id", None)

    # Fetch all bids for this RFQ (ACTIVE status or no status field)
    # Hide REJECTED bids from non-owners
    bids = []
    async for bid in db["bids"].find({"rfq_id": rfq_id}).sort("bid_price", 1):
        bid.pop("_id", None)
        
        # Check BOTH status fields - if either is REJECTED, hide from non-owners
        is_rejected = bid.get("status") == "REJECTED" or bid.get("bid_status") == "REJECTED"
        
        # Skip rejected bids if user is not the owner
        if is_rejected and not is_owner:
            continue

        # Enrich with supplier company data
        supplier = await db["companies"].find_one({
            "$or": [
                {"id": bid.get("supplier_id")},
                {"unique_id": bid.get("supplier_id")},
            ]
        })

        if supplier:
            supplier.pop("_id", None)
            bid["company_name"] = supplier.get("name", bid.get("supplier_name", "Unknown"))
            bid["trust_score"] = supplier.get("trust_score", 0)

            # Calculate average rating from reviews if available
            try:
                reviews = await db["reviews"].find({"supplier_id": bid["supplier_id"]}).to_list(length=100)
                if reviews:
                    bid["average_rating"] = round(sum(r.get("rating", 0) for r in reviews) / len(reviews), 1)
                else:
                    bid["average_rating"] = 0.0
            except Exception:
                bid["average_rating"] = 0.0

            bid["verification_status"] = supplier.get("overall_status", "DRAFT")

            # ── Capacity enrichment ──
            cap = await get_supplier_capacity(bid.get("supplier_id", ""))
            rfq_quantity = rfq.get("quantity", 0)
            if cap.get("has_data"):
                estimated = cap["estimated_monthly_units"]
                available = cap.get("available_capacity", estimated)
                bid["capacity_workers"] = cap.get("total_workers")
                bid["capacity_machines"] = cap.get("total_machines")
                bid["capacity_monthly_units"] = available
                bid["capacity_can_fulfill"] = available >= rfq_quantity
                bid["capacity_shortfall"] = max(0, rfq_quantity - available)
            else:
                bid["capacity_workers"] = None
                bid["capacity_machines"] = None
                bid["capacity_monthly_units"] = None
                bid["capacity_can_fulfill"] = None
                bid["capacity_shortfall"] = 0
        else:
            bid["company_name"] = bid.get("supplier_name", "Unknown Supplier")
            bid["trust_score"] = 0
            bid["average_rating"] = 0.0
            bid["verification_status"] = "UNKNOWN"
            bid["capacity_workers"] = None
            bid["capacity_machines"] = None
            bid["capacity_monthly_units"] = None
            bid["capacity_can_fulfill"] = None
            bid["capacity_shortfall"] = 0

        # Serialize datetime
        if isinstance(bid.get("timestamp"), datetime):
            bid["timestamp"] = bid["timestamp"].isoformat() + "Z"

        bids.append(bid)

    # Serialize RFQ dates
    for key in ("created_at", "deadline", "target_delivery_date", "auction_end_time"):
        if isinstance(rfq.get(key), datetime):
            rfq[key] = rfq[key].isoformat() + "Z"

    return {
        "success": True,
        "rfq": {
            "id": rfq.get("id"),
            "title": rfq.get("title"),
            "product_category": rfq.get("product_category"),
            "quantity": rfq.get("quantity"),
            "status": rfq.get("status"),
            "incoterm": rfq.get("incoterm", "FOB"),
            "target_price": rfq.get("target_price"),
            "target_delivery_date": rfq.get("target_delivery_date"),
        },
        "bids": bids,
        "total_bids": len(bids),
    }


@app.post("/rfq/{rfq_id}/bids/{bid_id}/accept")
async def accept_bid_legacy(rfq_id: str, bid_id: str, user: dict = Depends(require_buyer)):
    """Accept a specific bid and reject all others for this RFQ. Only the RFQ owner can accept."""
    from database import db

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    rfq = await db["rfqs"].find_one({"id": rfq_id})
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Only the buyer who created this RFQ can accept bids
    user_company = await db["companies"].find_one({"id": user.get("company_id")})
    rfq_buyer_id = rfq.get("buyer_id")
    user_id = user.get("id")
    
    # Check if current user is the RFQ owner (buyer_id is the user's ID)
    if rfq_buyer_id != user_id:
        raise HTTPException(status_code=403, detail="You can only accept bids on RFQs you created.")

    bid = await db["bids"].find_one({"id": bid_id, "rfq_id": rfq_id})
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Accept the selected bid
    await db["bids"].update_one(
        {"id": bid_id},
        {"$set": {"bid_status": "ACCEPTED"}}
    )

    # Reject all other bids for this RFQ
    await db["bids"].update_many(
        {"rfq_id": rfq_id, "id": {"$ne": bid_id}},
        {"$set": {"bid_status": "REJECTED"}}
    )

    # Update RFQ status to AWARDED
    await db["rfqs"].update_one(
        {"id": rfq_id},
        {"$set": {
            "status": "AWARDED",
            "lowest_bidder_id": bid.get("supplier_id"),
            "current_lowest_bid": bid.get("bid_price"),
        }}
    )

    # Notify the supplier whose bid was accepted
    import uuid as _uuid
    bid_owner_company = await db["companies"].find_one({
        "$or": [{"unique_id": bid.get("supplier_id")}, {"id": bid.get("supplier_id")}]
    })
    if bid_owner_company:
        bid_owner_user = await db["users"].find_one({"company_id": bid_owner_company.get("id")})
        if bid_owner_user:
            buyer_company = await db["companies"].find_one({"id": user.get("company_id")})
            buyer_name = buyer_company.get("name", user.get("email", "")) if buyer_company else user.get("email", "")
            await db["notifications"].insert_one({
                "id": str(_uuid.uuid4()),
                "user_id": bid_owner_user.get("id"),
                "type": "bid_accepted",
                "title": "Your Bid Was Accepted!",
                "message": f"{buyer_name} accepted your bid of {bid.get('bid_price'):,.2f}/unit for '{rfq.get('title', '')}'. Please confirm you can fulfill this order.",
                "is_read": False,
                "created_at": datetime.utcnow(),
                "related_id": rfq_id,
            })

    return {
        "success": True,
        "message": f"Bid from {bid.get('supplier_name', 'supplier')} accepted. RFQ awarded.",
        "accepted_bid_id": bid_id,
    }


# ----------------------------------------
# REAL-TIME CHAT ENGINE (WebSockets)
# ----------------------------------------

class ConnectionManager:
    """Manages active WebSocket connections keyed by rfq_id and user_id."""
    def __init__(self):
        # Structure: { rfq_id: { user_id: WebSocket } }
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, rfq_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if rfq_id not in self.active_connections:
            self.active_connections[rfq_id] = {}
        self.active_connections[rfq_id][user_id] = websocket

    def disconnect(self, rfq_id: str, user_id: str):
        if rfq_id in self.active_connections:
            self.active_connections[rfq_id].pop(user_id, None)
            if not self.active_connections[rfq_id]:
                del self.active_connections[rfq_id]

    async def send_personal_message(self, message: dict, rfq_id: str, user_id: str):
        """Send a message to a specific user in a specific RFQ room."""
        if rfq_id in self.active_connections:
            ws = self.active_connections[rfq_id].get(user_id)
            if ws:
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(rfq_id, user_id)

    async def broadcast_to_room(self, message: dict, rfq_id: str, exclude_user: str = None):
        """Broadcast a message to all users in an RFQ room except the sender."""
        if rfq_id in self.active_connections:
            for uid, ws in list(self.active_connections[rfq_id].items()):
                if uid != exclude_user:
                    try:
                        await ws.send_json(message)
                    except Exception:
                        self.disconnect(rfq_id, uid)


manager = ConnectionManager()


@app.websocket("/ws/chat/{rfq_id}/{user_id}")
async def websocket_chat(websocket: WebSocket, rfq_id: str, user_id: str):
    """WebSocket endpoint for real-time buyer ↔ supplier chat within an RFQ context."""
    from database import db

    await manager.connect(rfq_id, user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content", "").strip()
            receiver_id = data.get("receiver_id", "")
            image_url = data.get("image_url", "")

            if not content and not image_url:
                continue

            # Build and persist the message
            msg = {
                "id": str(__import__('uuid').uuid4()),
                "rfq_id": rfq_id,
                "sender_id": user_id,
                "receiver_id": receiver_id,
                "content": content,
                "image_url": image_url,
                "timestamp": datetime.utcnow(),
            }

            # Save to MongoDB asynchronously
            if db is not None:
                await db["messages"].insert_one(msg.copy())

            # Prepare the broadcast payload (serialize datetime)
            broadcast = {
                **msg,
                "timestamp": msg["timestamp"].isoformat() + "Z",
            }
            broadcast.pop("_id", None)

            # Send to the specific receiver if connected
            # (No echo back to sender — the frontend renders sent messages locally)
            await manager.send_personal_message(broadcast, rfq_id, receiver_id)

            # Create notification for the receiver
            if receiver_id and db is not None:
                try:
                    sender_user = await db["users"].find_one({"id": user_id})
                    sender_company = await db["companies"].find_one({"id": sender_user.get("company_id")}) if sender_user else None
                    sender_name = (sender_company or {}).get("name") or (sender_user or {}).get("email", "Someone")
                    rfq = await db["rfqs"].find_one({"id": rfq_id})
                    rfq_title = (rfq or {}).get("title", "an RFQ")
                    preview = content[:50] + ("..." if len(content) > 50 else "") if content else "Sent an image"
                    # Determine receiver user ID and role for notification
                    receiver_user_id = receiver_id
                    receiver_role = "BUYER"
                    
                    receiver_user = await db["users"].find_one({"id": receiver_id})
                    if not receiver_user:
                        # Receiver might be a company ID
                        receiver_user = await db["users"].find_one({"company_id": receiver_id})
                        if receiver_user:
                            receiver_user_id = receiver_user.get("id")
                            receiver_role = "SUPPLIER"
                    else:
                        company = await db["companies"].find_one({"id": receiver_user.get("company_id")})
                        if company:
                            receiver_role = company.get("role", "BUYER").upper()
                    
                    notif_link = f"/supplier/bids?open_chat={user_id}&rfq_id={rfq_id}" if receiver_role == "SUPPLIER" else f"/rfq/{rfq_id}/bids?open_chat={user_id}"

                    await create_notification(
                        user_id=receiver_user_id,
                        notification_type="chat_message",
                        title=f"New message from {sender_name}",
                        message=f'"{preview}" – regarding {rfq_title}',
                        related_id=rfq_id,
                        link=notif_link,
                    )
                except Exception as notif_err:
                    print(f"⚠️ Failed to create chat notification: {notif_err}")

    except WebSocketDisconnect:
        manager.disconnect(rfq_id, user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id} in RFQ {rfq_id}: {e}")
        manager.disconnect(rfq_id, user_id)


@app.post("/api/chat/{rfq_id}/send")
async def send_chat_message(rfq_id: str, request: Request, user: dict = Depends(require_login)):
    """HTTP fallback for sending chat messages when WebSocket is unavailable."""
    from database import db
    import uuid as _uuid

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    body = await request.json()
    content = body.get("content", "").strip()
    receiver_id = body.get("receiver_id", "")
    image_url = body.get("image_url", "")

    if not content and not image_url:
        raise HTTPException(status_code=400, detail="Message content or image is required")

    user_id = user.get("id")
    sender_id = user_id
    if user.get("company_id"):
        company = await db["companies"].find_one({"id": user.get("company_id")})
        if company and company.get("role") == "SUPPLIER":
            sender_id = company.get("unique_id") or company.get("id")

    msg = {
        "id": str(_uuid.uuid4()),
        "rfq_id": rfq_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
        "image_url": image_url,
        "timestamp": datetime.utcnow(),
    }

    await db["messages"].insert_one(msg.copy())

    # Also push via WebSocket if connected
    broadcast = {**msg, "timestamp": msg["timestamp"].isoformat() + "Z"}
    broadcast.pop("_id", None)
    # Send only to receiver — sender already rendered the message locally
    await manager.send_personal_message(broadcast, rfq_id, receiver_id)

    # Create notification for the receiver
    if receiver_id and db is not None:
        try:
            sender_user = await db["users"].find_one({"id": user_id})
            sender_company = await db["companies"].find_one({"id": sender_user.get("company_id")}) if sender_user else None
            sender_name = (sender_company or {}).get("name") or (sender_user or {}).get("email", "Someone")
            rfq = await db["rfqs"].find_one({"id": rfq_id})
            rfq_title = (rfq or {}).get("title", "an RFQ")
            preview = content[:50] + ("..." if len(content) > 50 else "") if content else "Sent an image"
            # Determine receiver user ID and role for notification
            receiver_user_id = receiver_id
            receiver_role = "BUYER"
            
            receiver_user = await db["users"].find_one({"id": receiver_id})
            if not receiver_user:
                # Receiver might be a company ID
                receiver_user = await db["users"].find_one({"company_id": receiver_id})
                if receiver_user:
                    receiver_user_id = receiver_user.get("id")
                    receiver_role = "SUPPLIER"
            else:
                company = await db["companies"].find_one({"id": receiver_user.get("company_id")})
                if company:
                    receiver_role = company.get("role", "BUYER").upper()

            notif_link = f"/supplier/bids?open_chat={sender_id}&rfq_id={rfq_id}" if receiver_role == "SUPPLIER" else f"/rfq/{rfq_id}/bids?open_chat={sender_id}"

            await create_notification(
                user_id=receiver_user_id,
                notification_type="chat_message",
                title=f"New message from {sender_name}",
                message=f'"{preview}" – regarding {rfq_title}',
                related_id=rfq_id,
                link=notif_link,
            )
        except Exception as notif_err:
            print(f"⚠️ Failed to create chat notification: {notif_err}")

    return {"success": True, "message": broadcast}


@app.post("/api/chat/upload-image")
async def upload_chat_image(
    request: Request,
    file: UploadFile = File(None),
    image: UploadFile = File(None),
    user: dict = Depends(require_login),
):
    """Upload an image for chat. Returns a URL that can be embedded in a message.
    
    Accepts the file under either field name 'file' or 'image' for
    backwards compatibility with both buyer and supplier frontends.
    """
    import uuid as _uuid
    import os

    # Accept whichever field was provided
    upload = file or image
    if upload is None:
        raise HTTPException(status_code=400, detail="No image file provided. Send as 'file' or 'image'.")

    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if upload.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, GIF, and WebP images are allowed")

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "uploads", "chat")
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    ext = upload.filename.split(".")[-1] if "." in upload.filename else "png"
    filename = f"{_uuid.uuid4().hex[:12]}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    # Save file
    file_bytes = await upload.read()
    if len(file_bytes) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="Image must be under 5MB")

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    # Return url under both field names for compatibility
    return {"success": True, "url": f"/uploads/chat/{filename}", "image_url": f"/uploads/chat/{filename}"}


@app.get("/api/chat/{rfq_id}/history")
async def get_chat_history(rfq_id: str, receiver_id: str = None, user: dict = Depends(require_login)):
    """Fetch chat history between the current user and another user for a specific RFQ."""
    from database import db

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    user_id = user.get("id")
    company_id = user.get("company_id")
    
    user_ids = [user_id]
    if company_id:
        user_ids.append(company_id)
        company = await db["companies"].find_one({"id": company_id})
        if company and company.get("unique_id"):
            user_ids.append(company.get("unique_id"))
            
    # Remove duplicates
    user_ids = list(set([uid for uid in user_ids if uid]))

    # Build query: messages where current user is sender or receiver in this RFQ
    query = {"rfq_id": rfq_id}
    if receiver_id:
        query["$or"] = [
            {"sender_id": {"$in": user_ids}, "receiver_id": receiver_id},
            {"sender_id": receiver_id, "receiver_id": {"$in": user_ids}},
        ]
    else:
        query["$or"] = [
            {"sender_id": {"$in": user_ids}},
            {"receiver_id": {"$in": user_ids}},
        ]

    messages = []
    async for msg in db["messages"].find(query).sort("timestamp", 1).limit(200):
        msg.pop("_id", None)
        if isinstance(msg.get("timestamp"), datetime):
            msg["timestamp"] = msg["timestamp"].isoformat() + "Z"
        messages.append(msg)

    return {"success": True, "messages": messages}


