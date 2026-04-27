#!/usr/bin/env python3
"""
Script to fix the auction room delete button issue - Version 2
Uses regex to handle formatting variations
"""
import re

def fix_auction_room():
    file_path = 'frontend/src/pages/auction_room.html'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the section to replace using a more flexible pattern
    # Look for the map function and replace everything until the join
    pattern = r"(bidsTable\.innerHTML = data\.bids\.map\(\(bid, index\) => )`\s*<tr class=\"border-b border-slate-200.*?`\)\.join\(''\);"
    
    replacement = r"""\1{
                            const isOwnBid = userCompanyId && bid.supplier_id === userCompanyId;
                            const deleteButton = isOwnBid 
                                ? `<button onclick="deleteBid('$\{bid.id || ''}')\" class=\"bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-xs font-semibold transition-colors\">Delete</button>`
                                : `<span class=\"text-gray-400 text-xs\">—</span>`;
                            
                            return `
                            <tr class="border-b border-slate-200 hover:bg-slate-50 transition $\{index === 0 ? 'bg-green-50 border-l-4 border-l-green-600' : ''}">
                                <td class="px-6 py-4">
                                    <span class="inline-flex items-center justify-center bg-slate-700 text-white font-bold px-3 py-1 rounded-full text-sm $\{index === 0 ? 'bg-green-600' : ''}">
                                        #$\{index + 1}
                                    </span>
                                </td>
                                <td class="px-6 py-4 font-mono text-xs text-gray-700">$\{bid.supplier_id || '—'}</td>
                                <td class="px-6 py-4 font-semibold text-gray-900">$\{bid.supplier_name}</td>
                                <td class="px-6 py-4 text-right">
                                    <span class="text-lg font-bold $\{index === 0 ? 'text-green-600' : 'text-gray-800'}">
                                        $$\{bid.bid_price.toFixed(2)}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-center text-xs text-gray-500">
                                    $\{new Date(bid.timestamp).toLocaleDateString()}
                                </td>
                                <td class="px-6 py-4 text-center">
                                    $\{deleteButton}
                                </td>
                            </tr>
                        `}).join('');"""
    
    # Try to find and replace
    if re.search(pattern, content, re.DOTALL):
        print("✅ Found the code pattern!")
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
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
        print("❌ Could not find the pattern")
        print("Let me try a simpler approach...")
        
        # Simpler approach - just find and insert the Actions column
        if '<td class="px-6 py-4 text-center text-xs text-gray-500">' in content and \
           '${new Date(bid.timestamp).toLocaleDateString()}' in content:
            print("✅ Found the timestamp column, will add Actions column after it")
            
            # Find the closing </td> after the timestamp
            old_timestamp = '''<td class="px-6 py-4 text-center text-xs text-gray-500">
                                    ${new Date(bid.timestamp).toLocaleDateString()}
                                </td>
                            </tr>
                        `).join('');'''
            
            new_timestamp = '''<td class="px-6 py-4 text-center text-xs text-gray-500">
                                    ${new Date(bid.timestamp).toLocaleDateString()}
                                </td>
                                <td class="px-6 py-4 text-center">
                                    ${deleteButton}
                                </td>
                            </tr>
                        `}).join('');'''
            
            if old_timestamp in content:
                # Also need to add the deleteButton logic
                old_map_start = "bidsTable.innerHTML = data.bids.map((bid, index) => `"
                new_map_start = """bidsTable.innerHTML = data.bids.map((bid, index) => {
                            const isOwnBid = userCompanyId && bid.supplier_id === userCompanyId;
                            const deleteButton = isOwnBid 
                                ? `<button onclick="deleteBid('${bid.id || ''}')" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-xs font-semibold transition-colors">Delete</button>`
                                : `<span class="text-gray-400 text-xs">—</span>`;
                            
                            return `"""
                
                content = content.replace(old_map_start, new_map_start)
                content = content.replace(old_timestamp, new_timestamp)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ File updated successfully using simpler approach!")
                return True
        
        return False

if __name__ == "__main__":
    print("🔧 Fixing auction room delete button issue (v2)...")
    print("=" * 60)
    fix_auction_room()
