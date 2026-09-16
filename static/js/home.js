/* ============================================================
   FinCore — Homepage interactions
   ============================================================ */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var body = document.body;

  /* ---------- Preloader ---------- */
  var preloader = document.getElementById('preloader');
  function hidePreloader() {
    if (!preloader) return;
    preloader.classList.add('hidden');
    body.classList.remove('loading');
    setTimeout(function () {
      if (preloader && preloader.parentNode) preloader.setAttribute('aria-hidden', 'true');
    }, 600);
  }
  if (document.readyState === 'complete') setTimeout(hidePreloader, 280);
  else {
    window.addEventListener('load', function () { setTimeout(hidePreloader, 280); });
    setTimeout(hidePreloader, 2800);
  }

  /* ---------- Nav scrolled state ---------- */
  var nav = document.getElementById('site-nav');
  function updateNav() {
    var y = window.scrollY || window.pageYOffset;
    if (y > 12) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  }
  window.addEventListener('scroll', updateNav, { passive: true });
  updateNav();

  /* ---------- Mobile nav ---------- */
  var navToggle = document.querySelector('.nav-toggle');
  var navLinks = document.getElementById('navlinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      var open = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!open));
      navLinks.classList.toggle('open', !open);
    });
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('open');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navToggle.getAttribute('aria-expanded') === 'true') {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('open');
        navToggle.focus();
      }
    });
    var mq = window.matchMedia('(min-width: 861px)');
    mq.addEventListener('change', function (e) {
      if (e.matches) {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('open');
      }
    });
  }

  /* ---------- Scroll reveal ---------- */
  var revealTargets = document.querySelectorAll(
    '.section-head, .problem-item, .ecosystem, .demo-shell, .flow, ' +
    '.feature, .solutions-grid, .solution-detail, .numbers-grid, ' +
    '.steps, .trust-grid, .pricing-controls, .pricing-grid, .faq-list'
  );
  revealTargets.forEach(function (el) { el.classList.add('reveal'); });

  if ('IntersectionObserver' in window && !reduce) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add('in-view'); });
  }

  /* ---------- Scroll spy ---------- */
  var navAnchors = Array.prototype.slice.call(
    document.querySelectorAll('nav ul li a[data-nav]')
  );
  var sections = navAnchors.map(function (a) {
    var href = a.getAttribute('href');
    return href && href.charAt(0) === '#' ? document.querySelector(href) : null;
  }).filter(Boolean);

  function updateActiveNav() {
    var y = window.scrollY || window.pageYOffset;
    var offset = 140;
    var current = null;
    sections.forEach(function (sec) {
      if (sec.offsetTop - offset <= y) current = sec;
    });
    navAnchors.forEach(function (a) {
      a.classList.toggle('active', current && a.getAttribute('href') === '#' + current.id);
    });
  }
  if (sections.length) {
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(function () { updateActiveNav(); ticking = false; });
        ticking = true;
      }
    }, { passive: true });
    updateActiveNav();
  }

  /* ---------- Smooth anchor offset ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (!href || href === '#' || href.length < 2) return;
      var target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.pageYOffset - 76;
      window.scrollTo({ top: top, behavior: reduce ? 'auto' : 'smooth' });
      if (history.pushState) history.pushState(null, '', href);
    });
  });

  /* ---------- Number counters ---------- */
  function formatNPR(n) {
    var s = String(Math.round(n));
    if (s.length <= 3) return s;
    var last3 = s.slice(-3);
    var rest = s.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ',');
    return rest + ',' + last3;
  }
  function animateCounter(el) {
    var target = parseFloat(el.getAttribute('data-counter'));
    if (isNaN(target)) return;
    var duration = 1400;
    var start = performance.now();
    function frame(now) {
      var t = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = 'Rs. ' + formatNPR(target * eased);
      if (t < 1) requestAnimationFrame(frame);
      else el.textContent = 'Rs. ' + formatNPR(target);
    }
    requestAnimationFrame(frame);
  }
  var counters = document.querySelectorAll('[data-counter]');
  if ('IntersectionObserver' in window && !reduce) {
    var counterObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { counterObserver.observe(el); });
  }

  /* ---------- Interactive demo tabs ---------- */
  var demoTabs = document.querySelectorAll('.demo-tab');
  var demoPanels = document.querySelectorAll('.demo-panel');
  demoTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var target = tab.getAttribute('data-tab');
      demoTabs.forEach(function (t) {
        var isActive = t === tab;
        t.classList.toggle('active', isActive);
        t.setAttribute('aria-selected', String(isActive));
      });
      demoPanels.forEach(function (p) {
        if (p.getAttribute('data-panel') === target) {
          p.hidden = false;
          p.style.animation = 'none';
          void p.offsetWidth;
          p.style.animation = '';
        } else {
          p.hidden = true;
        }
      });
    });
  });

  /* ---------- Solutions selector ---------- */
  var solutionData = {
    startups: {
      title: 'Startups',
      body: 'From pre-seed to Series A, FinCore keeps your burn, runway, and revenue visible in one place. Track investor funding, categorize spend, and see how long your current cash lasts — without a finance hire.',
      points: ['Funding and grant tracking', 'Burn rate and runway visibility', 'Expense categorization by team', 'Revenue and MRR overview']
    },
    smb: {
      title: 'Small businesses',
      body: 'Run your day-to-day without a dedicated accountant. FinCore handles sales, purchases, inventory, customers, and the accounting that ties them together.',
      points: ['Sales and purchase tracking', 'Customer and supplier records', 'Product and inventory overview', 'Monthly P&L and balance sheet']
    },
    agency: {
      title: 'Agencies & freelancers',
      body: 'Track clients, raise invoices, record payments, and see which projects are actually profitable — not just which ones are busy.',
      points: ['Client and project tracking', 'Invoice and payment status', 'Project-level expense capture', 'Profitability by client']
    },
    growing: {
      title: 'Growing companies',
      body: 'When one spreadsheet is no longer enough, FinCore centralizes financial operations across teams, entities, and accounts.',
      points: ['Multi-user access and roles', 'Consolidated reporting', 'Audit trail and exports', 'Cash across multiple accounts']
    }
  };
  var solutionBtns = document.querySelectorAll('.solution');
  var sdTitle = document.querySelector('[data-sd-title]');
  var sdBody = document.querySelector('[data-sd-body]');
  var sdPoints = document.querySelector('[data-sd-points]');

  solutionBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var key = btn.getAttribute('data-solution');
      var data = solutionData[key];
      if (!data) return;
      solutionBtns.forEach(function (b) {
        var isActive = b === btn;
        b.classList.toggle('active', isActive);
        b.setAttribute('aria-pressed', String(isActive));
      });
      sdTitle.textContent = data.title;
      sdBody.textContent = data.body;
      sdPoints.innerHTML = data.points.map(function (p) {
        return '<li>' + p + '</li>';
      }).join('');
    });
  });

  /* ---------- Billing toggle ---------- */
  var billingOpts = document.querySelectorAll('.bt-opt');
  var priceEls = document.querySelectorAll('[data-price-monthly]');
  var perEls = document.querySelectorAll('.pc-per');
  billingOpts.forEach(function (opt) {
    opt.addEventListener('click', function () {
      var billing = opt.getAttribute('data-billing');
      billingOpts.forEach(function (o) {
        var isActive = o === opt;
        o.classList.toggle('active', isActive);
        o.setAttribute('aria-pressed', String(isActive));
      });
      priceEls.forEach(function (el) {
        el.textContent = el.getAttribute(billing === 'monthly' ? 'data-price-monthly' : 'data-price-yearly');
      });
      perEls.forEach(function (el) {
        el.textContent = billing === 'monthly' ? '/ month' : '/ year';
      });
    });
  });

  /* ---------- FAQ: close others on open ---------- */
  var faqs = document.querySelectorAll('details.faq');
  faqs.forEach(function (faq) {
    faq.addEventListener('toggle', function () {
      if (faq.open) {
        faqs.forEach(function (other) {
          if (other !== faq) other.open = false;
        });
      }
    });
  });

})();