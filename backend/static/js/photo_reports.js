(() => {
  const viewer = document.getElementById('photo-viewer');
  if (!viewer || !viewer.showModal) return;
  const image = document.getElementById('photo-viewer-image');
  const caption = document.getElementById('photo-viewer-caption');
  const error = viewer.querySelector('[data-preview-error]');
  let opener;
  document.querySelectorAll('.photo-enlarge').forEach(link => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      error.hidden = true;
      image.hidden = false;
      image.alt = link.querySelector('img').alt;
      caption.replaceChildren(link.closest('figure').querySelector('figcaption').cloneNode(true));
      image.src = link.href;
      viewer.showModal();
    });
  });
  image.addEventListener('error', () => { error.hidden = false; image.hidden = true; });
  viewer.querySelector('[data-close-viewer]').addEventListener('click', () => viewer.close());
  viewer.addEventListener('close', () => { image.removeAttribute('src'); opener?.focus(); });
})();
