#!/usr/bin/env python3
"""
Test script to verify the review system implementation
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_review_models():
    """Test that review models are properly imported"""
    try:
        from models import ReviewModel, ReviewTagEnum
        print("✅ ReviewModel and ReviewTagEnum imported successfully")
        
        # Test ReviewTagEnum values
        buyer_tags = [
            ReviewTagEnum.ON_TIME_DELIVERY,
            ReviewTagEnum.GOOD_QUALITY,
            ReviewTagEnum.CLEAR_COMMUNICATION,
            ReviewTagEnum.LATE_DELIVERY,
            ReviewTagEnum.POOR_QUALITY
        ]
        
        supplier_tags = [
            ReviewTagEnum.FAST_PAYMENT,
            ReviewTagEnum.CLEAR_REQUIREMENTS,
            ReviewTagEnum.PROFESSIONAL_BEHAVIOR,
            ReviewTagEnum.LATE_PAYMENT,
            ReviewTagEnum.UNCLEAR_INSTRUCTIONS
        ]
        
        print(f"✅ Buyer tags: {[tag.value for tag in buyer_tags]}")
        print(f"✅ Supplier tags: {[tag.value for tag in supplier_tags]}")
        
        # Test ReviewModel creation
        from datetime import datetime
        review = ReviewModel(
            transaction_id="TEST123",
            reviewer_id="user123",
            reviewee_id="user456",
            reviewer_role="BUYER",
            reviewee_company="Test Company",
            selected_tags=["On-time Delivery", "Good Quality"],
            comment="Great service!"
        )
        
        print("✅ ReviewModel creation successful")
        print(f"   Review ID: {review.id}")
        print(f"   Transaction: {review.transaction_id}")
        print(f"   Tags: {review.selected_tags}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing review models: {e}")
        return False

def test_review_submission_request():
    """Test ReviewSubmissionRequest model"""
    try:
        # Check if the model is defined correctly by looking at the source
        with open("main.py", "r", encoding='utf-8') as f:
            content = f.read()
            
        if "class ReviewSubmissionRequest(BaseModel):" in content:
            print("✅ ReviewSubmissionRequest model found in main.py")
            
            # Count occurrences to ensure no duplicates
            count = content.count("class ReviewSubmissionRequest(BaseModel):")
            if count == 1:
                print("✅ No duplicate ReviewSubmissionRequest models")
            else:
                print(f"❌ Found {count} ReviewSubmissionRequest models (should be 1)")
                return False
        else:
            print("❌ ReviewSubmissionRequest model not found in main.py")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing ReviewSubmissionRequest: {e}")
        return False

def test_api_routes():
    """Test that review API routes are defined"""
    try:
        with open("main.py", "r", encoding='utf-8') as f:
            content = f.read()
            
        routes_to_check = [
            '@app.post("/api/review/submit")',
            '@app.get("/api/review/check/{transaction_id}")'
        ]
        
        for route in routes_to_check:
            if route in content:
                print(f"✅ Found route: {route}")
            else:
                print(f"❌ Missing route: {route}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing API routes: {e}")
        return False

def test_frontend_integration():
    """Test that frontend files have review integration"""
    try:
        # Check buyer_orders.html
        with open("../frontend/src/pages/buyer_orders.html", "r", encoding='utf-8') as f:
            buyer_content = f.read()
            
        buyer_checks = [
            'onclick="showReviewModal(',
            '    Review',
            'src="/static/js/review_modal.js"'
        ]
        
        for check in buyer_checks:
            if check in buyer_content:
                print(f"✅ buyer_orders.html has: {check}")
            else:
                print(f"❌ buyer_orders.html missing: {check}")
                return False
        
        # Check supplier_orders.html
        with open("../frontend/src/pages/supplier_orders.html", "r", encoding='utf-8') as f:
            supplier_content = f.read()
            
        supplier_checks = [
            'onclick="showReviewModal(',
            '    Review',
            'src="/static/js/review_modal.js"'
        ]
        
        for check in supplier_checks:
            if check in supplier_content:
                print(f"✅ supplier_orders.html has: {check}")
            else:
                print(f"❌ supplier_orders.html missing: {check}")
                return False
        
        # Check review_modal.js exists
        if os.path.exists("../frontend/src/components/js/review_modal.js"):
            print("✅ review_modal.js exists")
        else:
            print("❌ review_modal.js not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing frontend integration: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Review System Implementation")
    print("=" * 50)
    
    tests = [
        ("Review Models", test_review_models),
        ("Review Submission Request", test_review_submission_request),
        ("API Routes", test_api_routes),
        ("Frontend Integration", test_frontend_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Review system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)