# TexBid — Bid to Payment Workflow

## Full Flow

```
Supplier submits bid
        ↓
Buyer accepts bid  →  Supplier notified
        ↓
Supplier confirms order  →  Buyer notified ("Ready to Pay")
        ↓
Buyer generates contract  →  Both parties notified
        ↓
Buyer signs contract  →  Supplier notified ("Awaiting your signature")
        ↓
Supplier signs contract  →  Buyer notified ("Fully Executed")
        ↓
Buyer completes payment  →  Supplier notified ("Funds in Escrow")
        ↓
Admin releases escrow  →  Order complete
```

## Step 1 — Supplier Submits Bid
- Via **Submit a Bid** page or **Auction Room** (Premium)
- Buyer receives notification: "New Bid Received"

## Step 2 — Buyer Accepts Bid
- Only the RFQ owner (buyer) can accept
- All other bids on that RFQ are marked REJECTED (hidden from suppliers)
- RFQ status → EVALUATING
- Supplier receives notification: "Your Bid Was Accepted!"

## Step 3 — Supplier Confirms Order
- Supplier clicks **Confirm Order** on their dashboard
- Buyer receives notification: "Supplier Confirmed — Ready to Pay"
- **Pay Now** button unlocks for the buyer

## Step 4 — Contract Generation
- Buyer clicks **Generate Contract**
- Buyer notified: "Contract Ready to Sign"
- Supplier notified: "Contract Generated — Awaiting Signatures"

## Step 5 — Contract Signing
- Buyer signs first (drawn digital signature)
- Supplier notified: "Contract Awaiting Your Signature"
- Supplier signs
- Buyer notified: "Contract Fully Executed"
- Contract status → FULLY EXECUTED

## Step 6 — Payment
- Buyer clicks **Pay Now** and completes payment
- Funds held in escrow
- Supplier notified: "Payment Completed — Funds in Escrow"
- RFQ status → AWARDED

## Step 7 — Escrow Release
- Admin reviews and releases escrow to supplier
- Order complete

## Bid Visibility Rules
| Who | Sees |
|-----|------|
| Buyer (RFQ owner) | All bids including rejected |
| Supplier | Only their own accepted/pending bids |
| Other buyers | Only non-rejected bids |
