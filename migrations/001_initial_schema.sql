-- ==========================================================
-- SHREE SHYAM TOYS - B2B WHOLESALE CATALOGUE & ENQUIRY ENGINE
-- Migration: 001_initial_schema.sql
-- Target: Supabase PostgreSQL (Standard ANSI SQL compatible)
-- ==========================================================

-- Enable UUID extension if supported
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(64) PRIMARY KEY,
    google_id VARCHAR(128) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mobile VARCHAR(32),
    avatar_url TEXT,
    status VARCHAR(32) DEFAULT 'active' CHECK (status IN ('active', 'disabled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_google_id ON customers(google_id);

-- 2. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id VARCHAR(64) PRIMARY KEY,
    google_id VARCHAR(128) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(32) DEFAULT 'admin' CHECK (role IN ('superadmin', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);

-- 3. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    image_url TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    seo_title VARCHAR(255),
    seo_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_order ON categories(display_order);

-- 4. Products Table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    sku VARCHAR(64) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT,
    description TEXT,
    material VARCHAR(255),
    size_info VARCHAR(255),
    available_colours VARCHAR(255),
    moq INTEGER DEFAULT 1 CHECK (moq >= 1),
    weight VARCHAR(64),
    dimensions VARCHAR(128),
    tags TEXT,
    availability VARCHAR(32) DEFAULT 'in_stock' CHECK (availability IN ('in_stock', 'out_of_stock', 'coming_soon', 'hidden')),
    is_featured BOOLEAN DEFAULT FALSE,
    is_new_arrival BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    seo_title VARCHAR(255),
    seo_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_availability ON products(availability);
CREATE INDEX IF NOT EXISTS idx_products_archived ON products(is_archived);

-- 5. Product Variants Table
CREATE TABLE IF NOT EXISTS product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    size VARCHAR(64) NOT NULL,
    colour VARCHAR(64) NOT NULL,
    sku_suffix VARCHAR(64),
    variant_moq INTEGER CHECK (variant_moq IS NULL OR variant_moq >= 1),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id);

-- 6. Product Images Table
CREATE TABLE IF NOT EXISTS product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    alt_text VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_images_product ON product_images(product_id);
CREATE INDEX IF NOT EXISTS idx_images_order ON product_images(display_order);

-- 7. Enquiries Table
CREATE TABLE IF NOT EXISTS enquiries (
    id SERIAL PRIMARY KEY,
    enquiry_reference VARCHAR(64) UNIQUE NOT NULL,
    customer_id VARCHAR(64) REFERENCES customers(id) ON DELETE RESTRICT,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_mobile VARCHAR(32) NOT NULL,
    status VARCHAR(32) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'quotation_sent', 'confirmed', 'completed', 'cancelled')),
    notes TEXT,
    whatsapp_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_enquiries_customer ON enquiries(customer_id);
CREATE INDEX IF NOT EXISTS idx_enquiries_status ON enquiries(status);
CREATE INDEX IF NOT EXISTS idx_enquiries_ref ON enquiries(enquiry_reference);
CREATE INDEX IF NOT EXISTS idx_enquiries_created ON enquiries(created_at DESC);

-- 8. Enquiry Items Table (Preserves snapshot of product & variant)
CREATE TABLE IF NOT EXISTS enquiry_items (
    id SERIAL PRIMARY KEY,
    enquiry_id INTEGER REFERENCES enquiries(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(255) NOT NULL,
    sku VARCHAR(64) NOT NULL,
    category_name VARCHAR(255),
    selected_size VARCHAR(64),
    selected_colour VARCHAR(64),
    quantity INTEGER NOT NULL CHECK (quantity >= 1),
    moq_at_enquiry INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_enquiry_items_enquiry ON enquiry_items(enquiry_id);

-- 9. Website Settings Table
CREATE TABLE IF NOT EXISTS website_settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL,
    type VARCHAR(32) DEFAULT 'text',
    description VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Homepage Sections Table
CREATE TABLE IF NOT EXISTS homepage_sections (
    section_key VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255),
    subtitle TEXT,
    content TEXT,
    cta_label VARCHAR(128),
    cta_url VARCHAR(255),
    image_url TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Social Links Table
CREATE TABLE IF NOT EXISTS social_links (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    url TEXT NOT NULL,
    icon VARCHAR(64),
    is_enabled BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. FAQs Table
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. Media Manifest Table
CREATE TABLE IF NOT EXISTS media_manifest (
    id SERIAL PRIMARY KEY,
    file_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(64) NOT NULL,
    file_size INTEGER DEFAULT 0,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    admin_email VARCHAR(255) NOT NULL,
    action VARCHAR(128) NOT NULL,
    target_type VARCHAR(64) NOT NULL,
    target_id VARCHAR(64),
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at DESC);
