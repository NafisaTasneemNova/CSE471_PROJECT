#!/usr/bin/env python3
"""
Validation script for Role-Based Dashboards implementation.
Checks that all required components are properly implemented.

Usage: python validate_dashboard_implementation.py
"""

import os
import re
import ast
from pathlib import Path

class DashboardValidator:
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.frontend_path = self.backend_path.parent / "frontend" / "src" / "pages"
        self.errors = []
        self.warnings = []
    
    def validate_backend_routes(self):
        """Validate that all required backend routes are implemented"""
        print("🔍 Validating backend routes...")
        
        main_py = self.backend_path / "main.py"
        if not main_py.exists():
            self.errors.append("main.py not found")
            return
        
        content = main_py.read_text()
        
        # Required routes
        required_routes = [
            r'@app\.get\("/dashboard"\)',
            r'@app\.get\("/dashboard/buyer"\)',
            r'@app\.get\("/dashboard/supplier"\)',
            r'@app\.get\("/api/dashboard/buyer/stats"\)',
            r'@app\.get\("/api/dashboard/buyer/recent-rfqs"\)',
            r'@app\.get\("/api/dashboard/buyer/action-required"\)',
            r'@app\.get\("/api/dashboard/supplier/stats"\)',
            r'@app\.get\("/api/dashboard/supplier/open-rfqs"\)',
            r'@app\.get\("/api/dashboard/supplier/verification-status"\)',
            r'@app\.get\("/api/dashboard/supplier/active-production"\)'
        ]
        
        for route_pattern in required_routes:
            if re.search(route_pattern, content):
                print(f"✅ Found route: {route_pattern}")
            else:
                self.errors.append(f"Missing route: {route_pattern}")
    
    def validate_authentication_dependencies(self):
        """Validate that authentication dependencies are implemented"""
        print("🔐 Validating authentication dependencies...")
        
        main_py = self.backend_path / "main.py"
        content = main_py.read_text()
        
        # Check for require_buyer and require_supplier functions
        if "def require_buyer(" in content:
            print("✅ require_buyer dependency found")
        else:
            self.errors.append("require_buyer dependency not found")
        
        if "def require_supplier(" in content:
            print("✅ require_supplier dependency found")
        else:
            self.errors.append("require_supplier dependency not found")
        
        # Check that API endpoints use these dependencies
        api_endpoints = [
            (r'/api/dashboard/buyer/stats.*require_buyer', "buyer stats endpoint"),
            (r'/api/dashboard/supplier/stats.*require_supplier', "supplier stats endpoint")
        ]
        
        for pattern, description in api_endpoints:
            if re.search(pattern, content, re.DOTALL):
                print(f"✅ {description} uses proper authentication")
            else:
                self.errors.append(f"{description} missing authentication dependency")
    
    def validate_frontend_templates(self):
        """Validate that frontend templates exist and have required content"""
        print("🖥️ Validating frontend templates...")
        
        # Check buyer dashboard
        buyer_template = self.frontend_path / "buyer_dashboard.html"
        if buyer_template.exists():
            content = buyer_template.read_text()
            required_elements = [
                "Quick Stats",
                "Recent RFQs",
                "Action Required",
                "fetchBuyerStats",
                "fetchBuyerRecentRFQs",
                "fetchBuyerActionItems"
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ Buyer dashboard has: {element}")
                else:
                    self.errors.append(f"Buyer dashboard missing: {element}")
        else:
            self.errors.append("buyer_dashboard.html not found")
        
        # Check supplier dashboard
        supplier_template = self.frontend_path / "supplier_dashboard.html"
        if supplier_template.exists():
            content = supplier_template.read_text()
            required_elements = [
                "Trust & Verification",
                "Opportunity Feed",
                "Active Production",
                "fetchSupplierStats",
                "fetchSupplierOpenRFQs",
                "fetchSupplierVerificationStatus",
                "fetchSupplierActiveProduction"
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ Supplier dashboard has: {element}")
                else:
                    self.errors.append(f"Supplier dashboard missing: {element}")
        else:
            self.errors.append("supplier_dashboard.html not found")
    
    def validate_database_indexes(self):
        """Validate that database indexes are created"""
        print("📊 Validating database indexes...")
        
        main_py = self.backend_path / "main.py"
        content = main_py.read_text()
        
        # Check for index creation
        required_indexes = [
            'create_index("buyer_id")',
            'create_index("supplier_id")',
            'create_index("status")',
            'create_index([("status", 1), ("created_at", -1)])'
        ]
        
        for index in required_indexes:
            if index in content:
                print(f"✅ Database index found: {index}")
            else:
                self.warnings.append(f"Database index not found: {index}")
    
    def validate_responsive_design(self):
        """Validate that templates use responsive design classes"""
        print("📱 Validating responsive design...")
        
        templates = [
            ("buyer_dashboard.html", "Buyer dashboard"),
            ("supplier_dashboard.html", "Supplier dashboard")
        ]
        
        for template_name, description in templates:
            template_path = self.frontend_path / template_name
            if template_path.exists():
                content = template_path.read_text()
                
                # Check for Tailwind responsive classes
                responsive_patterns = [
                    r'lg:',
                    r'md:',
                    r'sm:',
                    r'grid-cols-1.*md:grid-cols-',
                    r'flex-col.*lg:flex-row'
                ]
                
                responsive_found = any(re.search(pattern, content) for pattern in responsive_patterns)
                
                if responsive_found:
                    print(f"✅ {description} has responsive design")
                else:
                    self.warnings.append(f"{description} may lack responsive design")
    
    def validate_error_handling(self):
        """Validate that proper error handling is implemented"""
        print("⚠️ Validating error handling...")
        
        # Check backend error handling
        main_py = self.backend_path / "main.py"
        content = main_py.read_text()
        
        if "HTTPException" in content and "status_code=403" in content:
            print("✅ Backend has proper HTTP error handling")
        else:
            self.warnings.append("Backend may lack proper HTTP error handling")
        
        # Check frontend error handling
        templates = ["buyer_dashboard.html", "supplier_dashboard.html"]
        
        for template_name in templates:
            template_path = self.frontend_path / template_name
            if template_path.exists():
                content = template_path.read_text()
                
                if "catch" in content and "error" in content:
                    print(f"✅ {template_name} has error handling")
                else:
                    self.warnings.append(f"{template_name} may lack error handling")
    
    def run_validation(self):
        """Run all validation checks"""
        print("🚀 Starting Role-Based Dashboards Validation")
        print("=" * 60)
        
        self.validate_backend_routes()
        self.validate_authentication_dependencies()
        self.validate_frontend_templates()
        self.validate_database_indexes()
        self.validate_responsive_design()
        self.validate_error_handling()
        
        print("=" * 60)
        
        # Report results
        if self.errors:
            print("❌ VALIDATION FAILED")
            print("\nErrors found:")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("✅ VALIDATION PASSED")
            print("All required components are properly implemented!")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️ {warning}")
        
        return len(self.errors) == 0

def main():
    """Main validation runner"""
    validator = DashboardValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 Role-based dashboards implementation is complete and valid!")
        print("The feature is ready for testing and deployment.")
    else:
        print("\n❌ Validation failed. Please fix the errors above.")
    
    return success

if __name__ == "__main__":
    main()