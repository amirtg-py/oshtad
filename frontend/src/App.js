import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import { Stethoscope, ShoppingCart, LogIn, UserPlus, Phone, Mail, MapPin } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardFooter, CardTitle } from './components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    }
    setLoading(false);
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        return true;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        return true;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Header Component
const Header = ({ onLoginClick, onRegisterClick, onCartClick, cartCount, onProductsClick, currentPage, setCurrentPage }) => {
  const { user, logout } = useAuth();

  return (
    <header className="backdrop-blur-md bg-gradient-to-r from-blue-600/90 to-cyan-600/90 text-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-reverse space-x-8">
            <h1
              className="text-2xl font-bold text-right cursor-pointer hover:text-blue-200 transition-colors flex items-center gap-2"
              onClick={() => setCurrentPage('home')}
            >
              <Stethoscope className="w-6 h-6" />
              <span>پیک سلامت</span>
            </h1>
            <nav className="hidden md:flex space-x-reverse space-x-6">
              <button 
                onClick={() => setCurrentPage('home')}
                className={`hover:text-blue-200 transition-colors ${currentPage === 'home' ? 'text-blue-200' : ''}`}
              >
                صفحه اصلی
              </button>
              <button 
                onClick={() => setCurrentPage('products')}
                className={`hover:text-blue-200 transition-colors ${currentPage === 'products' ? 'text-blue-200' : ''}`}
              >
                فروشگاه
              </button>
              <button 
                onClick={() => setCurrentPage('discounts')}
                className={`hover:text-blue-200 transition-colors ${currentPage === 'discounts' ? 'text-blue-200' : ''}`}
              >
                تخفیف‌ها
              </button>
              <a href="#blog" className="hover:text-blue-200 transition-colors">وبلاگ</a>
              <a href="#services" className="hover:text-blue-200 transition-colors">درباره ما</a>
              <a href="#contact" className="hover:text-blue-200 transition-colors">تماس با ما</a>
            </nav>
          </div>
          
          <div className="flex items-center space-x-reverse space-x-4">
            <Button
              onClick={onCartClick}
              className="relative flex items-center gap-2 bg-blue-700 hover:bg-blue-600 px-3 py-2"
              aria-label="سبد خرید"
            >
              <ShoppingCart className="w-5 h-5" />
              <span className="hidden sm:inline">سبد خرید</span>
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs h-6 w-6 flex items-center justify-center animate-pulse">
                  {cartCount}
                </span>
              )}
            </Button>

            {user ? (
              <div className="flex items-center space-x-reverse space-x-4">
                <span className="text-sm">سلام {user.full_name}</span>
                <Button
                  onClick={logout}
                  className="bg-red-500 hover:bg-red-600 px-4 py-2 shadow-lg"
                >
                  خروج
                </Button>
              </div>
            ) : (
              <div className="flex space-x-reverse space-x-2">
                <Button
                  onClick={onLoginClick}
                  className="bg-blue-500 hover:bg-blue-600 px-4 py-2 shadow-lg flex items-center gap-1"
                >
                  <LogIn className="w-4 h-4" /> ورود
                </Button>
                <Button
                  onClick={onRegisterClick}
                  className="bg-green-500 hover:bg-green-600 px-4 py-2 shadow-lg flex items-center gap-1"
                >
                  <UserPlus className="w-4 h-4" /> ثبت نام
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

// Hero Section
const HeroSection = ({ onProductsClick }) => {
  return (
    <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20 overflow-hidden">
      <div className="container mx-auto px-4">
        <div className="flex flex-col lg:flex-row items-center">
          <div className="lg:w-1/2 text-right hero-content">
            <h2 className="text-4xl lg:text-6xl font-bold text-gray-800 mb-6 leading-tight">
              برای پزشکان
              <br />
              <span className="text-blue-600 gradient-text">و متخصصان پزشکی</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              ما محصولات و خدمات بهداشتی با کیفیت را ارائه می دهیم
            </p>
            <div className="flex space-x-reverse space-x-4">
              <Button
                onClick={onProductsClick}
                className="bg-blue-600 hover:bg-blue-700 px-8 py-4 text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:-translate-y-1 pulse-glow"
              >
                اکنون خرید کنید
              </Button>
              <Button
                variant="outline"
                className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-4 text-lg font-semibold shadow-lg"
              >
                مشاهده کاتالوگ
              </Button>
            </div>
          </div>
          <div className="lg:w-1/2 mt-10 lg:mt-0 hero-image">
            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1615177393114-bd2917a4f74a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxkb2N0b3IlMjBwcm9mZXNzaW9uYWx8ZW58MHx8fHwxNzU1MTc0Mzc1fDA&ixlib=rb-4.1.0&q=85"
                alt="Medical Professional"
                className="shadow-2xl w-full h-auto object-cover transform hover:scale-[1.02] transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-blue-900/20 to-transparent"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Categories Section
const CategoriesSection = ({ onSelectCategory }) => {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/categories`);
        if (res.ok) {
          const data = await res.json();
          setCategories(data);
        }
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };
    fetchCategories();
  }, []);

  const colors = [
    'from-teal-100 to-blue-50',
    'from-pink-100 to-rose-50',
    'from-yellow-100 to-amber-50',
    'from-indigo-100 to-purple-50'
  ];

  return (
    <section className="py-12 bg-white">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {categories.map((cat, idx) => (
            <Card
              key={cat.name}
              className={`relative overflow-hidden rounded-2xl shadow-md bg-gradient-to-br ${colors[idx % colors.length]}`}
            >
              <CardContent className="p-6 flex flex-col items-end text-right h-full">
                <h3 className="text-lg font-bold mb-4">{cat.name}</h3>
                <Button
                  onClick={() => onSelectCategory(cat.name)}
                  className="mt-auto bg-white text-blue-600 border-2 border-blue-600 hover:bg-blue-50 px-4 py-2 rounded-xl"
                >
                  مشاهده محصولات
                </Button>
              </CardContent>
              {cat.image && (
                <img
                  src={cat.image}
                  alt={cat.name}
                  className="w-24 h-24 object-cover absolute left-4 bottom-4 rounded-lg shadow-lg"
                />
              )}
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

// Product Card Component
const ProductCard = ({ product, onAddToCart, onProductClick }) => {
  const hasDiscount = product.discount_percentage;
  const discountedPrice = hasDiscount ? product.price * (1 - product.discount_percentage / 100) : product.price;

  return (
    <Card
      className="product-card rounded-2xl border border-gray-200 hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-3 group cursor-pointer"
      onClick={() => onProductClick(product)}
    >
      <div className="relative overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-48 object-cover transition-transform duration-500 group-hover:scale-110"
        />
        {hasDiscount && (
          <div className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 text-sm font-bold animate-bounce">
            {product.discount_percentage}% تخفیف
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      </div>
      <CardContent className="p-6">
        <CardTitle className="text-xl font-bold text-gray-800 mb-2 text-right group-hover:text-blue-600 transition-colors">
          {product.name}
        </CardTitle>
        <p className="text-gray-600 mb-4 text-right text-sm leading-relaxed">{product.description}</p>
      </CardContent>
      <CardFooter className="flex justify-between items-center">
        <Button
          onClick={(e) => {
            e.stopPropagation();
            onAddToCart(product);
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
        >
          افزودن به سبد
        </Button>
        <div className="text-right">
          {hasDiscount && (
            <span className="text-lg text-gray-400 line-through block">
              {product.price.toLocaleString()} تومان
            </span>
          )}
          <span className="text-2xl font-bold text-blue-600">
            {Math.round(discountedPrice).toLocaleString()} تومان
          </span>
        </div>
      </CardFooter>
    </Card>
  );
};

// Products Section
const ProductsSection = ({ onAddToCart, featured = true }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, [featured]);

  const fetchProducts = async () => {
    try {
      const endpoint = featured ? '/api/products/featured' : '/api/products';
      const response = await fetch(`${BACKEND_URL}${endpoint}`);
      if (response.ok) {
        const data = await response.json();
        setProducts(featured ? data : data.products || data);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <section id="products" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            {featured ? 'پرفروش ترین ها' : 'تمام محصولات'}
          </h2>
          <p className="text-xl text-gray-600">محصولاتی که بیشترین فروش را داشته اند</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {products.map((product) => (
            <ProductCard 
              key={product.id} 
              product={product} 
              onAddToCart={onAddToCart}
              onProductClick={setSelectedProduct}
            />
          ))}
        </div>
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductDetailModal 
          product={selectedProduct} 
          onClose={() => setSelectedProduct(null)}
          onAddToCart={onAddToCart}
        />
      )}
    </section>
  );
};

// Product Detail Modal
const ProductDetailModal = ({ product, onClose, onAddToCart }) => {
  const [reviews, setReviews] = useState([]);
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' });
  const [showReviewForm, setShowReviewForm] = useState(false);
  const { user, token } = useAuth();

  useEffect(() => {
    fetchReviews();
  }, [product.id]);

  const fetchReviews = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products/${product.id}/reviews`);
      if (response.ok) {
        const data = await response.json();
        setReviews(data);
      }
    } catch (error) {
      console.error('Error fetching reviews:', error);
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('برای ثبت نظر باید وارد شوید');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/products/${product.id}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newReview),
      });

      if (response.ok) {
        setNewReview({ rating: 5, comment: '' });
        setShowReviewForm(false);
        fetchReviews();
        alert('نظر شما با موفقیت ثبت شد');
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('خطا در ثبت نظر');
    }
  };

  const hasDiscount = product.discount_percentage;
  const discountedPrice = hasDiscount ? product.price * (1 - product.discount_percentage / 100) : product.price;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl transform transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative">
          <button 
            onClick={onClose}
            className="absolute top-4 left-4 text-white bg-black bg-opacity-50 hover:bg-opacity-70 w-10 h-10 flex items-center justify-center z-10 transition-all"
          >
            ✕
          </button>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
            {/* Product Image */}
            <div className="relative">
              <img 
                src={product.image} 
                alt={product.name}
                className="w-full h-96 object-cover shadow-lg"
              />
              {hasDiscount && (
                <div className="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 font-bold">
                  {product.discount_percentage}% تخفیف
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="text-right">
              <h1 className="text-3xl font-bold text-gray-800 mb-4">{product.name}</h1>
              <div className="mb-6">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 text-sm font-semibold">
                  {product.category}
                </span>
              </div>
              
              <p className="text-gray-600 mb-6 leading-relaxed text-lg">{product.description}</p>
              
              <div className="mb-6">
                <span className="text-gray-600">موجودی: </span>
                <span className="font-semibold text-green-600">{product.stock} عدد</span>
              </div>

              <div className="mb-8">
                {hasDiscount && (
                  <span className="text-2xl text-gray-400 line-through block mb-2">
                    {product.price.toLocaleString()} تومان
                  </span>
                )}
                <span className="text-4xl font-bold text-blue-600">
                  {Math.round(discountedPrice).toLocaleString()} تومان
                </span>
              </div>

              <button 
                onClick={() => onAddToCart(product)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-xl font-bold transition-all shadow-xl hover:shadow-2xl transform hover:-translate-y-1 mb-4"
              >
                افزودن به سبد خرید
              </button>

              <button 
                className="w-full border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-4 text-xl font-bold transition-all"
              >
                خرید فوری
              </button>
            </div>
          </div>

          {/* Reviews Section */}
          <div className="border-t bg-gray-50 p-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-800">نظرات کاربران</h3>
              {user && (
                <button 
                  onClick={() => setShowReviewForm(!showReviewForm)}
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 font-semibold transition-colors"
                >
                  ثبت نظر
                </button>
              )}
            </div>

            {showReviewForm && (
              <form onSubmit={submitReview} className="mb-8 bg-white p-6 shadow-lg">
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
                    امتیاز
                  </label>
                  <select
                    value={newReview.rating}
                    onChange={(e) => setNewReview(prev => ({...prev, rating: parseInt(e.target.value)}))}
                    className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500"
                  >
                    {[1,2,3,4,5].map(rating => (
                      <option key={rating} value={rating}>{rating} ستاره</option>
                    ))}
                  </select>
                </div>
                
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
                    نظر شما
                  </label>
                  <textarea
                    value={newReview.comment}
                    onChange={(e) => setNewReview(prev => ({...prev, comment: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right"
                    rows="4"
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold transition-colors"
                >
                  ثبت نظر
                </button>
              </form>
            )}

            <div className="space-y-4">
              {reviews.length === 0 ? (
                <p className="text-gray-600 text-center py-8">هنوز نظری ثبت نشده است</p>
              ) : (
                reviews.map((review) => (
                  <div key={review.id} className="bg-white p-6 shadow">
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-right">
                        <div className="font-semibold text-gray-800">{review.user_name}</div>
                        <div className="text-yellow-500">
                          {'★'.repeat(review.rating)}{'☆'.repeat(5-review.rating)}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(review.created_at).toLocaleDateString('fa-IR')}
                      </div>
                    </div>
                    <p className="text-gray-700 text-right">{review.comment}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Full Products Page
const ProductsPage = ({ onAddToCart, initialCategory = '' }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({
    category: initialCategory,
    search: '',
    min_price: '',
    max_price: '',
    sort_by: 'name'
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 12,
    total: 0,
    total_pages: 0
  });
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [filters, pagination.page]);

  useEffect(() => {
    if (initialCategory) {
      setFilters(prev => ({ ...prev, category: initialCategory }));
      setPagination(prev => ({ ...prev, page: 1 }));
    }
  }, [initialCategory]);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products/categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.page,
        limit: pagination.limit,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      });

      const response = await fetch(`${BACKEND_URL}/api/products?${params}`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || []);
        setPagination(prev => ({
          ...prev,
          total: data.total || 0,
          total_pages: data.total_pages || 0
        }));
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">فروشگاه تجهیزات پزشکی</h1>
          <p className="text-xl text-gray-600">بهترین محصولات پزشکی با قیمت مناسب</p>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 shadow-lg mb-8">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">جستجو</label>
              <input
                type="text"
                placeholder="نام محصول..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">دسته‌بندی</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500"
              >
                <option value="">همه دسته‌ها</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">حداقل قیمت</label>
              <input
                type="number"
                placeholder="0"
                value={filters.min_price}
                onChange={(e) => handleFilterChange('min_price', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">حداکثر قیمت</label>
              <input
                type="number"
                placeholder="1000000"
                value={filters.max_price}
                onChange={(e) => handleFilterChange('max_price', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">مرتب‌سازی</label>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500"
              >
                <option value="name">نام محصول</option>
                <option value="price_low">قیمت: کم به زیاد</option>
                <option value="price_high">قیمت: زیاد به کم</option>
                <option value="newest">جدیدترین</option>
              </select>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="loading-spinner"></div>
          </div>
        ) : (
          <>
            <div className="mb-6 text-right text-gray-600">
              {pagination.total} محصول یافت شد
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
              {products.map((product) => (
                <ProductCard 
                  key={product.id} 
                  product={product} 
                  onAddToCart={onAddToCart}
                  onProductClick={setSelectedProduct}
                />
              ))}
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
              <div className="flex justify-center space-x-reverse space-x-2">
                {[...Array(pagination.total_pages)].map((_, index) => (
                  <button
                    key={index + 1}
                    onClick={() => handlePageChange(index + 1)}
                    className={`px-4 py-2 font-semibold transition-colors ${
                      pagination.page === index + 1
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-blue-600 hover:bg-blue-50'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductDetailModal 
          product={selectedProduct} 
          onClose={() => setSelectedProduct(null)}
          onAddToCart={onAddToCart}
        />
      )}
    </div>
  );
};

// Discounts Page
const DiscountsPage = ({ onAddToCart }) => {
  const [discountedProducts, setDiscountedProducts] = useState([]);
  const [discountCodes, setDiscountCodes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDiscountedProducts();
    fetchDiscountCodes();
  }, []);

  const fetchDiscountedProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products/discounted`);
      if (response.ok) {
        const data = await response.json();
        setDiscountedProducts(data);
      }
    } catch (error) {
      console.error('Error fetching discounted products:', error);
    }
  };

  const fetchDiscountCodes = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/discounts`);
      if (response.ok) {
        const data = await response.json();
        setDiscountCodes(data);
      }
    } catch (error) {
      console.error('Error fetching discount codes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">🎯 پیشنهادات ویژه و تخفیف‌ها</h1>
          <p className="text-xl text-gray-600">بهترین پیشنهادات ما را از دست ندهید!</p>
        </div>

        {/* Discount Codes */}
        <div className="bg-white shadow-xl p-8 mb-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">کدهای تخفیف فعال</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {discountCodes.map((discount) => (
              <div key={discount.id} className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 shadow-lg transform hover:scale-105 transition-transform">
                <div className="flex justify-between items-center mb-4">
                  <div className="text-3xl font-bold">{discount.percentage}%</div>
                  <div className="text-right">
                    <div className="font-bold text-lg">{discount.code}</div>
                    <div className="text-sm opacity-90">کد تخفیف</div>
                  </div>
                </div>
                <p className="text-right mb-3">{discount.description}</p>
                <div className="text-sm opacity-90 text-right">
                  حداقل خرید: {discount.min_amount.toLocaleString()} تومان
                </div>
                <div className="text-sm opacity-90 text-right">
                  تا تاریخ: {discount.valid_until}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Discounted Products */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">محصولات با تخفیف ویژه</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {discountedProducts.map((product) => (
              <ProductCard 
                key={product.id} 
                product={product} 
                onAddToCart={onAddToCart}
                onProductClick={() => {}}
              />
            ))}
          </div>
        </div>

        {/* Special Offer Banner */}
        <div className="bg-gradient-to-r from-red-500 to-pink-500 text-white p-12 shadow-2xl text-center">
          <h2 className="text-4xl font-bold mb-4">🔥 فروش ویژه هفته</h2>
          <p className="text-xl mb-6">تا ۵۰٪ تخفیف روی محصولات منتخب</p>
          <div className="text-6xl font-bold mb-4">۲۵٪</div>
          <p className="text-lg">تخفیف روی تمام تجهیزات پزشکی</p>
        </div>
      </div>
    </div>
  );
};

// Articles Section
const ArticlesSection = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchArticles();
  }, []);

  const fetchArticles = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/articles`);
      if (response.ok) {
        const data = await response.json();
        setArticles(data.slice(0, 3)); // Show only first 3 articles
      }
    } catch (error) {
      console.error('Error fetching articles:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <section id="blog" className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">آخرین مقالات وبلاگ</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {articles.map((article) => (
            <div key={article.id} className="bg-white shadow-lg hover:shadow-2xl transition-all duration-500 article-card overflow-hidden">
              <img 
                src={article.image} 
                alt={article.title}
                className="w-full h-48 object-cover transform hover:scale-105 transition-transform duration-500"
              />
              <div className="p-6">
                <div className="text-blue-600 text-sm mb-2 text-right">{article.date}</div>
                <h3 className="text-xl font-bold text-gray-800 mb-3 text-right hover:text-blue-600 transition-colors">{article.title}</h3>
                <p className="text-gray-600 text-right text-sm leading-relaxed">{article.summary}</p>
                <button className="mt-4 text-blue-600 hover:text-blue-700 font-bold transition-colors">
                  ادامه مطلب ←
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Services Section
const ServicesSection = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/services`);
      if (response.ok) {
        const data = await response.json();
        setServices(data);
      }
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <section id="services" className="py-20 bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <span className="text-blue-600 font-bold text-lg">اکسیژن اشباع شده</span>
          <h2 className="text-4xl font-bold text-gray-800 mt-2 mb-4">مراقبت های پزشکی ویژه</h2>
          <p className="text-xl text-gray-600">
            ما بهترین و جدیدترین تجهیزات پزشکی را برای مراقبت های ویژه در منزل با مرکز درمان فراهم می کنیم
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {services.map((service, index) => (
            <div key={service.id} className="relative overflow-hidden shadow-2xl group service-card">
              <img 
                src={service.image} 
                alt={service.title}
                className="w-full h-96 object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                <h3 className="text-2xl font-bold mb-4 text-right">{service.title}</h3>
                <p className="mb-6 text-right opacity-90 leading-relaxed">{service.description}</p>
                <button className="bg-white text-gray-800 px-8 py-3 font-bold hover:bg-gray-100 transition-colors shadow-lg transform hover:-translate-y-1">
                  {index === 0 ? 'بیشتر بدانید' : 'مشاهده محصولات'}
                </button>
              </div>
              {index === 1 && (
                <div className="absolute top-4 right-4 bg-red-500 text-white px-6 py-3 font-bold animate-pulse shadow-lg">
                  ۲۵% تخفیف
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      icon: '💳',
      title: 'پرداخت امن',
      description: 'درگاه پرداخت معتبر'
    },
    {
      icon: '✅',
      title: 'تضمین کیفیت',
      description: 'محصولات اورجینال'
    },
    {
      icon: '🔒',
      title: 'پشتیبانی آنلاین',
      description: 'پشتیبانی ۲۴ ساعته'
    },
    {
      icon: '🚚',
      title: 'ارسال سریع',
      description: 'ارسال به سراسر کشور'
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="text-center p-8 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 bg-white">
              <div className="text-5xl mb-6 feature-icon">{feature.icon}</div>
              <h3 className="text-xl font-bold text-gray-800 mb-3">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Login Modal
const LoginModal = ({ isOpen, onClose, onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(username, password);
      onClose();
      setUsername('');
      setPassword('');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 modal-overlay" onClick={onClose}>
      <div 
        className="bg-white p-8 w-full max-w-md mx-4 transform transition-all modal-content shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-bold text-center mb-6 text-right">ورود به حساب کاربری</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-4 text-right">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              نام کاربری
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              رمز عبور
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 transition-all disabled:opacity-50 btn-primary shadow-lg"
          >
            {loading ? 'در حال ورود...' : 'ورود'}
          </button>
        </form>

        <div className="text-center mt-6">
          <span className="text-gray-600">حساب کاربری ندارید؟ </span>
          <button 
            onClick={onSwitchToRegister}
            className="text-blue-600 hover:text-blue-700 font-bold"
          >
            ثبت نام کنید
          </button>
        </div>
      </div>
    </div>
  );
};

// Register Modal
const RegisterModal = ({ isOpen, onClose, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await register(formData);
      setSuccess('ثبت نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.');
      setFormData({
        username: '',
        email: '',
        password: '',
        full_name: '',
        phone: ''
      });
      setTimeout(() => {
        onSwitchToLogin();
      }, 2000);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 modal-overlay" onClick={onClose}>
      <div 
        className="bg-white p-8 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto transform transition-all modal-content shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-bold text-center mb-6 text-right">ثبت نام</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-4 text-right">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 mb-4 text-right">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              نام و نام خانوادگی
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              نام کاربری
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              ایمیل
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              شماره تلفن
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
              رمز عبور
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 transition-all disabled:opacity-50 btn-primary shadow-lg"
          >
            {loading ? 'در حال ثبت نام...' : 'ثبت نام'}
          </button>
        </form>

        <div className="text-center mt-6">
          <span className="text-gray-600">حساب کاربری دارید؟ </span>
          <button 
            onClick={onSwitchToLogin}
            className="text-blue-600 hover:text-blue-700 font-bold"
          >
            وارد شوید
          </button>
        </div>
      </div>
    </div>
  );
};

// Cart Modal
const CartModal = ({ isOpen, onClose, cartItems, onRemoveItem, onCheckout }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (cartItems.length > 0) {
      fetchProductDetails();
    } else {
      setProducts([]);
      setLoading(false);
    }
  }, [cartItems]);

  const fetchProductDetails = async () => {
    try {
      const productDetails = await Promise.all(
        cartItems.map(async (item) => {
          const response = await fetch(`${BACKEND_URL}/api/products/${item.product_id}`);
          if (response.ok) {
            const product = await response.json();
            return { ...product, quantity: item.quantity };
          }
          return null;
        })
      );
      setProducts(productDetails.filter(p => p !== null));
    } catch (error) {
      console.error('Error fetching product details:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculatePrice = (product) => {
    const basePrice = product.discount_percentage 
      ? product.price * (1 - product.discount_percentage / 100)
      : product.price;
    return Math.round(basePrice);
  };

  const totalAmount = products.reduce((total, product) => total + (calculatePrice(product) * product.quantity), 0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 modal-overlay" onClick={onClose}>
      <div 
        className="bg-white w-full max-w-3xl mx-4 max-h-[90vh] overflow-y-auto transform transition-all modal-content shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-8">
          <div className="flex justify-between items-center mb-6">
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ✕
            </button>
            <h2 className="text-3xl font-bold text-right">سبد خرید</h2>
          </div>
          
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="loading-spinner"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🛒</div>
              <p className="text-xl text-gray-600 mb-6">سبد خرید شما خالی است</p>
              <button 
                onClick={onClose}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 font-bold transition-colors"
              >
                ادامه خرید
              </button>
            </div>
          ) : (
            <>
              <div className="space-y-6 mb-8">
                {products.map((product) => (
                  <div key={product.id} className="flex items-center space-x-4 space-x-reverse border-b pb-6 hover:bg-gray-50 p-4 transition-colors">
                    <img 
                      src={product.image} 
                      alt={product.name}
                      className="w-20 h-20 object-cover shadow-lg"
                    />
                    <div className="flex-1 text-right">
                      <h3 className="font-bold text-lg text-gray-800">{product.name}</h3>
                      <p className="text-gray-600 mb-2">دسته: {product.category}</p>
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="text-lg font-semibold text-gray-700">تعداد: {product.quantity}</span>
                        </div>
                        <div className="text-right">
                          {product.discount_percentage && (
                            <span className="text-sm text-gray-400 line-through block">
                              {product.price.toLocaleString()} تومان
                            </span>
                          )}
                          <span className="text-xl font-bold text-blue-600">
                            {(calculatePrice(product) * product.quantity).toLocaleString()} تومان
                          </span>
                        </div>
                      </div>
                    </div>
                    <button 
                      onClick={() => onRemoveItem(product.id)}
                      className="text-red-500 hover:text-red-700 bg-red-100 hover:bg-red-200 p-2 transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>

              <div className="border-t pt-6 bg-gray-50 p-6">
                <div className="flex justify-between items-center mb-6">
                  <div className="text-3xl font-bold text-blue-600">
                    {totalAmount.toLocaleString()} تومان
                  </div>
                  <div className="text-xl font-bold text-gray-800">مجموع:</div>
                </div>
                
                <button 
                  onClick={onCheckout}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 text-xl transition-all shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
                >
                  🛒 تسویه حساب
                </button>
                
                <button 
                  onClick={onClose}
                  className="w-full mt-3 border-2 border-gray-300 text-gray-700 hover:bg-gray-100 font-bold py-3 px-6 transition-colors"
                >
                  ادامه خرید
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Checkout Modal
const CheckoutModal = ({ isOpen, onClose, cartItems, totalAmount, onOrderComplete }) => {
  const [shippingAddress, setShippingAddress] = useState('');
  const [discountCode, setDiscountCode] = useState('');
  const [discountInfo, setDiscountInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { user, token } = useAuth();

  const finalAmount = discountInfo ? discountInfo.final_amount : totalAmount;

  const validateDiscount = async () => {
    if (!discountCode.trim()) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/discounts/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: discountCode, amount: totalAmount }),
      });

      if (response.ok) {
        const data = await response.json();
        setDiscountInfo(data);
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail);
        setDiscountInfo(null);
      }
    } catch (error) {
      console.error('Discount validation error:', error);
      setError('خطا در بررسی کد تخفیف');
      setDiscountInfo(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const orderData = {
        user_id: user.id,
        items: cartItems,
        total_amount: totalAmount,
        discount_amount: discountInfo ? discountInfo.discount_amount : 0,
        final_amount: finalAmount,
        shipping_address: shippingAddress,
        discount_code: discountCode || null
      };

      const response = await fetch(`${BACKEND_URL}/api/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(orderData),
      });

      if (response.ok) {
        const result = await response.json();
        onOrderComplete(result.order_id);
        setShippingAddress('');
        setDiscountCode('');
        setDiscountInfo(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'خطا در ثبت سفارش');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      setError('خطا در اتصال به سرور');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 modal-overlay" onClick={onClose}>
      <div 
        className="bg-white w-full max-w-lg mx-4 transform transition-all modal-content shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-8">
          <h2 className="text-3xl font-bold text-center mb-8 text-right">💳 تسویه حساب</h2>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-6 text-right">
              {error}
            </div>
          )}

          {/* Order Summary */}
          <div className="mb-8 p-6 bg-gray-50 shadow-lg">
            <h3 className="font-bold text-lg mb-4 text-right">خلاصه سفارش</h3>
            <div className="space-y-2 text-right">
              <div className="flex justify-between">
                <span className="font-semibold">{totalAmount.toLocaleString()} تومان</span>
                <span>مجموع محصولات:</span>
              </div>
              {discountInfo && (
                <div className="flex justify-between text-green-600">
                  <span className="font-semibold">-{discountInfo.discount_amount.toLocaleString()} تومان</span>
                  <span>تخفیف ({discountInfo.discount_percentage}%):</span>
                </div>
              )}
              <hr className="my-3" />
              <div className="flex justify-between text-xl font-bold text-blue-600">
                <span>{finalAmount.toLocaleString()} تومان</span>
                <span>مبلغ نهایی:</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Discount Code */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
                کد تخفیف (اختیاری)
              </label>
              <div className="flex space-x-reverse space-x-2">
                <input
                  type="text"
                  value={discountCode}
                  onChange={(e) => setDiscountCode(e.target.value)}
                  placeholder="کد تخفیف خود را وارد کنید"
                  className="flex-1 px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right"
                />
                <button
                  type="button"
                  onClick={validateDiscount}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 font-semibold transition-colors"
                >
                  اعمال
                </button>
              </div>
              {discountInfo && (
                <p className="text-green-600 text-sm mt-2 text-right">
                  ✅ {discountInfo.description}
                </p>
              )}
            </div>

            <div className="mb-8">
              <label className="block text-gray-700 text-sm font-bold mb-2 text-right">
                آدرس تحویل
              </label>
              <textarea
                value={shippingAddress}
                onChange={(e) => setShippingAddress(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 focus:outline-none focus:border-blue-500 text-right form-input"
                rows="4"
                placeholder="آدرس کامل خود را وارد کنید..."
                required
              />
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 p-6 mb-8 shadow-lg">
              <p className="text-sm text-yellow-800 text-right leading-relaxed">
                📝 <strong>توجه:</strong> در حال حاضر درگاه پرداخت در حال توسعه است. سفارش شما ثبت شده و کارشناسان ما با شما تماس خواهند گرفت.
              </p>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 text-xl transition-all disabled:opacity-50 shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
            >
              {loading ? '⏳ در حال ثبت سفارش...' : '🛒 ثبت سفارش نهایی'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-right">
            <h3 className="text-2xl font-bold mb-4 flex items-center justify-end gap-2">
              <Stethoscope className="w-5 h-5" /> پیک سلامت
            </h3>
            <p className="text-gray-300 leading-relaxed">
              فروشگاه آنلاین تجهیزات پزشکی با بهترین کیفیت و قیمت
            </p>
          </div>
          
          <div className="text-right">
            <h4 className="text-lg font-bold mb-4">لینک های مفید</h4>
            <ul className="space-y-3">
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">درباره ما</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">تماس با ما</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">شرایط و قوانین</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">حریم خصوصی</a></li>
            </ul>
          </div>
          
          <div className="text-right">
            <h4 className="text-lg font-bold mb-4">دسته بندی ها</h4>
            <ul className="space-y-3">
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">تجهیزات پزشکی</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">دارو و مکمل</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">لوازم بهداشتی</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors hover:underline">تجهیزات توانبخشی</a></li>
            </ul>
          </div>
          
          <div className="text-right">
            <h4 className="text-lg font-bold mb-4">تماس با ما</h4>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-center justify-end space-x-reverse space-x-2">
                <span>۰۲۱-۱۲۳۴۵۶۷۸</span>
                <Phone className="w-5 h-5" />
              </li>
              <li className="flex items-center justify-end space-x-reverse space-x-2">
                <span>info@pickselamat.com</span>
                <Mail className="w-5 h-5" />
              </li>
              <li className="flex items-center justify-end space-x-reverse space-x-2">
                <span>تهران، خیابان ولیعصر</span>
                <MapPin className="w-5 h-5" />
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-gray-300">
            © ۱۴۰۳ پیک سلامت. تمامی حقوق محفوظ است.
          </p>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showCartModal, setShowCartModal] = useState(false);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [cartItems, setCartItems] = useState([]);
  const [orderSuccess, setOrderSuccess] = useState(false);

  const { user, token, loading } = useAuth();

  // Load cart from localStorage on component mount
  useEffect(() => {
    if (user) {
      const savedCart = localStorage.getItem(`cart_${user.id}`);
      if (savedCart) {
        setCartItems(JSON.parse(savedCart));
      }
    }
  }, [user]);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    if (user && cartItems.length > 0) {
      localStorage.setItem(`cart_${user.id}`, JSON.stringify(cartItems));
    }
  }, [cartItems, user]);

  const handleAddToCart = (product) => {
    if (!user) {
      setShowLoginModal(true);
      return;
    }

    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.product_id === product.id);
      if (existingItem) {
        return prevItems.map(item =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevItems, { product_id: product.id, quantity: 1 }];
      }
    });

    // Show success message
    alert('✅ محصول به سبد خرید اضافه شد!');
  };

  const handleRemoveFromCart = (productId) => {
    setCartItems(prevItems => prevItems.filter(item => item.product_id !== productId));
  };

  const handleCheckout = () => {
    if (!user) {
      setShowLoginModal(true);
      return;
    }
    setShowCartModal(false);
    setShowCheckoutModal(true);
  };

  const handleOrderComplete = (orderId) => {
    setCartItems([]);
    if (user) {
      localStorage.removeItem(`cart_${user.id}`);
    }
    setShowCheckoutModal(false);
    setOrderSuccess(true);
    alert(`🎉 سفارش شما با کد ${orderId} ثبت شد!`);
  };

  const switchToRegister = () => {
    setShowLoginModal(false);
    setShowRegisterModal(true);
  };

  const switchToLogin = () => {
    setShowRegisterModal(false);
    setShowLoginModal(true);
  };

  const closeAllModals = () => {
    setShowLoginModal(false);
    setShowRegisterModal(false);
    setShowCartModal(false);
    setShowCheckoutModal(false);
  };

  const calculateTotalAmount = () => {
    // This will be calculated in CartModal based on actual product prices
    return 0;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="loading-spinner mb-4"></div>
          <p className="text-gray-600">در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'products':
        return <ProductsPage onAddToCart={handleAddToCart} initialCategory={selectedCategory} />;
      case 'discounts':
        return <DiscountsPage onAddToCart={handleAddToCart} />;
      default:
        return (
          <>
            <HeroSection onProductsClick={() => setCurrentPage('products')} />
            <CategoriesSection onSelectCategory={(cat) => { setSelectedCategory(cat); setCurrentPage('products'); }} />
            <ProductsSection onAddToCart={handleAddToCart} />
            <ServicesSection />
            <ArticlesSection />
            <FeaturesSection />
          </>
        );
    }
  };

  return (
    <div className="min-h-screen bg-white" dir="rtl">
      <Header 
        onLoginClick={() => setShowLoginModal(true)}
        onRegisterClick={() => setShowRegisterModal(true)}
        onCartClick={() => setShowCartModal(true)}
        cartCount={cartItems.reduce((total, item) => total + item.quantity, 0)}
        onProductsClick={() => setCurrentPage('products')}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />
      
      <main>
        {renderCurrentPage()}
      </main>

      <Footer />

      {/* Modals */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={closeAllModals} 
        onSwitchToRegister={switchToRegister}
      />
      
      <RegisterModal 
        isOpen={showRegisterModal} 
        onClose={closeAllModals} 
        onSwitchToLogin={switchToLogin}
      />
      
      <CartModal 
        isOpen={showCartModal} 
        onClose={closeAllModals}
        cartItems={cartItems}
        onRemoveItem={handleRemoveFromCart}
        onCheckout={handleCheckout}
      />
      
      <CheckoutModal 
        isOpen={showCheckoutModal} 
        onClose={closeAllModals}
        cartItems={cartItems}
        totalAmount={calculateTotalAmount()}
        onOrderComplete={handleOrderComplete}
      />
    </div>
  );
}

// App with Auth Provider
const AppWithAuth = () => {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
};

export default AppWithAuth;