// FIXED updateAuctionStatus function
// Replace the existing function in auction_room.html (around line 248-280)

async function updateAuctionStatus() {
    try {
        const response = await fetch(`/api/auction/${rfqId}/status`);
        const data = await response.json();

        if (data.success && data.bids) {
            const bidsTable = document.getElementById('bids-table');
            if (data.bids.length > 0) {
                bidsTable.innerHTML = data.bids.map((bid, index) => {
                    // Check if this bid belongs to the logged-in user
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
            }
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}
