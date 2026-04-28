/**
 * Premium Upgrade Modal
 * 
 * This script provides a reusable modal for prompting users to upgrade to Premium.
 * Include this script in any page where you want to show premium feature locks.
 * 
 * Usage:
 * 1. Include this script: <script src="/static/js/premium_modal.js"></script>
 * 2. Call showPremiumModal() when a locked feature is clicked
 */

function showPremiumModal(featureName = "this feature") {
    // Create modal HTML if it doesn't exist
    if (!document.getElementById('premiumModal')) {
        const modalHTML = `
            <div id="premiumModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden transform transition-all">
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-8 text-center">
                        <div class="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-4">
                            <svg class="w-10 h-10 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                            </svg>
                        </div>
                        <h3 class="text-2xl font-bold text-white">Premium Feature</h3>
                    </div>
                    
                    <!-- Body -->
                    <div class="px-6 py-6">
                        <div class="text-center mb-6">
                            <p class="text-lg text-gray-800 font-semibold mb-2">Upgrade to Premium to access</p>
                            <p id="featureName" class="text-xl text-purple-700 font-bold"></p>
                        </div>
                        
                        <div class="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 mb-6">
                            <p class="text-sm text-gray-700 font-semibold mb-3">Premium includes:</p>
                            <ul class="space-y-2 text-sm text-gray-700">
                                <li class="flex items-center">
                                    <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                    Reverse Auction Access
                                </li>
                                <li class="flex items-center">
                                    <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                    AI-Based Recommendations
                                </li>
                                <li class="flex items-center">
                                    <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                    Order Analytics Dashboard
                                </li>
                                <li class="flex items-center">
                                    <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                    Automated Contract Generation
                                </li>
                            </ul>
                        </div>
                        
                        <div class="text-center mb-4">
                            <p class="text-3xl font-bold text-gray-900">$99<span class="text-lg text-gray-600">/month</span></p>
                        </div>
                        
                        <!-- Buttons -->
                        <div class="space-y-3">
                            <a href="/pricing" class="block w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-lg text-center transition-all shadow-lg hover:shadow-xl">
                                Upgrade Now
                            </a>
                            <button onclick="closePremiumModal()" class="block w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition-colors">
                                Maybe Later
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    // Update feature name and show modal
    document.getElementById('featureName').textContent = featureName;
    document.getElementById('premiumModal').classList.remove('hidden');
}

function closePremiumModal() {
    const modal = document.getElementById('premiumModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('premiumModal');
    if (modal && event.target === modal) {
        closePremiumModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closePremiumModal();
    }
});
