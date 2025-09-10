# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Starting the Server
- **Development server:** `python run.py` 
- **Alternative:** `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Server runs on:** `http://localhost:8000`

### Database Operations
- **Initialize MongoDB database:** `python scripts/init_db.py`
- **Seed dummy data:** `python scripts/seed_dummy_data.py`
- **MongoDB URL:** Configured in `mongodb_url` setting (default: `mongodb://localhost:27017`)
- **Database name:** Configured in `mongodb_database` setting (default: `pixelforge_db`)

### Testing
- **Run tests:** `pytest tests/ -v`
- **Run with async support:** `pytest tests/ -v --asyncio-mode=auto`

### Dependencies
- **Install dependencies:** `pip install -r requirements.txt`
- **Virtual environment activation:** `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)

## Architecture Overview

This is a FastAPI-based e-commerce backend for PixelForge Studio specializing in custom magnets and photo products.

### Core Architecture Patterns
- **FastAPI routers** organize endpoints by feature domain (auth, users, products, categories, inquiry)
- **Service layer** handles business logic in `app/services/` (auth, email, upload, imagekit)
- **CRUD layer** in `app/crud/` provides database operations using Beanie ODM
- **Pydantic schemas** in `app/schemas/` for request/response validation
- **Dependency injection** pattern for authentication (no database sessions needed)

### Key Components

**Authentication & Authorization:**
- JWT-based authentication with role-based access (USER/ADMIN)
- Admin-only endpoints for product management
- Public endpoints for product viewing and inquiry submission
- Async authentication dependencies

**Product Management:**
- Three product categories: Photo Magnets, Fridge Magnets, Retro Prints
- Product locking mechanism to prevent modifications
- Multi-image upload support (up to 5 images per product, max 5MB each)
- ImageKit integration for cloud image storage and optimization

**Database Schema:**
- MongoDB with Beanie ODM (built on Motor async driver)
- Document-based data model with ObjectId primary keys
- Models defined in `app/models/` as Beanie Document classes
- Document references using Beanie Link for relationships

**Email System:**
- SMTP integration (Office365/Outlook) for notifications
- Welcome emails for new users
- Admin notifications for new products and inquiries
- Asynchronous email sending

### File Organization
```
app/
├── crud/          # Database operations with async MongoDB methods (user.py, product.py, category.py)
├── dependencies/  # FastAPI dependencies (auth.py) - async functions
├── models/        # Beanie Document models with MongoDB ObjectIds
├── routers/       # API endpoints by feature - all async handlers
├── schemas/       # Pydantic request/response models
├── services/      # Business logic (auth, email, upload, imagekit)
├── templates/     # Email templates
├── config.py      # Environment configuration
├── database.py    # MongoDB connection setup with Motor and Beanie
└── main.py        # FastAPI application with MongoDB lifecycle
```

### Configuration Management
- Environment-based configuration using Pydantic Settings
- `.env` file for local development
- Required environment variables: MONGODB_URL, MONGODB_DATABASE, SECRET_KEY, SMTP credentials, ImageKit API keys

### Upload System
- Local file storage in `uploads/products/` directory
- UUID-based filenames to prevent conflicts
- File validation for type (images only) and size limits
- Static file serving at `/uploads` endpoint

### API Response Format
All endpoints use consistent response format:
```json
{
  "success": boolean,
  "message": string,
  "data": object|array|null,
  "total": number (for paginated responses)
}
```

### Testing Infrastructure
- pytest with async support for FastAPI testing
- Test database configuration in `tests/conftest.py`
- Authentication tests in `tests/test_auth.py`