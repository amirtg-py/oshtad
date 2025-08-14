from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from pymongo import MongoClient
import os
import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical Equipment Store API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/medical_store')
    client = MongoClient(mongo_url)
    db = client['medical_store']
    
    # Collections
    products_collection = db['products']
    articles_collection = db['articles']
    services_collection = db['services']
    users_collection = db['users']
    cart_collection = db['cart']
    orders_collection = db['orders']
    reviews_collection = db['reviews']
    discounts_collection = db['discounts']
    
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise e

# Security
security = HTTPBearer()
SECRET_KEY = "medical_store_secret_key_2025"
ALGORITHM = "HS256"

# Pydantic models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: int
    image: str
    category: str
    stock: int = 100
    featured: bool = False

class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    image: str
    summary: str
    date: str
    author: str = "نویسنده مجله"

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    image: str
    features: List[str]

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    password: str
    full_name: str
    phone: str
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Cart(BaseModel):
    user_id: str
    items: List[CartItem]

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    rating: int  # 1-5
    comment: str
    user_name: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Discount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    percentage: int
    description: str
    valid_until: str
    min_amount: int = 0
    active: bool = True

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem]
    total_amount: int
    discount_amount: int = 0
    final_amount: int
    status: str = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    shipping_address: str
    discount_code: Optional[str] = None

