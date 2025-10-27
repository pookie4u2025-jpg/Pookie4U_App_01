#!/usr/bin/env python3
"""
Backend Testing Suite for Pookie4u Gifts Endpoint
Testing the gifts endpoint to ensure all 99 gift items are loaded correctly
"""

import requests
import json
import sys
from typing import Dict, List, Any
from collections import Counter

# Configuration
BACKEND_URL = "https://couple-referrals.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class GiftsEndpointTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        
        self.test_results.append(result)
        print(result)
        
    def test_gifts_endpoint_basic(self):
        """Test basic gifts endpoint functionality"""
        print("\n🎁 TESTING GIFTS ENDPOINT BASIC FUNCTIONALITY")
        print("=" * 60)
        
        try:
            response = requests.get(f"{API_BASE}/gifts", timeout=10)
            
            # Test 1: Status Code
            self.log_test(
                "GET /api/gifts returns 200 status",
                response.status_code == 200,
                f"Got status {response.status_code}"
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Response content check",
                    False,
                    f"Error response: {response.text[:200]}"
                )
                return None
                
            # Test 2: JSON Response
            try:
                data = response.json()
                self.log_test("Response is valid JSON", True)
            except json.JSONDecodeError as e:
                self.log_test("Response is valid JSON", False, f"JSON decode error: {e}")
                return None
                
            # Test 3: Response contains gifts array
            has_gifts_array = isinstance(data, list) or 'gifts' in data
            if isinstance(data, list):
                gifts = data
                self.log_test("Response contains gifts array", True, "Response is direct array")
            elif 'gifts' in data:
                gifts = data['gifts']
                self.log_test("Response contains gifts array", True, "Response has 'gifts' key")
            else:
                self.log_test("Response contains gifts array", False, f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return None
                
            # Test 4: Total count is 99 gifts
            gift_count = len(gifts)
            self.log_test(
                "Total count is 99 gifts",
                gift_count == 99,
                f"Found {gift_count} gifts"
            )
            
            return gifts
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/gifts endpoint accessible", False, f"Request error: {e}")
            return None
            
    def test_gift_structure(self, gifts: List[Dict[str, Any]]):
        """Test structure of each gift item"""
        print("\n🔍 TESTING GIFT ITEM STRUCTURE")
        print("=" * 60)
        
        required_fields = ['id', 'name', 'category', 'price_range', 'link', 'description', 'image']
        
        # Test 5: All gifts have required fields
        missing_fields_count = 0
        sample_gift = None
        
        for i, gift in enumerate(gifts[:10]):  # Check first 10 for detailed analysis
            if sample_gift is None:
                sample_gift = gift
                
            missing_fields = [field for field in required_fields if field not in gift or not gift[field]]
            if missing_fields:
                missing_fields_count += 1
                if i < 3:  # Log first 3 failures
                    self.log_test(
                        f"Gift {gift.get('id', i+1)} has all required fields",
                        False,
                        f"Missing: {missing_fields}"
                    )
        
        self.log_test(
            "All gifts have required fields (id, name, category, price_range, link, description, image)",
            missing_fields_count == 0,
            f"{missing_fields_count} gifts missing fields" if missing_fields_count > 0 else "All gifts have complete structure"
        )
        
        # Show sample gift structure
        if sample_gift:
            print(f"\n📋 Sample Gift Structure (ID: {sample_gift.get('id', 'Unknown')}):")
            for field in required_fields:
                value = sample_gift.get(field, 'MISSING')
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"  {field}: {value}")
                
    def test_gift_categories(self, gifts: List[Dict[str, Any]]):
        """Test gift categories"""
        print("\n📂 TESTING GIFT CATEGORIES")
        print("=" * 60)
        
        expected_categories = {
            'Romantic', 'Chocolates', 'Footwear', 'Watches', 'Jewelry', 
            'Soft Toys', 'Health & Wellness', 'Beauty', 'Home', 'Fashion'
        }
        
        # Get all categories from gifts
        found_categories = set()
        category_counts = Counter()
        
        for gift in gifts:
            category = gift.get('category', '')
            if category:
                found_categories.add(category)
                category_counts[category] += 1
                
        # Test 6: All expected categories present
        missing_categories = expected_categories - found_categories
        extra_categories = found_categories - expected_categories
        
        self.log_test(
            "All expected categories present",
            len(missing_categories) == 0,
            f"Missing: {missing_categories}" if missing_categories else "All categories found"
        )
        
        if extra_categories:
            self.log_test(
                "No unexpected categories",
                len(extra_categories) == 0,
                f"Extra categories: {extra_categories}"
            )
        else:
            self.log_test("No unexpected categories", True)
            
        # Show category distribution
        print(f"\n📊 Category Distribution:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count} items")
            
    def test_amazon_links(self, gifts: List[Dict[str, Any]]):
        """Test Amazon links format and presence"""
        print("\n🔗 TESTING AMAZON LINKS")
        print("=" * 60)
        
        valid_amazon_prefixes = ['https://www.amazon.in', 'https://amzn.to']
        
        invalid_links = []
        missing_links = []
        
        for gift in gifts:
            link = gift.get('link', '')
            gift_id = gift.get('id', 'Unknown')
            
            if not link:
                missing_links.append(gift_id)
            elif not any(link.startswith(prefix) for prefix in valid_amazon_prefixes):
                invalid_links.append((gift_id, link))
                
        # Test 7: All gifts have Amazon links
        self.log_test(
            "All gifts have Amazon links",
            len(missing_links) == 0,
            f"{len(missing_links)} gifts missing links: {missing_links[:5]}" if missing_links else "All gifts have links"
        )
        
        # Test 8: All links are valid Amazon format
        self.log_test(
            "All Amazon links are in correct format",
            len(invalid_links) == 0,
            f"{len(invalid_links)} invalid links found" if invalid_links else "All links are valid Amazon URLs"
        )
        
        if invalid_links and len(invalid_links) <= 3:
            print("  Invalid link examples:")
            for gift_id, link in invalid_links[:3]:
                print(f"    Gift {gift_id}: {link[:60]}...")
                
    def test_data_integrity(self, gifts: List[Dict[str, Any]]):
        """Test data integrity"""
        print("\n🔍 TESTING DATA INTEGRITY")
        print("=" * 60)
        
        # Test 9: No duplicate IDs
        gift_ids = [gift.get('id', '') for gift in gifts]
        id_counts = Counter(gift_ids)
        duplicate_ids = [gift_id for gift_id, count in id_counts.items() if count > 1]
        
        self.log_test(
            "No duplicate gift IDs",
            len(duplicate_ids) == 0,
            f"Duplicate IDs: {duplicate_ids}" if duplicate_ids else "All IDs are unique"
        )
        
        # Test 10: ID range verification (should be 1-99)
        try:
            numeric_ids = [int(gift_id) for gift_id in gift_ids if str(gift_id).isdigit()]
            expected_ids = set(range(1, 100))  # 1 to 99
            found_ids = set(numeric_ids)
            
            missing_ids = expected_ids - found_ids
            extra_ids = found_ids - expected_ids
            
            self.log_test(
                "Gift IDs are in range 1-99",
                len(missing_ids) == 0 and len(extra_ids) == 0,
                f"Missing: {sorted(list(missing_ids))[:10]}, Extra: {sorted(list(extra_ids))[:10]}" if missing_ids or extra_ids else "All IDs 1-99 present"
            )
            
        except ValueError as e:
            self.log_test("Gift IDs are numeric", False, f"Non-numeric IDs found: {e}")
            
        # Test 11: New Amazon gift items (IDs 7-99) verification
        new_gift_ids = [gift_id for gift_id in gift_ids if str(gift_id).isdigit() and int(gift_id) >= 7]
        self.log_test(
            "New Amazon gift items (IDs 7-99) are present",
            len(new_gift_ids) >= 93,  # Should have at least 93 items (7-99)
            f"Found {len(new_gift_ids)} items with ID >= 7"
        )
        
    def test_specific_requirements(self, gifts: List[Dict[str, Any]]):
        """Test specific requirements from review request"""
        print("\n✅ TESTING SPECIFIC REQUIREMENTS")
        print("=" * 60)
        
        # Test 12: Verify images are present and not duplicated
        images = [gift.get('image', '') for gift in gifts if gift.get('image')]
        image_counts = Counter(images)
        duplicate_images = [img for img, count in image_counts.items() if count > 1]
        
        self.log_test(
            "All gifts have unique images",
            len(duplicate_images) == 0,
            f"{len(duplicate_images)} duplicate images found" if duplicate_images else "All images are unique"
        )
        
        # Test 13: Verify Amazon CDN images
        amazon_cdn_images = [img for img in images if 'amazon.com' in img or 'media-amazon' in img]
        self.log_test(
            "Amazon product images from CDN",
            len(amazon_cdn_images) > 0,
            f"Found {len(amazon_cdn_images)} Amazon CDN images out of {len(images)} total"
        )
        
        # Test 14: Price range format verification
        price_ranges = [gift.get('price_range', '') for gift in gifts]
        valid_price_formats = ['Under ₹', '₹', 'Free']
        
        invalid_prices = []
        for i, price in enumerate(price_ranges):
            if not any(format_str in price for format_str in valid_price_formats):
                invalid_prices.append((gifts[i].get('id', i+1), price))
                
        self.log_test(
            "All price ranges are in Indian Rupee format",
            len(invalid_prices) == 0,
            f"{len(invalid_prices)} invalid price formats" if invalid_prices else "All prices in ₹ format"
        )
        
    def run_all_tests(self):
        """Run all tests"""
        print("🎁 GIFTS ENDPOINT COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"Testing endpoint: {API_BASE}/gifts")
        print(f"Expected: 99 gift items with complete Amazon product data")
        print("=" * 60)
        
        # Test basic functionality
        gifts = self.test_gifts_endpoint_basic()
        
        if gifts is None:
            print("\n❌ CRITICAL: Cannot proceed with detailed tests - basic endpoint failed")
            self.print_summary()
            return
            
        # Run detailed tests
        self.test_gift_structure(gifts)
        self.test_gift_categories(gifts)
        self.test_amazon_links(gifts)
        self.test_data_integrity(gifts)
        self.test_specific_requirements(gifts)
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 GIFTS ENDPOINT TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED! Gifts endpoint is working perfectly.")
        elif success_rate >= 90:
            print(f"\n✅ EXCELLENT! {success_rate:.1f}% success rate - minor issues only.")
        elif success_rate >= 75:
            print(f"\n⚠️  GOOD with issues: {success_rate:.1f}% success rate - some problems need attention.")
        else:
            print(f"\n❌ CRITICAL ISSUES: {success_rate:.1f}% success rate - major problems found.")
            
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")

def main():
    """Main test execution"""
    tester = GiftsEndpointTester()
    tester.run_all_tests()
    
    # Return exit code based on success rate
    success_rate = (tester.passed_tests / tester.total_tests * 100) if tester.total_tests > 0 else 0
    sys.exit(0 if success_rate >= 90 else 1)

if __name__ == "__main__":
    main()