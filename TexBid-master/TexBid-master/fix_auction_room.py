#!/usr/bin/env python3
"""
Script to fix the auction room delete button issue.
This adds the Actions column with delete buttons to the dynamic leaderboard updates.
"""

def fix_auction_room():
    file_path = 'frontend/src/pages/auction_room.html'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The old code (without Actions column)
    old_code = """                    if (data.bids.length > 0) {
                        bidsTable.innerHTML = data.bids.map((bid, index) => `
                            <tr class="border-b border-slate-200 hover:bg-slate-50 transition ${index === 0 ? 'bg-green-50 border-l-4 border-l-green-600' : ''}">
                                <td class="px-6 py-4">
                                    <span class="inline-flex items-center justify-center bg-slate-700 text-white font-bold px-3 py-1 rounded-full text-sm ${index === 0 ? 'bg-green-600' : ''}">
                                        #${index + 1}
                                    </span>
                                </td>
                                <td class="px-6 py-4 font-mono text-xs text-gray-700">${bid.supplier_id || '—'}</td>
                                <td class="px-6 py-4 font-semibold text-gray-900">${bid.supplier_name}</td>
                                <td class="px-6 py-4 text-right">
                                    <span class="text-lg font-bold ${index === 0 ? 'text-green-600' : 'text-gray-800'}">
                                        ${bid.bid_price.toFixed(2)}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-center text-xs text-gray-500">
                                    ${new Date(bid.timestamp).toLocaleDateString()}
                                </td>
                            </tr>
                        `).join('');
                    }"""
    
    # The new code (with Actions column and delete button)
    new_code = """                    if (data.bids.length > 0) {
                        bidsTable.innerHTML = data.bids.map((bid, index) => {
                            const isOwnBid = userCompanyId && bid.supplier_id === userCompanyId;
                            const deleteButton = isOwnBid 
                                ? `<button onclick="deleteBid('${bid.id || ''}')" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-xs font-semibold transition-colors">Delete</button>`
                                : `<span class="text-gray-400 text-xs">—</span>`;
                            
                            return `
                            <tr class="border-b border-slate-200 hover:bg-slate-50 transition ${index === 0 ? 'bg-green-50 border-l-4 border-l-green-600' : ''}">
                                <td class="px-6 py-4">
                                    <span class="inline-flex items-center justify-center bg-slate-700 text-white font-bold px-3 py-1 rounded-full text-sm ${index === 0 ? 'bg-green-600' : ''}">
                                        #${index + 1}
                                    </span>
                                </td>
                                <td class="px-6 py-4 font-mono text-xs text-gray-700">${bid.supplier_id || '—'}</td>
                                <td class="px-6 py-4 font-semibold text-gray-900">${bid.supplier_name}</td>
                                <td class="px-6 py-4 text-right">
                                    <span class="text-lg font-bold ${index === 0 ? 'text-green-600' : 'text-gray-800'}">
                                        $${bid.bid_price.toFixed(2)}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-center text-xs text-gray-500">
                                    ${new Date(bid.timestamp).toLocaleDateString()}
                                </td>
                                <td class="px-6 py-4 text-center">
                                    ${deleteButton}
                                </td>
                            </tr>
                        `}).join('');
                    }"""
    
    # Check if old code exists
    if old_code in content:
        print("✅ Found the code to replace!")
        new_content = content.replace(old_code, new_code)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ File updated successfully!")
        print("✅ Delete buttons will now persist when leaderboard refreshes!")
        print("\n📝 Next steps:")
        print("1. Clear your browser cache (Ctrl + Shift + Delete)")
        print("2. Refresh the auction page (Ctrl + F5)")
        print("3. Place a bid and watch the delete button stay after 3 seconds!")
        return True
    else:
        print("❌ Could not find the exact code to replace")
        print("The file might have been modified already or has different formatting")
        print(f"File length: {len(content)} characters")
        
        # Try to find similar patterns
        if "bidsTable.innerHTML = data.bids.map" in content:
            print("\n⚠️  Found similar code but formatting doesn't match exactly")
            print("Please check HOW_TO_ADD_DELETE_BUTTON.md for manual instructions")
        return False

if __name__ == "__main__":
    print("🔧 Fixing auction room delete button issue...")
    print("=" * 60)
    fix_auction_room()