# Authentication functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = users_collection.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Initialize sample data
def initialize_data():
    logger.info("Starting data initialization")
    # Sample products
    logger.info(f"Products count: {products_collection.count_documents({})}")
    if products_collection.count_documents({}) == 0:
        logger.info("Inserting sample products")
        sample_products = [
            {
                "id": str(uuid.uuid4()),
                "name": "شیرنیت ضد سرطان",
                "description": "محصولاتی که بیشترین فروش را داشته اند",
                "price": 70000,
                "image": "https://images.unsplash.com/photo-1595464144526-5fb181b74625?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwxfHxtZWRpY2FsJTIwZXF1aXBtZW50fGVufDB8fHx8MTc1NTE3NDMyOXww&ixlib=rb-4.1.0&q=85",
                "category": "دارو",
                "stock": 50,
                "featured": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "چسب زخم پارچه ای",
                "description": "چسب زخم با کیفیت بالا برای مراقبت از زخم ها",
                "price": 25000,
                "image": "https://images.unsplash.com/photo-1605176173609-a0067079b419?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwxfHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "category": "لوازم پزشکی",
                "stock": 100,
                "featured": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "بسته سرنگ BD",
                "description": "سرنگ های یکبار مصرف استریل",
                "price": 85000,
                "image": "https://images.unsplash.com/photo-1518152006812-edab29b069ac?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwzfHxtZWRpY2FsJTIwZXF1aXBtZW50fGVufDB8fHx8MTc1NTE3NDMyOXww&ixlib=rb-4.1.0&q=85",
                "category": "تجهیزات",
                "stock": 75,
                "featured": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "کپسول ویتامین D",
                "description": "مکمل ویتامین D برای تقویت استخوان ها",
                "price": 120000,
                "image": "https://images.unsplash.com/photo-1561328165-f0b762a9508e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "category": "مکمل",
                "stock": 30,
                "featured": True
            }
        ]
        products_collection.insert_many(sample_products)

    # Add more sample products for variety
    if products_collection.count_documents({}) < 12:
        additional_products = [
            {
                "id": str(uuid.uuid4()),
                "name": "ترمومتر دیجیتال",
                "description": "ترمومتر دیجیتال سریع و دقیق",
                "price": 45000,
                "image": "https://images.unsplash.com/photo-1606206873764-fd15e242df52?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHxtZWRpY2FsJTIwZXF1aXBtZW50fGVufDB8fHx8MTc1NTE3NDMyOXww&ixlib=rb-4.1.0&q=85",
                "category": "تجهیزات",
                "stock": 60,
                "featured": False
            },
            {
                "id": str(uuid.uuid4()),
                "name": "دستکش یکبار مصرف",
                "description": "دستکش های لاتکس بسته 100 عددی",
                "price": 35000,
                "image": "https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "category": "لوازم پزشکی",
                "stock": 200,
                "featured": False
            },
            {
                "id": str(uuid.uuid4()),
                "name": "ماسک N95",
                "description": "ماسک N95 بسته 20 عددی",
                "price": 65000,
                "image": "https://images.unsplash.com/photo-1581056771085-3ce30d907416?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwzfHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "category": "لوازم پزشکی",
                "stock": 150,
                "featured": False
            },
            {
                "id": str(uuid.uuid4()),
                "name": "قطره چشم مرطوب کننده",
                "description": "قطره چشم مرطوب کننده برای خشکی چشم",
                "price": 28000,
                "image": "https://images.pexels.com/photos/287237/pexels-photo-287237.jpeg",
                "category": "دارو",
                "stock": 80,
                "featured": False,
                "discount_percentage": 15
            },
            {
                "id": str(uuid.uuid4()),
                "name": "فشارسنج عقربه ای",
                "description": "فشارسنج عقربه ای حرفه ای",
                "price": 180000,
                "image": "https://images.unsplash.com/photo-1595464144526-5fb181b74625?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwxfHxtZWRpY2FsJTIwZXF1aXBtZW50fGVufDB8fHx8MTc1NTE3NDMyOXww&ixlib=rb-4.1.0&q=85",
                "category": "تجهیزات",
                "stock": 25,
                "featured": False,
                "discount_percentage": 20
            },
            {
                "id": str(uuid.uuid4()),
                "name": "پماد آنتی بیوتیک",
                "description": "پماد آنتی بیوتیک برای زخم ها",
                "price": 22000,
                "image": "https://images.unsplash.com/photo-1605176173609-a0067079b419?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwxfHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "category": "دارو",
                "stock": 90,
                "featured": False
            },
            {
                "id": str(uuid.uuid4()),
                "name": "میکروسکوپ آزمایشگاهی",
                "description": "میکروسکوپ با قدرت بزرگنمایی بالا",
                "price": 2500000,
                "image": "https://images.unsplash.com/photo-1518152006812-edab29b069ac?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwzfHxtZWRpY2FsJTIwZXF1aXBtZW50fGVufDB8fHx8MTc1NTE3NDMyOXww&ixlib=rb-4.1.0&q=85",
                "category": "تجهیزات",
                "stock": 10,
                "featured": False
            },
            {
                "id": str(uuid.uuid4()),
                "name": "مکمل کلسیم و ویتامین D3",
                "description": "مکمل کلسیم و ویتامین D3 برای استخوان",
                "price": 95000,
                "image": "https://images.unsplash.com/photo-1561328165-f0b762a9508e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "category": "مکمل",
                "stock": 40,
                "featured": False,
                "discount_percentage": 10
            }
        ]
        products_collection.insert_many(additional_products)

    # Sample articles
    logger.info(f"Articles count: {articles_collection.count_documents({})}")
    if articles_collection.count_documents({}) == 0:
        logger.info("Inserting sample articles")
        sample_articles = [
            {
                "id": str(uuid.uuid4()),
                "title": "اهمیت پایش فشار خون در منزل",
                "content": "پایش منظم فشار خون در منزل یکی از مهم ترین راه های مراقبت از سلامت قلب و عروق است...",
                "image": "https://images.unsplash.com/photo-1606206873764-fd15e242df52?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHxtZWRpY2FsJTIwZXF1aXBtZW50fGVufDB8fHx8MTc1NTE3NDMyOXww&ixlib=rb-4.1.0&q=85",
                "summary": "راهنمای کامل پایش فشار خون در منزل",
                "date": "۱۹ خرداد ۱۴۰۳",
                "author": "دکتر احمدی"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "چگونه از ماسک به درستی استفاده کنیم؟",
                "content": "استفاده صحیح از ماسک های پزشکی برای محافظت در برابر آلودگی ها و بیماری های تنفسی...",
                "image": "https://images.unsplash.com/photo-1581056771085-3ce30d907416?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwzfHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "summary": "راهنمای صحیح استفاده از ماسک",
                "date": "۲۲ خرداد ۱۴۰۳",
                "author": "دکتر محمدی"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "نکات مهم در انتخاب تجهیزات اتاق عمل",
                "content": "انتخاب تجهیزات مناسب برای اتاق عمل نیازمند دقت و بررسی های ویژه است...",
                "image": "https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxtZWRpY2FsJTIwc3VwcGxpZXN8ZW58MHx8fHwxNzU1MTc0MzM1fDA&ixlib=rb-4.1.0&q=85",
                "summary": "راهنمای انتخاب تجهیزات اتاق عمل",
                "date": "۲۵ خرداد ۱۴۰۳",
                "author": "دکتر رضایی"
            }
        ]
        articles_collection.insert_many(sample_articles)

    # Sample services
    logger.info(f"Services count: {services_collection.count_documents({})}")
    if services_collection.count_documents({}) == 0:
        logger.info("Inserting sample services")
        sample_services = [
            {
                "id": str(uuid.uuid4()),
                "title": "مراقبت های پزشکی ویژه",
                "description": "ما بهترین و جدیدترین تجهیزات پزشکی را برای مراقبت های ویژه در منزل با مرکز درمان فراهم می کنیم",
                "image": "https://images.pexels.com/photos/5214995/pexels-photo-5214995.jpeg",
                "features": ["مشاوره ۲۴ ساعته", "تجهیزات پیشرفته", "کادر متخصص"]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "داروخانه آنلاین",
                "description": "با چند کلیک ساده، داروهای خود را درب منزل تحویل بگیرید",
                "image": "https://images.unsplash.com/photo-1615177393114-bd2917a4f74a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxkb2N0b3IlMjBwcm9mZXNzaW9uYWx8ZW58MHx8fHwxNzU1MTc0Mzc1fDA&ixlib=rb-4.1.0&q=85",
                "features": ["تحویل سریع", "قیمت مناسب", "کیفیت تضمینی"]
            }
        ]
        services_collection.insert_many(sample_services)

    # Sample discounts
    logger.info(f"Discounts count: {discounts_collection.count_documents({})}")
    if discounts_collection.count_documents({}) == 0:
        logger.info("Inserting sample discounts")
        sample_discounts = [
            {
                "id": str(uuid.uuid4()),
                "code": "NEWUSER20",
                "percentage": 20,
                "description": "تخفیف ۲۰ درصدی برای کاربران جدید",
                "valid_until": "2025-12-31",
                "min_amount": 100000,
                "active": True
            },
            {
                "id": str(uuid.uuid4()),
                "code": "SUMMER15",
                "percentage": 15,
                "description": "تخفیف تابستانی ۱۵ درصد",
                "valid_until": "2025-09-30",
                "min_amount": 50000,
                "active": True
            }
        ]
        discounts_collection.insert_many(sample_discounts)

    # Create admin user
    logger.info(f"Admin users count: {users_collection.count_documents({'is_admin': True})}")
    if users_collection.count_documents({"is_admin": True}) == 0:
        logger.info("Creating admin user")
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@medical.com",
            "password": hash_password("admin123"),
            "full_name": "مدیر سیستم",
            "phone": "09123456789",
            "is_admin": True
        }
        users_collection.insert_one(admin_user)

