-- ==========================================================
-- SHREE SHYAM TOYS - Content Safety / Production URL Cleanup
-- Migration: 003_content_safety_cleanup.sql
-- Idempotent cleanup for databases that already received 001/002.
-- ==========================================================

-- Keep seed/demo products out of the public catalogue until verified product data is entered.
UPDATE products
SET availability = 'hidden',
    description = 'Sample catalogue record. Replace with verified product information before publishing.',
    material = 'To be confirmed',
    size_info = 'To be confirmed',
    available_colours = 'To be confirmed',
    weight = 'To be confirmed',
    dimensions = 'To be confirmed',
    seo_description = 'Sample catalogue record. Replace with verified product information before publishing.'
WHERE id BETWEEN 1 AND 12;

-- Disable placeholder social URLs until the real business links are entered through the admin panel.
UPDATE social_links
SET is_enabled = FALSE
WHERE platform IN ('instagram', 'facebook', 'youtube', 'telegram', 'twitter');

-- Neutralize unsupported seeded FAQ/business claims.
UPDATE faqs SET answer = 'Each product in the catalogue has an independently defined Minimum Order Quantity (MOQ). The applicable MOQ is shown on the product page and is validated by the enquiry system before submission.'
WHERE question = 'What is the Minimum Order Quantity (MOQ) for bulk orders?';

UPDATE faqs SET answer = 'Wholesale pricing is not displayed publicly. Submit an enquiry with your quantities and requirements to discuss applicable pricing and availability.'
WHERE question = 'Why are prices not displayed publicly on the website?';

UPDATE faqs SET answer = 'Sample availability can be discussed with our team as part of the enquiry process. Please mention any sample requirement in your enquiry.'
WHERE question = 'Can we request physical sample pieces before committing to a bulk production run?';

UPDATE faqs SET answer = 'Product material, construction, dimensions, colours, and other specifications are shown only when they have been entered for that product in the catalogue. Please contact us if you need any additional product information.'
WHERE question = 'What materials and safety standards are used for stuffing and fabrics?';

UPDATE faqs SET answer = 'When you add items to your enquiry list and click submit, the enquiry is saved in the system first. The selected products and quantities are then formatted for WhatsApp when a business WhatsApp number is configured.'
WHERE question = 'How does the enquiry process work with WhatsApp?';

UPDATE faqs SET answer = 'If you have custom requirements, mention them in your enquiry and our team can confirm what options are available for the requested products.'
WHERE question = 'Do you support custom OEM designs and private labelling?';

-- Neutralize seeded category claims.
UPDATE categories SET description = 'Teddy bear products in the catalogue.', seo_description = 'Browse the teddy bear products available in this category.' WHERE id = 1;
UPDATE categories SET description = 'Larger teddy bear products in the catalogue.', seo_description = 'Browse larger teddy bear products available in this category.' WHERE id = 2;
UPDATE categories SET description = 'Wildlife-themed soft toy products in the catalogue.', seo_description = 'Browse wildlife-themed soft toy products available in this category.' WHERE id = 3;
UPDATE categories SET description = 'Marine and aquatic-themed soft toy products in the catalogue.', seo_description = 'Browse marine and aquatic soft toy products available in this category.' WHERE id = 4;
UPDATE categories SET description = 'Novelty and character soft toy products in the catalogue.', seo_description = 'Browse novelty and character soft toy products available in this category.' WHERE id = 5;
UPDATE categories SET description = 'Baby and infant soft toy products in the catalogue.', seo_description = 'Browse baby and infant soft toy products available in this category.' WHERE id = 6;

-- Neutralize seeded homepage/footer business claims.
UPDATE website_settings SET value = 'Shree Shyam Toys — B2B Soft Toy & Teddy Bear Catalogue' WHERE key = 'website_title';
UPDATE website_settings SET value = 'Browse our soft toy and teddy bear catalogue and contact us for product details and bulk enquiries.' WHERE key = 'footer_text';
UPDATE website_settings SET value = '' WHERE key = 'address' AND value = 'Delhi, India';

UPDATE homepage_sections SET
  subtitle = 'Explore our soft toy and teddy bear catalogue. Connect with us for product specifications and bulk enquiries.'
WHERE section_key = 'hero';

UPDATE homepage_sections SET
  subtitle = 'Browse products, check item-level MOQs, and send a structured bulk enquiry.',
  content = 'Explore the catalogue, review the information available for each product, and contact us with your wholesale requirements.'
WHERE section_key = 'why_choose_us';

UPDATE homepage_sections SET
  subtitle = 'Have a bulk requirement or need more information about a product?',
  content = 'Submit an enquiry with your quantities and requirements to contact our team.'
WHERE section_key = 'bulk_cta';
