/*Nairobi ICT Attachment & Internship Directory*/
(function () {
  'use strict';

  var ALL = [];
  var state = { q: '', cat: '', area: '', diplomaOnly: false, paidOnly: false, sort: 'name' };

  var els = {
    grid: document.getElementById('cardGrid'),
    empty: document.getElementById('emptyState'),
    count: document.getElementById('resultCount'),
    search: document.getElementById('searchInput'),
    area: document.getElementById('areaFilter'),
    sort: document.getElementById('sortSelect'),
    chips: document.getElementById('categoryChips'),
    diplomaToggle: document.getElementById('toggleDiploma'),
    paidToggle: document.getElementById('togglePaid'),
    clearBtn: document.getElementById('clearFilters'),
    emptyClearBtn: document.getElementById('emptyClearBtn'),
    statTotal: document.getElementById('statTotal'),
    aggDot: document.getElementById('aggDot'),
    freshnessSummary: document.getElementById('freshnessSummary'),
    footerUpdated: document.getElementById('footerUpdated')
  };

  function esc(str) {
    return String(str == null ? '' : str).replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
  }

  /* ---------- time helpers ---------- */
  function relativeTime(iso) {
    var then = new Date(iso), now = new Date();
    var days = Math.floor((now - then) / 86400000);
    if (days <= 0) return 'today';
    if (days === 1) return '1 day ago';
    if (days < 14) return days + ' days ago';
    if (days < 60) return Math.round(days / 7) + ' weeks ago';
    if (days < 365) return Math.round(days / 30) + ' months ago';
    return Math.round(days / 365) + ' years ago';
  }

  function freshnessInfo(c) {
    if (!c.last_checked || c.link_status === 'unchecked') {
      return { status: 'unchecked', label: 'Not yet auto-checked' };
    }
    var rel = relativeTime(c.last_checked);
    if (c.link_status === 'broken') {
      return { status: 'broken', label: 'Link may be down \u00b7 checked ' + rel };
    }
    if (c.link_status === 'unverified') {
      return { status: 'unchecked', label: 'Couldn\u2019t auto-confirm \u00b7 checked ' + rel };
    }
    var days = Math.floor((new Date() - new Date(c.last_checked)) / 86400000);
    var status = days <= 14 ? 'ok' : 'stale';
    var kw = c.keyword_hit === true ? ' \u00b7 mentions internships' : '';
    return { status: status, label: 'Checked ' + rel + kw };
  }

  /* ---------- rendering ---------- */
  function skeletons(n) {
    var out = '';
    for (var i = 0; i < n; i++) out += '<div class="skel" aria-hidden="true"></div>';
    els.grid.innerHTML = out;
  }

  function cardHTML(c) {
    var fresh = freshnessInfo(c);
    var diplomaClass = c.diploma === 'yes' ? 'pos' : 'mid';
    var stipendClass = c.stipend === 'paid' ? 'pos' : '';
    var isMailto = c.apply_url.indexOf('mailto:') === 0;
    var sameLink = c.apply_url === c.careers_url;
    var applyLabel = isMailto ? 'Email to apply' : 'Apply';

    var applyIcon = isMailto ? 'icon-mail' : 'icon-arrow';
    var actions = '<a class="btn btn--primary" href="' + esc(c.apply_url) + '" target="_blank" rel="noopener">' +
      esc(applyLabel) + '<svg class="icon"><use href="#' + applyIcon + '"></use></svg></a>';
    if (!sameLink) {
      actions += '<a class="btn btn--ghost" href="' + esc(c.careers_url) + '" target="_blank" rel="noopener">Careers page</a>';
    }

    return (
      '<article class="card" data-id="' + esc(c.id) + '">' +
        '<div class="card__top">' +
          '<span class="cat-tag cat-' + esc(c.category) + '"><span class="cat-tag__dot"></span>' + esc(c.category_label) + '</span>' +
          (c.featured ? '<span class="featured-tag">Popular</span>' : '') +
        '</div>' +
        '<h3 class="card__name">' + esc(c.company) + '</h3>' +
        '<p class="card__location"><b>' + esc(c.area_display) + '</b> \u00b7 ' + esc(c.address) + '</p>' +
        '<p class="card__focus">' + esc(c.focus) + '</p>' +
        '<dl class="card__meta">' +
          '<div class="card__meta-item"><dt>Diploma</dt><dd class="' + diplomaClass + '">' + esc(c.diploma_text) + '</dd></div>' +
          '<div class="card__meta-item"><dt>Stipend</dt><dd class="' + stipendClass + '">' + esc(c.stipend_text) + '</dd></div>' +
        '</dl>' +
        '<p class="card__intake">Intake: <b>' + esc(c.intake) + '</b></p>' +
        '<div class="card__footer">' +
          '<span class="freshness-line"><span class="freshness-dot" data-status="' + fresh.status + '"></span>' + esc(fresh.label) + '</span>' +
          '<div class="card__actions">' + actions + '</div>' +
        '</div>' +
      '</article>'
    );
  }

  function render(list) {
    if (list.length === 0) {
      els.grid.innerHTML = '';
      els.empty.hidden = false;
    } else {
      els.empty.hidden = true;
      els.grid.innerHTML = list.map(cardHTML).join('');
    }
    var total = ALL.length;
    els.count.innerHTML = list.length === total ?
      'Showing all <strong>' + total + '</strong> companies' :
      'Showing <strong>' + list.length + '</strong> of ' + total + ' companies';

    var filtersActive = !!(state.q || state.cat || state.area || state.diplomaOnly || state.paidOnly);
    els.clearBtn.hidden = !filtersActive;
  }

  function applyState() {
    var q = state.q.trim().toLowerCase();
    var list = ALL.filter(function (c) {
      if (state.cat && c.category !== state.cat) return false;
      if (state.area && c.area !== state.area) return false;
      if (state.diplomaOnly && c.diploma !== 'yes') return false;
      if (state.paidOnly && c.stipend !== 'paid') return false;
      if (q) {
        var hay = (c.company + ' ' + c.area_display + ' ' + c.address + ' ' + c.category_label + ' ' + c.focus).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });

    list.sort(function (a, b) {
      if (state.sort === 'category') {
        return a.category_label.localeCompare(b.category_label) || a.company.localeCompare(b.company);
      }
      if (state.sort === 'freshness') {
        var at = a.last_checked ? new Date(a.last_checked).getTime() : -1;
        var bt = b.last_checked ? new Date(b.last_checked).getTime() : -1;
        return bt - at || a.company.localeCompare(b.company);
      }
      return a.company.localeCompare(b.company);
    });

    render(list);
  }

  function updateCounts() {
    var counts = {};
    ALL.forEach(function (c) { counts[c.category] = (counts[c.category] || 0) + 1; });
    var nodes = els.chips.querySelectorAll('.chip-count');
    for (var i = 0; i < nodes.length; i++) {
      var cat = nodes[i].getAttribute('data-count-for');
      nodes[i].textContent = ' (' + (counts[cat] || 0) + ')';
    }
  }

  function updateAggregate(meta) {
    var checked = ALL.filter(function (c) { return c.last_checked; });
    if (checked.length === 0) {
      els.aggDot.setAttribute('data-status', 'unchecked');
      els.freshnessSummary.textContent = 'Link health checked automatically \u2014 first run pending';
      return;
    }
    var ok = checked.filter(function (c) { return c.link_status === 'ok'; }).length;
    var broken = checked.filter(function (c) { return c.link_status === 'broken'; }).length;
    var unverified = checked.filter(function (c) { return c.link_status === 'unverified'; }).length;
    els.aggDot.setAttribute('data-status', broken > 0 ? 'stale' : 'ok');
    var text = ok + ' of ' + ALL.length + ' links verified alive';
    if (broken) text += ', ' + broken + ' flagged';
    if (unverified) text += ', ' + unverified + ' unconfirmed';
    els.freshnessSummary.textContent = text;
    if (meta && meta.last_scraped) {
      els.freshnessSummary.textContent += ' \u00b7 last run ' + relativeTime(meta.last_scraped);
    }
  }

  /* ---------- filter chip / toggle wiring ---------- */
  function setActiveChip(cat) {
    var chips = els.chips.querySelectorAll('.chip');
    for (var i = 0; i < chips.length; i++) {
      chips[i].classList.toggle('is-active', chips[i].getAttribute('data-cat') === cat);
    }
  }

  function resetControls() {
    state = { q: '', cat: '', area: '', diplomaOnly: false, paidOnly: false, sort: 'name' };
    els.search.value = '';
    els.area.value = '';
    els.sort.value = 'name';
    els.diplomaToggle.setAttribute('aria-pressed', 'false');
    els.paidToggle.setAttribute('aria-pressed', 'false');
    setActiveChip('');
  }

  function wireEvents() {
    els.search.addEventListener('input', function () { state.q = els.search.value; applyState(); });
    els.area.addEventListener('change', function () { state.area = els.area.value; applyState(); });
    els.sort.addEventListener('change', function () { state.sort = els.sort.value; applyState(); });

    els.chips.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      state.cat = btn.getAttribute('data-cat');
      setActiveChip(state.cat);
      applyState();
    });

    els.diplomaToggle.addEventListener('click', function () {
      state.diplomaOnly = !state.diplomaOnly;
      els.diplomaToggle.setAttribute('aria-pressed', String(state.diplomaOnly));
      applyState();
    });
    els.paidToggle.addEventListener('click', function () {
      state.paidOnly = !state.paidOnly;
      els.paidToggle.setAttribute('aria-pressed', String(state.paidOnly));
      applyState();
    });

    function clearAll() { resetControls(); applyState(); }
    els.clearBtn.addEventListener('click', clearAll);
    els.emptyClearBtn.addEventListener('click', clearAll);
  }

  /* ---------- boot ---------- */
  function boot(data) {
    ALL = data.companies || [];
    els.statTotal.textContent = ALL.length;
    if (data.meta && data.meta.last_manual_review) {
      els.footerUpdated.innerHTML = '<strong>Directory last reviewed ' + esc(data.meta.last_manual_review) +
        '.</strong> Company listings were manually researched, then handed to the auto-checker above to keep them honest.';
    }
    updateCounts();
    updateAggregate(data.meta);
    wireEvents();
    applyState();
  }

  function showLoadError() {
    var openedAsFile = location.protocol === 'file:';
    els.grid.innerHTML = '';
    els.empty.hidden = false;
    els.empty.querySelector('h3').textContent = "Couldn't load the directory data";
    els.empty.querySelector('p').textContent = openedAsFile ?
      'Looks like this page was opened directly from a folder. Browsers block that for security \u2014 run a local server (see README.md) or visit the deployed site instead.' :
      'data/companies.json failed to load. Check your connection and try refreshing.';
    els.empty.querySelector('button').hidden = true;
    els.count.textContent = '';
  }

  skeletons(8);
  fetch('data/companies.json')
    .then(function (res) { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(boot)
    .catch(showLoadError);
})();
