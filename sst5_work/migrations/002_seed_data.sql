-- ==========================================================
-- SHREE SHYAM TOYS - Seed Data
-- Migration: 002_seed_data.sql
-- ==========================================================

-- Website Settings
INSERT INTO website_settings (key, value, type, description) VALUES
('business_name', 'Shree Shyam Toys', 'text', 'Official trading name'),
('website_title', 'Shree Shyam Toys — B2B Soft Toy & Teddy Bear Catalogue', 'text', 'Default browser title'),
('meta_description', 'Explore our curated wholesale collection of soft toys, teddy bears, and plush animals. Connect with us for product specifications, custom quantities, and bulk enquiries.', 'text', 'Meta description for search engines'),
('phone', '', 'text', 'Primary business phone number'),
('whatsapp_number', '', 'text', 'Primary WhatsApp Business number (international format with country code, no +)'),
('email', 'contact@shreeshyamtoys.com', 'text', 'Official contact email'),
('address', '', 'text', 'Business address'),
('business_hours', 'Monday – Saturday: 9:30 AM – 7:00 PM IST', 'text', 'Operating hours'),
('logo_url', '/static/images/logo.svg', 'image', 'Main brand logo path'),
('favicon_url', '/static/images/favicon.ico', 'image', 'Favicon path'),
('og_image_url', '/static/images/og-image.png', 'image', 'Default social sharing image'),
('announcement_text', 'Wholesale Catalogue is now live. Explore our plush collections and submit bulk enquiries.', 'text', 'Announcement bar message'),
('announcement_enabled', 'true', 'boolean', 'Show or hide announcement bar'),
('announcement_link', '/catalogue', 'text', 'Announcement bar link URL'),
('footer_text', 'Browse our soft toy and teddy bear catalogue and contact us for product details and bulk enquiries.', 'text', 'Footer about summary'),
('copyright_text', '© 2026 Shree Shyam Toys. All rights reserved. B2B Wholesale Catalogue.', 'text', 'Copyright statement')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Homepage Sections
INSERT INTO homepage_sections (section_key, title, subtitle, content, cta_label, cta_url, image_url, is_enabled, display_order) VALUES
('hero', 'Discover Something Soft & Special', 'Explore our soft toy and teddy bear catalogue. Connect with us for product specifications and bulk enquiries.', '', 'Explore Catalogue', '/catalogue', '/static/images/hero-plush.svg', TRUE, 1),
('why_choose_us', 'Why Choose Shree Shyam Toys', 'Browse products, check item-level MOQs, and send a structured bulk enquiry.', 'Explore the catalogue, review the information available for each product, and contact us with your wholesale requirements.', 'Submit Wholesale Enquiry', '/catalogue', '', TRUE, 2),
('how_it_works', 'Simple 4-Step Wholesale Enquiry Flow', 'We simplify catalogue selection and wholesale communication without unnecessary e-commerce overhead.', '1. Sign in with Google | 2. Select products & custom variants | 3. Meet item-level MOQs | 4. Confirm your WhatsApp enquiry directly with our sales desk.', 'Start Browsing', '/catalogue', '', TRUE, 3),
('bulk_cta', 'Bulk Enquiries & Product Details', 'Have a bulk requirement or need more information about a product?', 'Submit an enquiry with your quantities and requirements to contact our team.', 'Contact Sales Desk', '#contact', '', TRUE, 4),
('about', 'Discover Something Soft & Special', 'Curated Soft Toys & Plush Collections', 'Shree Shyam Toys offers a versatile collection of soft toys and teddy bears tailored for retailers, gift shops, and bulk purchasers. Connect with us for product information and wholesale enquiries.', 'Learn More', '/catalogue', '/static/images/about-plush.svg', TRUE, 5)
ON CONFLICT (section_key) DO UPDATE SET 
  title = EXCLUDED.title,
  subtitle = EXCLUDED.subtitle,
  content = EXCLUDED.content,
  cta_label = EXCLUDED.cta_label,
  cta_url = EXCLUDED.cta_url;

