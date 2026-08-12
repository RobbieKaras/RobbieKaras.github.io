/* Two small things: a theme toggle, and copy buttons on code blocks. */

(function () {
  'use strict';

  // ---- theme toggle -----------------------------------------------------
  var root = document.documentElement;
  var toggle = document.getElementById('theme-toggle');
  var icon = toggle && toggle.querySelector('[data-theme-icon]');

  function activeTheme() {
    var explicit = root.getAttribute('data-theme');
    if (explicit) return explicit;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function paintIcon() {
    if (icon) icon.textContent = activeTheme() === 'dark' ? '☀' : '☾';
  }

  if (toggle) {
    paintIcon();
    toggle.addEventListener('click', function () {
      var next = activeTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      paintIcon();
    });
  }

  // ---- copy buttons on code blocks --------------------------------------
  document.querySelectorAll('.codehilite').forEach(function (block) {
    var pre = block.querySelector('pre');
    if (!pre) return;

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-btn';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');

    button.addEventListener('click', function () {
      var text = pre.innerText;
      var done = function (label) {
        button.textContent = label;
        button.setAttribute('data-state', 'done');
        setTimeout(function () {
          button.textContent = 'Copy';
          button.removeAttribute('data-state');
        }, 1400);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
          .then(function () { done('Copied'); })
          .catch(function () { done('Failed'); });
      } else {
        // fallback for non-secure contexts (e.g. plain http on localhost)
        var scratch = document.createElement('textarea');
        scratch.value = text;
        scratch.setAttribute('readonly', '');
        scratch.style.position = 'absolute';
        scratch.style.left = '-9999px';
        document.body.appendChild(scratch);
        scratch.select();
        try { document.execCommand('copy'); done('Copied'); }
        catch (e) { done('Failed'); }
        document.body.removeChild(scratch);
      }
    });

    block.appendChild(button);
  });

  // ---- wide tables get their own scroll container ------------------------
  document.querySelectorAll('.prose table').forEach(function (table) {
    if (table.parentElement.classList.contains('table-scroll')) return;
    var box = document.createElement('div');
    box.className = 'table-scroll';
    table.parentNode.insertBefore(box, table);
    box.appendChild(table);
  });
})();
