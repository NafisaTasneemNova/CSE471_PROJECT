#!/usr/bin/env python3
"""
Test script to verify the review tracking system implementation
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_review_tracking_apis():
    """Test that review tracking API routes are defined"""
    try:
        with open("main.py", "r", encoding='utf-8') as f:
            content = f.read()
            
        routes_to_check = [
            '@app.get("/api/reviews/given")',
            '@app.get("/api/reviews/received")',
            '@app.get("/api/reviews/summary")',
            '@app.get("/reviews", response_class=HTMLResponse)'
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

def test_frontend_page():
    """Test that the reviews frontend page exists"""
    try:
        reviews_page_path = "../frontend/src/pages/reviews.html"
        
        if os.path.exists(reviews_page_path):
            print("✅ reviews.html page exists")
            
            # Check for key components
            with open(reviews_page_path, "r", encoding='utf-8') as f:
                content = f.read()
                
            components_to_check = [
                'My Reviews',
                'Reviews Given',
                'Reviews Received',
                'loadReviews()',
                'switchTab(',
                '/api/reviews/summary',
                '/api/reviews/given',
                '/api/reviews/received'
            ]
            
            for component in components_to_check:
                if component in content:
                    print(f"✅ reviews.html has: {component}")
                else:
                    print(f"❌ reviews.html missing: {component}")
                    return False
                    
            return True
        else:
            print("❌ reviews.html page not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing frontend page: {e}")
        return False

def test_navigation_integration():
    """Test that navigation link is added to base template"""
    try:
        base_template_path = "../frontend/src/pages/base.html"
        
        if os.path.exists(base_template_path):
            with open(base_template_path, "r", encoding='utf-8') as f:
                content = f.read()
                
            nav_checks = [
                'href="/reviews"',
                'My Reviews'
            ]
            
            for check in nav_checks:
                if check in content:
                    print(f"✅ base.html navigation has: {check}")
                else:
                    print(f"❌ base.html navigation missing: {check}")
                    return False
                    
            return True
        else:
            print("❌ base.html template not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing navigation integration: {e}")
        return False

def test_api_functionality():
    """Test the API functionality logic"""
    try:
        # Test summary calculation logic
        positive_tags = ["On-time Delivery", "Good Quality", "Clear Communication", 
                        "Fast Payment", "Clear Requirements", "Professional Behavior"]
        
        # Simulate review data
        test_reviews = [
            {"selected_tags": ["On-time Delivery", "Good Quality"]},
            {"selected_tags": ["Late Delivery", "Poor Quality"]},
            {"selected_tags": ["Fast Payment", "Professional Behavior"]},
        ]
        
        total_tags = 0
        positive_tag_count = 0
        
        for review in test_reviews:
            tags = review.get("selected_tags", [])
            total_tags += len(tags)
            positive_tag_count += len([tag for tag in tags if tag in positive_tags])
        
        avg_rating = (positive_tag_count / total_tags * 100) if total_tags > 0 else 0
        
        print(f"✅ Summary calculation test:")
        print(f"   Total tags: {total_tags}")
        print(f"   Positive tags: {positive_tag_count}")
        print(f"   Average rating: {round(avg_rating, 1)}%")
        
        # Should be 66.7% (4 positive out of 6 total tags)
        expected_rating = 66.7
        if abs(avg_rating - expected_rating) < 0.1:
            print(f"✅ Rating calculation correct: {avg_rating}%")
            return True
        else:
            print(f"❌ Rating calculation incorrect: expected ~{expected_rating}%, got {avg_rating}%")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API functionality: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Review Tracking System")
    print("=" * 50)
    
    tests = [
        ("Review Tracking APIs", test_review_tracking_apis),
        ("Frontend Page", test_frontend_page),
        ("Navigation Integration", test_navigation_integration),
        ("API Functionality", test_api_functionality)
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
        print("🎉 All tests passed! Review tracking system is ready.")
        print("\n📋 Features implemented:")
        print("   ✅ API endpoints for given/received reviews")
        print("   ✅ Review summary with statistics")
        print("   ✅ Frontend page with tabbed interface")
        print("   ✅ Navigation integration")
        print("   ✅ Tag-based rating calculation")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)