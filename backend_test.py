#!/usr/bin/env python3
"""
Backend API Testing Suite for Pookie4u Gift Ideas API
Testing the updated Gift Ideas API with Amazon affiliate links integration
"""

import requests
import json
import time
from datetime import datetime
import uuid
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://relationship-app-4.preview.emergentagent.com/api"

class GiftIdeasAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.backend_url = BACKEND_URL
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"     Details: {details}")
        if not success and response_data:
            print(f"     Response: {response_data}")
        print()
        
    def test_gifts_api_basic_functionality(self):
        """Test basic API functionality"""
        try:
            response = self.session.get(f"{self.backend_url}/gifts")
            status_code = response.status_code
            
            # Test 1: API responds with 200 status
            if status_code == 200:
                self.log_test("API Response Status", True, f"Status code: {status_code}")
            else:
                self.log_test("API Response Status", False, f"Expected 200, got {status_code}", response.text)
                return False
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                self.log_test("JSON Response Format", False, "Response is not valid JSON", response.text)
                return False
                
            # Test 2: Response has correct structure
            if "gifts" in response_data and isinstance(response_data["gifts"], list):
                self.log_test("Response Structure", True, "Contains 'gifts' array")
            else:
                self.log_test("Response Structure", False, "Missing 'gifts' array or wrong type", response_data)
                return False
            
            # Test 3: Correct number of gifts (should be 6)
            gifts = response_data["gifts"]
            if len(gifts) == 6:
                self.log_test("Gift Count", True, f"Found {len(gifts)} gifts")
            else:
                self.log_test("Gift Count", False, f"Expected 6 gifts, found {len(gifts)}", gifts)
            
            return gifts
            
        except Exception as e:
            self.log_test("API Basic Functionality", False, f"Exception: {str(e)}")
            return False
            
    def test_gift_data_structure(self, gifts: List[Dict]):
        """Test each gift has required fields with correct data types"""
        required_fields = ["id", "name", "category", "price_range", "link", "description", "image"]
        
        for i, gift in enumerate(gifts, 1):
            gift_id = gift.get("id", f"gift_{i}")
            
            # Test required fields presence
            missing_fields = [field for field in required_fields if field not in gift]
            if not missing_fields:
                self.log_test(f"Gift {gift_id} - Required Fields", True, "All required fields present")
            else:
                self.log_test(f"Gift {gift_id} - Required Fields", False, f"Missing fields: {missing_fields}", gift)
                
            # Test field data types and content
            if "name" in gift:
                if isinstance(gift["name"], str) and len(gift["name"]) > 0:
                    self.log_test(f"Gift {gift_id} - Name Field", True, f"Name: '{gift['name']}'")
                else:
                    self.log_test(f"Gift {gift_id} - Name Field", False, "Name is empty or not string", gift["name"])
                    
            if "description" in gift:
                if isinstance(gift["description"], str) and len(gift["description"]) > 10:
                    self.log_test(f"Gift {gift_id} - Description Field", True, f"Description length: {len(gift['description'])} chars")
                else:
                    self.log_test(f"Gift {gift_id} - Description Field", False, "Description too short or not string", gift.get("description"))
                    
            if "price_range" in gift:
                price = gift["price_range"]
                if isinstance(price, str) and "₹" in price:
                    self.log_test(f"Gift {gift_id} - Price Range", True, f"Price: {price}")
                else:
                    self.log_test(f"Gift {gift_id} - Price Range", False, "Price missing ₹ symbol or not string", price)
                    
            if "image" in gift:
                image_url = gift["image"]
                if isinstance(image_url, str) and image_url.startswith("https://"):
                    self.log_test(f"Gift {gift_id} - Image URL", True, f"Image URL valid: {image_url[:50]}...")
                else:
                    self.log_test(f"Gift {gift_id} - Image URL", False, "Image URL invalid or not HTTPS", image_url)
                    
            if "link" in gift:
                link = gift["link"]
                if isinstance(link, str) and "amzn.to/" in link:
                    self.log_test(f"Gift {gift_id} - Amazon Link", True, f"Amazon affiliate link: {link}")
                else:
                    self.log_test(f"Gift {gift_id} - Amazon Link", False, "Not a valid Amazon affiliate link", link)
                    
    def test_amazon_product_data_quality(self, gifts: List[Dict]):
        """Test quality of Amazon product data"""
        
        # Test 1: All gifts should have Amazon product images
        amazon_image_count = 0
        for gift in gifts:
            if "image" in gift and "m.media-amazon.com/images/" in gift["image"]:
                amazon_image_count += 1
                
        if amazon_image_count == len(gifts):
            self.log_test("Amazon Product Images", True, f"All {amazon_image_count} gifts have Amazon product images")
        else:
            self.log_test("Amazon Product Images", False, f"Only {amazon_image_count}/{len(gifts)} gifts have Amazon images")
            
        # Test 2: Product names should reflect actual Amazon products
        realistic_product_names = 0
        for gift in gifts:
            name = gift.get("name", "")
            # Check for realistic product naming patterns
            if any(keyword in name.lower() for keyword in ["women", "formal", "trouser", "pants", "style", "high waist"]):
                realistic_product_names += 1
                
        if realistic_product_names >= len(gifts) * 0.8:  # At least 80% should have realistic names
            self.log_test("Realistic Product Names", True, f"{realistic_product_names}/{len(gifts)} gifts have realistic product names")
        else:
            self.log_test("Realistic Product Names", False, f"Only {realistic_product_names}/{len(gifts)} gifts have realistic names")
            
        # Test 3: Descriptions should be meaningful
        meaningful_descriptions = 0
        for gift in gifts:
            description = gift.get("description", "")
            if len(description) > 20 and any(keyword in description.lower() for keyword in ["elegant", "comfortable", "style", "office", "wear", "perfect"]):
                meaningful_descriptions += 1
                
        if meaningful_descriptions >= len(gifts) * 0.8:
            self.log_test("Meaningful Descriptions", True, f"{meaningful_descriptions}/{len(gifts)} gifts have meaningful descriptions")
        else:
            self.log_test("Meaningful Descriptions", False, f"Only {meaningful_descriptions}/{len(gifts)} gifts have meaningful descriptions")
            
        # Test 4: Price ranges should be realistic Indian rupee amounts
        realistic_prices = 0
        for gift in gifts:
            price = gift.get("price_range", "")
            # Check for Indian rupee prices in reasonable ranges
            if "₹" in price and any(char.isdigit() for char in price):
                # Extract numbers from price
                import re
                numbers = re.findall(r'\d+', price)
                if numbers:
                    min_price = int(numbers[0])
                    if 100 <= min_price <= 5000:  # Reasonable price range
                        realistic_prices += 1
                        
        if realistic_prices == len(gifts):
            self.log_test("Realistic Price Ranges", True, f"All {realistic_prices} gifts have realistic Indian rupee prices")
        else:
            self.log_test("Realistic Price Ranges", False, f"Only {realistic_prices}/{len(gifts)} gifts have realistic prices")
            
    def test_api_performance_and_reliability(self):
        """Test API performance and reliability"""
        
        # Test multiple consecutive requests
        response_times = []
        successful_requests = 0
        
        for i in range(5):
            try:
                start_time = datetime.now()
                response = self.session.get(f"{self.backend_url}/gifts")
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                    
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
                
        if successful_requests == 5:
            avg_response_time = sum(response_times) / len(response_times)
            self.log_test("API Reliability", True, f"5/5 requests successful, avg response time: {avg_response_time:.3f}s")
        else:
            self.log_test("API Reliability", False, f"Only {successful_requests}/5 requests successful")
            
        # Test response time performance
        if response_times and max(response_times) < 5.0:  # Should respond within 5 seconds
            self.log_test("API Performance", True, f"Max response time: {max(response_times):.3f}s")
        else:
            self.log_test("API Performance", False, f"Response time too slow: {max(response_times) if response_times else 'N/A'}s")
            
    def test_specific_amazon_products(self, gifts: List[Dict]):
        """Test specific Amazon product details mentioned in the review request"""
        
        # Test for the specific product mentioned in review request
        high_waist_trouser_found = False
        for gift in gifts:
            if "High Waist Formal Trousers for Women" in gift.get("name", ""):
                high_waist_trouser_found = True
                
                # Check specific details
                expected_price = "₹449"
                expected_link = "https://amzn.to/46k7tSR"
                expected_image = "https://m.media-amazon.com/images/I/51Fpt5hLOML._SY445_.jpg"
                
                if gift.get("price_range") == expected_price:
                    self.log_test("Specific Product - Price", True, f"Correct price: {expected_price}")
                else:
                    self.log_test("Specific Product - Price", False, f"Expected {expected_price}, got {gift.get('price_range')}")
                    
                if gift.get("link") == expected_link:
                    self.log_test("Specific Product - Link", True, "Correct Amazon affiliate link")
                else:
                    self.log_test("Specific Product - Link", False, f"Link mismatch: {gift.get('link')}")
                    
                if gift.get("image") == expected_image:
                    self.log_test("Specific Product - Image", True, "Correct Amazon product image")
                else:
                    self.log_test("Specific Product - Image", False, f"Image mismatch: {gift.get('image')}")
                    
                break
                
        if high_waist_trouser_found:
            self.log_test("Specific Product Found", True, "High Waist Formal Trousers product found")
        else:
            self.log_test("Specific Product Found", False, "High Waist Formal Trousers product not found")
            
    def run_all_tests(self):
        """Run all Gift Ideas API tests"""
        print("🎁 STARTING GIFT IDEAS API COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Basic API functionality
        print("📋 TESTING BASIC API FUNCTIONALITY")
        print("-" * 40)
        gifts = self.test_gifts_api_basic_functionality()
        
        if gifts:
            # Test 2: Gift data structure
            print("🔍 TESTING GIFT DATA STRUCTURE")
            print("-" * 40)
            self.test_gift_data_structure(gifts)
            
            # Test 3: Amazon product data quality
            print("🛍️ TESTING AMAZON PRODUCT DATA QUALITY")
            print("-" * 40)
            self.test_amazon_product_data_quality(gifts)
            
            # Test 4: Specific Amazon products
            print("🎯 TESTING SPECIFIC AMAZON PRODUCTS")
            print("-" * 40)
            self.test_specific_amazon_products(gifts)
            
        # Test 5: API performance and reliability
        print("⚡ TESTING API PERFORMANCE & RELIABILITY")
        print("-" * 40)
        self.test_api_performance_and_reliability()
        
        # Generate summary
        self.generate_test_summary()
        
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎁 GIFT IDEAS API TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
            
        print("✅ CRITICAL FINDINGS:")
        
        # Check for critical issues
        api_working = any(r["test"] == "API Response Status" and r["success"] for r in self.test_results)
        structure_correct = any(r["test"] == "Response Structure" and r["success"] for r in self.test_results)
        gift_count_correct = any(r["test"] == "Gift Count" and r["success"] for r in self.test_results)
        amazon_images = any(r["test"] == "Amazon Product Images" and r["success"] for r in self.test_results)
        
        if api_working:
            print("  • Gift Ideas API is responding correctly (200 status)")
        else:
            print("  • ❌ CRITICAL: Gift Ideas API not responding properly")
            
        if structure_correct:
            print("  • API returns correct JSON structure with 'gifts' array")
        else:
            print("  • ❌ CRITICAL: API response structure is incorrect")
            
        if gift_count_correct:
            print("  • Correct number of gifts (6) returned")
        else:
            print("  • ⚠️ WARNING: Incorrect number of gifts returned")
            
        if amazon_images:
            print("  • All gifts have proper Amazon product images")
        else:
            print("  • ⚠️ WARNING: Some gifts missing Amazon product images")
            
        print()
        print("🎯 AMAZON AFFILIATE INTEGRATION STATUS:")
        
        # Check Amazon integration specific items
        affiliate_links = sum(1 for r in self.test_results if "Amazon Link" in r["test"] and r["success"])
        product_images = sum(1 for r in self.test_results if "Image URL" in r["test"] and r["success"])
        realistic_names = any(r["test"] == "Realistic Product Names" and r["success"] for r in self.test_results)
        meaningful_descriptions = any(r["test"] == "Meaningful Descriptions" and r["success"] for r in self.test_results)
        
        print(f"  • Amazon affiliate links: {affiliate_links}/6 gifts")
        print(f"  • Product images: {product_images}/6 gifts")
        print(f"  • Realistic product names: {'✅' if realistic_names else '❌'}")
        print(f"  • Meaningful descriptions: {'✅' if meaningful_descriptions else '❌'}")
        
        print()
        print("📊 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("  🎉 EXCELLENT: Gift Ideas API with Amazon integration is working perfectly!")
        elif success_rate >= 75:
            print("  ✅ GOOD: Gift Ideas API is working well with minor issues")
        elif success_rate >= 50:
            print("  ⚠️ MODERATE: Gift Ideas API has some issues that need attention")
        else:
            print("  ❌ CRITICAL: Gift Ideas API has major issues requiring immediate fixes")
            
        print(f"\nTest completed at: {datetime.now().isoformat()}")

def main():
    """Main test execution"""
    tester = GiftIdeasAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()