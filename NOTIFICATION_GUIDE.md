# Notification System - Complete Guide

## Overview
TexBid's notification system keeps users informed about important events like new RFQs, bids, and auction updates.

---

## Notification Features

### Bell Icon in Navigation
- 🔔 Always visible when logged in
- Badge shows unread count
- Click to see dropdown
- Real-time updates every 30 seconds

### Notification Dropdown
- Shows last 20 notifications
- Unread highlighted in blue
- Click to mark as read
- "View all" link to full page
- "Mark all as read" button

### Full Notifications Page
- Shows last 100 notifications
- Filter by type (All, Unread, Bids, Auctions, Payments)
- Detailed view with timestamps
- Color-coded by type
- Pagination support

---

## Notification Types

### For Buyers:

#### 1. Bid Submitted
**When**: Supplier submits bid on your RFQ
**Message**: "New bid received on [RFQ Title]"
**Icon**: 🟢 Green checkmark

#### 2. Sample Approved/Rejected
**When**: Sample review completed
**Message**: "Sample [approved/rejected] for [RFQ Title]"
**Icon**: 🔵 Blue check / 🔴 Red X

#### 3. Auction Deadline
**When**: Auction closing soon (15 min warning)
**Message**: "Auction ending soon: [RFQ Title]"
**Icon**: 🟠 Orange clock

#### 4. Contract Sign-off
**When**: Contract ready for signature
**Message**: "Contract ready for [RFQ Title]"
**Icon**: 🟣 Purple document

### For Suppliers:

#### 1. New RFQ Posted
**When**: Buyer creates new RFQ matching your profile
**Message**: "New RFQ: [RFQ Title]"
**Icon**: 🟢 Teal document

#### 2. New Auction
**When**: Reverse auction starts
**Message**: "New reverse auction: [RFQ Title]"
**Icon**: 🟡 Yellow lightning

#### 3. Bid Status Update
**When**: Your bid is accepted/rejected
**Message**: "Your bid on [RFQ Title] was [accepted/rejected]"
**Icon**: 🔵 Blue / 🔴 Red

#### 4. Escrow Released
**When**: Payment released after delivery
**Message**: "Payment released for [RFQ Title]"
**Icon**: 🟣 Purple money

---

## How Notifications Work

### Automatic Triggers:

```
Event Happens → Notification Created → Users Notified
```

**Example Flow:**
1. Buyer creates RFQ
2. System finds matching suppliers
3. Notification created for each supplier
4. Badge count updates
5. Suppliers see notification

### Real-Time Updates:
- Auto-refresh every 30 seconds
- No page reload needed
- Badge updates automatically
- Dropdown refreshes on open

---

## Notification Setup

### For Suppliers to Receive RFQ Notifications:

**Requirements:**
1. ✅ Have a user account
2. ✅ User account linked to company profile
3. ✅ Company profile has `company_id`
4. ✅ Company role is "SUPPLIER"

**How to Link:**
```python
# User model must have company_id
user = {
    "id": "user_123",
    "email": "supplier@example.com",
    "company_id": "company_456"  # ← Must be set!
}

# Company model
company = {
    "id": "company_456",
    "name": "ABC Textiles",
    "role": "SUPPLIER"
}
```

### Verification:
1. Log in as supplier
2. Go to profile page
3. Check if company is linked
4. If not, contact admin

---

## Managing Notifications

### Mark as Read:
**Individual:**
- Click on notification in dropdown
- Automatically marked as read
- Badge count decreases

**All at Once:**
- Click "Mark all as read" button
- All notifications marked as read
- Badge count goes to 0

### Filter Notifications:
On full notifications page:
- **All**: Show everything
- **Unread**: Only unread notifications
- **Bids**: Only bid-related
- **Auctions**: Only auction-related
- **Payments**: Only payment-related

---

## Notification Timing

### When Are Notifications Sent?

| Event | Timing | Recipients |
|-------|--------|-----------|
| **RFQ Created** | Immediately | Matching suppliers |
| **Bid Submitted** | Immediately | RFQ owner (buyer) |
| **Auction Starts** | Immediately | All premium suppliers |
| **Auction Closing** | 15 min before | All bidders |
| **Auction Ends** | Immediately | Winner + buyer |
| **Sample Review** | When reviewed | Supplier |
| **Payment Released** | When released | Supplier |

