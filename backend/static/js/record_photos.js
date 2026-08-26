(() => {
  const form = document.getElementById('record-photo-form');
  if (!form) return;
  const container = document.getElementById('photo-forms');
  const total = document.getElementById('id_form-TOTAL_FORMS');
  const add = document.getElementById('add-photo');
  function renumber() {
    const rows = container.querySelectorAll('.photo-fields');
    rows.forEach((row, index) => {
      row.querySelectorAll('[name], [id], [for]').forEach(element => {
        ['name', 'id', 'for'].forEach(attribute => {
          if (element.hasAttribute(attribute)) element.setAttribute(attribute, element.getAttribute(attribute).replace(/form-\d+-/g, `form-${index}-`));
        });
      });
    });
    total.value = rows.length;
    add.disabled = rows.length >= 10;
  }
  add.addEventListener('click', () => {
    if (Number(total.value) >= 10) return;
    container.insertAdjacentHTML('beforeend', document.getElementById('empty-photo-form').innerHTML.replaceAll('__prefix__', total.value));
    renumber();
  });
  form.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button) return;
    const row = button.closest('.photo-fields');
    if (!row) return;
    if (button.hasAttribute('data-remove-photo')) {
      if (container.children.length > 1) { row.remove(); renumber(); }
      return;
    }
    const field = name => row.querySelector(`[name$="-${name}"]`);
    const status = row.querySelector('[data-gps-status]');
    if (button.hasAttribute('data-clear-gps')) {
      ['latitude', 'longitude', 'location_accuracy_metres'].forEach(name => { field(name).value = ''; });
      status.textContent = 'GPS cleared.';
    }
    if (!button.hasAttribute('data-capture-gps')) return;
    if (!navigator.geolocation) { status.textContent = 'GPS is unavailable. You can enter coordinates or continue without GPS.'; return; }
    button.disabled = true;
    status.textContent = 'Requesting current location…';
    navigator.geolocation.getCurrentPosition(position => {
      field('latitude').value = position.coords.latitude.toFixed(6);
      field('longitude').value = position.coords.longitude.toFixed(6);
      field('location_accuracy_metres').value = position.coords.accuracy.toFixed(2);
      status.textContent = 'Current GPS added. Check that it matches the photo location.';
      button.disabled = false;
    }, () => {
      status.textContent = 'Location unavailable or permission declined. You can continue without GPS.';
      button.disabled = false;
    }, { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 });
  });
  renumber();
})();
