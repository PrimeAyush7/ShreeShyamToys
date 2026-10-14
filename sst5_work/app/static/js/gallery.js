// ==========================================================
// SHREE SHYAM TOYS — PRODUCT GALLERY & ZOOM
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  const mainImage = document.getElementById('galleryMainImage');
  const thumbs = document.querySelectorAll('.gallery-thumb');
  const zoomLens = document.getElementById('galleryZoomLens');
  const mainContainer = document.getElementById('galleryMainContainer');

  if (!mainImage || !thumbs.length) return;

  // Thumbnail click / switch
  thumbs.forEach(thumb => {
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      const newSrc = thumb.getAttribute('data-img-src');
      if (newSrc) {
        mainImage.src = newSrc;
      }
    });
  });

  // Interactive Zoom on Hover
  if (mainContainer && mainImage) {
    mainContainer.addEventListener('mousemove', (e) => {
      const rect = mainContainer.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      mainImage.style.transformOrigin = `${x}% ${y}%`;
      mainImage.style.transform = 'scale(1.8)';
    });

    mainContainer.addEventListener('mouseleave', () => {
      mainImage.style.transformOrigin = 'center center';
      mainImage.style.transform = 'scale(1)';
    });
  }
});