# Initialize data on startup
initialize_data()
logger.info("Data initialization completed")

# API Routes

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user: User):
    try:
        # Check if user exists
        existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
        if existing_user:
            raise HTTPException(status_code=400, detail="کاربر با این مشخصات قبلاً ثبت شده است")
        
        # Hash password
        user.password = hash_password(user.password)
        
        # Insert user
        users_collection.insert_one(user.dict())
        
        return {"message": "ثبت نام با موفقیت انجام شد"}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="خطا در ثبت نام")

@app.post("/api/auth/login")
async def login(user_login: UserLogin):
    try:
        user = users_collection.find_one({"username": user_login.username})
        if not user or not verify_password(user_login.password, user["password"]):
            raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")
        
        token = create_token(data={"sub": user["username"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "is_admin": user["is_admin"]
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="خطا در ورود")

# Product endpoints
@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort_by: Optional[str] = "name",
    page: int = 1,
    limit: int = 12
):
    try:
        # Build filter query
        filter_query = {}
        
        if category:
            filter_query["category"] = category
            
        if search:
            filter_query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
            
        if min_price is not None:
            filter_query["price"] = filter_query.get("price", {})
            filter_query["price"]["$gte"] = min_price
            
        if max_price is not None:
            filter_query["price"] = filter_query.get("price", {})
            filter_query["price"]["$lte"] = max_price
        
        # Sort options
        sort_options = {
            "name": [("name", 1)],
            "price_low": [("price", 1)],
            "price_high": [("price", -1)],
            "newest": [("_id", -1)]
        }
        
        sort_query = sort_options.get(sort_by, [("name", 1)])
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get products with pagination
        products = list(products_collection.find(filter_query, {"_id": 0}).sort(sort_query).skip(skip).limit(limit))
        
        # Get total count for pagination
        total_count = products_collection.count_documents(filter_query)
        
        return {
            "products": products,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت محصولات")

@app.get("/api/products/categories")
async def get_categories():
    try:
        categories = products_collection.distinct("category")
        return categories
    except Exception as e:
        logger.error(f"Get categories error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت دسته‌بندی‌ها")

@app.get("/api/products/discounted")
async def get_discounted_products():
    try:
        products = list(products_collection.find({"discount_percentage": {"$exists": True}}, {"_id": 0}))
        return products
    except Exception as e:
        logger.error(f"Get discounted products error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت محصولات تخفیف‌دار")

@app.get("/api/products/featured")
async def get_featured_products():
    try:
        products = list(products_collection.find({"featured": True}, {"_id": 0}))
        return products
    except Exception as e:
        logger.error(f"Get featured products error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت محصولات ویژه")

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    try:
        product = products_collection.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="محصول یافت نشد")
        return product
    except Exception as e:
        logger.error(f"Get product error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت محصول")

@app.post("/api/products")
async def create_product(product: Product, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="دسترسی محدود به مدیر")
        
        products_collection.insert_one(product.dict())
        return {"message": "محصول با موفقیت اضافه شد"}
    except Exception as e:
        logger.error(f"Create product error: {e}")
        raise HTTPException(status_code=500, detail="خطا در اضافه کردن محصول")

# Article endpoints
@app.get("/api/articles")
async def get_articles():
    try:
        articles = list(articles_collection.find({}, {"_id": 0}))
        return articles
    except Exception as e:
        logger.error(f"Get articles error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت مقالات")

@app.get("/api/articles/{article_id}")
async def get_article(article_id: str):
    try:
        article = articles_collection.find_one({"id": article_id}, {"_id": 0})
        if not article:
            raise HTTPException(status_code=404, detail="مقاله یافت نشد")
        return article
    except Exception as e:
        logger.error(f"Get article error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت مقاله")

@app.post("/api/articles")
async def create_article(article: Article, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="دسترسی محدود به مدیر")
        
        articles_collection.insert_one(article.dict())
        return {"message": "مقاله با موفقیت اضافه شد"}
    except Exception as e:
        logger.error(f"Create article error: {e}")
        raise HTTPException(status_code=500, detail="خطا در اضافه کردن مقاله")

# Reviews endpoints
@app.get("/api/products/{product_id}/reviews")
async def get_product_reviews(product_id: str):
    try:
        reviews = list(reviews_collection.find({"product_id": product_id}, {"_id": 0}).sort([("created_at", -1)]))
        return reviews
    except Exception as e:
        logger.error(f"Get reviews error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت نظرات")

@app.post("/api/products/{product_id}/reviews")
async def add_review(product_id: str, review: Review, current_user: dict = Depends(get_current_user)):
    try:
        # Check if product exists
        product = products_collection.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="محصول یافت نشد")
        
        # Set review data
        review.product_id = product_id
        review.user_id = current_user["id"]
        review.user_name = current_user["full_name"]
        
        reviews_collection.insert_one(review.dict())
        return {"message": "نظر شما با موفقیت ثبت شد"}
    except Exception as e:
        logger.error(f"Add review error: {e}")
        raise HTTPException(status_code=500, detail="خطا در ثبت نظر")

