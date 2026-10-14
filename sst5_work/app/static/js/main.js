// ==========================================================
// SHREE SHYAM TOYS — MAIN CLIENT INTERACTIONS
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Nav Drawer
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const mobileNavBackdrop = document.getElementById('mobileNavBackdrop');
  const mobileNavClose = document.getElementById('mobileNavClose');

  if (hamburgerBtn && mobileNavBackdrop) {
    hamburgerBtn.addEventListener('click', () => {
      mobileNavBackdrop.classList.add('open');
      document.body.style.overflow = 'hidden';
    });
    if (mobileNavClose) {
      mobileNavClose.addEventListener('click', () => {
        mobileNavBackdrop.classList.remove('open');
        document.body.style.overflow = '';
      });
    }
    mobileNavBackdrop.addEventListener('click', (e) => {
      if (e.target === mobileNavBackdrop) {
        mobileNavBackdrop.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  }

  // FAQ Accordion
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isActive = item.classList.contains('active');
      // Close all
      document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('active'));
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });

  // Mobile Filters Drawer Toggle
  const mobileFilterBtn = document.getElementById('mobileFilterToggle');
  const filtersSidebar = document.querySelector('.filters-sidebar');
  if (mobileFilterBtn && filtersSidebar) {
    mobileFilterBtn.addEventListener('click', () => {
      const isVisible = window.getComputedStyle(filtersSidebar).display !== 'none';
      filtersSidebar.style.display = isVisible ? 'none' : 'block';
    });
  }
});

// Toast Helper
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
