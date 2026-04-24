# Reverse Auction System - Testing Guide

## Quick Start Testing

### Step 1: Prepare Test Data

To test the reverse auction system, you need to create a test RFQ with reverse auction enabled.

**Option A: Using MongoDB Compass or CLI**
```json
// Insert into 'rfqs' collection:
{
  "id": "test-auction-001",
  "buyer_id": "buyer-123",
  "title": "Test Reverse Auction",
  "product_category": "T-Shirts",
  "quantity": 5000,
  "fabric_type": "100% Cotton",
  "status": "OPEN",
  "is_reverse_auction": true,
  "auction_end_time": "2026-04-21T15:00:00",
  "current_lowest_bid": null,
  "lowest_bidder_id": null,
  "created_at": "2026-04-21T14:00:00"
}
```

### Step 2: Access the Auction Room

Navigate to: `http://localhost:8000/auction/test-auction-001`

You should see:
- ✅ RFQ details panel on the left
- ✅ Countdown timer in the middle (decreasing in real-time)
- ✅ Current Lowest Bid card on the right
- ✅ Live Leaderboard table (empty initially)
- ✅ Bid submission form on the right

### Step 3: Test Placing Bids

**Test Bid #1 (Opening Bid):**
1. Fill in the bid form:
   - Supplier ID: `supplier-001`
   - Supplier Name: `Company A`
   - Bid Price: `5.50`
2. Click "Submit Bid"
3. Verify:
   - ✅ Success message appears
   - ✅ Current Lowest Bid updates to $5.50
   - ✅ Supplier appears in leaderboard as rank 1
   - ✅ Price shows in green

**Test Bid #2 (Lower Bid):**
1. Scroll down or reset form
2. Fill in:
   - Supplier ID: `supplier-002`
   - Supplier Name: `Company B`
   - Bid Price: `4.75` (lower than 5.50)
3. Click "Submit Bid"
4. Verify:
   - ✅ Success message: "Bid placed successfully! New lowest bid: $4.75"
   - ✅ Current Lowest Bid updates to $4.75
   - ✅ Company B is now rank 1 (green highlight)
   - ✅ Company A drops to rank 2
   - ✅ Leaderboard updates in real-time

**Test Invalid Bid #3 (Higher Price):**
1. Fill form with:
   - Supplier ID: `supplier-003`
   - Supplier Name: `Company C`
   - Bid Price: `5.00` (higher than 4.75)
2. Click "Submit Bid"
3. Verify:
   - ✅ Error message: "Bid must be lower than $4.75"
   - ✅ Bid is NOT added to leaderboard

### Step 4: Test Real-Time Updates

1. Open two browser windows to `http://localhost:8000/auction/test-auction-001`
2. In Window 1: Place a bid for `$4.25`
3. In Window 2: Watch the leaderboard update automatically (within 3 seconds)
4. Verify both windows stay synchronized

### Step 5: Test Countdown Timer

1. Create an RFQ with `auction_end_time` set to 5 minutes from now
2. Navigate to auction room
3. Watch the timer count down: `05:00` → `04:59` → ... → `00:00`
4. When timer reaches `00:00`, verify:
   - ✅ Bid form becomes disabled
   - ✅ Timer displays "Auction Closed"
   - ✅ RFQ status changes to "EVALUATING" (check MongoDB)

### Step 6: Test Manual Auction Close

Using Postman or curl:
```bash
POST http://localhost:8000/api/auction/test-auction-001/close

# Expected response:
{
  "success": true,
  "message": "Auction closed successfully",
  "winning_bid_price": 4.75,
  "winning_supplier_id": "supplier-002"
}
```

Verify:
- ✅ RFQ status changes to "EVALUATING"
- ✅ Bid form is disabled
- ✅ Leaderboard shows read-only

### Step 7: Test Real-Time Status API

Using Postman:
```bash
GET http://localhost:8000/api/auction/test-auction-001/status

# Response shows:
{
  "success": true,
  "current_lowest_bid": 4.75,
  "lowest_bidder": "supplier-002",
  "bid_count": 3,
  "bids": [
    {"supplier_name": "Company B", "bid_price": 4.75, ...},
    {"supplier_name": "Company A", "bid_price": 5.50, ...}
  ],
  "time_remaining": 180
}
```

## Common Test Scenarios

### Scenario 1: Fierce Competition
- Multiple suppliers (5+) placing bids
- Bids lowered by 10-25 cents each time
- Watch leaderboard update in real-time
- Final winner announced

### Scenario 2: Early Bird Advantage
- First supplier places opening bid
- No other bids for several minutes (test timeout)
- Auction closes - first bidder wins

### Scenario 3: Last-Minute Bidding War
- No bids for first 3 minutes
- Two suppliers place bids in final 30 seconds
- Multiple bids placed, rapidly updating leaderboard
- Test timer and updates are accurate

### Scenario 4: Error Handling
- Try placing bid when auction is closed
- Try exceeding (placing higher) bid than current
- Try placing bid with missing fields
- All should return appropriate error messages

## Debugging

### Check MongoDB Data:
```bash
# In MongoDB shell:
use texbid_db

# View RFQ:
db.rfqs.findOne({id: "test-auction-001"})

# View all bids for auction:
db.bids.find({rfq_id: "test-auction-001"}).sort({timestamp: -1})

# View bid count:
db.bids.countDocuments({rfq_id: "test-auction-001"})
```

### Check Backend Logs:
Look for messages like:
```
Error placing bid: ...
Error fetching auction data: ...
Error closing auction: ...
```

### Browser Console:
- Open DevTools (F12)
- Check Console for JavaScript errors
- Check Network tab for failed API calls
- Verify real-time fetch requests to `/api/auction/{rfq_id}/status`

## Success Criteria

✅ All features implemented and working:
- Countdown timer counts down in real-time
- Multiple suppliers can bid
- Only lower bids are accepted
- Leaderboard updates every 3-5 seconds
- Current lowest bid highlighted in green
- Auction auto-closes when timer expires
- Manual close endpoint works
- Error messages are clear and helpful

Run the test suite above to verify everything is working correctly!
