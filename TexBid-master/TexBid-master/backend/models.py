from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid

# --- Enums ---
class RoleEnum(str, Enum):
    BUYER = "BUYER"
    SUPPLIER = "SUPPLIER"

class OverallStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class CertTypeEnum(str, Enum):
    ISO_9001 = "ISO_9001"
    WRAP = "WRAP"
    OEKO_TEX = "OEKO_TEX"
    BSCI = "BSCI"
    OTHER = "OTHER"

class VerificationStatusEnum(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    INVALID = "INVALID"

class RFQStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    EVALUATING = "EVALUATING"
    AWARDED = "AWARDED"
    CLOSED = "CLOSED"

class UrgencyLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class SubscriptionTierEnum(str, Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"

class EscrowStatusEnum(str, Enum):
    PENDING = "PENDING"
    PAID_IN_ESCROW = "PAID_IN_ESCROW"
    WORK_IN_PROGRESS = "WORK_IN_PROGRESS"
    SENT_FOR_DELIVERY = "SENT_FOR_DELIVERY"
    RELEASED = "RELEASED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"

class UserModel(BaseModel):
    """Model for user authentication."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique user ID")
    email: str = Field(..., description="User email (unique)")
    password_hash: str = Field(..., description="Hashed password")
    company_id: Optional[str] = Field(None, description="Linked company ID")
    is_admin: bool = Field(default=False, description="Whether user is an admin")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")



# --- Models ---
class CompanyModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the company")
    name: str = Field(..., description="The official registered name of the business")
    role: RoleEnum = Field(..., description="BUYER or SUPPLIER")
    overall_status: OverallStatusEnum = Field(default=OverallStatusEnum.DRAFT, description="Approval status")
    trust_score: int = Field(default=0, ge=0, le=100, description="Calculated score (0-100) based on verified data")
    subscription_tier: SubscriptionTierEnum = Field(default=SubscriptionTierEnum.FREE, description="Subscription plan: FREE or PREMIUM")
    subscription_start_date: Optional[datetime] = Field(None, description="When current subscription started")
    subscription_can_change_after: Optional[datetime] = Field(None, description="Date when subscription can be changed again (30 days lock)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the profile was created")

class LegalAndCapacityModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str = Field(..., description="Links back to the Companies table")
    business_license_no: str = Field(..., description="The official government license number")
    business_license_url: str = Field(..., description="Secure link to uploaded document")
    trade_license_no: str = Field(..., description="The trade license number")
    manufacturing_type: str = Field(..., description="e.g. Knit, Woven, Denim")
    total_workers: int = Field(default=0, description="Total number of employees")
    total_machines: int = Field(default=0, description="Total machinery count")
    annual_turnover: float = Field(default=0.0, description="Approximate yearly revenue")

class CertificationModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str = Field(..., description="Links back to Companies table")
    cert_type: CertTypeEnum = Field(..., description="Type of certification")
    cert_number: str = Field(..., description="Unique ID on the certificate")
    document_url: str = Field(..., description="Secure link to the uploaded certificate")
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    verification_status: VerificationStatusEnum = Field(default=VerificationStatusEnum.PENDING)

class RFQModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str = Field(..., description="Simulated Buyer ID")
    title: str = Field(default="Untitled RFQ", description="Project or Order Title")
    product_category: str = Field(..., description="e.g. T-Shirts, Denim, Activewear")
    urgency_level: UrgencyLevelEnum = Field(default=UrgencyLevelEnum.MEDIUM)
    quantity: int = Field(default=0, description="Total units required (sum of breakdown or legacy)")
    quantity_breakdown: List[dict] = Field(default_factory=list, description="List of {size, color, quantity} dicts")
    target_price: Optional[float] = Field(None, description="Optional target price per unit")
    fabric_type: str = Field(..., description="e.g. 100% Cotton, Poly-blend")
    fabric_gsm: Optional[str] = Field(None, description="e.g. 160-190 or Custom 175")
    certifications_required: List[CertTypeEnum] = Field(default_factory=list, description="List of required certificates")
    
    # Step 2: Specs
    bom_buttons: Optional[str] = None
    bom_zippers: Optional[str] = None
    bom_thread: Optional[str] = None
    labeling_reqs: List[str] = Field(default_factory=list)
    packaging_type: Optional[str] = None
    measurement_tolerance: Optional[str] = None
    
    # Step 3: Logistics
    target_delivery_date: Optional[datetime] = None
    proto_sample_req: bool = False
    proto_sample_date: Optional[datetime] = None
    pp_sample_req: bool = False
    pp_sample_date: Optional[datetime] = None
    incoterm: str = Field(default="FOB")
    incoterms: str = Field(default="FOB") # Legacy compat
    shipping_method: Optional[str] = None
    destination_port: Optional[str] = None

    status: RFQStatusEnum = Field(default=RFQStatusEnum.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    special_instructions: Optional[str] = None
    tech_pack_url: Optional[str] = Field(None, description="URL to main tech pack")
    design_files: List[str] = Field(default_factory=list, description="List of URLs for inspiration gallery")
    pantone_colors: List[str] = Field(default_factory=list, description="Primary visual specs")
    
    # Reverse Auction Fields
    is_reverse_auction: bool = Field(default=False, description="Whether this RFQ uses reverse auction")
    auction_end_time: Optional[datetime] = Field(None, description="When the reverse auction ends")
    current_lowest_bid: Optional[float] = Field(None, description="Current lowest bid price per unit")
    lowest_bidder_id: Optional[str] = Field(None, description="Supplier ID of current lowest bidder")


class BidModel(BaseModel):
    """Model for storing individual bids in a reverse auction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique bid ID")
    rfq_id: str = Field(..., description="RFQ ID for which the bid is placed")
    supplier_id: str = Field(..., description="Supplier ID placing the bid")
    supplier_name: str = Field(..., description="Supplier company name (for display)")
    bid_price: float = Field(..., gt=0, description="Bid price per unit (must be positive)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the bid was placed")
    status: str = Field(default="ACTIVE", description="ACTIVE or CANCELLED")


class NotificationTypeEnum(str, Enum):
    BID_SUBMITTED = "bid_submitted"
    SAMPLE_APPROVED = "sample_approved"
    SAMPLE_REJECTED = "sample_rejected"
    ESCROW_RELEASED = "escrow_released"
    AUCTION_DEADLINE = "auction_deadline"
    CONTRACT_SIGNOFF = "contract_signoff"
    NEW_RFQ = "new_rfq"
    NEW_AUCTION = "new_auction"


class NotificationModel(BaseModel):
    """Model for user notifications."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique notification ID")
    user_id: str = Field(..., description="User ID who receives this notification")
    type: NotificationTypeEnum = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    is_read: bool = Field(default=False, description="Whether notification has been read")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When notification was created")
    related_id: Optional[str] = Field(None, description="Related entity ID (RFQ, bid, etc.)")


class RatingModel(BaseModel):
    """Model for mutual buyer-supplier ratings after order completion."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique rating ID")
    reviewer_id: str = Field(..., description="User ID of the person giving the rating")
    reviewer_company_id: str = Field(..., description="Company ID of the reviewer")
    reviewer_name: str = Field(..., description="Company name of the reviewer (for display)")
    reviewed_user_id: str = Field(..., description="User ID of the person being rated")
    reviewed_company_id: str = Field(..., description="Company ID of the company being rated")
    reviewed_company_name: str = Field(..., description="Company name being rated (for display)")
    order_id: str = Field(..., description="RFQ/Order ID this rating is tied to (prevents duplicate ratings)")
    rating: int = Field(..., ge=1, le=5, description="Numeric rating from 1 to 5")
    review_text: Optional[str] = Field(None, max_length=1000, description="Optional written review")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the rating was submitted")


class MilestoneStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MilestoneStageModel(BaseModel):
    name: str = Field(..., description="Stage name e.g. Order Placed, Fabric Sourcing")
    status: MilestoneStatusEnum = Field(default=MilestoneStatusEnum.PENDING)
    timestamp: Optional[datetime] = Field(None, description="When this stage was last updated")
    note: Optional[str] = Field(None, max_length=300, description="Optional supplier note for this stage")


class OrderMilestoneModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique milestone doc ID")
    order_id: str = Field(..., description="RFQ/Order ID this milestone belongs to")
    current_stage: str = Field(default="Order Placed", description="Name of the currently active stage")
    stages: List[MilestoneStageModel] = Field(default_factory=list, description="Ordered list of all stages with status")

class PaymentModel(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str = Field(..., description="Unique txnid for gateway")
    order_id: str = Field(..., description="Linked RFQ or Order ID")
    bid_id: Optional[str] = Field(None, description="Linked Bid ID")
    buyer_id: str = Field(...)
    supplier_id: str = Field(...)
    amount: float = Field(...)
    original_amount: float = Field(default=0.0, description="Amount in local currency")
    original_currency: str = Field(default="BDT", description="Local currency code")
    base_amount_usd: float = Field(default=0.0, description="Equivalent amount in USD")
    exchange_rate: float = Field(default=1.0, description="Conversion rate used")
    status: EscrowStatusEnum = Field(default=EscrowStatusEnum.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SupplierCapacityModel(BaseModel):
    """Tracks a supplier's monthly production capacity and availability."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique capacity record ID")
    supplier_id: str = Field(..., description="Company ID of the supplier")
    supplier_name: str = Field(..., description="Company name (for display)")
    total_capacity: int = Field(..., gt=0, description="Total monthly production capacity in units")
    available_capacity: int = Field(..., ge=0, description="Currently available units this month")
    reserved_capacity: int = Field(default=0, ge=0, description="Units reserved by confirmed orders")
    unit: str = Field(default="units/month", description="Capacity unit label")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When capacity was last updated")
    updated_by: Optional[str] = Field(None, description="User ID who last updated this record")


class BidRecommendationModel(BaseModel):
    """Stores AI-generated bid recommendation results for a supplier."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique recommendation ID")
    supplier_id: str = Field(..., description="Company ID of the supplier")
    supplier_name: str = Field(..., description="Company name (for display)")
    rfq_id: Optional[str] = Field(None, description="RFQ this recommendation was generated for")
    # Input costs
    input_costs: dict = Field(..., description="Raw cost inputs: material, labor, shipping, quantity")
    # AI output
    base_cost: float = Field(..., description="Sum of all input costs per unit")
    suggested_price: float = Field(..., description="Recommended optimal bid price per unit")
    price_range_min: float = Field(..., description="Lower bound of suggested price range")
    price_range_max: float = Field(..., description="Upper bound of suggested price range")
    profit_margin_pct: float = Field(..., description="Applied profit margin percentage")
    market_adjustment: float = Field(..., description="Market-based price adjustment applied")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence score 0.0–1.0")
    confidence_label: str = Field(..., description="Human-readable confidence: Low / Medium / High")
    reasoning: List[str] = Field(default_factory=list, description="Bullet-point reasoning for the recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AISettingsModel(BaseModel):
    """Platform-wide AI settings controlled by admin."""
    id: str = Field(default="ai_settings", description="Singleton document ID")
    min_profit_margin_pct: float = Field(default=10.0, ge=0, le=100, description="Minimum allowed profit margin %")
    max_market_adjustment_pct: float = Field(default=25.0, ge=0, le=100, description="Max market adjustment % allowed")
    underbid_protection: bool = Field(default=True, description="Prevent bids below base cost + min margin")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="Admin user ID who last changed settings")

# ----------------------------------------
# CONTRACT MODELS
# ----------------------------------------

class ContractStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING_BUYER_SIGNATURE = "PENDING_BUYER_SIGNATURE"
    PENDING_SUPPLIER_SIGNATURE = "PENDING_SUPPLIER_SIGNATURE"
    FULLY_EXECUTED = "FULLY_EXECUTED"
    VOIDED = "VOIDED"


class ContractModel(BaseModel):
    contract_id: str = Field(default_factory=lambda: f"TXB-{str(uuid.uuid4())[:8].upper()}")
    rfq_id: str = Field(...)
    bid_id: str = Field(...)
    payment_id: Optional[str] = Field(None)
    buyer_id: str = Field(...)
    supplier_id: str = Field(...)
    status: ContractStatusEnum = Field(default=ContractStatusEnum.PENDING_BUYER_SIGNATURE)

    # Snapshot of deal data at contract generation time
    rfq_title: str = Field(default="")
    rfq_product_category: str = Field(default="")
    rfq_quantity: int = Field(default=0)
    rfq_incoterm: str = Field(default="FOB")
    rfq_shipping_method: str = Field(default="")
    rfq_destination_port: str = Field(default="")
    rfq_proto_sample_req: bool = Field(default=False)
    rfq_pp_sample_req: bool = Field(default=False)
    rfq_fabric_type: str = Field(default="")
    rfq_special_instructions: str = Field(default="")

    bid_price: float = Field(default=0.0)
    bid_total_value: float = Field(default=0.0)
    bid_supplier_name: str = Field(default="")

    buyer_legal_name: str = Field(default="")
    buyer_email: str = Field(default="")
    supplier_legal_name: str = Field(default="")
    supplier_email: str = Field(default="")

    # Signature records
    buyer_signed_at: Optional[datetime] = Field(None)
    buyer_signed_by: Optional[str] = Field(None)   # user_id
    supplier_signed_at: Optional[datetime] = Field(None)
    supplier_signed_by: Optional[str] = Field(None)  # user_id

    # SHA-256 hash of contract content for tamper detection
    content_hash: str = Field(default="")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = Field(None)


# ----------------------------------------
# SHIPPING & INCOTERMS CALCULATOR MODELS
# ----------------------------------------

class ShippingMethodEnum(str, Enum):
    SEA = "SEA"
    AIR = "AIR"
    ROAD = "ROAD"

class IncotermEnum(str, Enum):
    EXW = "EXW"
    FOB = "FOB"
    CFR = "CFR"
    CIF = "CIF"
    DAP = "DAP"
    DDP = "DDP"

class ShippingCalculateRequest(BaseModel):
    rfq_id: Optional[str] = None
    origin_port_code: str = Field(..., description="Origin port code e.g. BDCGP")
    dest_port_code: str = Field(..., description="Destination port code e.g. NLRTM")
    shipping_method: ShippingMethodEnum = Field(default=ShippingMethodEnum.SEA)
    incoterm: IncotermEnum = Field(default=IncotermEnum.FOB)
    quantity: int = Field(..., gt=0, description="Number of garment units")
    goods_value_usd: Optional[float] = Field(default=0.0, ge=0)

class ShippingRateModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin_region: str = Field(..., description="e.g. Asia, Europe, Americas")
    dest_region: str = Field(..., description="e.g. Asia, Europe, Americas")
    method: ShippingMethodEnum = Field(default=ShippingMethodEnum.SEA)
    base_rate_per_kg: float = Field(..., gt=0, description="USD per kg")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
