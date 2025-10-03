(function() {
  function byId(id){ return document.getElementById(id); }

  function setDistanceFromSPBU() {
    const spbuSel = byId('id_spbu');
    const target = byId('id_estimated_distance_km');
    if (!spbuSel || !target) return;

    // If you rendered extra data attributes via a custom widget, you could read them here.
    // Easiest: ask your backend to add default distance on the option label like "SPBU A (12.3 km)"
    // but better approach is AJAX (Option B). For a simple copy from hidden field:
    const selected = spbuSel.options[spbuSel.selectedIndex];
    if (!selected) return;

    // Example: if you put data-distance-km in the <option>
    const km = selected.getAttribute('data-distance-km');
    if (km) {
      target.value = km;
      target.dispatchEvent(new Event('change'));
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    const spbuSel = byId('id_spbu');
    if (spbuSel) {
      spbuSel.addEventListener('change', setDistanceFromSPBU);
      // run once on load
      setDistanceFromSPBU();
    }
  });
})();