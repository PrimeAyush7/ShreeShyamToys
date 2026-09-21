-- ==========================================================
-- SHREE SHYAM TOYS - Seed Data
-- Migration: 002_seed_data.sql
-- ==========================================================

-- Website Settings
INSERT INTO website_settings (key, value, type, description) VALUES
('business_name', 'Shree Shyam Toys', 'text', 'Official trading name'),
('website_title', 'Shree Shyam Toys — Premium B2B Soft Toy & Teddy Bear Wholesale Catalogue', 'text', 'Default browser title'),
('meta_description', 'Explore our curated wholesale collection of soft toys, teddy bears, and plush animals. Connect with us for product specifications, custom quantities, and bulk enquiries.', 'text', 'Meta description for search engines'),
('phone', '', 'text', 'Primary business phone number'),
('whatsapp_number', '', 'text', 'Primary WhatsApp Business number (international format with country code, no +)'),
('email', 'contact@shreeshyamtoys.com', 'text', 'Official contact email'),
('address', 'Delhi, India', 'text', 'Physical office / factory address'),
('business_hours', 'Monday – Saturday: 9:30 AM – 7:00 PM IST', 'text', 'Operating hours'),
('logo_url', '/static/images/logo.svg', 'image', 'Main brand logo path'),
('favicon_url', '/static/images/favicon.ico', 'image', 'Favicon path'),
('og_image_url', '/static/images/og-image.png', 'image', 'Default social sharing image'),
('announcement_text', 'Wholesale Catalogue is now live. Explore our plush collections and submit bulk enquiries.', 'text', 'Announcement bar message'),
('announcement_enabled', 'true', 'boolean', 'Show or hide announcement bar'),
('announcement_link', '/catalogue', 'text', 'Announcement bar link URL'),
('footer_text', 'Shree Shyam Toys supplies retail chains, gift shops, and corporate partners with quality plush toys and teddy bears. Connect with us for product details and wholesale bulk enquiries.', 'text', 'Footer about summary'),
('copyright_text', '© 2026 Shree Shyam Toys. All rights reserved. B2B Wholesale Catalogue.', 'text', 'Copyright statement')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Homepage Sections
INSERT INTO homepage_sections (section_key, title, subtitle, content, cta_label, cta_url, image_url, is_enabled, display_order) VALUES
('hero', 'Discover Something Soft & Special', 'Explore our curated collection of soft toys and teddy bears crafted for wholesale distributors and retail partners. Connect with us for product specifications and bulk enquiries.', '', 'Explore Catalogue', '/catalogue', '/static/images/hero-plush.svg', TRUE, 1),
('why_choose_us', 'Why Choose Shree Shyam Toys', 'Quality soft toys and dedicated B2B service for retail partners.', 'We provide a curated collection of soft toys with consistent quality, pleasing designs, and straightforward wholesale enquiry support.', 'Submit Wholesale Enquiry', '/catalogue', '', TRUE, 2),
('how_it_works', 'Simple 4-Step Wholesale Enquiry Flow', 'We simplify catalogue selection and wholesale communication without unnecessary e-commerce overhead.', '1. Sign in with Google | 2. Select products & custom variants | 3. Meet item-level MOQs | 4. Confirm your WhatsApp enquiry directly with our sales desk.', 'Start Browsing', '/catalogue', '', TRUE, 3),
('bulk_cta', 'Bulk Enquiries & Volume Assistance', 'Our sales desk assists retailers, gift shops, and corporate clients with bulk requirements.', 'Looking for specific quantities or product details? Submit an enquiry to connect with our team today.', 'Contact Sales Desk', '#contact', '', TRUE, 4),
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
('instagram', 'Instagram', 'https://instagram.com/shreeshyamtoys', 'instagram', TRUE, 2),
('facebook', 'Facebook', 'https://facebook.com/shreeshyamtoys', 'facebook', TRUE, 3),
('youtube', 'YouTube', 'https://youtube.com/@shreeshyamtoys', 'youtube', TRUE, 4),
('telegram', 'Telegram', 'https://t.me/shreeshyamtoys', 'telegram', TRUE, 5),
('twitter', 'X / Twitter', 'https://x.com/shreeshyamtoys', 'twitter', TRUE, 6)
ON CONFLICT DO NOTHING;

