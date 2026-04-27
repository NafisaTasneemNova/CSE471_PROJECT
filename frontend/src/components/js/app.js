document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle logic
    const mobileBtn = document.querySelector('nav button');
    const navBar = document.querySelector('nav');

    // Smooth transition effect on navbar on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            navBar.classList.add('shadow-lg', 'bg-opacity-95');
            navBar.classList.remove('shadow-md', 'bg-opacity-100');
        } else {
            navBar.classList.add('shadow-md', 'bg-opacity-100');
            navBar.classList.remove('shadow-lg', 'bg-opacity-95');
        }
    });

    // Logging initialization
    console.log("TexBid Premium Interface Initialized.");

    // Enforce UI-level RBAC
    const currentRole = document.body.getAttribute('data-current-role');
    if (currentRole && currentRole !== 'guest') {
        applyUI_RBAC(currentRole);
    }
});
/**
 * Utility function to enforce UI-level Role-Based Access Control (RBAC).
 * Scans the DOM for elements with a `data-role` attribute. If the `currentRole`
 * does not match the element's `data-role` (case-insensitive), the element is hidden.
 * 
 * @param {string} currentRole - The role of the currently logged-in user.
 */
function applyUI_RBAC(currentRole) {
    if (!currentRole) return;
    const role = currentRole.toUpperCase();
    
    // Find all elements with a data-role attribute
    const restrictedElements = document.querySelectorAll('[data-role]');
    
    restrictedElements.forEach(el => {
        const requiredRole = el.getAttribute('data-role').toUpperCase();
        
        // If the current role doesn't match the required role (and it's not a generic ADMIN override scenario)
        if (role !== requiredRole && role !== 'ADMIN') {
            el.classList.add('hidden');
        } else {
            // Optional: If you want to ensure it's unhidden if the role is correct and was previously hidden
            // el.classList.remove('hidden');
        }
    });
}
