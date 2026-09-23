/* ============================================================
   FinCore — script.js
   Implements every interactive hook declared in the template.
   Safe: guards every selector, respects prefers-reduced-motion,
   always removes the preloader even if other init fails.
   ============================================================ */

(function () {
  'use strict';

  var prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----------------------------------------------------------
     1. Preloader
     ---------------------------------------------------------- */
  function hidePreloader() {
    document.body.classList.remove('loading');
    var pl = document.getElementById('preloader');
    if (!pl) return;
    pl.style.transition = 'opacity .4s ease';
    pl.style.opacity = '0';
    window.setTimeout(function () {
      if (pl.parentNode) pl.parentNode.removeChild(pl);
    }, 450);
  }

  /* ----------------------------------------------------------
     2. Animated counters
     ---------------------------------------------------------- */
  function formatNPR(value) {
    var s = Math.round(value).toString();
    if (s.length <= 3) return 'Rs. ' + s;
    var last3 = s.slice(-3);
    var rest = s.slice(0, -3);
    rest = rest.replace(/\B(?=(\d{2})+(?!\d))/g, ',');
    return 'Rs. ' + rest + ',' + last3;
  }

  function formatValue(value, format) {
    if (format === 'npr') return formatNPR(value);
    return String(Math.round(value));
  }

  function animateCounter(el) {
    if (el.dataset.counterDone === '1') return;
    el.dataset.counterDone = '1';

    var target = parseFloat(el.dataset.counter);
    if (!isFinite(target)) return;
    var format = el.dataset.format || '';

    if (prefersReducedMotion) {
      el.textContent = formatValue(target, format);
      return;
    }

    var duration = 1400;
    var start = null;

    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = formatValue(target * eased, format);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = formatValue(target, format);
    }
    requestAnimationFrame(step);
  }

  function initCounters() {
    var counters = document.querySelectorAll('[data-counter]');
    if (!counters.length) return;

    if (!('IntersectionObserver' in window) || prefersReducedMotion) {
      counters.forEach(animateCounter);
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.35 }
    );
    counters.forEach(function (c) { io.observe(c); });
  }

  /* ----------------------------------------------------------
     3. Demo tabs
     ---------------------------------------------------------- */
  function initDemoTabs() {
    var tabs = document.querySelectorAll('.demo-tab');
    var panels = document.querySelectorAll('.demo-panel');
    if (!tabs.length || !panels.length) return;

    function activate(name) {
      tabs.forEach(function (t) {
        var on = t.dataset.tab === name;
        t.classList.toggle('active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.setAttribute('tabindex', on ? '0' : '-1');
      });
      panels.forEach(function (p) {
        var on = p.dataset.panel === name;
        if (on) p.removeAttribute('hidden');
        else p.setAttribute('hidden', '');
      });
    }

    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () {
        activate(tab.dataset.tab);
      });
      tab.addEventListener('keydown', function (e) {
        var next = null;
        if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
        else if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (next) {
          e.preventDefault();
          next.focus();
          activate(next.dataset.tab);
        }
      });
    });
  }

  /* ----------------------------------------------------------
     4. Billing toggle
     ---------------------------------------------------------- */
  function initBillingToggle() {
    var opts = document.querySelectorAll('.bt-opt[data-billing]');
    var prices = document.querySelectorAll('[data-price-monthly]');
    if (!opts.length || !prices.length) return;

    function apply(mode) {
      opts.forEach(function (o) {
        var on = o.dataset.billing === mode;
        o.classList.toggle('active', on);
        o.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      prices.forEach(function (p) {
        var next = mode === 'yearly' ? p.dataset.priceYearly : p.dataset.priceMonthly;
        if (next) p.textContent = next;
      });
    }

    opts.forEach(function (o) {
      o.addEventListener('click', function () { apply(o.dataset.billing); });
    });
  }

  /* ----------------------------------------------------------
     5. Solution selector
     ---------------------------------------------------------- */
  function initSolutionSelector() {
    var buttons = document.querySelectorAll('.solution[data-solution]');
    var title = document.querySelector('[data-sd-title]');
    var body = document.querySelector('[data-sd-body]');
    var points = document.querySelector('[data-sd-points]');
    if (!buttons.length || !title || !body || !points) return;

    var CONTENT = {
      startups: {
        title: 'Startups',
        body:
          'Pre-seed to Series A, FinCore keeps your burn, runway, and revenue ' +
          'visible in one place. Track investor funding, categorize spend, and ' +
          'see how long your current cash lasts — without a finance hire.',
        points: [
          'Funding and grant tracking',
          'Burn rate and runway visibility',
          'Expense categorization by team',
          'Revenue and MRR overview'
        ]
      },
      smb: {
        title: 'Small businesses',
        body:
          'From daily sales to supplier payments, FinCore gives small ' +
          'businesses one clear place to see money in, money out, and what is ' +
          'left — without juggling spreadsheets or a separate accounting tool.',
        points: [
          'Sales, purchases, and expenses in one ledger',
          'Customer and supplier management',
          'Invoices and payment tracking',
          'Simple financial statements'
        ]
      },
      agency: {
        title: 'Agencies & freelancers',
        body:
          'Track every client, invoice, and project cost in one place. See ' +
          'which projects are profitable, which invoices are still open, and ' +
          'what your effective hourly rate really is.',
        points: [
          'Client and project tracking',
          'Invoice and payment status',
          'Project cost and margin visibility',
          'Recurring retainer support'
        ]
      },
      growing: {
        title: 'Growing companies',
        body:
          'As headcount and revenue grow, financial operations get more ' +
          'complex. FinCore centralizes them — approvals, categories, ' +
          'reporting — so nothing slips as you scale.',
        points: [
          'Role-based access for teams',
          'Centralized approvals and audit trail',
          'Multi-account cash visibility',
          'Advanced financial reporting'
        ]
      }
    };

    function render(key) {
      var data = CONTENT[key];
      if (!data) return;
      title.textContent = data.title;
      body.textContent = data.body;
      points.innerHTML = '';
      data.points.forEach(function (item) {
        var li = document.createElement('li');
        li.textContent = item;
        points.appendChild(li);
      });
      buttons.forEach(function (b) {
        var on = b.dataset.solution === key;
        b.classList.toggle('active', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    }

    buttons.forEach(function (b) {
      b.addEventListener('click', function () { render(b.dataset.solution); });
    });
  }

  /* ----------------------------------------------------------
     6. Mobile navigation
     ---------------------------------------------------------- */
  function initMobileNav() {
    var toggle = document.querySelector('.nav-toggle');
    var links = document.getElementById('navlinks');
    if (!toggle || !links) return;

    function setOpen(open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      links.classList.toggle('open', open);
      document.body.classList.toggle('nav-open', open);
    }

    toggle.addEventListener('click', function () {
      var isOpen = toggle.getAttribute('aria-expanded') === 'true';
      setOpen(!isOpen);
    });

    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 900 && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
      }
    });
  }

  /* ----------------------------------------------------------
     7. Scroll-spy
     ---------------------------------------------------------- */
  function initScrollSpy() {
    var navLinks = document.querySelectorAll('[data-nav]');
    if (!navLinks.length) return;
    var map = {};
    navLinks.forEach(function (a) {
      var key = a.dataset.nav;
      if (key === 'index') return;
      var section = document.getElementById(key);
      if (section) map[key] = { link: a, section: section };
    });
    var keys = Object.keys(map);
    if (!keys.length) return;

    function update() {
      var fromTop = window.scrollY + 140;
      var current = null;
      keys.forEach(function (k) {
        var el = map[k].section;
        if (el.offsetTop <= fromTop) current = k;
      });
      keys.forEach(function (k) {
        map[k].link.classList.toggle('active', k === current);
      });
    }

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        update();
        ticking = false;
      });
    }, { passive: true });

    update();
  }

  /* ----------------------------------------------------------
     8. Flow animation
     ---------------------------------------------------------- */
  function initFlow() {
    var tokens = document.querySelectorAll('.flow-token[data-flow]');
    if (!tokens.length) return;

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      tokens.forEach(function (t) { t.classList.add('is-active'); });
      return;
    }

    var started = false;
    var io = new IntersectionObserver(
      function (entries) {
        if (started) return;
        if (!entries.some(function (e) { return e.isIntersecting; })) return;
        started = true;
        tokens.forEach(function (t, i) {
          window.setTimeout(function () { t.classList.add('is-active'); }, i * 140);
        });
        io.disconnect();
      },
      { threshold: 0.25 }
    );
    io.observe(tokens[0].parentNode);
  }

  /* ----------------------------------------------------------
     9. Cash-flow bar visibility
     ---------------------------------------------------------- */
  function initCashFlowBars() {
    var bars = document.querySelectorAll('.mcf-bar');
    if (!bars.length || prefersReducedMotion) return;
    if (!('IntersectionObserver' in window)) return;

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.3 }
    );
    bars.forEach(function (b) { io.observe(b); });
  }

  /* ----------------------------------------------------------
     10. Boot
     ---------------------------------------------------------- */
  function init() {
    hidePreloader();
    try { initCounters(); } catch (e) { console.error('counters', e); }
    try { initDemoTabs(); } catch (e) { console.error('demo tabs', e); }
    try { initBillingToggle(); } catch (e) { console.error('billing', e); }
    try { initSolutionSelector(); } catch (e) { console.error('solutions', e); }
    try { initMobileNav(); } catch (e) { console.error('mobile nav', e); }
    try { initScrollSpy(); } catch (e) { console.error('scroll spy', e); }
    try { initFlow(); } catch (e) { console.error('flow', e); }
    try { initCashFlowBars(); } catch (e) { console.error('cashflow', e); }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.addEventListener('load', function () {
    document.body.classList.remove('loading');
    var pl = document.getElementById('preloader');
    if (pl) pl.style.display = 'none';
  });
})();