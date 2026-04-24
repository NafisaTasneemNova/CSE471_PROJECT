# RFQ System - Complete Guide

## Overview
The RFQ (Request for Quotation) system allows buyers to post requirements and suppliers to browse and respond.

---

## Access Control

### Who Can Create RFQs?
**Only logged-in BUYERS can create RFQs**

| User Type | Can See RFQ Menu? | Can Create RFQ? | Can Browse RFQs? |
|-----------|-------------------|-----------------|------------------|
| **Not Logged In** | ❌ No | ❌ No | ✅ Yes |
| **Supplier** | ✅ Yes | ❌ No (Error) | ✅ Yes |
| **Buyer** | ✅ Yes | ✅ Yes | ✅ Yes |

### Security Layers
```
User tries to create RFQ
    ↓
Is user logged in?
    ├─ No → Redirect to login ❌
    └─ Yes → Continue
        ↓
    Is user a BUYER?
        ├─ No → Show error page ❌
        └─ Yes → Allow RFQ creation ✅
```

---

## Creating an RFQ

### Step 1: Access RFQ Builder
1. Log in as a buyer
2. Hover over **"RFQ"** in navigation
3. Click **"Create RFQ"**

### Step 2: Fill in Details
**Basic Information:**
- Title
- Product category
- Quantity
- Fabric type
- Certifications required

**Specifications:**
- BOM (Bill of Materials)
- Labeling requirements
- Packaging type
- Measurement tolerance

**Logistics:**
- Target delivery date
- Sample requirements
- Incoterms
- Shipping method

### Step 3: Submit
- Click "Create RFQ"
- RFQ is posted and visible to suppliers
- Notifications sent to relevant suppliers

---

## Managing RFQs

### View RFQ Details
1. Go to "Browse RFQs"
2. Click on any RFQ card
3. See full details, specifications, and logistics

### Edit RFQ
**Only the RFQ owner can edit:**
1. Open RFQ detail page
2. Click "Edit" button (only visible to owner)
3. Update information
4. Save changes

### Delete RFQ
**Only the RFQ owner can delete:**
1. Open RFQ detail page
2. Click "Delete" button (only visible to owner)
3. Confirm deletion
4. RFQ is permanently removed

### Ownership Verification
The system checks ownership using:
1. User ID matches RFQ buyer_id
2. User's company_id matches RFQ buyer_id
3. User's email matches RFQ buyer_id
4. Legacy simulated buyer ID support
5. Admin override capability

---

## RFQ Status Flow

```
DRAFT → OPEN → EVALUATING → AWARDED → CLOSED
```

- **DRAFT**: Being created
- **OPEN**: Published and accepting quotes
- **EVALUATING**: Reviewing submissions
- **AWARDED**: Winner selected
- **CLOSED**: Process complete

---

## Browsing RFQs

### For Suppliers:
1. Click "Browse RFQs" in navigation
2. See all open RFQs
3. Filter by category, quantity, etc.
4. Click to view details
5. Submit quotes/bids

### For Buyers:
1. Click "Browse RFQs" in navigation
2. See all RFQs (including your own)
3. Your RFQs show edit/delete buttons
4. Track responses and quotes

---

## RFQ Features

### Quantity Breakdown
- Specify sizes, colors, and quantities
- Dynamic input fields
- Automatic total calculation

### Certifications
- ISO 9001
- WRAP
- OEKO-TEX
- BSCI
- Custom certifications

### Sample Requirements
- Prototype samples
- Pre-production samples
- Custom dates for each

### Tech Pack Upload
- Upload design files
- Attach specifications
- Share with suppliers

---

## Notifications

### Buyers Receive:
- New bid submitted
- Sample approved/rejected
- Auction deadline reminders

### Suppliers Receive:
- New RFQ posted (matching their profile)
- RFQ updated
- Bid accepted/rejected

---

## Tips for Buyers

1. **Be Specific**: More details = better quotes
2. **Set Realistic Deadlines**: Allow time for quality work
3. **Include Tech Packs**: Visual references help suppliers
4. **Specify Certifications**: Ensure compliance upfront
5. **Use Quantity Breakdown**: Clear size/color requirements

---

## Tips for Suppliers

1. **Browse Regularly**: New RFQs posted daily
2. **Read Carefully**: Understand all requirements
3. **Respond Quickly**: Early bids get noticed
4. **Be Competitive**: Price and quality matter
5. **Ask Questions**: Use messaging if unclear

---

## Troubleshooting

### Can't Create RFQ
- **Not logged in**: Log in first
- **Supplier account**: Only buyers can create RFQs
- **No company**: Complete company profile

### Can't Edit/Delete RFQ
- **Not owner**: Only RFQ creator can edit/delete
- **Wrong account**: Make sure you're logged in as the creator
- **RFQ closed**: Closed RFQs may be locked

### RFQ Not Showing
- **Status**: Check if it's still OPEN
- **Filters**: Clear any active filters
- **Permissions**: Some RFQs may be private

---

## API Endpoints

### For Developers:
- `GET /rfq/create` - RFQ creation page
- `POST /rfq/create` - Submit new RFQ
- `GET /rfq/{id}` - View RFQ details
- `GET /rfq/{id}/edit` - Edit RFQ page
- `POST /rfq/{id}/update` - Update RFQ
- `POST /rfq/{id}/delete` - Delete RFQ
- `GET /dashboard/supplier` - Browse RFQs