### Not Retroactive:
❌ Old RFQs don't trigger notifications
✅ Only new events trigger notifications
✅ Notifications created at event time

---

## Notification Display

### Dropdown Panel:
```
┌─────────────────────────────────┐
│ Notifications            Mark all│
├─────────────────────────────────┤
│ 🟢 New RFQ: T-Shirts            │
│    2 hours ago              NEW │
├─────────────────────────────────┤
│ 🔵 Bid submitted on Denim       │
│    5 hours ago                  │
├─────────────────────────────────┤
│ View all notifications          │
└─────────────────────────────────┘
```

### Full Page:
- Large cards with icons
- Detailed messages
- Timestamps (relative and absolute)
- Type badges
- Color-coded by status
- Hover effects

---

## Troubleshooting

### Not Receiving Notifications

**Check:**
1. ✅ Are you logged in?
2. ✅ Is your user account linked to company?
3. ✅ Is company_id set correctly?
4. ✅ Is company role correct (BUYER/SUPPLIER)?
5. ✅ Are notifications being created? (check database)

**Debug Steps:**
```python
# Check user-company link
db.users.findOne({email: "your@email.com"})
# Should have company_id field

# Check company
db.companies.findOne({id: "company_id"})
# Should exist and have correct role

# Check notifications
db.notifications.find({user_id: "your_user_id"})
# Should show notifications
```

### Notifications Not Showing in Dropdown

**Possible Causes:**
- JavaScript error (check browser console)
- API endpoint failing
- Session expired
- Cache issue

**Solutions:**
1. Refresh page (Ctrl+R)
2. Clear browser cache
3. Check browser console for errors
4. Log out and log back in

### "Failed to Load Notifications"

**Causes:**
- Database connection issue
- API endpoint error
- Serialization problem
- Network issue

**Solutions:**
1. Restart backend server
2. Check server logs
3. Test API directly: `/api/notifications`
4. Clear browser cache

---

## API Endpoints

### For Developers:

```python
# Get notifications (with pagination)
GET /api/notifications?limit=20

# Get unread count
GET /api/notifications/count

# Mark notification as read
POST /api/notifications/{id}/read

# Mark all as read
POST /api/notifications/mark-all-read

# Full notifications page
GET /notifications
```

### Response Format:
```json
{
  "notifications": [
    {
      "id": "notif_123",
      "user_id": "user_456",
      "type": "new_rfq",
      "title": "New RFQ Posted",
      "message": "New RFQ: Cotton T-Shirts",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00Z",
      "related_id": "rfq_789"
    }
  ],
  "unread_count": 3
}
```

---

## Notification Creation

### For Developers:

```python
# Create notification helper function
await create_notification(
    user_id="user_123",
    notification_type="new_rfq",
    title="New RFQ Posted",
    message="New RFQ: Cotton T-Shirts",
    related_id="rfq_456"
)
```

### Trigger Points:
1. **RFQ Created**: Notify matching suppliers
2. **Bid Submitted**: Notify RFQ owner
3. **Auction Started**: Notify all suppliers
4. **Auction Ending**: Notify all bidders
5. **Sample Reviewed**: Notify supplier
6. **Payment Released**: Notify supplier

---

## Best Practices

### For Users:
1. **Check Regularly**: Look for new notifications
2. **Mark as Read**: Keep inbox clean
3. **Act Quickly**: Respond to time-sensitive notifications
4. **Enable Sounds**: (Future feature) Get audio alerts
5. **Link Company**: Ensure account is properly linked

### For Developers:
1. **Create Immediately**: Don't delay notification creation
2. **Be Specific**: Clear, actionable messages
3. **Include Context**: Related IDs for linking
4. **Test Thoroughly**: Verify all trigger points
5. **Handle Errors**: Graceful failure if notification fails

---

## Future Enhancements

### Planned Features:
- 📧 Email notifications
- 📱 Push notifications (mobile app)
- 🔊 Sound alerts
- ⚙️ Notification preferences
- 📊 Notification analytics
- 🔕 Do not disturb mode
- 📅 Scheduled digest emails

---

## Tips

💡 Check notifications before starting work
💡 Mark as read to track what you've seen
💡 Use filters to find specific types
💡 Link your company account for full functionality
💡 Contact admin if notifications aren't working