-- FAQs
INSERT INTO faqs (question, answer, display_order, is_active) VALUES
('What is the Minimum Order Quantity (MOQ) for bulk orders?', 'Each product in our catalogue has an independently defined Minimum Order Quantity (MOQ) calibrated to its production run—typically starting from 20 to 100 pieces per design. The enquiry system automatically calculates and validates MOQ limits before allowing submission.', 1, TRUE),
('Why are prices not displayed publicly on the website?', 'As a dedicated wholesale supplier, our pricing depends on order volumes, delivery location, and order requirements. Contacting us via our structured enquiry system ensures you receive an accurate, tailored wholesale quotation.', 2, TRUE),
('Can we request physical sample pieces before committing to a bulk production run?', 'Yes! Once you submit an initial wholesale enquiry and discuss your order requirements with our sales desk, we can dispatch physical pre-production samples for fabric inspection, stitching review, and density verification.', 3, TRUE),
('What materials and safety standards are used for stuffing and fabrics?', 'Shree Shyam Toys products feature soft plush fabrics and resilient polyfill stuffing, designed with neat stitching and secure detailing suitable for retail distribution.', 4, TRUE),
('How does the enquiry process work with WhatsApp?', 'When you add items to your enquiry list and click submit, the system first securely archives your enquiry, chosen variants, and quantities in our database. It then automatically formats an itemized summary and opens a WhatsApp chat with our dedicated B2B sales team.', 5, TRUE),
('Do you support custom OEM designs and private labelling?', 'For commercial volume orders, we can discuss specific color preferences, assorted packing, and customized branding requirements.', 6, TRUE)
ON CONFLICT DO NOTHING;

-- Categories
INSERT INTO categories (id, name, slug, description, image_url, display_order, is_active, seo_title, seo_description) VALUES
(1, 'Classic Teddy Bears', 'classic-teddy-bears', 'Timeless cuddly teddy bears in traditional earthen and pastel shades.', '/static/images/cat-classic-bears.svg', 1, TRUE, 'Classic Teddy Bears Wholesale | Shree Shyam Toys', 'Explore bulk classic teddy bears in multi-size variants from 30cm to 120cm.'),
(2, 'Jumbo & Giant Bears', 'jumbo-giant-bears', 'Lifesize and extra-large plush bears engineered for gift stores and showpieces.', '/static/images/cat-jumbo-bears.svg', 2, TRUE, 'Jumbo & Giant Teddy Bears Bulk Supplier', 'High-volume wholesale supply of giant 4ft, 5ft, and 6ft plush teddy bears.'),
(3, 'Plush Safari & Wildlife', 'plush-safari-wildlife', 'Wild animal soft toys including lions, tigers, elephants, pandas, and giraffes.', '/static/images/cat-safari.svg', 3, TRUE, 'Plush Safari & Wildlife Toys Wholesale', 'Soft wild animal toys made from premium fur materials for wholesale buyers.'),
(4, 'Marine & Aquatic Plush', 'marine-aquatic-plush', 'Whimsical aquatic creatures including octopuses, dolphins, penguins, and whales.', '/static/images/cat-aquatic.svg', 4, TRUE, 'Marine & Ocean Plush Soft Toys B2B', 'Ocean creature plushies available in bulk quantities with certified safety stitching.'),
(5, 'Novelty & Character Plush', 'novelty-character-plush', 'Trendy fruit plushies, boba cups, reversible toys, and modern cushions.', '/static/images/cat-novelty.svg', 5, TRUE, 'Novelty & Trend Plush Soft Toys', 'Cute and trendy plush items designed for modern lifestyle stores and gift retailers.'),
(6, 'Baby & Infant Soft Toys', 'baby-infant-soft-toys', 'Soft baby plush, cuddle companions, and snuggle blankets.', '/static/images/cat-baby.svg', 6, TRUE, 'Baby Soft Toys Wholesale', 'Soft baby plush toys designed for gentle touch and neat finish.')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, slug = EXCLUDED.slug, description = EXCLUDED.description;