-- Social Links
INSERT INTO social_links (platform, name, url, icon, is_enabled, display_order) VALUES
('whatsapp', 'WhatsApp Business', '', 'whatsapp', FALSE, 1),
('instagram', 'Instagram', 'https://instagram.com/shreeshyamtoys', 'instagram', FALSE, 2),
('facebook', 'Facebook', 'https://facebook.com/shreeshyamtoys', 'facebook', FALSE, 3),
('youtube', 'YouTube', 'https://youtube.com/@shreeshyamtoys', 'youtube', FALSE, 4),
('telegram', 'Telegram', 'https://t.me/shreeshyamtoys', 'telegram', FALSE, 5),
('twitter', 'X / Twitter', 'https://x.com/shreeshyamtoys', 'twitter', FALSE, 6)
ON CONFLICT DO NOTHING;

-- FAQs
INSERT INTO faqs (question, answer, display_order, is_active) VALUES
('What is the Minimum Order Quantity (MOQ) for bulk orders?', 'Each product in the catalogue has an independently defined Minimum Order Quantity (MOQ). The applicable MOQ is shown on the product page and is validated by the enquiry system before submission.', 1, TRUE),
('Why are prices not displayed publicly on the website?', 'Wholesale pricing is not displayed publicly. Submit an enquiry with your quantities and requirements to discuss applicable pricing and availability.', 2, TRUE),
('Can we request physical sample pieces before committing to a bulk production run?', 'Sample availability can be discussed with our team as part of the enquiry process. Please mention any sample requirement in your enquiry.', 3, TRUE),
('What materials and safety standards are used for stuffing and fabrics?', 'Product material, construction, dimensions, colours, and other specifications are shown only when they have been entered for that product in the catalogue. Please contact us if you need any additional product information.', 4, TRUE),
('How does the enquiry process work with WhatsApp?', 'When you add items to your enquiry list and click submit, the enquiry is saved in the system first. The selected products and quantities are then formatted for WhatsApp when a business WhatsApp number is configured.', 5, TRUE),
('Do you support custom OEM designs and private labelling?', 'If you have custom requirements, mention them in your enquiry and our team can confirm what options are available for the requested products.', 6, TRUE)
ON CONFLICT DO NOTHING;

-- Categories
INSERT INTO categories (id, name, slug, description, image_url, display_order, is_active, seo_title, seo_description) VALUES
(1, 'Classic Teddy Bears', 'classic-teddy-bears', 'Teddy bear products in the catalogue.', '/static/images/cat-classic-bears.svg', 1, TRUE, 'Classic Teddy Bears Wholesale | Shree Shyam Toys', 'Browse the teddy bear products available in this category.'),
(2, 'Jumbo & Giant Bears', 'jumbo-giant-bears', 'Larger teddy bear products in the catalogue.', '/static/images/cat-jumbo-bears.svg', 2, TRUE, 'Jumbo & Giant Teddy Bears Bulk Supplier', 'Browse larger teddy bear products available in this category.'),
(3, 'Plush Safari & Wildlife', 'plush-safari-wildlife', 'Wild animal soft toys including lions, tigers, elephants, pandas, and giraffes.', '/static/images/cat-safari.svg', 3, TRUE, 'Plush Safari & Wildlife Toys Wholesale', 'Browse wildlife-themed soft toy products available in this category.'),
(4, 'Marine & Aquatic Plush', 'marine-aquatic-plush', 'Marine and aquatic-themed soft toy products in the catalogue.', '/static/images/cat-aquatic.svg', 4, TRUE, 'Marine & Ocean Plush Soft Toys B2B', 'Browse marine and aquatic soft toy products available in this category.'),
(5, 'Novelty & Character Plush', 'novelty-character-plush', 'Novelty and character soft toy products in the catalogue.', '/static/images/cat-novelty.svg', 5, TRUE, 'Novelty & Trend Plush Soft Toys', 'Browse novelty and character soft toy products available in this category.'),
(6, 'Baby & Infant Soft Toys', 'baby-infant-soft-toys', 'Baby and infant soft toy products in the catalogue.', '/static/images/cat-baby.svg', 6, TRUE, 'Baby Soft Toys Wholesale', 'Browse baby and infant soft toy products available in this category.')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, slug = EXCLUDED.slug, description = EXCLUDED.description;

