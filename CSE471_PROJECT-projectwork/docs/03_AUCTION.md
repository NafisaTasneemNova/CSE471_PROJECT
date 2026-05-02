# TexBid — Reverse Auction System

## Overview
A reverse auction is a special RFQ where suppliers compete by submitting bids in real time. The buyer reviews all bids after the auction ends and accepts the best one.

## Access
- **Auction Room is Premium-only**
- Free users see an "Upgrade to Premium" message instead of the Join button
- Direct URL access (`/auction/{rfq_id}`) also blocked for free users

## Creating a Reverse Auction (Buyer)
1. Create an RFQ as normal
2. Check **Enable Reverse Auction**
3. Set **Auction End Time**
4. Submit — the RFQ will show a "REVERSE AUCTION" badge

## Joining the Auction Room (Premium Supplier)
1. Open the RFQ detail page
2. In **Reverse Auction Details**, click **Join Auction Room**
3. The live leaderboard shows all current bids

## Placing a Bid in the Auction Room
1. Select currency (BDT ৳, USD $, EUR €, GBP £, INR ₹, CNY ¥)
2. Enter price per unit
3. Total estimate auto-calculates (price × quantity)
4. Click **Place Bid**

## Live Leaderboard
- Shows: Supplier ID, Company, Price/Unit, Total Estimate, Time
- **Latest bid per supplier only** — previous bids from same supplier are hidden
- Latest bid appears at the top (sorted by time, not price)
- No rank column

## After Auction Ends
- Auction status changes to EVALUATING
- Buyer reviews bids and accepts the best one manually
- Accepted supplier gets notified to confirm the order

## Currency Symbols
| Code | Symbol |
|------|--------|
| BDT | ৳ |
| USD | $ |
| EUR | € |
| GBP | £ |
| INR | ₹ |
| CNY | ¥ |
