/**
 * Review Modal Component
 * 
 * Tag-based review system for TexBid transactions
 * Usage: Call showReviewModal(transactionId) when Review button is clicked
 */

let currentTransactionId = null;
let currentUserRole = null;
let currentCompanyName = null;

// Tag definitions based on user role
const REVIEW_TAGS = {
    BUYER: {
        positive: [
            { id: 'On-time Delivery', label: 'On-time Delivery', type: 'positive' },
            { id: 'Good Quality', label: 'Good Quality', type: 'positive' },
            { id: 'Clear Communication', label: 'Clear Communication', type: 'positive' }
        ],
        negative: [
            { id: 'Late Delivery', label: 'Late Delivery', type: 'negative' },
            { id: 'Poor Quality', label: 'Poor Quality', type: 'negative' }
        ]
    },
    SUPPLIER: {
        positive: [
            { id: 'Fast Payment', label: 'Fast Payment', type: 'positive' },
            { id: 'Clear Requirements', label: 'Clear Requirements', type: 'positive' },
            { id: 'Professional Behavior', label: 'Professional Behavior', type: 'positive' }
        ],
        negative: [
            { id: 'Late Payment', label: 'Late Payment', type: 'negative' },
            { id: 'Unclear Instructions', label: 'Unclear Instructions', type: 'negative' }
        ]
    }
};

async function showReviewModal(transactionId) {
    console.log('Opening review modal for transaction:', transactionId);
    currentTransactionId = transactionId;
    
    // Check if user can review this transaction
    try {
        const response = await fetch(`/api/review/check/${transactionId}`);
        const data = await response.json();
        
        if (!data.can_review) {
            showAlert('error', `Cannot leave review: ${data.reason}`);
            return;
        }
        
        currentUserRole = data.user_role;
        currentCompanyName = data.company_name;
        createReviewModal();
        document.getElementById('reviewModal').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error checking review status:', error);
        showAlert('error', 'Failed to load review form');
    }
}

