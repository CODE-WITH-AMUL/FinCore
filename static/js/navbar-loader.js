/**
 * FinCore — Reusable Standard HTML Navbar Loader
 * Loads the canonical navbar into #navbar-placeholder via fetch().
 * Idempotent, accessible, handles failure gracefully, supports mobile toggle and active states.
 */
(function () {
  'use strict';

  function initMobileNav(navElement) {
    if (!navElement) return;
    var toggle = navElement.querySelector('.nav-toggle');
    var links = navElement.querySelector('#navlinks');
    if (!toggle || !links) return;

    if (toggle.dataset.navInitialized === 'true') return;
    toggle.dataset.navInitialized = 'true';

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
      if (e.target.closest('a')) {
        setOpen(false);
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 860 && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
      }
    });
  }

  function updateActiveState(navElement) {
    if (!navElement) return;
    var currentPath = window.location.pathname.replace(/\/+$/, '') || '/';
    var currentHash = window.location.hash;

    // Check auth links
    var signinLink = navElement.querySelector('a.nav-login');
    var signupLink = navElement.querySelector('a.nav-cta');

    if (signinLink) {
      var isSignin = currentPath === '/user/accounts/signin' || currentPath.endsWith('/signin');
      signinLink.classList.toggle('active', isSignin);
      if (isSignin) signinLink.setAttribute('aria-current', 'page');
    }

    if (signupLink) {
      var isSignup = currentPath === '/user/accounts/signup' || currentPath.endsWith('/signup');
      signupLink.classList.toggle('active', isSignup);
      if (isSignup) signupLink.setAttribute('aria-current', 'page');
    }

    // Check section links if on landing page
    if (currentPath === '' || currentPath === '/') {
      var navLinks = navElement.querySelectorAll('#navlinks a[data-nav]');
      navLinks.forEach(function (link) {
        var href = link.getAttribute('href') || '';
        var hash = href.indexOf('#') !== -1 ? href.substring(href.indexOf('#')) : '';
        if (currentHash && hash === currentHash) {
          link.classList.add('active');
          link.setAttribute('aria-current', 'page');
        }
      });
    }
  }

  function initNavScroll(navElement) {
    if (!navElement) return;
    function checkScroll() {
      if (window.scrollY > 20) {
        navElement.classList.add('scrolled');
      } else {
        navElement.classList.remove('scrolled');
      }
    }
    window.addEventListener('scroll', checkScroll, { passive: true });
    checkScroll();
  }

  function renderFallback(container, errorMsg) {
    container.innerHTML =
      '<nav aria-label="Primary" id="site-nav" class="navbar-fallback" style="position:fixed;top:0;left:0;right:0;z-index:200;background:rgba(250,250,248,0.96);border-bottom:1px solid #dedbd3;padding:12px 0;">' +
        '<div class="wrap" style="max-width:1200px;margin:0 auto;padding:0 6vw;display:flex;justify-content:space-between;align-items:center;">' +
          '<div class="brand" style="font-weight:700;display:flex;align-items:center;gap:10px;">' +
            '<span class="dot" style="width:8px;height:8px;background:#2563eb;display:inline-block;"></span>' +
            '<a href="/" style="text-decoration:none;color:#14181c;">FinCore</a>' +
          '</div>' +
          '<div style="display:flex;align-items:center;gap:16px;">' +
            '<a href="/" style="font-size:0.86rem;color:#5b5f63;text-decoration:none;">Home</a>' +
            '<a href="/user/accounts/signin/" style="font-size:0.86rem;color:#5b5f63;text-decoration:none;">Sign In</a>' +
            '<a href="/user/accounts/signup/" style="font-size:0.82rem;font-weight:600;padding:8px 14px;border:1px solid #14181c;border-radius:2px;text-decoration:none;color:#14181c;">Get Started</a>' +
            '<button type="button" onclick="window.loadNavbar && window.loadNavbar()" style="font-size:0.75rem;padding:4px 8px;border:1px solid #b91c1c;border-radius:4px;background:#fff;color:#b91c1c;cursor:pointer;" title="' + (errorMsg || 'Load failed') + '">Retry Navigation</button>' +
          '</div>' +
        '</div>' +
      '</nav>';
  }

  function loadNavbar(targetSelector, navbarUrl) {
    var selector = targetSelector || '#navbar-placeholder';
    var url = navbarUrl || '/navbar.html';
    var container = document.querySelector(selector);

    if (!container) return Promise.resolve(null);

    // Prevent duplicate loading
    if (container.dataset.navbarLoading === 'true') {
      return Promise.resolve(container);
    }
    container.dataset.navbarLoading = 'true';

    return fetch(url)
      .then(function (response) {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status + ' while fetching ' + url);
        }
        return response.text();
      })
      .then(function (html) {
        container.innerHTML = html;
        container.dataset.navbarLoaded = 'true';
        container.dataset.navbarLoading = 'false';

        var navElement = container.querySelector('#site-nav') || container.querySelector('nav');
        if (navElement) {
          initMobileNav(navElement);
          updateActiveState(navElement);
          initNavScroll(navElement);
        }

        window.dispatchEvent(new CustomEvent('navbar:loaded', {
          detail: { container: container, nav: navElement }
        }));

        return container;
      })
      .catch(function (err) {
        container.dataset.navbarLoading = 'false';
        console.error('Navbar component loader error:', err);
        renderFallback(container, err.message);
        return container;
      });
  }

  // Expose global loader function
  window.loadNavbar = loadNavbar;

  // Auto-run if placeholder exists
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      if (document.querySelector('#navbar-placeholder')) {
        loadNavbar();
      }
    });
  } else {
    if (document.querySelector('#navbar-placeholder')) {
      loadNavbar();
    }
  }
})();
