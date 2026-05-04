/* ═══════════════════════════════════════════════════════
   Cardian — menu.js
   Mobile hamburger menu + auth state for mobile header.
   Loaded on every page after main.js.
   Uses DOMContentLoaded so DOM is guaranteed ready.
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  /* ──────────────────────────────────────────────────
     1. HAMBURGER TOGGLE
  ────────────────────────────────────────────────── */
  var menuBtn    = document.getElementById('menu-btn');
  var mobileMenu = document.getElementById('mobile-menu');

  function closeMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.remove('open');
    if (menuBtn) {
      menuBtn.setAttribute('aria-expanded', 'false');
      var icon = menuBtn.querySelector('i[data-lucide]');
      if (icon) {
        icon.setAttribute('data-lucide', 'menu');
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    }
  }

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(isOpen));
      var icon = menuBtn.querySelector('i[data-lucide]');
      if (icon) {
        icon.setAttribute('data-lucide', isOpen ? 'x' : 'menu');
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    });

    /* Close when clicking outside the header */
    document.addEventListener('click', function (e) {
      var header = document.getElementById('navbar');
      if (header && !header.contains(e.target)) {
        closeMenu();
      }
    });

    /* Close when viewport becomes desktop */
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1024) closeMenu();
    }, { passive: true });
  }

  /* ──────────────────────────────────────────────────
     2. NAVBAR SCROLL SHADOW
  ────────────────────────────────────────────────── */
  var navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      navbar.classList.toggle('scrolled', window.scrollY > 8);
    }, { passive: true });
  }

  /* ──────────────────────────────────────────────────
     3. MOBILE AUTH WIRING (sign-in / sign-up / logout)
     main.js calls window.setMobileAuthState() to show/hide
  ────────────────────────────────────────────────── */
  document.addEventListener('click', function (e) {
    /* Mobile sign-in */
    var mobileSignin = e.target.closest('#btn-signin-mobile');
    if (mobileSignin) {
      e.preventDefault();
      closeMenu();
      if (typeof clearError === 'function') clearError('signin-error');
      if (typeof openModal  === 'function') openModal('modal-signin');
      return;
    }

    /* Mobile sign-up */
    var mobileSignup = e.target.closest('#btn-signup-mobile');
    if (mobileSignup) {
      e.preventDefault();
      closeMenu();
      if (typeof clearError === 'function') clearError('signup-error');
      if (typeof openModal  === 'function') openModal('modal-signup');
      return;
    }

    /* Mobile logout */
    var mobileLogout = e.target.closest('#btn-logout-mobile');
    if (mobileLogout) {
      e.preventDefault();
      closeMenu();
      if (typeof handleLogout === 'function') handleLogout();
      return;
    }

    /* Mobile top-up */
    var mobileTopup = e.target.closest('#btn-topup-mobile');
    if (mobileTopup) {
      e.preventDefault();
      if (typeof openModal === 'function') openModal('modal-topup');
      return;
    }
  });

  /* ──────────────────────────────────────────────────
     4. setMobileAuthState — called by main.js
     loggedIn: true/false
     balance:  number or string token count
  ────────────────────────────────────────────────── */
  window.setMobileAuthState = function (loggedIn, balance) {
    var tokenBadge    = document.getElementById('mobile-token-badge');
    var profileBtn    = document.getElementById('mobile-profile-btn');
    var mobileGuest   = document.getElementById('mobile-auth-guest');
    var mobileUser    = document.getElementById('mobile-auth-user');
    var mobileBalance = document.getElementById('header-balance-mobile');

    if (loggedIn) {
      /* Inline navbar: show token badge + profile icon */
      if (tokenBadge) tokenBadge.style.display = 'flex';
      if (profileBtn) profileBtn.style.display  = 'flex';

      /* Dropdown: hide guest row, show user row */
      if (mobileGuest) {
        mobileGuest.classList.remove('visible');
        mobileGuest.style.display = 'none';
      }
      if (mobileUser) {
        mobileUser.classList.add('visible');
        mobileUser.style.display = 'flex';
      }

      /* Sync balance text */
      var display = (balance !== undefined && balance !== null && balance !== '') ? balance : '—';
      if (tokenBadge) {
        var span = tokenBadge.querySelector('span');
        if (span) span.textContent = display;
      }
      if (mobileBalance) mobileBalance.textContent = 'Tokens: ' + display;

    } else {
      /* Inline navbar: hide token badge + profile icon */
      if (tokenBadge) tokenBadge.style.display = 'none';
      if (profileBtn) profileBtn.style.display  = 'none';

      /* Dropdown: show guest row, hide user row */
      if (mobileGuest) {
        mobileGuest.classList.add('visible');
        mobileGuest.style.display = 'flex';
      }
      if (mobileUser) {
        mobileUser.classList.remove('visible');
        mobileUser.style.display = 'none';
      }
    }
  };

});