# Discount endpoints
@app.get("/api/discounts")
async def get_active_discounts():
    try:
        discounts = list(discounts_collection.find({"active": True}, {"_id": 0}))
        return discounts
    except Exception as e:
        logger.error(f"Get discounts error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت تخفیف‌ها")

@app.post("/api/discounts/validate")
async def validate_discount(discount_data: dict):
    try:
        code = discount_data.get("code")
        amount = discount_data.get("amount", 0)
        
        discount = discounts_collection.find_one({"code": code, "active": True})
        if not discount:
            raise HTTPException(status_code=404, detail="کد تخفیف معتبر نیست")
        
        if amount < discount["min_amount"]:
            raise HTTPException(status_code=400, detail=f"حداقل مبلغ خرید {discount['min_amount']} تومان است")
        
        discount_amount = (amount * discount["percentage"]) // 100
        final_amount = amount - discount_amount
        
        return {
            "valid": True,
            "discount_percentage": discount["percentage"],
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "description": discount["description"]
        }
    except Exception as e:
        logger.error(f"Validate discount error: {e}")
        raise HTTPException(status_code=500, detail="خطا در بررسی کد تخفیف")

# Service endpoints
@app.get("/api/services")
async def get_services():
    try:
        services = list(services_collection.find({}, {"_id": 0}))
        return services
    except Exception as e:
        logger.error(f"Get services error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت خدمات")