-- Products
INSERT INTO products (id, name, slug, sku, category_id, description, material, size_info, available_colours, moq, weight, dimensions, tags, availability, is_featured, is_new_arrival, seo_title, seo_description) VALUES
(1, 'Heritage Cuddle Teddy Bear', 'heritage-cuddle-teddy-bear', 'SST-TB-101', 1, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 30, 'To be confirmed', 'To be confirmed', 'teddy,classic,gift', 'hidden', TRUE, FALSE, 'Heritage Cuddle Teddy Bear Wholesale | Shree Shyam Toys', 'Sample catalogue record. Replace with verified product information before publishing.'),

(2, 'Royal Velvet Giant Bear 5FT', 'royal-velvet-giant-bear-5ft', 'SST-JB-201', 2, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 10, 'To be confirmed', 'To be confirmed', 'giant bear,5ft,luxury,jumbo', 'hidden', TRUE, TRUE, 'Royal Velvet Giant Bear 5FT Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(3, 'Sweetheart Blush Ribbon Bear', 'sweetheart-blush-ribbon-bear', 'SST-TB-102', 1, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 50, 'To be confirmed', 'To be confirmed', 'heart bear,ribbon,pastel,gift', 'hidden', TRUE, FALSE, 'Sweetheart Blush Ribbon Bear Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(4, 'Gentle Giant Panda Plush', 'gentle-giant-panda-plush', 'SST-WL-301', 3, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 25, 'To be confirmed', 'To be confirmed', 'panda,wildlife,safari,zoo', 'hidden', TRUE, TRUE, 'Gentle Giant Panda Plush Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(5, 'Sahara Savannah Plush Lion', 'sahara-savannah-plush-lion', 'SST-WL-302', 3, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 40, 'To be confirmed', 'To be confirmed', 'lion,safari,animals,wildlife', 'hidden', FALSE, FALSE, 'Sahara Savannah Plush Lion Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(6, 'Deep Sea Emperor Whale Cushion', 'deep-sea-emperor-whale-cushion', 'SST-AQ-401', 4, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 35, 'To be confirmed', 'To be confirmed', 'whale,marine,cushion,aquatic', 'hidden', TRUE, TRUE, 'Deep Sea Emperor Whale Cushion B2B', 'Sample catalogue record. Replace with verified product information before publishing.'),

(7, 'Kawaii Reversible Octopus Mood Toy', 'kawaii-reversible-octopus-mood-toy', 'SST-NV-501', 5, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 100, 'To be confirmed', 'To be confirmed', 'octopus,reversible,mood toy,trendy', 'hidden', FALSE, TRUE, 'Kawaii Reversible Octopus Mood Toy Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(8, 'Dreamy Boba Milk Tea Plushie', 'dreamy-boba-milk-tea-plushie', 'SST-NV-502', 5, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 50, 'To be confirmed', 'To be confirmed', 'boba,bubble tea,cute,novelty', 'hidden', TRUE, FALSE, 'Dreamy Boba Milk Tea Plushie Bulk', 'Sample catalogue record. Replace with verified product information before publishing.'),

(9, 'Starlight Slumber Elephant Soft Toy', 'starlight-slumber-elephant-soft-toy', 'SST-BB-601', 6, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 50, 'To be confirmed', 'To be confirmed', 'baby,infant,elephant,safe', 'hidden', TRUE, FALSE, 'Baby Elephant Soft Toy Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(10, 'Nordic Timber Wolf Plush', 'nordic-timber-wolf-plush', 'SST-WL-303', 3, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 30, 'To be confirmed', 'To be confirmed', 'wolf,wildlife,nordic,collector', 'hidden', FALSE, TRUE, 'Nordic Timber Wolf Plush Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),

(11, 'Cozy Snuggle Bear 3FT', 'cozy-snuggle-bear-3ft', 'SST-JB-202', 2, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 20, 'To be confirmed', 'To be confirmed', '3ft bear,jumbo,gift,wholesale', 'hidden', FALSE, FALSE, 'Cozy Snuggle Bear 3FT Wholesale Enquiry', 'Sample catalogue record. Replace with verified product information before publishing.'),

(12, 'Playful Paws Fox Soft Toy', 'playful-paws-fox-soft-toy', 'SST-WL-304', 3, 'Sample catalogue record. Replace with verified product information before publishing.', 'To be confirmed', 'To be confirmed', 'To be confirmed', 45, 'To be confirmed', 'To be confirmed', 'fox,woodland,safari,animals', 'hidden', FALSE, FALSE, 'Playful Paws Fox Soft Toy Wholesale', 'Sample catalogue record. Replace with verified product information before publishing.'),
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, sku = EXCLUDED.sku, moq = EXCLUDED.moq;

-- Seed products are placeholders for development/testing only. They are hidden from the public catalogue
-- until verified product information is entered through the admin panel.
UPDATE products
SET description = 'Sample catalogue record. Replace with verified product information before publishing.',
    material = 'To be confirmed',
    size_info = 'To be confirmed',
    available_colours = 'To be confirmed',
    weight = 'To be confirmed',
    dimensions = 'To be confirmed',
    seo_description = 'Sample catalogue record. Replace with verified product information before publishing.'
WHERE id BETWEEN 1 AND 12;

-- Product Variants
INSERT INTO product_variants (product_id, size, colour, sku_suffix, variant_moq, is_active) VALUES
(1, '30 CM', 'Classic Brown', '-30-BRN', 30, TRUE),
(1, '45 CM', 'Classic Brown', '-45-BRN', 30, TRUE),
(1, '60 CM', 'Classic Brown', '-60-BRN', 30, TRUE),
(1, '90 CM', 'Classic Brown', '-90-BRN', 20, TRUE),
(1, '45 CM', 'Cream Ivory', '-45-CRM', 30, TRUE),
(1, '60 CM', 'Cream Ivory', '-60-CRM', 30, TRUE),
(1, '45 CM', 'Soft Pink', '-45-PNK', 30, TRUE),

(2, '150 CM (5FT)', 'Caramel Tan', '-150-TAN', 10, TRUE),
(2, '150 CM (5FT)', 'Pure White', '-150-WHT', 10, TRUE),
(2, '150 CM (5FT)', 'Dark Chocolate', '-150-CHO', 10, TRUE),

(3, '40 CM', 'Blush Pink', '-40-PNK', 50, TRUE),
(3, '60 CM', 'Blush Pink', '-60-PNK', 40, TRUE),
(3, '40 CM', 'Lilac Lavender', '-40-LAV', 50, TRUE),

(4, '35 CM', 'Black & White Natural', '-35-NAT', 25, TRUE),
(4, '50 CM', 'Black & White Natural', '-50-NAT', 25, TRUE),
(4, '75 CM', 'Black & White Natural', '-75-NAT', 15, TRUE),

(5, '40 CM', 'Golden Amber', '-40-AMB', 40, TRUE),
(5, '65 CM', 'Golden Amber', '-65-AMB', 30, TRUE),

(6, '60 CM', 'Ocean Blue', '-60-BLU', 35, TRUE),
(6, '90 CM', 'Ocean Blue', '-90-BLU', 25, TRUE),
(6, '120 CM', 'Ocean Blue', '-120-BLU', 15, TRUE),

(7, '20 CM', 'Blue / Pink Reversible', '-20-BLPN', 100, TRUE),
(7, '20 CM', 'Yellow / Orange Reversible', '-20-YLOR', 100, TRUE),
(7, '20 CM', 'Purple / Blue Reversible', '-20-PRBL', 100, TRUE),

(8, '25 CM', 'Classic Milk Tea', '-25-MLK', 50, TRUE),
(8, '40 CM', 'Classic Milk Tea', '-40-MLK', 40, TRUE),
(8, '40 CM', 'Strawberry Pink', '-40-STR', 40, TRUE),

(9, '30 CM', 'Soft Grey', '-30-GRY', 50, TRUE),
(9, '50 CM', 'Soft Grey', '-50-GRY', 35, TRUE),
(9, '30 CM', 'Baby Blue', '-30-BLU', 50, TRUE),

(10, '45 CM', 'Silver Grey & White', '-45-SGW', 30, TRUE),
(11, '90 CM (3FT)', 'Honey Golden', '-90-GLD', 20, TRUE),
(11, '90 CM (3FT)', 'Mocha Brown', '-90-MCH', 20, TRUE),
(12, '38 CM', 'Autumn Rust', '-38-RST', 45, TRUE)
ON CONFLICT DO NOTHING;

-- Product Images
INSERT INTO product_images (product_id, image_url, alt_text, display_order, is_primary) VALUES
(1, '/static/images/products/heritage-bear-1.svg', 'Heritage Cuddle Teddy Bear Front View', 1, TRUE),
(1, '/static/images/products/heritage-bear-2.svg', 'Heritage Cuddle Teddy Bear Side Angle', 2, FALSE),
(1, '/static/images/products/heritage-bear-3.svg', 'Heritage Cuddle Teddy Bear Ribbon Detail', 3, FALSE),

(2, '/static/images/products/giant-bear-1.svg', 'Royal Velvet Giant Bear 5FT Full Display', 1, TRUE),
(2, '/static/images/products/giant-bear-2.svg', 'Royal Velvet Giant Bear Scale with Model', 2, FALSE),

(3, '/static/images/products/sweetheart-bear-1.svg', 'Sweetheart Blush Ribbon Bear Front', 1, TRUE),
(3, '/static/images/products/sweetheart-bear-2.svg', 'Sweetheart Blush Ribbon Bear Heart Embroidery', 2, FALSE),

(4, '/static/images/products/panda-plush-1.svg', 'Gentle Giant Panda Plush Sitting', 1, TRUE),
(4, '/static/images/products/panda-plush-2.svg', 'Gentle Giant Panda Plush Bamboo Detail', 2, FALSE),

(5, '/static/images/products/lion-plush-1.svg', 'Sahara Savannah Plush Lion Display', 1, TRUE),
(6, '/static/images/products/whale-plush-1.svg', 'Deep Sea Emperor Whale Cushion Profile', 1, TRUE),
(7, '/static/images/products/octopus-plush-1.svg', 'Kawaii Reversible Octopus Mood Toy Happy & Angry', 1, TRUE),
(8, '/static/images/products/boba-plush-1.svg', 'Dreamy Boba Milk Tea Plushie', 1, TRUE),
(9, '/static/images/products/elephant-plush-1.svg', 'Starlight Slumber Elephant Soft Toy', 1, TRUE),
(10, '/static/images/products/wolf-plush-1.svg', 'Nordic Timber Wolf Plush Sitting Posture', 1, TRUE),
(11, '/static/images/products/snuggle-bear-1.svg', 'Cozy Snuggle Bear 3FT', 1, TRUE),
(12, '/static/images/products/fox-plush-1.svg', 'Playful Paws Fox Soft Toy', 1, TRUE)
ON CONFLICT DO NOTHING;
