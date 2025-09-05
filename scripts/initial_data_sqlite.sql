-- PixelForge Backend - Initial Data SQL (SQLite Version)
-- This file contains the initial data for the database
-- Execute this file after running migrations

-- Categories data
-- Note: Using INSERT OR IGNORE for SQLite compatibility
-- to avoid duplicate entries when running multiple times

-- Initial categories based on the original hardcoded categories
INSERT OR IGNORE INTO categories (name, description, is_active) VALUES 
('Photo Magnets', 'Custom photo magnets for personalized memories', 1),
('Fridge Magnets', 'Decorative and functional fridge magnets', 1),
('Retro Prints', 'Vintage-style prints and posters', 1);

-- Sample admin user (if not exists)
-- Password hash for 'admin1234' using bcrypt
INSERT OR IGNORE INTO users (email, hashed_password, role) VALUES 
('admin@pfs.in', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ADMIN');

-- Sample products with category references
-- Note: This assumes categories have been inserted first
INSERT OR IGNORE INTO products (title, price, category_id, rating, images, is_locked) 
SELECT 'Family Photo Magnet', 15.99, c.id, 4.5, '["sample1.jpg"]', 0
FROM categories c WHERE c.name = 'Photo Magnets';

INSERT OR IGNORE INTO products (title, price, category_id, rating, images, is_locked) 
SELECT 'Vintage Landscape Print', 25.99, c.id, 4.8, '["sample2.jpg"]', 0
FROM categories c WHERE c.name = 'Retro Prints';

INSERT OR IGNORE INTO products (title, price, category_id, rating, images, is_locked) 
SELECT 'Funny Cat Fridge Magnet', 8.99, c.id, 4.2, '["sample3.jpg"]', 0
FROM categories c WHERE c.name = 'Fridge Magnets';

-- Update any existing products that might have NULL category_id
-- This is for migration purposes if products exist without categories
UPDATE products 
SET category_id = (SELECT id FROM categories WHERE name = 'Photo Magnets' LIMIT 1)
WHERE category_id IS NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_is_locked ON products(is_locked);
CREATE INDEX IF NOT EXISTS idx_categories_is_active ON categories(is_active);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Insert metadata about this data load
INSERT OR IGNORE INTO categories (name, description, is_active) VALUES 
('_SYSTEM_DATA_LOADED', 'Marker to indicate initial data has been loaded', 0);