-- Products
INSERT INTO products (id, name, slug, sku, category_id, description, material, size_info, available_colours, moq, weight, dimensions, tags, availability, is_featured, is_new_arrival, seo_title, seo_description) VALUES
(1, 'Heritage Cuddle Teddy Bear', 'heritage-cuddle-teddy-bear', 'SST-TB-101', 1, 'Classic traditional teddy bear crafted with soft plush velboa, satin neckbow, embroidered paw pads, and virgin polyfill filling.', 'Soft Velboa & Resilient Polyfill', '30cm, 45cm, 60cm, 90cm', 'Classic Brown, Cream Ivory, Soft Pink', 30, '450g - 1.8kg', '30x25x20 cm to 90x60x45 cm', 'teddy,classic,gift', 'in_stock', TRUE, FALSE, 'Heritage Cuddle Teddy Bear Wholesale | Shree Shyam Toys', 'Bulk enquiry for Heritage Cuddle Teddy Bear with multiple sizes and colors.'),

(2, 'Royal Velvet Giant Bear 5FT', 'royal-velvet-giant-bear-5ft', 'SST-JB-201', 2, 'Show-stopping 5-foot (150cm) giant teddy bear designed for luxury gifting displays, retail window centerpieces, and festival bulk promotions. Reinforced internal seam construction.', 'High-pile Velvet Plush & High Resilience Cotton', '150cm (5 Feet)', 'Caramel Tan, Pure White, Dark Chocolate', 10, '4.8kg', '150x85x65 cm', 'giant bear,5ft,luxury,jumbo', 'in_stock', TRUE, TRUE, 'Royal Velvet Giant Bear 5FT Wholesale', 'Wholesale supplier of 5-foot giant plush bears. Enquire for bulk quotation.'),

(3, 'Sweetheart Blush Ribbon Bear', 'sweetheart-blush-ribbon-bear', 'SST-TB-102', 1, 'Pastel-toned adorable teddy bear with dual-color heart embroidery on the chest and an imported organza ribbon bow. Highly popular for Valentine and festival retail batches.', 'Soft Feather Plush & Polyfill', '40cm, 60cm', 'Blush Pink, Lilac Lavender, Snow White', 50, '550g - 1.1kg', '40x28x22 cm', 'heart bear,ribbon,pastel,gift', 'in_stock', TRUE, FALSE, 'Sweetheart Blush Ribbon Bear Wholesale', 'B2B order for Sweetheart Ribbon Bear with MOQ of 50 pcs.'),

(4, 'Gentle Giant Panda Plush', 'gentle-giant-panda-plush', 'SST-WL-301', 3, 'Authentically styled realistic giant panda sitting soft toy holding a plush bamboo shoot. Crafted with dual-tone black and white plush fur with weighted bottom beans.', 'Microfiber Crystal Velvet & Polyfill with Bean Pellets', '35cm, 50cm, 75cm', 'Black & White Natural', 25, '600g - 2.2kg', '35x30x25 cm', 'panda,wildlife,safari,zoo', 'in_stock', TRUE, TRUE, 'Gentle Giant Panda Plush Wholesale', 'High quality panda soft toys in bulk for wholesale buyers.'),

(5, 'Sahara Savannah Plush Lion', 'sahara-savannah-plush-lion', 'SST-WL-302', 3, 'Majestic plush safari lion with a rich fluffy mane, lifelike sculpted muzzle, and ultra-soft huggable body. Neat stitching and realistic detailing.', 'Long-pile Faux Fur Mane & Soft Velboa Body', '40cm, 65cm', 'Golden Amber, Sandy Tan', 40, '700g - 1.5kg', '40x30x25 cm', 'lion,safari,animals,wildlife', 'in_stock', FALSE, FALSE, 'Sahara Savannah Plush Lion Wholesale', 'Safari plush lion wholesale enquiry from Shree Shyam Toys.'),

(6, 'Deep Sea Emperor Whale Cushion', 'deep-sea-emperor-whale-cushion', 'SST-AQ-401', 4, 'Ergonomically designed blue whale plush that doubles as a backrest pillow or bed companion. Features ribbed corduroy underbelly texture for sensory appeal.', 'Spandex Elastic Super-Soft Fabric & Down Cotton Filling', '60cm, 90cm, 120cm', 'Ocean Blue, Slate Grey, Mint Aqua', 35, '850g - 2.5kg', '60x35x25 cm', 'whale,marine,cushion,aquatic', 'in_stock', TRUE, TRUE, 'Deep Sea Emperor Whale Cushion B2B', 'Bulk enquiry for multi-size plush whale cushions.'),

