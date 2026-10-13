/* Content interactions use separate names from GA4 enhanced file_download. */
(() => {
  const record = (name, parameters) => {
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, { page_path: window.location.pathname, ...parameters });
    }
  };
  document.addEventListener('click', event => {
    const preview = event.target.closest?.('details.cv-preview > summary');
    if (preview && !preview.parentElement.open) {
      record('cv_preview_open', { file_name: 'cv.pdf' });
    }
    const link = event.target.closest?.('a[href]');
    if (!link) return;
    const pathname = new URL(link.href, window.location.href).pathname;
    if (pathname.endsWith('/cv.pdf')) {
      record('cv_pdf_click', { file_name: 'cv.pdf' });
    } else if (pathname.endsWith('/teaching-evaluations.pdf')) {
      record('teaching_summary_pdf_click', { file_name: 'teaching-evaluations.pdf' });
    }
  });
  document.addEventListener('toggle', event => {
    const details = event.target;
    if (!details.open) return;
    if (details.matches('details.research-abstract-toggle')) {
      record('abstract_open', { paper_title: details.closest('.paper-item')?.querySelector('h3')?.textContent.trim() || '' });
    }
  }, true);
})();