# Cart endpoints
@app.get("/api/cart/{user_id}")
async def get_cart(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        cart = cart_collection.find_one({"user_id": user_id}, {"_id": 0})
        return cart or {"user_id": user_id, "items": []}
    except Exception as e:
        logger.error(f"Get cart error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت سبد خرید")

@app.post("/api/cart/{user_id}/add")
async def add_to_cart(user_id: str, item: CartItem, current_user: dict = Depends(get_current_user)):
    try:
        cart = cart_collection.find_one({"user_id": user_id})
        if cart:
            # Update existing cart
            existing_item = next((i for i in cart["items"] if i["product_id"] == item.product_id), None)
            if existing_item:
                existing_item["quantity"] += item.quantity
            else:
                cart["items"].append(item.dict())
            cart_collection.update_one({"user_id": user_id}, {"$set": {"items": cart["items"]}})
        else:
            # Create new cart
            new_cart = {"user_id": user_id, "items": [item.dict()]}
            cart_collection.insert_one(new_cart)
        
        return {"message": "محصول به سبد خرید اضافه شد"}
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        raise HTTPException(status_code=500, detail="خطا در اضافه کردن به سبد خرید")

@app.delete("/api/cart/{user_id}/remove/{product_id}")
async def remove_from_cart(user_id: str, product_id: str, current_user: dict = Depends(get_current_user)):
    try:
        cart = cart_collection.find_one({"user_id": user_id})
        if cart:
            cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
            cart_collection.update_one({"user_id": user_id}, {"$set": {"items": cart["items"]}})
        
        return {"message": "محصول از سبد خرید حذف شد"}
    except Exception as e:
        logger.error(f"Remove from cart error: {e}")
        raise HTTPException(status_code=500, detail="خطا در حذف از سبد خرید")

# Order endpoints
@app.post("/api/orders")
async def create_order(order: Order, current_user: dict = Depends(get_current_user)):
    try:
        # Calculate final amount if discount is applied
        if not hasattr(order, 'final_amount') or order.final_amount == 0:
            order.final_amount = order.total_amount - order.discount_amount
            
        orders_collection.insert_one(order.dict())
        # Clear cart after order
        cart_collection.delete_one({"user_id": order.user_id})
        return {"message": "سفارش با موفقیت ثبت شد", "order_id": order.id}
    except Exception as e:
        logger.error(f"Create order error: {e}")
        raise HTTPException(status_code=500, detail="خطا در ثبت سفارش")

@app.get("/api/orders/{user_id}")
async def get_user_orders(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        orders = list(orders_collection.find({"user_id": user_id}, {"_id": 0}))
        return orders
    except Exception as e:
        logger.error(f"Get user orders error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت سفارشات")

@app.get("/api/admin/orders")
async def get_all_orders(current_user: dict = Depends(get_current_user)):
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="دسترسی محدود به مدیر")
        
        orders = list(orders_collection.find({}, {"_id": 0}))
        return orders
    except Exception as e:
        logger.error(f"Get all orders error: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت سفارشات")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)