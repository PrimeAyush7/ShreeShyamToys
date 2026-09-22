// ==========================================================
// SHREE SHYAM TOYS — MAIN CLIENT INTERACTIONS
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  // Responsive Admin Sidebar
  const adminLayout = document.querySelector('.admin-layout');
  const adminMobileMenu = document.getElementById('adminMobileMenu');
  const adminSidebar = document.getElementById('adminSidebar');
  const adminSidebarBackdrop = document.getElementById('adminSidebarBackdrop');

  if (adminLayout && adminMobileMenu && adminSidebar) {
    const setAdminSidebar = (open) => {
      adminLayout.classList.toggle('admin-sidebar-open', open);
      adminMobileMenu.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (adminSidebarBackdrop) {
        adminSidebarBackdrop.setAttribute('aria-hidden', open ? 'false' : 'true');
      }
      if (window.matchMedia('(max-width: 900px)').matches) {
        document.body.style.overflow = open ? 'hidden' : '';
      }
    };

    adminMobileMenu.addEventListener('click', () => {
      setAdminSidebar(!adminLayout.classList.contains('admin-sidebar-open'));
    });

    if (adminSidebarBackdrop) {
      adminSidebarBackdrop.addEventListener('click', () => setAdminSidebar(false));
    }

    adminSidebar.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.matchMedia('(max-width: 900px)').matches) {
          setAdminSidebar(false);
        }
      });
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && adminLayout.classList.contains('admin-sidebar-open')) {
        setAdminSidebar(false);
      }
    });

    window.addEventListener('resize', () => {
      if (!window.matchMedia('(max-width: 900px)').matches) {
        setAdminSidebar(false);
      }
    });
  }

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
