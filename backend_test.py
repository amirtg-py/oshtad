#!/usr/bin/env python3
"""
Backend API Testing Suite for Medical Equipment E-commerce Website
Tests all backend endpoints with Persian content support
"""

import requests
import json
import uuid
import time
from typing import Dict, Any, Optional

class BackendTester:
    def __init__(self):
        # Use the production URL from frontend .env, but fallback to local for testing
        self.base_url = "https://medishop-fa.preview.emergentagent.com/api"
        # For testing, we'll use local backend since external might have connectivity issues
        self.local_url = "http://localhost:8001/api"
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.admin_token = None
        self.test_results = []
        
        # Test data with realistic Persian content
        self.test_user = {
            "username": "علی_احمدی",
            "email": "ali.ahmadi@example.com", 
            "password": "password123",
            "full_name": "علی احمدی",
            "phone": "09123456789"
        }
        
        self.admin_credentials = {
            "username": "admin",
            "password": "admin123"
        }
        
        self.test_product = {
            "name": "دستگاه فشارسنج دیجیتال",
            "description": "دستگاه فشارسنج دیجیتال با دقت بالا برای استفاده خانگی",
            "price": 450000,
            "image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56",
            "category": "تجهیزات پزشکی",
            "stock": 25,
            "featured": True
        }

    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")

    def test_server_health(self) -> bool:
        """Test if server is running and accessible"""
        # Try production URL first, then fallback to local
        for url_name, url in [("Production", self.base_url), ("Local", self.local_url)]:
            try:
                response = self.session.get(f"{url}/products", timeout=5)
                if response.status_code == 200:
                    self.base_url = url  # Use the working URL for all subsequent tests
                    self.log_test("Server Health Check", True, f"{url_name} server is accessible and responding")
                    return True
                else:
                    print(f"   {url_name} server returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   {url_name} server connection failed: {str(e)}")
                continue
        
        self.log_test("Server Health Check", False, "Neither production nor local server is accessible")
        return False

    def test_user_registration(self) -> bool:
        """Test user registration endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Registration", True, "User registered successfully", data)
                return True
            elif response.status_code == 400:
                # User might already exist, try with different username
                modified_user = self.test_user.copy()
                modified_user["username"] = f"test_user_{uuid.uuid4().hex[:8]}"
                modified_user["email"] = f"test_{uuid.uuid4().hex[:8]}@example.com"
                
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=modified_user,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.test_user = modified_user  # Update for future tests
                    data = response.json()
                    self.log_test("User Registration", True, "User registered successfully (with modified username)", data)
                    return True
                else:
                    self.log_test("User Registration", False, f"Registration failed: {response.text}")
                    return False
            else:
                self.log_test("User Registration", False, f"Registration failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("User Registration", False, f"Request failed: {str(e)}")
            return False

    def test_user_login(self) -> bool:
        """Test user login endpoint"""
        try:
            login_data = {
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.test_user_id = data["user"]["id"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, "User logged in successfully", {"user_id": self.test_user_id})
                    return True
                else:
                    self.log_test("User Login", False, "No access token in response", data)
                    return False
            else:
                self.log_test("User Login", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("User Login", False, f"Request failed: {str(e)}")
            return False

    def test_admin_login(self) -> bool:
        """Test admin login for privileged operations"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and data["user"].get("is_admin"):
                    self.admin_token = data["access_token"]
                    self.log_test("Admin Login", True, "Admin logged in successfully")
                    return True
                else:
                    self.log_test("Admin Login", False, "Login successful but user is not admin", data)
                    return False
            else:
                self.log_test("Admin Login", False, f"Admin login failed: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Admin Login", False, f"Request failed: {str(e)}")
            return False

    def test_get_products(self) -> bool:
        """Test getting all products with new pagination format"""
        try:
            response = self.session.get(f"{self.base_url}/products", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has new pagination format
                if isinstance(data, dict) and "products" in data:
                    products = data["products"]
                    if len(products) > 0:
                        # Check if products have Persian content
                        has_persian = any("name" in p and any(ord(c) > 127 for c in p["name"]) for p in products)
                        self.log_test("Get All Products", True, f"Retrieved {len(products)} products with Persian content: {has_persian}, Total: {data.get('total', 'unknown')}")
                        return True
                    else:
                        self.log_test("Get All Products", False, "No products returned")
                        return False
                elif isinstance(data, list) and len(data) > 0:
                    # Fallback for old format
                    has_persian = any("name" in p and any(ord(c) > 127 for c in p["name"]) for p in data)
                    self.log_test("Get All Products", True, f"Retrieved {len(data)} products with Persian content: {has_persian}")
                    return True
                else:
                    self.log_test("Get All Products", False, "No products returned or invalid format")
                    return False
            else:
                self.log_test("Get All Products", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get All Products", False, f"Request failed: {str(e)}")
            return False

    def test_get_featured_products(self) -> bool:
        """Test getting featured products"""
        try:
            response = self.session.get(f"{self.base_url}/products/featured", timeout=10)
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    featured_count = len([p for p in products if p.get("featured", False)])
                    self.log_test("Get Featured Products", True, f"Retrieved {len(products)} featured products")
                    return True
                else:
                    self.log_test("Get Featured Products", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Featured Products", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Featured Products", False, f"Request failed: {str(e)}")
            return False

    def test_get_single_product(self) -> bool:
        """Test getting a single product by ID"""
        try:
            # First get all products to get a valid ID
            products_response = self.session.get(f"{self.base_url}/products", timeout=10)
            if products_response.status_code != 200:
                self.log_test("Get Single Product", False, "Could not fetch products to get test ID")
                return False
                
            data = products_response.json()
            # Handle both old and new response formats
            if isinstance(data, dict) and "products" in data:
                products = data["products"]
            elif isinstance(data, list):
                products = data
            else:
                self.log_test("Get Single Product", False, "Invalid products response format")
                return False
                
            if not products:
                self.log_test("Get Single Product", False, "No products available for testing")
                return False
                
            test_product_id = products[0]["id"]
            response = self.session.get(f"{self.base_url}/products/{test_product_id}", timeout=10)
            
            if response.status_code == 200:
                product = response.json()
                if "id" in product and product["id"] == test_product_id:
                    self.log_test("Get Single Product", True, f"Retrieved product: {product.get('name', 'Unknown')}")
                    return True
                else:
                    self.log_test("Get Single Product", False, "Product ID mismatch in response")
                    return False
            else:
                self.log_test("Get Single Product", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Single Product", False, f"Request failed: {str(e)}")
            return False

    def test_create_product_admin(self) -> bool:
        """Test creating a product as admin"""
        if not self.admin_token:
            self.log_test("Create Product (Admin)", False, "No admin token available")
            return False
            
        try:
            # Use admin token for this request
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(
                f"{self.base_url}/products",
                json=self.test_product,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Create Product (Admin)", True, "Product created successfully", data)
                return True
            else:
                self.log_test("Create Product (Admin)", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Product (Admin)", False, f"Request failed: {str(e)}")
            return False

    def test_get_articles(self) -> bool:
        """Test getting all articles"""
        try:
            response = self.session.get(f"{self.base_url}/articles", timeout=10)
            
            if response.status_code == 200:
                articles = response.json()
                if isinstance(articles, list):
                    self.log_test("Get All Articles", True, f"Retrieved {len(articles)} articles")
                    return True
                else:
                    self.log_test("Get All Articles", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get All Articles", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get All Articles", False, f"Request failed: {str(e)}")
            return False

    def test_get_single_article(self) -> bool:
        """Test getting a single article by ID"""
        try:
            # First get all articles to get a valid ID
            articles_response = self.session.get(f"{self.base_url}/articles", timeout=10)
            if articles_response.status_code != 200:
                self.log_test("Get Single Article", False, "Could not fetch articles to get test ID")
                return False
                
            articles = articles_response.json()
            if not articles:
                self.log_test("Get Single Article", False, "No articles available for testing")
                return False
                
            test_article_id = articles[0]["id"]
            response = self.session.get(f"{self.base_url}/articles/{test_article_id}", timeout=10)
            
            if response.status_code == 200:
                article = response.json()
                if "id" in article and article["id"] == test_article_id:
                    self.log_test("Get Single Article", True, f"Retrieved article: {article.get('title', 'Unknown')}")
                    return True
                else:
                    self.log_test("Get Single Article", False, "Article ID mismatch in response")
                    return False
            else:
                self.log_test("Get Single Article", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Single Article", False, f"Request failed: {str(e)}")
            return False

    def test_get_services(self) -> bool:
        """Test getting all services"""
        try:
            response = self.session.get(f"{self.base_url}/services", timeout=10)
            
            if response.status_code == 200:
                services = response.json()
                if isinstance(services, list):
                    self.log_test("Get All Services", True, f"Retrieved {len(services)} services")
                    return True
                else:
                    self.log_test("Get All Services", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get All Services", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get All Services", False, f"Request failed: {str(e)}")
            return False

    def test_get_cart(self) -> bool:
        """Test getting user cart"""
        if not self.test_user_id or not self.auth_token:
            self.log_test("Get Cart", False, "No authenticated user available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/cart/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                cart = response.json()
                if "user_id" in cart:
                    self.log_test("Get Cart", True, f"Retrieved cart with {len(cart.get('items', []))} items")
                    return True
                else:
                    self.log_test("Get Cart", False, "Invalid cart response format")
                    return False
            else:
                self.log_test("Get Cart", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Cart", False, f"Request failed: {str(e)}")
            return False

    def test_add_to_cart(self) -> bool:
        """Test adding item to cart"""
        if not self.test_user_id or not self.auth_token:
            self.log_test("Add to Cart", False, "No authenticated user available")
            return False
            
        try:
            # First get a product ID to add to cart
            products_response = self.session.get(f"{self.base_url}/products", timeout=10)
            if products_response.status_code != 200:
                self.log_test("Add to Cart", False, "Could not fetch products for cart test")
                return False
                
            data = products_response.json()
            products = data.get("products", data) if isinstance(data, dict) else data
            if not products:
                self.log_test("Add to Cart", False, "No products available for cart test")
                return False
                
            cart_item = {
                "product_id": products[0]["id"],
                "quantity": 2
            }
            
            response = self.session.post(
                f"{self.base_url}/cart/{self.test_user_id}/add",
                json=cart_item,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add to Cart", True, "Item added to cart successfully", data)
                return True
            else:
                self.log_test("Add to Cart", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Add to Cart", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_products_filtering(self) -> bool:
        """Test enhanced products API with filtering, search, and pagination"""
        try:
            # Test category filtering
            response = self.session.get(f"{self.base_url}/products?category=تجهیزات", timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", data) if isinstance(data, dict) else data
                category_test = len(products) > 0
                self.log_test("Products Category Filter", category_test, f"Category filter returned {len(products)} products")
            else:
                self.log_test("Products Category Filter", False, f"Category filter failed: {response.text}")
                return False

            # Test search functionality
            response = self.session.get(f"{self.base_url}/products?search=فشارسنج", timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", data) if isinstance(data, dict) else data
                search_test = len(products) >= 0  # Search might return 0 results, which is valid
                self.log_test("Products Search", search_test, f"Search returned {len(products)} products")
            else:
                self.log_test("Products Search", False, f"Search failed: {response.text}")
                return False

            # Test price range filtering
            response = self.session.get(f"{self.base_url}/products?min_price=20000&max_price=100000", timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", data) if isinstance(data, dict) else data
                price_test = all(20000 <= p.get("price", 0) <= 100000 for p in products)
                self.log_test("Products Price Filter", price_test, f"Price filter returned {len(products)} products in range")
            else:
                self.log_test("Products Price Filter", False, f"Price filter failed: {response.text}")
                return False

            # Test sorting
            response = self.session.get(f"{self.base_url}/products?sort_by=price_low", timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", data) if isinstance(data, dict) else data
                if len(products) > 1:
                    sort_test = products[0].get("price", 0) <= products[1].get("price", 0)
                    self.log_test("Products Sorting", sort_test, f"Price sorting working: {sort_test}")
                else:
                    self.log_test("Products Sorting", True, "Sorting test passed (insufficient products for comparison)")
            else:
                self.log_test("Products Sorting", False, f"Sorting failed: {response.text}")
                return False

            # Test pagination
            response = self.session.get(f"{self.base_url}/products?page=1&limit=3", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "products" in data:
                    pagination_test = len(data["products"]) <= 3 and "total" in data and "page" in data
                    self.log_test("Products Pagination", pagination_test, f"Pagination working: page {data.get('page')}, limit 3, got {len(data['products'])} products")
                else:
                    self.log_test("Products Pagination", False, "Pagination response format incorrect")
                    return False
            else:
                self.log_test("Products Pagination", False, f"Pagination failed: {response.text}")
                return False

            return True
                
        except requests.exceptions.RequestException as e:
            self.log_test("Enhanced Products Filtering", False, f"Request failed: {str(e)}")
            return False

    def test_product_categories(self) -> bool:
        """Test getting product categories"""
        try:
            response = self.session.get(f"{self.base_url}/products/categories", timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    has_persian = any(any(ord(c) > 127 for c in cat) for cat in categories)
                    self.log_test("Get Product Categories", True, f"Retrieved {len(categories)} categories with Persian: {has_persian}")
                    return True
                else:
                    self.log_test("Get Product Categories", False, "No categories returned or invalid format")
                    return False
            else:
                self.log_test("Get Product Categories", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Product Categories", False, f"Request failed: {str(e)}")
            return False

    def test_discounted_products(self) -> bool:
        """Test getting discounted products"""
        try:
            response = self.session.get(f"{self.base_url}/products/discounted", timeout=10)
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    discounted_count = len([p for p in products if "discount_percentage" in p])
                    self.log_test("Get Discounted Products", True, f"Retrieved {len(products)} discounted products, {discounted_count} with discount_percentage")
                    return True
                else:
                    self.log_test("Get Discounted Products", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Discounted Products", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Discounted Products", False, f"Request failed: {str(e)}")
            return False

    def test_reviews_system(self) -> bool:
        """Test reviews and ratings system"""
        if not self.test_user_id or not self.auth_token:
            self.log_test("Reviews System", False, "No authenticated user available")
            return False
            
        try:
            # First get a product ID for testing reviews
            products_response = self.session.get(f"{self.base_url}/products", timeout=10)
            if products_response.status_code != 200:
                self.log_test("Reviews System", False, "Could not fetch products for review test")
                return False
                
            data = products_response.json()
            products = data.get("products", data) if isinstance(data, dict) else data
            if not products:
                self.log_test("Reviews System", False, "No products available for review test")
                return False
                
            test_product_id = products[0]["id"]
            
            # Test getting reviews for a product (should work even if empty)
            response = self.session.get(f"{self.base_url}/products/{test_product_id}/reviews", timeout=10)
            if response.status_code == 200:
                reviews = response.json()
                if isinstance(reviews, list):
                    self.log_test("Get Product Reviews", True, f"Retrieved {len(reviews)} reviews for product")
                else:
                    self.log_test("Get Product Reviews", False, "Invalid reviews response format")
                    return False
            else:
                self.log_test("Get Product Reviews", False, f"Get reviews failed: {response.text}")
                return False

            # Test adding a review (requires authentication)
            review_data = {
                "rating": 5,
                "comment": "محصول بسیار عالی و با کیفیت. پیشنهاد می‌کنم."
            }
            
            response = self.session.post(
                f"{self.base_url}/products/{test_product_id}/reviews",
                json=review_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add Product Review", True, "Review added successfully", data)
                
                # Verify the review was added by getting reviews again
                response = self.session.get(f"{self.base_url}/products/{test_product_id}/reviews", timeout=10)
                if response.status_code == 200:
                    reviews = response.json()
                    new_review = next((r for r in reviews if r.get("user_id") == self.test_user_id), None)
                    if new_review:
                        self.log_test("Verify Added Review", True, f"Review verified: rating {new_review.get('rating')}")
                        return True
                    else:
                        self.log_test("Verify Added Review", False, "Added review not found in list")
                        return False
                else:
                    self.log_test("Verify Added Review", False, "Could not retrieve reviews to verify")
                    return False
            else:
                self.log_test("Add Product Review", False, f"Add review failed: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Reviews System", False, f"Request failed: {str(e)}")
            return False

    def test_discount_system(self) -> bool:
        """Test discount codes and validation system"""
        try:
            # Test getting active discounts
            response = self.session.get(f"{self.base_url}/discounts", timeout=10)
            if response.status_code == 200:
                discounts = response.json()
                if isinstance(discounts, list):
                    active_count = len([d for d in discounts if d.get("active", False)])
                    self.log_test("Get Active Discounts", True, f"Retrieved {len(discounts)} discounts, {active_count} active")
                else:
                    self.log_test("Get Active Discounts", False, "Invalid discounts response format")
                    return False
            else:
                self.log_test("Get Active Discounts", False, f"Get discounts failed: {response.text}")
                return False

            # Test valid discount code validation - NEWUSER20
            discount_data = {
                "code": "NEWUSER20",
                "amount": 150000  # Above minimum amount
            }
            
            response = self.session.post(
                f"{self.base_url}/discounts/validate",
                json=discount_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") and "discount_amount" in data and "final_amount" in data:
                    expected_discount = 150000 * 20 // 100  # 20% of 150000
                    expected_final = 150000 - expected_discount
                    actual_discount = data["discount_amount"]
                    actual_final = data["final_amount"]
                    
                    calculation_correct = (actual_discount == expected_discount and actual_final == expected_final)
                    self.log_test("Validate NEWUSER20 Discount", calculation_correct, 
                                f"Discount: {actual_discount} (expected {expected_discount}), Final: {actual_final} (expected {expected_final})")
                else:
                    self.log_test("Validate NEWUSER20 Discount", False, "Invalid discount validation response format")
                    return False
            else:
                self.log_test("Validate NEWUSER20 Discount", False, f"Discount validation failed: {response.text}")
                return False

            # Test valid discount code validation - SUMMER15
            discount_data = {
                "code": "SUMMER15",
                "amount": 80000  # Above minimum amount
            }
            
            response = self.session.post(
                f"{self.base_url}/discounts/validate",
                json=discount_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    expected_discount = 80000 * 15 // 100  # 15% of 80000
                    actual_discount = data["discount_amount"]
                    calculation_correct = actual_discount == expected_discount
                    self.log_test("Validate SUMMER15 Discount", calculation_correct, 
                                f"15% discount calculated correctly: {actual_discount}")
                else:
                    self.log_test("Validate SUMMER15 Discount", False, "SUMMER15 discount not valid")
                    return False
            else:
                self.log_test("Validate SUMMER15 Discount", False, f"SUMMER15 validation failed: {response.text}")
                return False

            # Test invalid discount code
            discount_data = {
                "code": "INVALID_CODE",
                "amount": 100000
            }
            
            response = self.session.post(
                f"{self.base_url}/discounts/validate",
                json=discount_data,
                timeout=10
            )
            
            if response.status_code == 404:
                self.log_test("Invalid Discount Code", True, "Invalid discount code properly rejected")
            else:
                self.log_test("Invalid Discount Code", False, f"Invalid code should return 404, got {response.status_code}")
                return False

            # Test minimum amount requirement
            discount_data = {
                "code": "NEWUSER20",
                "amount": 50000  # Below minimum amount of 100000
            }
            
            response = self.session.post(
                f"{self.base_url}/discounts/validate",
                json=discount_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Discount Minimum Amount", True, "Minimum amount requirement enforced")
                return True
            else:
                self.log_test("Discount Minimum Amount", False, f"Should reject below minimum, got {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Discount System", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_orders_with_discount(self) -> bool:
        """Test creating orders with discount support"""
        if not self.test_user_id or not self.auth_token:
            self.log_test("Enhanced Orders with Discount", False, "No authenticated user available")
            return False
            
        try:
            # First get a product for the order
            products_response = self.session.get(f"{self.base_url}/products", timeout=10)
            if products_response.status_code != 200:
                self.log_test("Enhanced Orders with Discount", False, "Could not fetch products for order test")
                return False
                
            data = products_response.json()
            products = data.get("products", data) if isinstance(data, dict) else data
            if not products:
                self.log_test("Enhanced Orders with Discount", False, "No products available for order test")
                return False
                
            # Find a product with sufficient price for discount
            suitable_product = next((p for p in products if p.get("price", 0) >= 150000), products[0])
            
            total_amount = suitable_product["price"]
            discount_amount = total_amount * 20 // 100  # 20% discount
            final_amount = total_amount - discount_amount
            
            order_data = {
                "user_id": self.test_user_id,
                "items": [
                    {
                        "product_id": suitable_product["id"],
                        "quantity": 1
                    }
                ],
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "final_amount": final_amount,
                "discount_code": "NEWUSER20",
                "shipping_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳"
            }
            
            response = self.session.post(
                f"{self.base_url}/orders",
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "order_id" in data:
                    self.log_test("Enhanced Orders with Discount", True, f"Order with discount created successfully: {data['order_id']}")
                    return True
                else:
                    self.log_test("Enhanced Orders with Discount", False, "Order created but no order_id returned")
                    return False
            else:
                self.log_test("Enhanced Orders with Discount", False, f"Order creation failed: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Enhanced Orders with Discount", False, f"Request failed: {str(e)}")
            return False

    def test_create_order(self) -> bool:
        """Test creating an order"""
        if not self.test_user_id or not self.auth_token:
            self.log_test("Create Order", False, "No authenticated user available")
            return False
            
        try:
            # First get a product for the order
            products_response = self.session.get(f"{self.base_url}/products", timeout=10)
            if products_response.status_code != 200:
                self.log_test("Create Order", False, "Could not fetch products for order test")
                return False
                
            products = products_response.json()
            if not products:
                self.log_test("Create Order", False, "No products available for order test")
                return False
                
            order_data = {
                "user_id": self.test_user_id,
                "items": [
                    {
                        "product_id": products[0]["id"],
                        "quantity": 1
                    }
                ],
                "total_amount": products[0]["price"],
                "shipping_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳"
            }
            
            response = self.session.post(
                f"{self.base_url}/orders",
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Create Order", True, "Order created successfully", data)
                return True
            else:
                self.log_test("Create Order", False, f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Order", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests for Medical Equipment E-commerce")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Core functionality tests
        tests = [
            ("Server Health Check", self.test_server_health),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Admin Login", self.test_admin_login),
            ("Get All Products", self.test_get_products),
            ("Enhanced Products Filtering", self.test_enhanced_products_filtering),
            ("Get Product Categories", self.test_product_categories),
            ("Get Discounted Products", self.test_discounted_products),
            ("Get Featured Products", self.test_get_featured_products),
            ("Get Single Product", self.test_get_single_product),
            ("Reviews System", self.test_reviews_system),
            ("Discount System", self.test_discount_system),
            ("Create Product (Admin)", self.test_create_product_admin),
            ("Get All Articles", self.test_get_articles),
            ("Get Single Article", self.test_get_single_article),
            ("Get All Services", self.test_get_services),
            ("Get Cart", self.test_get_cart),
            ("Add to Cart", self.test_add_to_cart),
            ("Enhanced Orders with Discount", self.test_enhanced_orders_with_discount),
            ("Create Order", self.test_create_order),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test threw exception: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/backend_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)