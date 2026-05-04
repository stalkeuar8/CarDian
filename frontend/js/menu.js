/* ═══════════════════════════════════════════════════
   Cardian — menu.js
   Universal mobile menu & header auth-state handler.
   Must be loaded AFTER main.js (or as a module).
   ═══════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ──────────────────────────────────────────────────
     1. HAMBURGER TOGGLE
  ────────────────────────────────────────────────── */
  const menuBtn    = document.getElementById('menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(isOpen));
      // swap icon
      const icon = menuBtn.querySelector('i[data-lucide]');
      if (icon) {
        icon.setAttribute('data-lucide', isOpen ? 'x' : 'menu');
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
        const icon = menuBtn.querySelector('i[data-lucide]');
        if (icon) {
          icon.setAttribute('data-lucide', 'menu');
          if (typeof lucide !== 'undefined') lucide.createIcons();
        }
      }
    });

    // Close on resize to desktop
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 1024) {
        mobileMenu.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    }, { passive: true });
  }

  /* ──────────────────────────────────────────────────
     2. MOBILE AUTH STATE
     Called by main.js checkAuthState / on DOMContentLoaded
  ────────────────────────────────────────────────── */

  /**
   * Sets the mobile header into logged-in or guest state.
   * @param {boolean} loggedIn
   * @param {string|number} balance  token count (only used when loggedIn)
   */
  window.setMobileAuthState = function (loggedIn, balance) {
    const tokenBadge     = document.getElementById('mobile-token-badge');
    const profileBtn     = document.getElementById('mobile-profile-btn');
    const mobileGuest    = document.getElementById('mobile-auth-guest');
    const mobileUser     = document.getElementById('mobile-auth-user');
    const mobileBalance  = document.getElementById('header-balance-mobile');

    if (loggedIn) {
      // Navbar inline: show token + profile icon
      if (tokenBadge)  { tokenBadge.style.display  = 'flex'; }
      if (profileBtn)  { profileBtn.style.display   = 'flex'; }

      // Menu section: hide guest, show user
      if (mobileGuest) { mobileGuest.classList.remove('visible'); }
      if (mobileUser)  { mobileUser.classList.add('visible');     }

      // Sync balance
      const displayBalance = (balance !== undefined && balance !== null) ? balance : '—';
      if (tokenBadge)  tokenBadge.querySelector('span').textContent = `${displayBalance}`;
      if (mobileBalance) mobileBalance.textContent = `Tokens: ${displayBalance}`;
    } else {
      // Navbar inline: hide token + profile icon
      if (tokenBadge)  { tokenBadge.style.display  = 'none'; }
      if (profileBtn)  { profileBtn.style.display   = 'none'; }

      // Menu section: show guest, hide user
      if (mobileGuest) { mobileGuest.classList.add('visible');    }
      if (mobileUser)  { mobileUser.classList.remove('visible');  }
    }
  };

  /* ──────────────────────────────────────────────────
     3. WIRE MOBILE LOGOUT / TOPUP
  ────────────────────────────────────────────────── */
  document.addEventListener('click', (e) => {
    // Mobile logout
    const mobileLogout = e.target.closest('#btn-logout-mobile');
    if (mobileLogout && typeof handleLogout === 'function') {
      e.preventDefault();
      handleLogout();
    }

    // Mobile sign-in
    const mobileSignin = e.target.closest('#btn-signin-mobile');
    if (mobileSignin) {
      e.preventDefault();
      if (mobileMenu) mobileMenu.classList.remove('open');
      if (typeof openModal === 'function') { clearError && clearError('signin-error'); openModal('modal-signin'); }
    }

    // Mobile sign-up
    const mobileSignup = e.target.closest('#btn-signup-mobile');
    if (mobileSignup) {
      e.preventDefault();
      if (mobileMenu) mobileMenu.classList.remove('open');
      if (typeof openModal === 'function') { clearError && clearError('signup-error'); openModal('modal-signup'); }
    }

    // Mobile top-up
    const mobileTopup = e.target.closest('#btn-topup-mobile');
    if (mobileTopup) {
      e.preventDefault();
      if (typeof openModal === 'function') openModal('modal-topup');
    }
  });

  /* ──────────────────────────────────────────────────
     4. NAVBAR SCROLL SHADOW
  ────────────────────────────────────────────────── */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 8);
    }, { passive: true });
  }

})();
