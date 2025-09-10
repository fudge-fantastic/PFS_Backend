# PixelForge Studio Backend - Frontend API Integration Guide

## Overview

This guide provides comprehensive instructions for integrating with the PixelForge Studio backend API. The backend is built with FastAPI and provides a RESTful API for managing authentication, products, categories, users, and customer inquiries.

**Base URL:** `http://localhost:8000`  
**API Documentation:** `http://localhost:8000/docs` (Interactive Swagger UI)

## 🔐 Authentication

### JWT Bearer Token Authentication
Only protected endpoints (POST, PUT, PATCH, DELETE) require a JWT token in the Authorization header:
```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN'
}
```

**Note:** Most GET endpoints are public and do not require authentication, except for user-related endpoints which still require authentication for security.

### 1. User Registration
**Endpoint:** `POST /auth/register`
**Access:** Public

```javascript
const registerUser = async (userData) => {
  const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: "user@example.com",
      password: "password123" // minimum 8 characters
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Store token and user data
    localStorage.setItem('access_token', data.data.access_token);
    localStorage.setItem('user', JSON.stringify(data.data.user));
  }
  
  return data;
};
```

**Response Format:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "USER"
    }
  }
}
```

### 2. User Login
**Endpoint:** `POST /auth/login`
**Access:** Public

```javascript
const loginUser = async (credentials) => {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    localStorage.setItem('access_token', data.data.access_token);
    localStorage.setItem('user', JSON.stringify(data.data.user));
  }
  
  return data;
};
```

## 🛍️ Products API

### 1. Get Public Products (Unlocked Only)
**Endpoint:** `GET /products/unlocked`
**Access:** Public (No authentication required)
**Query Parameters:**
- `skip` (optional): Number of products to skip (default: 0)
- `limit` (optional): Maximum products to return (default: 100, max: 1000)
- `category_id` (optional): Filter by category ID

```javascript
const getPublicProducts = async (page = 0, limit = 12, categoryId = null) => {
  const skip = page * limit;
  let url = `http://localhost:8000/products/unlocked?skip=${skip}&limit=${limit}`;
  
  if (categoryId) {
    url += `&category_id=${categoryId}`;
  }
  
  const response = await fetch(url);
  const data = await response.json();
  
  return data;
};
```

**Response Format:**
```json
{
  "success": true,
  "message": "Retrieved 12 unlocked products successfully",
  "data": [
    {
      "id": 1,
      "title": "Custom Photo Magnet",
      "description": "High-quality custom photo magnet with vibrant colors",
      "short_description": "Custom photo magnet",
      "price": 25.99,
      "category_id": 1,
      "category_name": "Photo Magnets",
      "rating": 4.5,
      "images": [
        "/uploads/products/image1.jpg",
        "/uploads/products/image2.jpg"
      ],
      "is_locked": false,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 25
}
```

### 2. Get All Products
**Endpoint:** `GET /products/`
**Access:** Public (No authentication required)
**Query Parameters:**
- `skip` (optional): Number of products to skip (default: 0)
- `limit` (optional): Maximum products to return (default: 100, max: 1000)
- `category_id` (optional): Filter by category ID

```javascript
const getAllProducts = async (page = 0, limit = 12, categoryId = null) => {
  const skip = page * limit;
  let url = `http://localhost:8000/products/?skip=${skip}&limit=${limit}`;
  
  if (categoryId) {
    url += `&category_id=${categoryId}`;
  }
  
  const response = await fetch(url);
  const data = await response.json();
  
  return data;
};
```

### 3. Get Product Details
**Endpoint:** `GET /products/{product_id}`
**Access:** Public (No authentication required)

```javascript
const getProductDetails = async (productId) => {
  const response = await fetch(`http://localhost:8000/products/${productId}`);
  const data = await response.json();
  
  return data;
};
```

### 4. Create Product (Admin Only)
**Endpoint:** `POST /products/`
**Access:** Admin only (Authentication required)
**Content-Type:** `multipart/form-data`

```javascript
const createProduct = async (productData, images = []) => {
  const token = localStorage.getItem('access_token');
  
  const formData = new FormData();
  formData.append('title', productData.title);
  formData.append('description', productData.description || '');
  formData.append('short_description', productData.short_description || '');
  formData.append('price', productData.price);
  formData.append('category_id', productData.category_id);
  formData.append('rating', productData.rating || 0.0);
  
  // Add images (max 5 files, max 5MB each)
  images.forEach((image, index) => {
    formData.append('images', image);
  });
  
  const response = await fetch('http://localhost:8000/products/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
};
```

### 5. Update Product (Admin Only)
**Endpoint:** `PUT /products/{product_id}`
**Access:** Admin only (Authentication required)
**Content-Type:** `multipart/form-data`

```javascript
const updateProduct = async (productId, updateData, newImages = []) => {
  const token = localStorage.getItem('access_token');
  
  const formData = new FormData();
  
  // Add only fields that need updating
  if (updateData.title !== undefined) formData.append('title', updateData.title);
  if (updateData.description !== undefined) formData.append('description', updateData.description);
  if (updateData.short_description !== undefined) formData.append('short_description', updateData.short_description);
  if (updateData.price !== undefined) formData.append('price', updateData.price);
  if (updateData.category_id !== undefined) formData.append('category_id', updateData.category_id);
  if (updateData.rating !== undefined) formData.append('rating', updateData.rating);
  
  // Add new images if provided (replaces existing images)
  newImages.forEach((image) => {
    formData.append('images', image);
  });
  
  const response = await fetch(`http://localhost:8000/products/${productId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
};
```

### 6. Lock/Unlock Products (Admin Only)
```javascript
const lockProduct = async (productId) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/products/${productId}/lock`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};

const unlockProduct = async (productId) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/products/${productId}/unlock`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### 7. Delete Product (Admin Only)
```javascript
const deleteProduct = async (productId) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/products/${productId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

## 📁 Categories API

### 1. Get All Categories
**Endpoint:** `GET /categories/`
**Access:** Public (No authentication required)
**Query Parameters:**
- `skip` (optional): Number of categories to skip (default: 0)
- `limit` (optional): Maximum categories to return (default: 100, max: 1000)
- `active_only` (optional): Filter to show only active categories (default: false)

```javascript
const getAllCategories = async (page = 0, limit = 100, activeOnly = false) => {
  const skip = page * limit;
  const url = `http://localhost:8000/categories/?skip=${skip}&limit=${limit}&active_only=${activeOnly}`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  return data;
};
```

### 2. Get Active Categories Only
**Endpoint:** `GET /categories/active`
**Access:** Public (No authentication required)

```javascript
const getActiveCategories = async (page = 0, limit = 100) => {
  const skip = page * limit;
  const url = `http://localhost:8000/categories/active?skip=${skip}&limit=${limit}`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  return data;
};
```

**Response Format:**
```json
{
  "success": true,
  "message": "Retrieved 3 active categories successfully",
  "data": [
    {
      "id": 1,
      "name": "Photo Magnets",
      "description": "Custom photo magnets in various sizes",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 3
}
```

### 3. Get Category Details
**Endpoint:** `GET /categories/{category_id}`
**Access:** Public (No authentication required)

```javascript
const getCategoryDetails = async (categoryId) => {
  const response = await fetch(`http://localhost:8000/categories/${categoryId}`);
  return await response.json();
};
```

### 4. Create Category (Admin Only)
**Endpoint:** `POST /categories/`
**Access:** Admin only (Authentication required)

```javascript
const createCategory = async (categoryData) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/categories/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      name: categoryData.name,
      description: categoryData.description
    })
  });
  
  return await response.json();
};
```

### 5. Update Category (Admin Only)
**Endpoint:** `PUT /categories/{category_id}`
**Access:** Admin only (Authentication required)

```javascript
const updateCategory = async (categoryId, updateData) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/categories/${categoryId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(updateData)
  });
  
  return await response.json();
};
```

### 6. Delete Category (Admin Only)
**Endpoint:** `DELETE /categories/{category_id}`
**Access:** Admin only (Authentication required)

```javascript
const deleteCategory = async (categoryId, hardDelete = false) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/categories/${categoryId}?hard_delete=${hardDelete}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