function createReviewModal() {
    // Remove existing modal if present
    const existingModal = document.getElementById('reviewModal');
    if (existingModal) {
        existingModal.remove();
    }

    const tags = REVIEW_TAGS[currentUserRole];
    const roleText = currentUserRole === 'BUYER' ? 'supplier' : 'buyer';
    
    const modalHTML = `
        <div id="reviewModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden transform transition-all">
                <!-- Header -->
                <div class="bg-gradient-to-r from-purple-600 to-purple-800 px-6 py-6 text-center">
                    <div class="inline-flex items-center justify-center w-12 h-12 bg-white rounded-full mb-3">
                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-white">Review Transaction</h3>
                    <p class="text-purple-100 text-sm mt-1">Rate your experience with ${currentCompanyName}</p>
                </div>
                
                <!-- Body -->
                <div class="px-6 py-6">
                    <form id="reviewForm">
                        <!-- Transaction Info -->
                        <div class="mb-4 p-3 bg-gray-50 rounded-lg">
                            <p class="text-sm text-gray-600">Transaction: <span class="font-mono font-semibold text-gray-800">${currentTransactionId}</span></p>
                            <p class="text-sm text-gray-600">Reviewing: <span class="font-semibold text-gray-800">${currentCompanyName}</span></p>
                        </div>
                        
                        <!-- Positive Tags -->
                        <div class="mb-6">
                            <h4 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                                <svg class="w-4 h-4 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"></path>
                                </svg>
                                Positive Feedback
                            </h4>
                            <div class="flex flex-wrap gap-2">
                                ${tags.positive.map(tag => `
                                    <button type="button" 
                                            class="review-tag px-3 py-2 rounded-lg border-2 border-green-200 text-green-700 text-sm font-medium hover:bg-green-50 transition-colors"
                                            data-tag="${tag.id}" 
                                            data-type="positive">
                                        ${tag.label}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                        
                        <!-- Negative Tags -->
                        <div class="mb-6">
                            <h4 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                                <svg class="w-4 h-4 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                </svg>
                                Areas for Improvement
                            </h4>
                            <div class="flex flex-wrap gap-2">
                                ${tags.negative.map(tag => `
                                    <button type="button" 
                                            class="review-tag px-3 py-2 rounded-lg border-2 border-red-200 text-red-700 text-sm font-medium hover:bg-red-50 transition-colors"
                                            data-tag="${tag.id}" 
                                            data-type="negative">
                                        ${tag.label}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                        
                        <!-- Comment -->
                        <div class="mb-6">
                            <label for="reviewComment" class="block text-sm font-semibold text-gray-800 mb-2">
                                Additional Comments (Optional)
                            </label>
                            <textarea id="reviewComment" 
                                      rows="3" 
                                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                                      placeholder="Share more details about your experience..."></textarea>
                        </div>
                        
                        <!-- Buttons -->
                        <div class="flex gap-3">
                            <button type="button" 
                                    onclick="closeReviewModal()" 
                                    class="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg transition-colors">
                                Cancel
                            </button>
                            <button type="submit" 
                                    id="submitReviewBtn"
                                    class="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900 text-white font-semibold rounded-lg transition-all shadow-lg hover:shadow-xl">
                                Submit Review
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add event listeners
    setupReviewModalEventListeners();
}

function setupReviewModalEventListeners() {
    // Tag selection with proper color coding
    document.querySelectorAll('.review-tag').forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('selected');
            
            if (this.classList.contains('selected')) {
                if (this.dataset.type === 'positive') {
                    // Green for positive tags
                    this.classList.add('bg-green-500', 'text-white', 'border-green-500');
                    this.classList.remove('border-green-200', 'text-green-700', 'hover:bg-green-50');
                } else {
                    // Red for negative tags
                    this.classList.add('bg-red-500', 'text-white', 'border-red-500');
                    this.classList.remove('border-red-200', 'text-red-700', 'hover:bg-red-50');
                }
            } else {
                if (this.dataset.type === 'positive') {
                    this.classList.remove('bg-green-500', 'text-white', 'border-green-500');
                    this.classList.add('border-green-200', 'text-green-700', 'hover:bg-green-50');
                } else {
                    this.classList.remove('bg-red-500', 'text-white', 'border-red-500');
                    this.classList.add('border-red-200', 'text-red-700', 'hover:bg-red-50');
                }
            }
        });
    });
    
    // Form submission
    document.getElementById('reviewForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitReview();
    });
}

async function submitReview() {
    const selectedTags = Array.from(document.querySelectorAll('.review-tag.selected'))
                             .map(button => button.dataset.tag);
    
    if (selectedTags.length === 0) {
        showAlert('warning', 'Please select at least one tag for your review');
        return;
    }
    
    const comment = document.getElementById('reviewComment').value.trim();
    const submitBtn = document.getElementById('submitReviewBtn');
    
    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch('/api/review/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transaction_id: currentTransactionId,
                selected_tags: selectedTags,
                comment: comment || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showAlert('success', 'Review submitted successfully!');
            closeReviewModal();
            // Refresh the page to update the UI
            setTimeout(() => window.location.reload(), 1500);
        } else {
            showAlert('error', data.detail || 'Failed to submit review');
        }
        
    } catch (error) {
        console.error('Error submitting review:', error);
        showAlert('error', 'Network error. Please try again.');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Review';
    }
}

function closeReviewModal() {
    const modal = document.getElementById('reviewModal');
    if (modal) {
        modal.classList.add('hidden');
        setTimeout(() => modal.remove(), 300);
    }
    currentTransactionId = null;
    currentUserRole = null;
    currentCompanyName = null;
}

function showAlert(type, message) {
    // Create alert element
    const alertId = 'reviewAlert_' + Date.now();
    const alertColors = {
        success: 'bg-green-50 border-green-200 text-green-700',
        error: 'bg-red-50 border-red-200 text-red-700',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-700'
    };
    
    const alertHTML = `
        <div id="${alertId}" class="fixed top-4 right-4 z-50 max-w-sm w-full ${alertColors[type]} border rounded-lg p-4 shadow-lg transform transition-all duration-300 translate-x-full">
            <div class="flex items-center gap-3">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${type === 'success' ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>' :
                      type === 'error' ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>' :
                      '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01"/>'}
                </svg>
                <p class="text-sm font-medium">${message}</p>
                <button onclick="document.getElementById('${alertId}').remove()" class="ml-auto">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHTML);
    
    // Animate in
    setTimeout(() => {
        document.getElementById(alertId).classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.classList.add('translate-x-full');
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('reviewModal');
    if (modal && e.target === modal) {
        closeReviewModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeReviewModal();
    }
});

// Make function globally available
window.showReviewModal = showReviewModal;

console.log('Review modal script loaded successfully');