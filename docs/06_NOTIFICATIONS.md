# TexBid — Notification System

## Overview
Notifications appear in the bell icon (🔔) in the top navigation bar. The badge shows unread count.

## Notification Triggers

| Event | Recipient | Message |
|-------|-----------|---------|
| Supplier submits bid | Buyer | "New Bid Received — {Supplier} submitted {price}/unit on {RFQ}" |
| Buyer accepts bid | Supplier | "Your Bid Was Accepted! Please confirm you can fulfill this order." |
| Supplier confirms order | Buyer | "Supplier Confirmed — Ready to Pay" |
| Contract generated | Buyer | "Contract Ready to Sign" |
| Contract generated | Supplier | "Contract Generated — Awaiting Signatures" |
| Buyer signs contract | Supplier | "Contract Awaiting Your Signature" |
| Supplier signs contract | Buyer | "Contract Fully Executed. Production can begin." |
| Buyer completes payment | Supplier | "Payment Completed — Funds in Escrow" |
| New RFQ posted | All Suppliers | "New RFQ Available — {title}" |

## Viewing Notifications
- Click the 🔔 bell icon in the navigation
- Or go to `http://localhost:8000/notifications`
- Unread notifications are highlighted
- Click a notification to mark it as read and navigate to the related item

## Notification Page
- Shows all notifications sorted by newest first
- Unread count shown in the bell badge
- Mark all as read button available

## Troubleshooting
| Problem | Fix |
|---------|-----|
| Not receiving notifications | Check backend is running and restarted after changes |
| Bell badge not updating | Refresh the page |
| Notifications going to wrong user | Check `buyer_id` in RFQ matches user's `id` field |