(7, 'Kawaii Reversible Octopus Mood Toy', 'kawaii-reversible-octopus-mood-toy', 'SST-NV-501', 5, 'Double-sided flip plush octopus with happy and angry expressions. Compact, viral trend item ideal for counter checkout sales and promotional bundles.', 'Short Crystal Plush with Neat Seam Flips', '20cm Diameter', 'Blue/Pink, Yellow/Orange, Purple/Blue, Black/Grey', 100, '120g', '20x20x10 cm', 'octopus,reversible,mood toy,trendy', 'in_stock', FALSE, TRUE, 'Kawaii Reversible Octopus Mood Toy Wholesale', 'MOQ 100 pcs bulk order for viral reversible octopus plush.'),

(8, 'Dreamy Boba Milk Tea Plushie', 'dreamy-boba-milk-tea-plushie', 'SST-NV-502', 5, 'Super cute cylindrical boba bubble tea cup plushie with embroidered facial expressions and 3D plush drinking straw. Irresistible novelty merchandise for lifestyle stores.', 'Elastic Spandex & Cloud Microfiber Fill', '25cm, 40cm, 60cm', 'Classic Milk Tea, Strawberry Pink, Matcha Green', 50, '350g - 1.2kg', '25x18x18 cm', 'boba,bubble tea,cute,novelty', 'in_stock', TRUE, FALSE, 'Dreamy Boba Milk Tea Plushie Bulk', 'Order wholesale boba milk tea plush toys.'),

(9, 'Starlight Slumber Elephant Soft Toy', 'starlight-slumber-elephant-soft-toy', 'SST-BB-601', 6, 'Designed for toddlers with oversized floppy ears, embroidered eyes (no plastic parts), and soft combed plush.', 'Combed Cotton Velour & Soft Polyfill', '30cm, 50cm', 'Baby Blue, Soft Grey, Powder Pink', 50, '380g - 900g', '30x25x20 cm', 'baby,infant,elephant,safe', 'in_stock', TRUE, FALSE, 'Baby Elephant Soft Toy Wholesale', 'Safe baby infant elephant plush in bulk with embroidered eyes.'),

(10, 'Nordic Timber Wolf Plush', 'nordic-timber-wolf-plush', 'SST-WL-303', 3, 'Artisanal sitting wolf plush featuring natural dual-layer grey and white airbrushed highlights, bushy tail, and striking expressive posture.', 'High-density Synthetic Fur & Polyester Wadding', '45cm', 'Silver Grey & Snow White', 30, '750g', '45x30x22 cm', 'wolf,wildlife,nordic,collector', 'coming_soon', FALSE, TRUE, 'Nordic Timber Wolf Plush Wholesale', 'Coming soon: Nordic Timber Wolf soft toy bulk supply.'),

(11, 'Cozy Snuggle Bear 3FT', 'cozy-snuggle-bear-3ft', 'SST-JB-202', 2, 'A versatile 3-foot (90cm) mid-jumbo teddy bear offering the perfect balance between impressive size and manageable shipping carton volume.', 'Plush Rose-swirl Fur & PP Fiber', '90cm (3 Feet)', 'Honey Golden, Mocha Brown, Cream White', 20, '2.1kg', '90x50x40 cm', '3ft bear,jumbo,gift,wholesale', 'in_stock', FALSE, FALSE, 'Cozy Snuggle Bear 3FT Wholesale Enquiry', 'Mid-jumbo 3ft teddy bear wholesale orders from Shree Shyam Toys.'),

(12, 'Playful Paws Fox Soft Toy', 'playful-paws-fox-soft-toy', 'SST-WL-304', 3, 'Charming woodland red fox with a fluffy white-tipped tail, black paw accents, and bright alert ears. Durable stitching suitable for vigorous play.', 'Velboa & Fluffy Boa Tail with Polyfill', '38cm', 'Autumn Rust & Frost White', 45, '420g', '38x22x18 cm', 'fox,woodland,safari,animals', 'out_of_stock', FALSE, FALSE, 'Playful Paws Fox Soft Toy Wholesale', 'Wholesale enquiry for woodland fox plush.')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, sku = EXCLUDED.sku, moq = EXCLUDED.moq;

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
