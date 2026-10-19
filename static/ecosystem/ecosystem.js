/* Nexus LATAM Ecosystem — loads full explorer from .chunks/ parts (see eco-file-07 bundle) */
(function () {
  'use strict';
  var urls = [0, 1, 2, 3, 4].map(function (i) {
    return '.chunks/ecosystem.js.part0' + i;
  });
  Promise.all(
    urls.map(function (u) {
      return fetch(u).then(function (r) {
        if (!r.ok) throw new Error('Failed to load ' + u + ': ' + r.status);
        return r.text();
      });
    })
  )
    .then(function (parts) {
      var el = document.createElement('script');
      el.textContent = parts.join('');
      document.head.appendChild(el);
    })
    .catch(function (err) {
      console.error(err);
      var grid = document.getElementById('actor-grid');
      if (grid) {
        grid.innerHTML =
          '<div class="empty-grid">Error loading ecosystem.js: ' +
          String(err.message || err) +
          '</div>';
      }
    });
})();
