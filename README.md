# PixelForge Backend

A secure and scalable backend API for PixelForge Studio's system built with FastAPI, PostgreSQL, JWT authentication, and SMTP email integration.

## Features

- **Product Management**: CRUD operations for products with category validation and descriptions
- **Image Storage**: ImageKit integration for cloud-based image storage and optimization
- **Advanced Product Filtering**: Get unlocked products only, filter by category with flexible options
- **User Management**: User registration, authentication with JWT, role-based access (Admin/User)
- **File Upload**: Image upload support for products (max 5 images per product) with ImageKit cloud storage
- **Product Locking**: Prevent accidental modifications to products
- **Email Integration**: Welcome emails for new users, admin notifications for new products
- **API Documentation**: Auto-generated Swagger UI at `/docs`

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **Passlib**: Password hashing
- **ImageKit**: Cloud-based image storage and optimization
- **SMTP**: Email service integration (Office365/Outlook)
- **Pydantic**: Data validation using Python type hints

## Project Structure

```
pfs backend/
├── app/
│   ├── crud/                 # Database CRUD operations
│   │   ├── user.py
│   │   └── product.py
│   ├── dependencies/         # FastAPI dependencies
│   │   └── auth.py
│   ├── models/              # SQLAlchemy models
│   │   └── __init__.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── products.py
│   ├── schemas/             # Pydantic models
│   │   └── __init__.py
│   ├── services/            # Business logic services
│   │   ├── auth.py
│   │   ├── email.py
│   │   └── upload.py
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection
│   └── main.py            # FastAPI application
├── alembic/               # Database migrations
├── tests/                 # Test files
├── uploads/               # File upload directory
├── requirements.txt       # Python dependencies
├── alembic.ini           # Alembic configuration
├── .env.example          # Environment variables template
└── run.py               # Development server
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "pfs backend"
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database**:
   - Create a PostgreSQL database named `pixelforge_db`
   - Update `DATABASE_URL` in `.env` file

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Start the development server**:
   ```bash
   python run.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Configuration

Update the `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/pixelforge_db

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=support@pixelforgestudio.in
SMTP_PASSWORD=your-smtp-password
ADMIN_EMAIL=admin@pfs.in

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/token` - OAuth2 compatible token endpoint

### Users
- `GET /users/me` - Get current user details
- `GET /users/` - List all users (Admin only)
- `GET /users/{id}` - Get user by ID (Admin only)

### Products
- `POST /products/` - Create product (Admin only)
- `GET /products/` - List products (with category filter)
- `GET /products/unlocked` - List only unlocked products (with optional category filter)
- `GET /products/category/{category}` - Get products by specific category (with unlocked_only parameter)
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product (Admin only)
- `DELETE /products/{id}` - Delete product (Admin only)
- `PATCH /products/{id}/lock` - Lock product (Admin only)
- `PATCH /products/{id}/unlock` - Unlock product (Admin only)

### Other
- `GET /` - Welcome message and API info
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## New Product Filtering Endpoints

### Get Unlocked Products
**Endpoint:** `GET /products/unlocked`

**Description:** Retrieve only products that are not locked, useful for displaying editable products in admin interfaces.

**Query Parameters:**
- `skip` (int, optional): Number of products to skip (default: 0)
- `limit` (int, optional): Maximum number of products to return (default: 100, max: 1000)
- `category` (str, optional): Filter by specific category

**Example:**
```
GET /products/unlocked?skip=0&limit=10&category=Photo Magnets
```

### Get Products by Category
**Endpoint:** `GET /products/category/{category}`

**Description:** Retrieve products filtered by a specific category with additional filtering options.

**Path Parameters:**
- `category` (str): The product category (Photo Magnets, Fridge Magnets, Retro Prints)

**Query Parameters:**
- `skip` (int, optional): Number of products to skip (default: 0)
- `limit` (int, optional): Maximum number of products to return (default: 100, max: 1000)
- `unlocked_only` (bool, optional): Filter to show only unlocked products (default: false)

**Examples:**
```
GET /products/category/Photo Magnets
GET /products/category/Fridge Magnets?unlocked_only=true&limit=20
```

**Response Format:**
```json
{
  "success": true,
  "message": "Retrieved X products in 'Category' category successfully",
  "data": [
    {
      "id": 1,
      "title": "Product Title",
      "price": 25.99,
      "category": "Photo Magnets",
      "rating": 4.5,
      "images": ["path/to/image.jpg"],
      "is_locked": false,
      "created_at": "2025-09-02T10:00:00",
      "updated_at": "2025-09-02T10:00:00"
    }
  ],
  "total": 25
}
```

## Product Categories

The API supports three product categories:
- Photo Magnets
- Fridge Magnets
- Retro Prints

## User Roles

- **Admin**: Full CRUD access to products, can view all users, receives email notifications
- **User**: Read-only access to products, can register and login

## Testing

Run tests using pytest:

```bash
pytest tests/ -v
```

## Email Features

- **Welcome Email**: Sent to new users upon registration
- **Admin Notification**: Sent to admin when new products are created
- **SMTP Integration**: Configured for Office365/Outlook

## File Upload

- **Image Support**: JPG, JPEG, PNG, GIF, WebP
- **Size Limit**: 5MB per image
- **Product Limit**: Maximum 5 images per product
- **Storage**: Files stored in `uploads/products/` directory

## Security Features

- **Password Hashing**: Bcrypt with salt
- **JWT Authentication**: Secure token-based auth
- **Role-based Access**: Admin/User permissions
- **Input Validation**: Pydantic models for request validation
- **CORS**: Configurable cross-origin resource sharing

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Development

- **Hot Reload**: Enabled in development mode
- **Logging**: Comprehensive logging throughout the application
- **Error Handling**: Global exception handlers
- **Validation**: Request/response validation with Pydantic

## Production Deployment

1. Set `SECRET_KEY` to a secure random string
2. Update `DATABASE_URL` for production database
3. Configure SMTP settings for email service
4. Set up proper CORS origins
5. Use a production WSGI server like Gunicorn
6. Set up reverse proxy (Nginx) for static files
7. Configure SSL/TLS certificates

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For issues and questions, contact: support@pixelforgestudio.in

## License

MIT License - see LICENSE file for details
