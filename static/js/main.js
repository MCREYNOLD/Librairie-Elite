/* ============================================================
   LIBRAIRIE ÉLITE — main.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss flash messages ──────────────────────────
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s ease';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  // ── Confirm avant suppression ─────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  // ── Navbar : active link ──────────────────────────────────
  var path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(function (link) {
    if (link.getAttribute('href') && path.startsWith(link.getAttribute('href')) &&
        link.getAttribute('href') !== '/') {
      link.style.background = 'var(--surface)';
      link.style.fontWeight = '600';
    }
  });

  // ── Quantity controls (+-) ────────────────────────────────
  document.querySelectorAll('.qty-input').forEach(function (input) {
    var min = parseInt(input.min) || 1;
    var max = parseInt(input.max) || 999;
    input.addEventListener('change', function () {
      var v = parseInt(input.value) || min;
      input.value = Math.min(Math.max(v, min), max);
    });
  });

  // ── Star picker hover + click ─────────────────────────────
  var picker = document.getElementById('starPicker');
  if (picker) {
    var labels = picker.querySelectorAll('label');
    labels.forEach(function (lbl) {
      lbl.addEventListener('mouseenter', function () {
        // CSS handles it via ~ selector, nothing needed
      });
    });
  }

  // ── Smooth scroll to anchor ───────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Add-to-cart button feedback ───────────────────────────
  document.querySelectorAll('.btn-add-cart').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      var original = btn.textContent;
      btn.textContent = '✓ Ajouté !';
      btn.style.background = 'var(--success)';
      setTimeout(function () {
        btn.textContent = original;
        btn.style.background = '';
      }, 1500);
    });
  });

  // ── Admin table : row click ───────────────────────────────
  document.querySelectorAll('.admin-table tbody tr[data-href]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function () {
      window.location = row.dataset.href;
    });
  });

  // ── Image preview for cover upload ───────────────────────
  var coverInput = document.querySelector('input[name="couverture"]');
  if (coverInput) {
    coverInput.addEventListener('change', function () {
      var file = coverInput.files[0];
      if (!file) return;
      var preview = document.getElementById('coverPreview');
      if (!preview) {
        preview = document.createElement('img');
        preview.id = 'coverPreview';
        preview.style.cssText = 'width:120px;height:170px;object-fit:cover;border-radius:4px 8px 8px 4px;margin-top:.75rem;box-shadow:-3px 3px 10px rgba(0,0,0,.2)';
        coverInput.parentNode.appendChild(preview);
      }
      var reader = new FileReader();
      reader.onload = function (e) { preview.src = e.target.result; };
      reader.readAsDataURL(file);
    });
  }

});
