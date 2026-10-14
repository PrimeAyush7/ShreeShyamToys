// ==========================================================
// SHREE SHYAM TOYS — B2B WHOLESALE ENQUIRY ENGINE (v2.0)
// Supports 1-Click Guest B2B Checkout + Google Account Sync
// ==========================================================

const SST_STORAGE_KEY = 'sst_enquiry_cart_v1';
const SST_BUYER_PROFILE_KEY = 'sst_guest_buyer_v2';

function getEnquiryCart() {
  try {
    const raw = localStorage.getItem(SST_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Error reading enquiry cart:', e);
    return [];
  }
}

function saveEnquiryCart(cart) {
  try {
    localStorage.setItem(SST_STORAGE_KEY, JSON.stringify(cart));
    updateCartBadges();
  } catch (e) {
    console.error('Error saving enquiry cart:', e);
  }
}

function updateCartBadges() {
  const cart = getEnquiryCart();
  const badges = document.querySelectorAll('.enquiry-count');
  badges.forEach(b => {
    b.textContent = cart.length;
    b.style.display = cart.length > 0 ? 'inline-flex' : 'none';
  });
}

function addToEnquiry(productId, productName, sku, moq, imageUrl, selectedSize = '', selectedColour = '', quantity = null) {
  const cart = getEnquiryCart();
  const effectiveMoq = parseInt(moq) || 1;
  const initialQty = quantity !== null ? parseInt(quantity) : effectiveMoq;

  if (initialQty < effectiveMoq) {
    showToast(`Minimum order quantity for this item is ${effectiveMoq} pieces.`, 'error');
    return;
  }

  const existingIndex = cart.findIndex(i => i.productId === productId && i.selectedSize === selectedSize && i.selectedColour === selectedColour);
  if (existingIndex > -1) {
    cart[existingIndex].quantity += initialQty;
    showToast(`Updated quantity for ${productName} to ${cart[existingIndex].quantity} pcs.`, 'success');
  } else {
    cart.push({
      productId,
      productName,
      sku,
      moq: effectiveMoq,
      imageUrl: imageUrl || '/static/images/placeholder.svg',
      selectedSize,
      selectedColour,
      quantity: initialQty
    });
    showToast(`Added ${productName} (${initialQty} pcs) to enquiry bag.`, 'success');
  }

  saveEnquiryCart(cart);
  renderEnquiryDrawer();
  openEnquiryDrawer();
}

function updateCartItemQty(index, newQty) {
  const cart = getEnquiryCart();
  if (index < 0 || index >= cart.length) return;

  const item = cart[index];
  const qty = parseInt(newQty);

  if (qty < item.moq) {
    showToast(`Minimum order quantity for this product is ${item.moq} pieces.`, 'error');
    renderEnquiryDrawer();
    return;
  }

  cart[index].quantity = qty;
  saveEnquiryCart(cart);
  renderEnquiryDrawer();
}

function removeCartItem(index) {
  const cart = getEnquiryCart();
  if (index >= 0 && index < cart.length) {
    const removed = cart.splice(index, 1);
    saveEnquiryCart(cart);
    renderEnquiryDrawer();
    showToast(`Removed ${removed[0].productName} from enquiry.`, 'info');
  }
}

function openEnquiryDrawer() {
  const backdrop = document.getElementById('enquiryDrawerBackdrop');
  if (backdrop) {
    renderEnquiryDrawer();
    backdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeEnquiryDrawer() {
  const backdrop = document.getElementById('enquiryDrawerBackdrop');
  if (backdrop) {
    backdrop.classList.remove('open');
    document.body.style.overflow = '';
  }
}

function renderEnquiryDrawer() {
  const listContainer = document.getElementById('enquiryDrawerItems');
  const footerContainer = document.getElementById('enquiryDrawerFooter');
  if (!listContainer) return;

  const cart = getEnquiryCart();
  if (cart.length === 0) {
    listContainer.innerHTML = `
      <div style="text-align: center; padding: 48px 16px; color: var(--text-muted);">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin: 0 auto 16px; color: var(--accent);">
          <path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
        </svg>
        <h4 style="font-size: 16px; font-weight: 700; color: var(--text-main); margin-bottom: 6px;">Your Enquiry Bag is Empty</h4>
        <p style="font-size: 13px; line-height: 1.5; margin-bottom: 20px;">Browse our wholesale plush catalogue and add MOQ lots or full cartons to request bulk quotations.</p>
        <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
          <a href="/catalogue" class="btn btn-primary btn-sm" onclick="closeEnquiryDrawer()">Browse Catalogue</a>
          <a href="/catalogue/pdf" class="btn btn-outline btn-sm">&#128229; Download PDF Sheet</a>
        </div>
      </div>
    `;
    if (footerContainer) footerContainer.style.display = 'none';
    return;
  }

  if (footerContainer) footerContainer.style.display = 'block';

  const totalPieces = cart.reduce((sum, item) => sum + item.quantity, 0);
  let html = `
    <div style="background: var(--primary-light); border: 1px solid #E6CCB2; border-radius: 8px; padding: 8px 12px; margin-bottom: 10px; font-size: 12.5px; display: flex; justify-content: space-between; align-items: center;">
      <span>Selected Designs: <strong>${cart.length} models</strong></span>
      <span>Total Volume: <strong style="color: var(--primary);">${totalPieces} pcs</strong></span>
    </div>
  `;
  cart.forEach((item, index) => {
    html += `
      <div class="enquiry-item-row">
        <img src="${item.imageUrl}" alt="${item.productName}" class="enquiry-item-thumb">
        <div class="enquiry-item-info">
          <div style="display: flex; justify-content: space-between; align-items: start;">
            <div class="enquiry-item-name">${item.productName}</div>
            <button onclick="removeCartItem(${index})" style="background: none; border: none; color: #9CA3AF; cursor: pointer; font-size: 18px;" title="Remove">&times;</button>
          </div>
          <div class="enquiry-item-sku">SKU: ${item.sku}</div>
          ${(item.selectedSize || item.selectedColour) ? `<div class="enquiry-item-variant">${item.selectedSize ? 'Size: ' + item.selectedSize : ''} ${item.selectedColour ? '| Colour: ' + item.selectedColour : ''}</div>` : ''}
          <div class="enquiry-item-moq-tag">MOQ: ${item.moq} pcs</div>
          <div class="qty-stepper">
            <span style="font-size: 12px; color: var(--text-muted); margin-right: 4px;">Qty:</span>
            <button type="button" class="qty-btn" onclick="updateCartItemQty(${index}, ${item.quantity - 5})">-</button>
            <input type="number" class="qty-input" value="${item.quantity}" min="${item.moq}" onchange="updateCartItemQty(${index}, this.value)">
            <button type="button" class="qty-btn" onclick="updateCartItemQty(${index}, ${item.quantity + 5})">+</button>
            <span style="font-size: 12px; color: var(--text-light); margin-left: 6px;">pcs</span>
          </div>
        </div>
      </div>
    `;
  });
  listContainer.innerHTML = html;
}

async function submitWholesaleEnquiry(event) {
  if (event) event.preventDefault();
  const cart = getEnquiryCart();
  if (cart.length === 0) {
    showToast('Please add products to your enquiry first.', 'error');
    return;
  }

  for (const itm of cart) {
    if (itm.quantity < itm.moq) {
      showToast(`Minimum order quantity for '${itm.productName}' is ${itm.moq} pieces.`, 'error');
      return;
    }
  }

  const mobileInput = document.getElementById('enquiryMobileInput');
  const cityInput = document.getElementById('enquiryCityInput');
  const nameInput = document.getElementById('enquiryNameInput');
  const emailInput = document.getElementById('enquiryEmailInput');
  const notesInput = document.getElementById('enquiryNotesInput');

  const mobileVal = mobileInput ? mobileInput.value.trim() : '';
  const cityVal = cityInput ? cityInput.value.trim() : '';
  const nameVal = nameInput ? nameInput.value.trim() : '';
  const emailVal = emailInput ? emailInput.value.trim() : '';
  const notesVal = notesInput ? notesInput.value.trim() : '';

  if (!mobileVal || mobileVal.length < 8) {
    showToast('Please provide a valid WhatsApp mobile number.', 'error');
    if (mobileInput) mobileInput.focus();
    return;
  }

  // Persist guest buyer profile locally for future convenience
  try {
    localStorage.setItem(SST_BUYER_PROFILE_KEY, JSON.stringify({
      mobile: mobileVal,
      city: cityVal,
      name: nameVal,
      email: emailVal
    }));
  } catch (e) {}

  const submitBtn = document.getElementById('enquirySubmitBtn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Archiving Enquiry...';
  }

  try {
    const payload = {
      customer_name: nameVal || 'Wholesale Buyer',
      customer_email: emailVal || 'guest@shreeshyamtoys.com',
      customer_mobile: mobileVal,
      customer_city: cityVal,
      notes: notesVal,
      items: cart.map(i => ({
        product_id: i.productId,
        selected_size: i.selectedSize,
        selected_colour: i.selectedColour,
        quantity: i.quantity
      }))
    };

    const response = await fetch('/api/enquiry/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Could not process enquiry');
    }

    saveEnquiryCart([]);
    closeEnquiryDrawer();

    showEnquirySuccessModal(result.enquiry_reference, result.whatsapp_url, result.whatsapp_message);

    try {
      if (result.whatsapp_url) { window.open(result.whatsapp_url, '_blank'); }
    } catch (e) {
      console.log('Browser blocked automatic popup; fallback button is visible.');
    }

  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Submit Enquiry to WhatsApp &rarr;';
    }
  }
}

function showEnquirySuccessModal(reference, whatsappUrl, messageText) {
  let modal = document.getElementById('enquirySuccessModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'enquirySuccessModal';
    modal.className = 'drawer-backdrop open';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    document.body.appendChild(modal);
  }

  modal.innerHTML = `
    <div style="background: #FFFFFF; border-radius: var(--radius-xl); max-width: 520px; width: 90%; padding: 32px; box-shadow: var(--shadow-lg); text-align: center; position: relative;">
      <div style="width: 64px; height: 64px; background: #D1FAE5; color: #059669; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 28px;">
        &#10003;
      </div>
      <h3 style="font-size: 22px; font-weight: 800; color: var(--text-main); margin-bottom: 8px;">Enquiry Saved &amp; Archived!</h3>
      <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 16px;">
        Reference: <strong style="color: var(--primary); font-family: monospace;">${reference}</strong>
      </p>
      <div style="background: var(--bg-page); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 14px; font-size: 12px; text-align: left; max-height: 160px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; margin-bottom: 24px; color: var(--text-muted);">${messageText}</div>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        ${whatsappUrl ? `
        <a href="${whatsappUrl}" target="_blank" class="btn btn-whatsapp btn-lg" style="text-decoration: none;">
          Open WhatsApp Business Chat &rarr;
        </a>` : `
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 12px; border-radius: var(--radius-md); font-size: 13px;">
          Your enquiry has been securely logged. Our wholesale team will reach out directly to your registered mobile number.
        </div>`}
        <button onclick="document.getElementById('enquirySuccessModal').remove(); document.body.style.overflow='';" class="btn btn-outline">
          Close Window
        </button>
      </div>
      <p style="font-size: 12px; color: var(--text-light); margin-top: 14px;">
        ${whatsappUrl ? 'Your enquiry is securely stored in our database. If WhatsApp did not open automatically, click the green button above.' : 'Enquiry safely archived in the database.'}
      </p>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', () => {
  updateCartBadges();

  // Restore saved guest buyer fields if empty
  try {
    const saved = JSON.parse(localStorage.getItem(SST_BUYER_PROFILE_KEY) || '{}');
    const mIn = document.getElementById('enquiryMobileInput');
    const cIn = document.getElementById('enquiryCityInput');
    const nIn = document.getElementById('enquiryNameInput');
    const eIn = document.getElementById('enquiryEmailInput');
    if (mIn && !mIn.value && saved.mobile) mIn.value = saved.mobile;
    if (cIn && !cIn.value && saved.city) cIn.value = saved.city;
    if (nIn && !nIn.value && saved.name) nIn.value = saved.name;
    if (eIn && !eIn.value && saved.email) eIn.value = saved.email;
  } catch (e) {}

  const closeBtn = document.getElementById('enquiryDrawerClose');
  const backdrop = document.getElementById('enquiryDrawerBackdrop');
  if (closeBtn) closeBtn.addEventListener('click', closeEnquiryDrawer);
  if (backdrop) {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closeEnquiryDrawer();
    });
  }
});