## 👥 Users API

### 1. Get Current User Profile
**Endpoint:** `GET /users/me`
**Access:** Authenticated users only

```javascript
const getCurrentUser = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/users/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### 2. Get All Users (Admin Only)
**Endpoint:** `GET /users/`
**Access:** Admin only (Authentication required)

```javascript
const getAllUsers = async (page = 0, limit = 50) => {
  const token = localStorage.getItem('access_token');
  const skip = page * limit;
  
  const response = await fetch(`http://localhost:8000/users/?skip=${skip}&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### 3. Get User by ID (Admin Only)
**Endpoint:** `GET /users/{user_id}`
**Access:** Admin only (Authentication required)

```javascript
const getUserById = async (userId) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/users/${userId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

## 📧 Contact/Inquiry API

### 1. Submit Customer Inquiry
**Endpoint:** `POST /inquiry/contact`
**Access:** Public

```javascript
const submitInquiry = async (inquiryData) => {
  const response = await fetch('http://localhost:8000/inquiry/contact', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      first_name: inquiryData.firstName,
      last_name: inquiryData.lastName,
      email: inquiryData.email,
      phone_number: inquiryData.phoneNumber || null, // optional
      subject: inquiryData.subject,
      message: inquiryData.message, // minimum 10 characters
      subscribe_newsletter: inquiryData.subscribeNewsletter || false
    })
  });
  
  const data = await response.json();
  return data;
};
```

**Response Format:**
```json
{
  "success": true,
  "message": "Thank you for your inquiry! We have received your message and will get back to you soon.",
  "data": {
    "reference_id": "INQ-20240115-1234",
    "submitted_at": "2024-01-15T14:30:00",
    "status": "received"
  }
}
```

### 2. Test Email Service
**Endpoint:** `GET /inquiry/contact/test`
**Access:** Public (No authentication required)

```javascript
const testEmailService = async () => {
  const response = await fetch('http://localhost:8000/inquiry/contact/test');
  return await response.json();
};
```

## 🏥 Health Check API

### Check API Health
**Endpoint:** `GET /health`
**Access:** Public (No authentication required)

```javascript
const checkApiHealth = async () => {
  const response = await fetch('http://localhost:8000/health');
  return await response.json();
};
```

**Response Format:**
```json
{
  "status": "healthy",
  "database": "connected",
  "upload_service": "active"
}
```

## 🛠️ Utility Functions

### Authentication Helpers
```javascript
// Check if user is authenticated
const isAuthenticated = () => {
  const token = localStorage.getItem('access_token');
  return !!token;
};

// Check if user is admin
const isAdmin = () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.role === 'ADMIN';
};

// Logout user
const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

// Get auth headers (only for protected endpoints)
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};
```

### Error Handling
```javascript
const handleApiResponse = async (response) => {
  if (!response.ok) {
    if (response.status === 401) {
      // Unauthorized - redirect to login
      logout();
      return;
    }
    
    const errorData = await response.json();
    throw new Error(errorData.detail || 'API request failed');
  }
  
  return await response.json();
};

// Usage example
const fetchWithErrorHandling = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);
    return await handleApiResponse(response);
  } catch (error) {
    console.error('API Error:', error.message);
    throw error;
  }
};
```

## 📱 Frontend Integration Examples

### React Hook for Products
```javascript
import { useState, useEffect } from 'react';

export const useProducts = (categoryId = null, page = 0, limit = 12, unlockedOnly = true) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const data = unlockedOnly 
          ? await getPublicProducts(page, limit, categoryId)
          : await getAllProducts(page, limit, categoryId);
        setProducts(data.data);
        setTotal(data.total);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, [categoryId, page, limit, unlockedOnly]);
  
  return { products, loading, error, total };
};
```

### Vue.js Composable for Categories
```javascript
import { ref, onMounted } from 'vue';

export function useCategories() {
  const categories = ref([]);
  const loading = ref(true);
  const error = ref(null);
  
  const fetchCategories = async () => {
    loading.value = true;
    try {
      const data = await getActiveCategories();
      categories.value = data.data;
      error.value = null;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(fetchCategories);
  
  return {
    categories,
    loading,
    error,
    refetch: fetchCategories
  };
}
```

### Simple JavaScript Product Listing
```javascript
// Fetch and display products without authentication
async function displayProducts(containerId, categoryId = null) {
  const container = document.getElementById(containerId);
  
  try {
    container.innerHTML = '<p>Loading products...</p>';
    
    const response = await getPublicProducts(0, 12, categoryId);
    const products = response.data;
    
    if (products.length === 0) {
      container.innerHTML = '<p>No products available.</p>';
      return;
    }
    
    const productHTML = products.map(product => `
      <div class="product-card">
        <h3>${product.title}</h3>
        <p>${product.short_description || ''}</p>
        <p class="price">$${product.price}</p>
        <p class="category">${product.category_name}</p>
        ${product.images.length > 0 ? `<img src="http://localhost:8000${product.images[0]}" alt="${product.title}">` : ''}
      </div>
    `).join('');
    
    container.innerHTML = productHTML;
    
  } catch (error) {
    container.innerHTML = `<p>Error loading products: ${error.message}</p>`;
  }
}

// Usage
displayProducts('products-container');
```

## 🔧 Configuration

### Environment Variables for Frontend
```javascript
// config.js
const config = {
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  UPLOAD_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
};

export default config;
```

### API Client Class
```javascript
class ApiClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };
    
    // Only add auth token for non-GET requests or user-related GET endpoints that require auth
    const requiresAuth = options.method && options.method !== 'GET' || 
                        endpoint.startsWith('/users/');
    
    if (requiresAuth) {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    const response = await fetch(url, config);
    return await handleApiResponse(response);
  }
  
  get(endpoint) {
    return this.request(endpoint);
  }
  
  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }
}

export const apiClient = new ApiClient();
```

## 📊 API Response Standards

All API responses follow this consistent format:
```json
{
  "success": boolean,
  "message": string,
  "data": object|array|null,
  "total": number (for paginated responses)
}
```

## 🚀 Getting Started Checklist

1. **Setup Base URL:** Configure your API base URL (`http://localhost:8000`)
2. **Public Endpoints First:** Start with categories and public products (no auth needed)
3. **Authentication Flow:** Implement login/register for admin features
4. **Product Display:** Use `/products/unlocked` for public product listings
5. **Category Navigation:** Use `/categories/active` for category filtering
6. **Contact Form:** Add customer inquiry submission (no auth needed)
7. **Admin Features:** Add authentication for product/category management
8. **Error Handling:** Add comprehensive error handling and user feedback
9. **File Uploads:** Implement image upload for product creation (Admin only)
10. **Testing:** Test all endpoints - public ones work without authentication

## 🔒 Security Notes

- Most GET endpoints are public and require no authentication (products, categories, contact endpoints)
- User-related GET endpoints (`/users/*`) still require authentication for security
- Only POST, PUT, PATCH, DELETE endpoints require JWT tokens
- Admin-only endpoints will return 403 Forbidden if user is not admin
- Implement proper error handling to avoid exposing sensitive information
- Use HTTPS in production
- Sanitize all user inputs
- Implement rate limiting on the frontend for API calls
- Store tokens securely (consider httpOnly cookies in production)

## 📚 Additional Resources

- **API Documentation:** Visit `http://localhost:8000/docs` for interactive API testing
- **Health Check:** `GET /health` to verify API status (no auth required)
- **Static Files:** Product images are served from `/uploads/products/`
- **Public Endpoints:** Most GET requests work without authentication (except user endpoints) for easy frontend development

---

This guide provides a complete foundation for integrating your frontend application with the PixelForge Studio backend API. Most GET endpoints are publicly accessible (except user-related endpoints), making it easy to build public-facing features without authentication complexity. Authentication is only required for data modification operations, user-related queries, and admin-specific functionality.