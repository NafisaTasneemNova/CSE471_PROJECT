#!/usr/bin/env python3
"""
Fix the template literal issue in auction_room.html
The problem is that ${} is being escaped incorrectly
"""

def fix_template_literals():
    file_path = 'frontend/src/pages/auction_room.html'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is that ${ is being written as $\{ which doesn't work in JavaScript
    # We need to replace $\{ with ${ in the JavaScript section
    
    # Find the updateAuctionStatus function and fix the template literals
    content = content.replace('$\\{index', '${index')
    content = content.replace('$\\{bid.', '${bid.')
    content = content.replace('$\\{new Date', '${new Date')
    content = content.replace('$\\{deleteButton}', '${deleteButton}')
    content = content.replace('$$\\{bid.bid_price', '$${bid.bid_price')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed template literals!")
    print("✅ The leaderboard should now display correctly!")
    print("\n📝 Clear cache and refresh to see the fix!")

if __name__ == "__main__":
    print("🔧 Fixing template literal escaping...")
    print("=" * 60)
    fix_template_literals()
