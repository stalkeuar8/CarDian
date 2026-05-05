/* ═══════════════════════════════════════════
   Cardian — main.js
   Lucide init · Mobile menu · Scroll effects
   Floating card animation · Auth modals
   ═══════════════════════════════════════════ */

/* ─────────────────────────────────────────
   Auth — Constants
   ───────────────────────────────────────── */
const API_BASE    = '/api';
const TOKEN_KEY   = 'cardian_token';
const REFRESH_KEY = 'cardian_refresh_token';

function getUserIdFromToken() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;
  try {
    const payloadPart = token.split('.')[1];
    if (!payloadPart) return null;
    let base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) {
      base64 += '=';
    }
    const decoded = JSON.parse(atob(base64));
    if (decoded.user_id) return String(decoded.user_id);
    if (decoded.sub) return String(decoded.sub);
    if (decoded.id) return String(decoded.id);
  } catch (e) {
    return null;
  }

  return null;
}

function getUserRoleFromToken() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;
  try {
    const payloadPart = token.split('.')[1];
    let base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) {
      base64 += '=';
    }
    const decoded = JSON.parse(atob(base64));
    return decoded.role || null;
  } catch (e) {
    return null;
  }
}

// Simplified RateTypes string
// RateTypes from OpenAPI spec is now an enum: "starter" or "pro"

/* ─────────────────────────────────────────
   Auth — fetchWithAuth Wrapper
   ───────────────────────────────────────── */
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb);
};

const onTokenRefreshed = (token) => {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
};

async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem(TOKEN_KEY);
  
  if (!options.headers) options.headers = {};
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  
  let response = await fetch(url, options);

  if (response.status === 401) {
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!refreshToken) {
      await handleLogout();
      return response;
    }

    if (isRefreshing) {
      return new Promise(resolve => {
        subscribeTokenRefresh(async (newToken) => {
          options.headers['Authorization'] = `Bearer ${newToken}`;
          resolve(await fetch(url, options));
        });
      });
    }

    isRefreshing = true;

    try {
      const refreshRes = await fetch(`${API_BASE}/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);
        
        onTokenRefreshed(data.access_token);
        isRefreshing = false;
        
        options.headers['Authorization'] = `Bearer ${data.access_token}`;
        response = await fetch(url, options);
      } else {
        isRefreshing = false;
        refreshSubscribers = [];
        await handleLogout();
        throw new Error('Refresh failed');
      }
    } catch (err) {
      isRefreshing = false;
      refreshSubscribers = [];
      await handleLogout();
      throw err;
    }
  }

  return response;
}

/* ─────────────────────────────────────────
   Auth — UI State: checkAuthState()
   Shows guest buttons OR My Profile + Logout
   Fetches profile to populate token balance
   ───────────────────────────────────────── */
async function checkAuthState() {
  const token    = localStorage.getItem(TOKEN_KEY);
  const guestNav = document.getElementById('auth-buttons-guest');
  const userNav  = document.getElementById('auth-buttons-user');
  const mobileUserElements = document.getElementById('mobile-user-elements');
  
  const heroGuest = document.getElementById('hero-cta-guest');
  const heroUser  = document.getElementById('hero-cta-user');

  if (!guestNav || !userNav) return;

  if (token) {
    guestNav.classList.add('hidden');
    guestNav.classList.remove('flex');
    userNav.classList.remove('hidden');
    userNav.classList.add('flex');
    if (mobileUserElements) {
      mobileUserElements.classList.remove('hidden');
      mobileUserElements.classList.add('flex');
    }

    if (heroGuest && heroUser) {
      heroGuest.classList.add('hidden');
      heroGuest.classList.remove('sm:flex', 'flex');
      heroUser.classList.remove('hidden');
      heroUser.classList.add('sm:flex', 'flex');
    }

    // Fetch profile to get current_balance and role
    try {
      let userRole = getUserRoleFromToken();

      const res = await fetchWithAuth(`${API_BASE}/v1/users/profile`);
      if (res.ok) {
        const user = await res.json();
        updateHeaderBalance(user.current_balance ?? '—');
        // Cache user_id for top-up
        window._cardianUserId = user.id;
        if (user.role) userRole = user.role;
      } else if (res.status === 401 || res.status === 403) {
        // Token invalid — force logout
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem('cardian_user_role');
        guestNav.classList.remove('hidden');
        guestNav.classList.add('flex');
        userNav.classList.remove('flex');
        userNav.classList.add('hidden');
        if (mobileUserElements) {
          mobileUserElements.classList.remove('flex');
          mobileUserElements.classList.add('hidden');
        }

        if (heroGuest && heroUser) {
          heroUser.classList.add('hidden');
          heroUser.classList.remove('sm:flex', 'flex');
          heroGuest.classList.remove('hidden');
          heroGuest.classList.add('sm:flex', 'flex');
        }
      }

      if (userRole) {
        localStorage.setItem('cardian_user_role', userRole);
      }

      if (userRole === 'admin') {
        let adminBtn = document.getElementById('btn-admin-panel');
        if (!adminBtn) {
          const logoutBtn = document.getElementById('btn-logout');
          if (logoutBtn) {
            const btnHtml = `
              <a href="./admin_panel.html" id="btn-admin-panel" class="hidden md:flex px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-gray-900 hover:bg-black hover:scale-105 transition-all duration-200 shadow-md items-center gap-1.5 shrink-0">
                <i data-lucide="shield" class="w-4 h-4"></i>
                Admin panel
              </a>
            `;
            logoutBtn.insertAdjacentHTML('beforebegin', btnHtml);
          }
        }
        let adminBtnMobile = document.getElementById('btn-admin-panel-mobile');
        if (!adminBtnMobile) {
          const logoutBtnMobile = document.getElementById('btn-logout-mobile');
          if (logoutBtnMobile) {
            const btnHtmlMobile = `
              <a href="./admin_panel.html" id="btn-admin-panel-mobile" class="flex w-full items-center gap-3 text-base font-medium text-gray-900 hover:bg-gray-100 py-3 rounded-lg transition-colors px-2">
                <i data-lucide="shield" class="w-5 h-5"></i>
                Admin panel
              </a>
            `;
            logoutBtnMobile.insertAdjacentHTML('beforebegin', btnHtmlMobile);
          }
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
      } else {
        const adminBtn = document.getElementById('btn-admin-panel');
        if (adminBtn) adminBtn.remove();
        const adminBtnMobile = document.getElementById('btn-admin-panel-mobile');
        if (adminBtnMobile) adminBtnMobile.remove();
      }

    } catch (_) { /* network error, leave balance as — */ }

  } else {
    userNav.classList.remove('flex');
    userNav.classList.add('hidden');
    guestNav.classList.remove('hidden');
    guestNav.classList.add('flex');
    if (mobileUserElements) {
      mobileUserElements.classList.remove('flex');
      mobileUserElements.classList.add('hidden');
    }

    if (heroGuest && heroUser) {
      heroUser.classList.add('hidden');
      heroUser.classList.remove('sm:flex', 'flex');
      heroGuest.classList.remove('hidden');
      heroGuest.classList.add('sm:flex', 'flex');
    }
  }

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function updateHeaderBalance(balance) {
  const el = document.getElementById('header-balance');
  if (el) el.textContent = `Tokens: ${balance}`;
  const mobileEl = document.getElementById('mobile-balance');
  if (mobileEl) mobileEl.textContent = `Tokens: ${balance}`;
}

/* ─────────────────────────────────────────
   Auth — Modal helpers
   ───────────────────────────────────────── */
function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  const first = modal.querySelector('input, button:not([aria-label="Close"])');
  if (first) setTimeout(() => first.focus(), 80);
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add('hidden');
  document.body.style.overflow = '';
}

function closeAllModals() {
  closeModal('modal-signin');
  closeModal('modal-signup');
  closeModal('modal-topup');
  closeModal('modal-edit-name');
  closeModal('modal-edit-email');
  closeModal('modal-change-password');
}

/* ─────────────────────────────────────────
   Auth — Error display helpers
   ───────────────────────────────────────── */
function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.classList.remove('hidden');
}

function clearError(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = '';
  el.classList.add('hidden');
}

function extractErrorMessage(data) {
  if (data?.detail && Array.isArray(data.detail)) {
    return data.detail.map(e => e.msg).join(', ');
  }
  if (typeof data?.detail === 'string') return data.detail;
  if (typeof data?.message === 'string') return data.message;
  return 'Something went wrong. Please try again.';
}

/* ─────────────────────────────────────────
   Auth — Sign In fetch
   POST /v1/auth/login  { email, password }
   ───────────────────────────────────────── */
async function handleSignIn(e) {
  e.preventDefault();
  clearError('signin-error');

  const btn      = document.getElementById('signin-submit');
  const email    = document.getElementById('signin-email').value.trim();
  const password = document.getElementById('signin-password').value;

  if (!email || !password) { showError('signin-error', 'Please fill in all fields.'); return; }

  btn.disabled    = true;
  btn.textContent = 'Signing in…';

  try {
    const res  = await fetch(`${API_BASE}/v1/auth/login`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email, password }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { showError('signin-error', extractErrorMessage(data)); return; }

    localStorage.setItem(TOKEN_KEY,   data.access_token);
    localStorage.setItem(REFRESH_KEY, data.refresh_token);
    closeModal('modal-signin');
    await checkAuthState();
    document.getElementById('form-signin').reset();
  } catch (err) {
    showError('signin-error', 'Network error — is the server running?');
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Sign in';
  }
}

/* ─────────────────────────────────────────
   Auth — Sign Up fetch
   POST /v1/auth/register  { full_name, email, password }
   ───────────────────────────────────────── */
async function handleSignUp(e) {
  e.preventDefault();
  clearError('signup-error');

  const btn       = document.getElementById('signup-submit');
  const full_name = document.getElementById('signup-fullname').value.trim();
  const email     = document.getElementById('signup-email').value.trim();
  const password  = document.getElementById('signup-password').value;

  if (!full_name || !email || !password) { showError('signup-error', 'Please fill in all fields.'); return; }

  btn.disabled    = true;
  btn.textContent = 'Creating account…';

  try {
    const res  = await fetch(`${API_BASE}/v1/auth/register`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ full_name, email, password }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { showError('signup-error', extractErrorMessage(data)); return; }

    localStorage.setItem(TOKEN_KEY,   data.access_token);
    localStorage.setItem(REFRESH_KEY, data.refresh_token);
    closeModal('modal-signup');
    await checkAuthState();
    document.getElementById('form-signup').reset();
  } catch (err) {
    showError('signup-error', 'Network error — is the server running?');
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Create account';
  }
}

/* ─────────────────────────────────────────
   Auth — Log out
   POST /v1/auth/logout (Bearer token)
   ───────────────────────────────────────── */
async function handleLogout() {
  const token = localStorage.getItem(TOKEN_KEY);
  try {
    await fetch(`${API_BASE}/v1/auth/logout`, {
      method:  'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
  } catch (_) {}
  finally {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem('cardian_user_role');
    window.location.href = './index.html';
  }
}

/* ─────────────────────────────────────────
   Checkout — LemonSqueezy redirect
   ───────────────────────────────────────── */
const CHECKOUT_LINKS = {
  starter: 'https://cardian.lemonsqueezy.com/checkout/buy/e0e2e8b4-41f7-4a3e-a3b6-6c0db1061287',
  pro: 'https://cardian.lemonsqueezy.com/checkout/buy/b84e1fa4-7107-4391-a0c3-64146b3fd02b'
};

function initiateLemonSqueezyCheckout(plan, btnElement) {
  const user_id = getUserIdFromToken();
  if (!user_id) {
    showToast('Please sign in to purchase.', 'error');
    return;
  }

  const baseLink = CHECKOUT_LINKS[plan];
  if (!baseLink) return;

  const finalUrl = `${baseLink}?checkout[custom][user_id]=${user_id}`;

  if (btnElement) {
    btnElement.style.pointerEvents = 'none';
    btnElement.style.opacity = '0.7';
    btnElement.textContent = 'Redirecting...';
  }

  window.location.href = finalUrl;
}

/* ─────────────────────────────────────────
   Profile — Edit Functions
   ───────────────────────────────────────── */

// Global Dynamic Toast System
function showToast(title, message, type = 'success') {
  if ((message === 'success' || message === 'error') && type === 'success') {
    type = message;
    message = '';
  }

  const toastId = 'toast-' + Date.now();
  const icon = type === 'success' ? 'check-circle' : 'x-circle';
  const color = type === 'success' ? 'border-green-500 text-green-600' : 'border-red-500 text-red-600';
  
  const toastHTML = `
    <div id="${toastId}" class="fixed bottom-6 right-6 z-[100] bg-white shadow-2xl rounded-xl border-l-4 ${color} p-4 flex items-start gap-3 transform translate-x-full opacity-0 transition-all duration-300">
      <i data-lucide="${icon}" class="w-5 h-5 flex-shrink-0 mt-0.5"></i>
      <div>
        <p class="text-sm font-bold text-gray-900">${title}</p>
        <p class="text-sm text-gray-500 mt-0.5">${message || ''}</p>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', toastHTML);
  if (typeof lucide !== 'undefined') lucide.createIcons();
  
  const el = document.getElementById(toastId);
  // Animate in
  setTimeout(() => {
    el.classList.remove('translate-x-full', 'opacity-0');
    el.classList.add('translate-x-0', 'opacity-100');
  }, 10);
  
  // Animate out and remove
  setTimeout(() => {
    el.classList.remove('translate-x-0', 'opacity-100');
    el.classList.add('translate-x-full', 'opacity-0');
    setTimeout(() => el.remove(), 300);
  }, 4000);
}

// Edit Name
async function handleEditName(e) {
  e.preventDefault();
  clearError('edit-name-error');
  const btn = document.getElementById('btn-submit-name');
  const newName = document.getElementById('edit-fullname').value.trim();
  const token = localStorage.getItem(TOKEN_KEY);
  if (!newName) { showError('edit-name-error', 'Name cannot be empty.'); return; }
  
  btn.disabled = true;
  btn.textContent = 'Saving...';
  try {
    const res = await fetchWithAuth(`${API_BASE}/v1/users/fullname`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_full_name: newName })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { showError('edit-name-error', extractErrorMessage(data)); return; }
    
    closeModal('modal-edit-name');
    document.getElementById('profile-fullname').textContent = newName;
    document.getElementById('form-edit-name').reset();
    showToast('Profile Updated', 'Name updated successfully!');
  } catch (err) {
    showError('edit-name-error', 'Network error.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Changes';
  }
}

// Edit Email
async function handleEditEmail(e) {
  e.preventDefault();
  clearError('edit-email-error');
  const btn = document.getElementById('btn-submit-email');
  const newEmail = document.getElementById('edit-email').value.trim();
  const token = localStorage.getItem(TOKEN_KEY);
  if (!newEmail) { showError('edit-email-error', 'Email cannot be empty.'); return; }
  
  btn.disabled = true;
  btn.textContent = 'Saving...';
  try {
    const res = await fetchWithAuth(`${API_BASE}/v1/users/email`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_email: newEmail })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { showError('edit-email-error', extractErrorMessage(data)); return; }
    
    closeModal('modal-edit-email');
    document.getElementById('profile-email').textContent = newEmail;
    document.getElementById('form-edit-email').reset();
    showToast('Profile Updated', 'Email updated successfully!');
  } catch (err) {
    showError('edit-email-error', 'Network error.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Changes';
  }
}

// Change Password
async function handleChangePassword(e) {
  e.preventDefault();
  clearError('edit-password-error');
  const btn = document.getElementById('btn-submit-password');
  const oldPwd = document.getElementById('edit-pwd-old').value;
  const newPwd = document.getElementById('edit-pwd-new').value;
  const token = localStorage.getItem(TOKEN_KEY);
  if (!oldPwd || !newPwd) { showError('edit-password-error', 'Both fields are required.'); return; }
  
  btn.disabled = true;
  btn.textContent = 'Updating...';
  try {
    const res = await fetchWithAuth(`${API_BASE}/v1/users/password`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { showError('edit-password-error', extractErrorMessage(data)); return; }
    
    closeModal('modal-change-password');
    document.getElementById('form-change-password').reset();
    showToast('Security Updated', 'Password changed successfully!');
  } catch (err) {
    showError('edit-password-error', 'Network error.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Update Password';
  }
}

/* ─────────────────────────────────────────
   Auth — Password visibility toggle
   ───────────────────────────────────────── */
function initPasswordToggles() {
  document.querySelectorAll('.pw-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input    = document.getElementById(targetId);
      const icon     = btn.querySelector('i');
      if (!input || !icon) return;
      const isHidden = input.type === 'password';
      input.type     = isHidden ? 'text' : 'password';
      icon.setAttribute('data-lucide', isHidden ? 'eye-off' : 'eye');
      if (typeof lucide !== 'undefined') lucide.createIcons();
    });
  });
}

/* ─────────────────────────────────────────
   Auth — Modal animation: add pop-in CSS
   ───────────────────────────────────────── */
(function injectModalStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .modal-panel {
      animation: modalPopIn .22s cubic-bezier(.22,1,.36,1) both;
    }
    @keyframes modalPopIn {
      from { opacity: 0; transform: scale(.95) translateY(8px); }
      to   { opacity: 1; transform: scale(1)   translateY(0);   }
    }
  `;
  document.head.appendChild(style);
}());

/* ═══════════════════════════════════════════
   DOMContentLoaded — wire everything up
   ═══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {

  /* 0. Ensure auth state is reflected immediately on load */
  await checkAuthState();

  /* ─────────────────────────────────────────
     Watchlist Navigation Guard
     ───────────────────────────────────────── */
  const watchlistLinks = document.querySelectorAll('a[href="./watchlists.html"], #nav-watchlist');
  watchlistLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        openModal('modal-signin');
      } else {
        window.location.href = './watchlists.html';
      }
    });
  });

  /* 1. Initialize Lucide Icons */
  if (typeof lucide !== 'undefined') lucide.createIcons();

  /* 2. Mobile Menu Toggle */
  const menuBtn    = document.getElementById('menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      const isOpen = !mobileMenu.classList.contains('hidden');
      mobileMenu.classList.toggle('hidden', isOpen);
      const icon = menuBtn.querySelector('i');
      if (icon) { icon.setAttribute('data-lucide', isOpen ? 'menu' : 'x'); lucide.createIcons(); }
      menuBtn.setAttribute('aria-expanded', String(!isOpen));
    });
    document.addEventListener('click', (e) => {
      if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.add('hidden');
        const icon = menuBtn.querySelector('i');
        if (icon) { icon.setAttribute('data-lucide', 'menu'); lucide.createIcons(); }
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 768) {
        mobileMenu.classList.add('hidden');
        const icon = menuBtn.querySelector('i');
        if (icon) { icon.setAttribute('data-lucide', 'menu'); lucide.createIcons(); }
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    }, { passive: true });
  }

  /* 3. Navbar — shadow on scroll */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => navbar.classList.toggle('shadow-md', window.scrollY > 8), { passive: true });
  }

  /* 4. Floating Cards */
  document.querySelectorAll('[data-float]').forEach((card, index) => {
    const amplitude  = 10 + Math.random() * 10;
    const frequency  = 0.0004 + Math.random() * 0.0003;
    const phaseShift = (index / document.querySelectorAll('[data-float]').length) * Math.PI * 2;
    const rotRange   = 2 + Math.random() * 3;
    let startTime = null;
    function animate(timestamp) {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const y   = Math.sin(elapsed * frequency * Math.PI * 2 + phaseShift) * amplitude;
      const rot = Math.sin(elapsed * frequency * Math.PI * 2 + phaseShift + 1) * rotRange;
      card.style.transform = `translateY(${y.toFixed(2)}px) rotate(${rot.toFixed(2)}deg)`;
      requestAnimationFrame(animate);
    }
    setTimeout(() => requestAnimationFrame(animate), index * 180);
  });

  /* 5. Pricing Cards — scroll-reveal */
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity   = '1';
        entry.target.style.transform = 'translateY(0)';
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('.pricing-card').forEach((card, i) => {
    card.style.opacity    = '0';
    card.style.transform  = 'translateY(36px)';
    card.style.transition = `opacity .6s ease ${i * 0.12}s, transform .6s cubic-bezier(.22,1,.36,1) ${i * 0.12}s`;
    revealObserver.observe(card);
  });

  /* 6. Smooth scroll for # anchors */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  /* 7. Auth — Modal trigger bindings */

  // Sign In
  document.getElementById('btn-signin')?.addEventListener('click', (e) => {
    e.preventDefault(); clearError('signin-error'); openModal('modal-signin');
  });

  // Sign Up
  document.getElementById('btn-signup')?.addEventListener('click', (e) => {
    e.preventDefault(); clearError('signup-error'); openModal('modal-signup');
  });

  // CTA Primary — open sign-in if guest, do nothing if logged in
  document.getElementById('cta-primary')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (localStorage.getItem(TOKEN_KEY)) {
      return;
    } else {
      clearError('signin-error');
      openModal('modal-signin');
    }
  });

  // Close modals
  document.getElementById('modal-signin-close')?.addEventListener('click', () => closeModal('modal-signin'));
  document.getElementById('modal-signup-close')?.addEventListener('click', () => closeModal('modal-signup'));
  document.getElementById('modal-signin-backdrop')?.addEventListener('click', () => closeModal('modal-signin'));
  document.getElementById('modal-signup-backdrop')?.addEventListener('click', () => closeModal('modal-signup'));

  // ESC
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAllModals(); });

  // Switch Sign In ↔ Sign Up
  document.getElementById('switch-to-signup')?.addEventListener('click', () => {
    closeModal('modal-signin'); clearError('signup-error'); openModal('modal-signup');
  });
  document.getElementById('switch-to-signin')?.addEventListener('click', () => {
    closeModal('modal-signup'); clearError('signin-error'); openModal('modal-signin');
  });

  // Log out
  document.getElementById('btn-logout')?.addEventListener('click', handleLogout);
  document.getElementById('btn-logout-mobile')?.addEventListener('click', handleLogout);

  /* Global checkout click delegation for index/profile modal contexts */
  document.addEventListener('click', (e) => {
    const topupBtn = e.target.closest('#btn-topup, #btn-topup-mobile');
    if (topupBtn) {
      e.preventDefault();
      document.getElementById('topup-error')?.classList.add('hidden');
      document.getElementById('topup-success')?.classList.add('hidden');
      openModal('modal-topup');
      return;
    }

    const closeTopupBtn = e.target.closest('#modal-topup-close') || e.target.closest('#modal-topup-backdrop');
    if (closeTopupBtn) {
      closeModal('modal-topup');
      return;
    }

    const starterPricingBtn = e.target.closest('#pricing-starter-cta');
    if (starterPricingBtn) {
      e.preventDefault();
      initiateLemonSqueezyCheckout('starter', starterPricingBtn);
      return;
    }

    const proPricingBtn = e.target.closest('#pricing-pro-cta');
    if (proPricingBtn) {
      e.preventDefault();
      initiateLemonSqueezyCheckout('pro', proPricingBtn);
      return;
    }

    const topupSubmitBtn = e.target.closest('#btn-topup-submit, #topup-submit');
    if (topupSubmitBtn) {
      e.preventDefault();
      const selectedPackage = document.querySelector('input[name="package"]:checked');
      if (!selectedPackage?.value) return;
      initiateLemonSqueezyCheckout(selectedPackage.value, topupSubmitBtn);
    }
  });

  /* 9. Auth & Profile Form submission */
  document.getElementById('form-signin')?.addEventListener('submit', handleSignIn);
  document.getElementById('form-signup')?.addEventListener('submit', handleSignUp);
  document.getElementById('form-edit-name')?.addEventListener('submit', handleEditName);
  document.getElementById('form-edit-email')?.addEventListener('submit', handleEditEmail);
  document.getElementById('form-change-password')?.addEventListener('submit', handleChangePassword);

  /* 10. Password visibility toggles */
  initPasswordToggles();

  /* 11. Navigation Logic (Auth Guards) */
  document.querySelectorAll('#nav-parse, .nav-parse-mobile').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      if (!localStorage.getItem(TOKEN_KEY)) {
        clearError('signin-error');
        openModal('modal-signin');
      } else {
        window.location.href = './parsed_lookups.html';
      }
    });
  });

  document.querySelectorAll('#nav-manual, .nav-manual-mobile').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      if (!localStorage.getItem(TOKEN_KEY)) {
        clearError('signin-error');
        openModal('modal-signin');
      } else {
        window.location.href = './manual_lookups.html';
      }
    });
  });

  /* ─────────────────────────────────────────
     Shared Polling Logic
     ───────────────────────────────────────── */
  function startPolling(lookupId, type, onSuccess, onFail) {
    const loadingText = document.getElementById('parse-loading-text');
    const texts = [
      "Running valuation models...", 
      "Comparing market data...", 
      "Evaluating condition impact...", 
      "Calculating precise estimate...", 
      "Finalizing AI verdict..."
    ];
    let textIdx = 0;
    const textInt = setInterval(() => {
      textIdx = (textIdx + 1) % texts.length;
      if (loadingText) loadingText.textContent = texts[textIdx];
    }, 2000);

    let attempts = 0;
    const maxAttempts = 10; // 10 attempts * 1500ms = 15 seconds
    const pollInterval = 1500;

    const pollInt = setInterval(async () => {
      attempts++;
      try {
        const url = `${API_BASE}/v1/lookups/${type}/${lookupId}/verdict`;
        const verdictRes = await fetchWithAuth(url);
        
        if (verdictRes.status === 202) {
          if (attempts >= maxAttempts) {
            clearInterval(pollInt);
            clearInterval(textInt);
            showToast('Request Timeout', 'The analysis is taking too long. Please try again later.', 'error');
            onFail();
          }
          return;
        }
        
        clearInterval(pollInt);
        clearInterval(textInt);
        
        if (!verdictRes.ok) {
          const errData = await verdictRes.json().catch(() => ({}));
          showToast('Prediction Failed', extractErrorMessage(errData), 'error');
          onFail();
          return;
        }
        
        const verdictData = await verdictRes.json();
        
        if (type === 'parsed') {
          const carRes = await fetchWithAuth(`${API_BASE}/v1/lookups/parsed/${lookupId}`);
          const carData = carRes.ok ? await carRes.json() : {};
          onSuccess(verdictData, carData);
        } else {
          onSuccess(verdictData, null);
        }
        
      } catch (pollErr) {
        clearInterval(pollInt);
        clearInterval(textInt);
        showToast('Network Error', 'Lost connection while analyzing.', 'error');
        onFail();
      }
    }, pollInterval);
  }

  /* ─────────────────────────────────────────
     UI Helpers
     ───────────────────────────────────────── */
  function resetSubmitButton(btnId, defaultText, iconName) {
    const btn = document.getElementById(btnId);
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5"></i> ${defaultText}`;
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  /* 13. URL Parser Logic */
  const parseForm = document.getElementById('form-parse-url');
  if (parseForm) {
    parseForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const urlInput = document.getElementById('parse-url');
      const btn = document.getElementById('btn-predict-price');
      const loadingEl = document.getElementById('parse-loading');
      const loadingText = document.getElementById('parse-loading-text');
      
      if (!urlInput || !urlInput.value) return;
      const url = urlInput.value;

      btn.disabled = true;
      btn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Processing...';
      if (typeof lucide !== 'undefined') lucide.createIcons();

      try {
        const initRes = await fetchWithAuth(`${API_BASE}/v1/lookups/parsed/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });
        
        const initData = await initRes.json().catch(() => ({}));
        
        if (!initRes.ok) {
          showToast('Parsing Failed', extractErrorMessage(initData), 'error');
          resetParseUI();
          return;
        }

        const lookupId = initData.lookup_id;
        
        // Show loading state
        parseForm.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        loadingEl.classList.add('flex');
        
        startPolling(
          lookupId, 
          'parsed',
          (verdictData, carData) => {
            renderCarResult(verdictData, carData);
          },
          () => {
            resetParseUI();
          }
        );

      } catch (err) {
        showToast('Network Error', 'Failed to start parsing. Is the server running?', 'error');
        resetParseUI();
      }
    });

    // Handle "Parse Another"
    document.getElementById('btn-parse-another')?.addEventListener('click', resetParseUI);

    function resetParseUI() {
      document.getElementById('form-parse-url').classList.remove('hidden');
      document.getElementById('parse-url').value = '';
      
      const loadingEl = document.getElementById('parse-loading');
      loadingEl.classList.add('hidden');
      loadingEl.classList.remove('flex');
      
      document.getElementById('parse-result').classList.add('hidden');
      
      resetSubmitButton('btn-predict-price', 'Predict Price', 'search');
    }

    function renderCarResult(verdict, car) {
      const loadingEl = document.getElementById('parse-loading');
      loadingEl.classList.add('hidden');
      loadingEl.classList.remove('flex');
      
      document.getElementById('parse-result').classList.remove('hidden');
      
      // Update Price
      document.getElementById('result-price').textContent = `€${(verdict.predicted_price || 0).toLocaleString()}`;
      document.getElementById('result-range').textContent = `€${(verdict.lower_bar || 0).toLocaleString()} to €${(verdict.upper_bar || 0).toLocaleString()}`;
      
      // Update Details
      const brandModel = car.brand ? `${car.brand} ${car.model || ''}` : 'Unknown Vehicle';
      document.getElementById('result-brand-model').textContent = brandModel;
      document.getElementById('result-year').textContent = car.year || '—';
      document.getElementById('result-mileage').textContent = car.mileage_km ? `${car.mileage_km.toLocaleString()} km` : '—';
      document.getElementById('result-listed-price').textContent = car.price_listed ? `€${car.price_listed.toLocaleString()}` : '—';
      
      // Update Verdict
      document.getElementById('result-feedback').textContent = verdict.llm_feedback || 'No feedback available.';

      // Refetch auth state to update token balance automatically
      checkAuthState();

      // Setup Add to Watchlist Button
      const btnWatchlist = document.getElementById('btn-add-watchlist');
      if (btnWatchlist) {
        // Reset button state
        btnWatchlist.disabled = false;
        btnWatchlist.innerHTML = `
          <i data-lucide="bookmark-plus" class="w-5 h-5 group-hover:fill-white transition-colors"></i>
          <span>Add to Watchlist (5 tokens)</span>
        `;
        btnWatchlist.className = 'w-full py-4 text-sm font-bold text-gray-900 bg-white border-2 border-gray-900 rounded-xl hover:bg-gray-900 hover:text-white transition-all duration-200 shadow-sm flex items-center justify-center gap-2 group';
        
        // Remove old listeners by cloning
        const newBtn = btnWatchlist.cloneNode(true);
        btnWatchlist.parentNode.replaceChild(newBtn, btnWatchlist);
        
        newBtn.addEventListener('click', async () => {
          const url = document.getElementById('parse-url').value;
          const lastPrice = car.price_listed || verdict.predicted_price || 0;
          
          if (!url) return;
          
          newBtn.disabled = true;
          newBtn.innerHTML = `
            <i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i>
            <span>Adding...</span>
          `;
          
          try {
            const res = await fetchWithAuth(`${API_BASE}/v1/watchlists/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                url: url,
                last_price: Number(lastPrice)
              })
            });
            
            if (res.ok) {
              showToast('Success', 'Car added to your watchlist!', 'success');
              newBtn.innerHTML = `
                <i data-lucide="check" class="w-5 h-5"></i>
                <span>Added to Watchlist</span>
              `;
              newBtn.className = 'w-full py-4 text-sm font-bold text-white bg-green-600 border-2 border-green-600 rounded-xl flex items-center justify-center gap-2 opacity-90 cursor-not-allowed';
              checkAuthState(); // update tokens if deducted
            } else if (res.status === 402) {
              showToast('Insufficient Tokens', 'You do not have enough tokens to add to watchlist.', 'error');
              resetBtn();
            } else if (res.status === 409) {
              showToast('Already Exists', 'This car is already in your watchlist.', 'error');
              newBtn.innerHTML = `
                <i data-lucide="bookmark-check" class="w-5 h-5"></i>
                <span>Already in Watchlist</span>
              `;
              newBtn.className = 'w-full py-4 text-sm font-bold text-gray-500 bg-gray-100 border-2 border-gray-200 rounded-xl flex items-center justify-center gap-2 opacity-90 cursor-not-allowed';
            } else {
              showToast('Error', 'Failed to add to watchlist.', 'error');
              resetBtn();
            }
          } catch (err) {
            showToast('Error', 'Network error. Please try again.', 'error');
            resetBtn();
          }
          
          function resetBtn() {
            newBtn.disabled = false;
            newBtn.innerHTML = `
              <i data-lucide="bookmark-plus" class="w-5 h-5 group-hover:fill-white transition-colors"></i>
              <span>Add to Watchlist (5 tokens)</span>
            `;
            if (typeof lucide !== 'undefined') lucide.createIcons();
          }
          
          if (typeof lucide !== 'undefined') lucide.createIcons();
        });
        
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    }
  }

  /* 14. Manual Parser Logic */
  const manualForm = document.getElementById('form-manual-lookup');
  if (manualForm) {
    let brandModelData = {};
    let selectedBrand = null;

    async function fetchBrandModelData() {
      try {
        const res = await fetch('./assets/images/brands_models.txt');
        if (!res.ok) return;
        const text = await res.text();
        const lines = text.split('\n');
        let currentBrand = null;
        for (let line of lines) {
          line = line.replace(/\r/g, '');
          if (!line.trim()) continue;
          if (line.endsWith(':') && !line.startsWith(' ')) {
            currentBrand = line.slice(0, -1).trim().toLowerCase();
            brandModelData[currentBrand] = [];
          } else if (line.startsWith('  - ') && currentBrand) {
            brandModelData[currentBrand].push(line.slice(4).trim().toLowerCase());
          }
        }
      } catch (e) {
        console.error('Failed to load brand model data', e);
      }
    }
    fetchBrandModelData();

    const brandInput = document.getElementById('manual-brand');
    const modelInput = document.getElementById('manual-model');
    const brandList = document.getElementById('brand-autocomplete-list');
    const modelList = document.getElementById('model-autocomplete-list');

    function closeAllLists(except) {
      if (except !== brandList && brandList) brandList.classList.add('hidden');
      if (except !== modelList && modelList) modelList.classList.add('hidden');
    }

    document.addEventListener('click', (e) => {
      if (e.target !== brandInput && e.target !== modelInput) {
        closeAllLists();
      }
    });

    if (brandInput) {
      brandInput.addEventListener('input', function() {
        const val = this.value.toLowerCase().trim();
        brandList.innerHTML = '';
        if (!val) {
          brandList.classList.add('hidden');
          selectedBrand = null;
          modelInput.disabled = true;
          modelInput.value = '';
          return;
        }
        const matches = Object.keys(brandModelData).filter(b => b.includes(val));
        if (matches.length > 0) {
          matches.forEach(match => {
            const li = document.createElement('li');
            li.className = 'px-4 py-2 cursor-pointer text-sm text-gray-700 hover:bg-[#ff9900]/10 hover:text-[#ff9900] transition-colors';
            // Capitalize for display
            li.textContent = match.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            li.addEventListener('click', () => {
              brandInput.value = li.textContent;
              selectedBrand = match;
              brandList.classList.add('hidden');
              modelInput.disabled = false;
              modelInput.value = '';
              modelInput.focus();
            });
            brandList.appendChild(li);
          });
          brandList.classList.remove('hidden');
        } else {
          brandList.classList.add('hidden');
        }
        
        if (brandModelData[val]) {
           selectedBrand = val;
           modelInput.disabled = false;
        } else {
           selectedBrand = null;
           modelInput.disabled = true;
           modelInput.value = '';
        }
      });

      brandInput.addEventListener('focus', function() {
        if (this.value) this.dispatchEvent(new Event('input'));
      });
    }

    if (modelInput) {
      modelInput.addEventListener('input', function() {
        const val = this.value.toLowerCase().trim();
        modelList.innerHTML = '';
        if (!selectedBrand) {
          modelList.classList.add('hidden');
          return;
        }
        const models = brandModelData[selectedBrand] || [];
        const matches = val ? models.filter(m => m.includes(val)) : models;
        if (matches.length > 0) {
          matches.forEach(match => {
            const li = document.createElement('li');
            li.className = 'px-4 py-2 cursor-pointer text-sm text-gray-700 hover:bg-[#ff9900]/10 hover:text-[#ff9900] transition-colors';
            li.textContent = match.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            li.addEventListener('click', () => {
              modelInput.value = li.textContent;
              modelList.classList.add('hidden');
            });
            modelList.appendChild(li);
          });
          modelList.classList.remove('hidden');
        } else {
          modelList.classList.add('hidden');
        }
      });

      modelInput.addEventListener('focus', function() {
        this.dispatchEvent(new Event('input'));
      });
    }

    // Segmented button toggles
    document.querySelectorAll('.segment-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const parent = btn.parentElement;
        const hiddenInput = parent.nextElementSibling;
        const value = btn.dataset.value;
        
        parent.querySelectorAll('.segment-btn').forEach(b => {
          b.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
          b.classList.add('text-gray-500');
        });
        
        btn.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        btn.classList.remove('text-gray-500');
        
        hiddenInput.value = value;
      });
    });

    manualForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const yearInput = document.getElementById('manual-year');
      const mileageInput = document.getElementById('manual-mileage');
      const powerInput = document.getElementById('manual-power');
      const ownersInput = document.getElementById('manual-owners');
      const brandInputEl = document.getElementById('manual-brand');
      const modelInputEl = document.getElementById('manual-model');

      let isValid = true;
      const highlightError = (el) => {
        el.classList.add('border-red-500', 'ring-red-500/20');
        el.classList.remove('border-gray-200', 'focus:border-[#ff9900]', 'focus:ring-[#ff9900]/10');
        isValid = false;
      };
      const resetError = (el) => {
        el.classList.remove('border-red-500', 'ring-red-500/20');
        el.classList.add('border-gray-200', 'focus:border-[#ff9900]', 'focus:ring-[#ff9900]/10');
      };

      [brandInputEl, modelInputEl, yearInput, mileageInput, powerInput, ownersInput].forEach(resetError);

      if (!selectedBrand || brandInputEl.value.trim() === '') { highlightError(brandInputEl); }
      if (modelInputEl.value.trim() === '') { highlightError(modelInputEl); }

      const yearStr = yearInput.value.trim();
      const yearVal = parseInt(yearStr, 10);
      if (yearStr === '' || isNaN(yearVal) || yearVal < 1851) { highlightError(yearInput); }

      const mileageStr = mileageInput.value.trim();
      const mileageVal = parseInt(mileageStr, 10);
      if (mileageStr === '' || isNaN(mileageVal) || mileageVal < 0) { highlightError(mileageInput); }

      const powerStr = powerInput.value.trim();
      const powerVal = parseInt(powerStr, 10);
      if (powerStr === '' || isNaN(powerVal) || powerVal <= 0) { highlightError(powerInput); }

      const ownersStr = ownersInput.value.trim();
      const ownersVal = parseInt(ownersStr, 10);
      if (ownersStr === '' || isNaN(ownersVal) || ownersVal < 0) { highlightError(ownersInput); }

      if (!isValid) {
        showToast('Validation Error', 'Please correct the highlighted fields.', 'error');
        return;
      }

      const userId = await getUserIdFromToken();
      if (!userId) {
        showToast('Auth Error', 'Could not determine user ID. Please sign in again.', 'error');
        return;
      }

      const payload = {
        brand: brandInputEl.value.trim().toLowerCase(),
        model: modelInputEl.value.trim().toLowerCase(),
        year: yearVal,
        mileage_km: mileageVal,
        power_kw: powerVal,
        previous_owners_qty: ownersVal,
        fuel_category: document.getElementById('manual-fuel').value.toLowerCase().trim(),
        condition: document.getElementById('manual-condition').value.toLowerCase().trim(),
        transmission: document.getElementById('manual-transmission').value.toLowerCase().trim(),
        body_type: document.getElementById('manual-body').value.toLowerCase().trim(),
        drive_train: document.getElementById('manual-drivetrain').value.toLowerCase().trim(),
        had_accident: parseInt(document.getElementById('manual-had-accident').value, 10) === 1 ? 1 : 0,
        has_full_service_history: parseInt(document.getElementById('manual-service-history').value, 10) === 1 ? 1 : 0,
        seller_is_dealer: parseInt(document.getElementById('manual-seller-dealer').value, 10) === 1 ? 1 : 0,
        user_id: parseInt(userId, 10)
      };

      const btn = document.getElementById('btn-manual-predict');
      const loadingEl = document.getElementById('parse-loading');
      const loadingText = document.getElementById('parse-loading-text');

      btn.disabled = true;
      btn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Processing...';
      if (typeof lucide !== 'undefined') lucide.createIcons();

      try {
        const initRes = await fetchWithAuth(`${API_BASE}/v1/lookups/manual/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        if (initRes.status === 422) {
          const errData = await initRes.json().catch(() => ({}));
          let errMsg = 'Validation failed.';
          if (errData.detail && Array.isArray(errData.detail) && errData.detail.length > 0) {
            const firstErr = errData.detail[0];
            const field = firstErr.loc ? firstErr.loc[firstErr.loc.length - 1] : 'Field';
            errMsg = `Validation error on '${field}': ${firstErr.msg}`;
          }
          showToast('Validation Error', errMsg, 'error');
          resetManualUI();
          return;
        }

        const initData = await initRes.json().catch(() => ({}));
        
        if (!initRes.ok) {
          showToast('Error', extractErrorMessage(initData), 'error');
          resetManualUI();
          return;
        }

        const lookupId = initData.lookup_id;
        
        manualForm.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        loadingEl.classList.add('flex');
        
        startPolling(
          lookupId, 
          'manual',
          (verdictData) => {
            renderCarResultManual(verdictData, payload);
          },
          () => {
            resetManualUI();
          }
        );

      } catch (err) {
        showToast('Network Error', 'Failed to start parsing. Is the server running?', 'error');
        resetManualUI();
      }
    });

    document.getElementById('btn-parse-another')?.addEventListener('click', resetManualUI);

    function resetManualUI() {
      document.getElementById('form-manual-lookup').classList.remove('hidden');
      
      const loadingEl = document.getElementById('parse-loading');
      loadingEl.classList.add('hidden');
      loadingEl.classList.remove('flex');
      
      document.getElementById('parse-result').classList.add('hidden');
      
      resetSubmitButton('btn-manual-predict', 'Predict Price', 'zap');
    }
    
    function renderCarResultManual(verdict, car) {
      const loadingEl = document.getElementById('parse-loading');
      loadingEl.classList.add('hidden');
      loadingEl.classList.remove('flex');
      
      document.getElementById('parse-result').classList.remove('hidden');
      
      document.getElementById('result-price').textContent = `€${(verdict.predicted_price || 0).toLocaleString()}`;
      document.getElementById('result-range').textContent = `€${(verdict.lower_bar || 0).toLocaleString()} to €${(verdict.upper_bar || 0).toLocaleString()}`;
      
      const brandModel = car.brand ? `${car.brand} ${car.model || ''}` : 'Unknown Vehicle';
      document.getElementById('result-brand-model').textContent = brandModel;
      document.getElementById('result-year').textContent = car.year || '—';
      document.getElementById('result-mileage').textContent = car.mileage_km ? `${car.mileage_km.toLocaleString()} km` : '—';
      document.getElementById('result-listed-price').textContent = 'N/A';
      
      document.getElementById('result-feedback').textContent = verdict.llm_feedback || 'No feedback available.';
      
      checkAuthState();
    }
  }

  /* 15. Profile Page Logic */
  if (window.location.pathname.includes('profile.html')) {
    await loadProfile();
  }

  /* 16. Watchlists Page Logic */
  if (window.location.pathname.includes('watchlists.html')) {
    initWatchlistsPage();
  }

});

/* ─────────────────────────────────────────
   Profile Page Logic
   ───────────────────────────────────────── */
async function loadProfile() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    window.location.href = './index.html';
    return;
  }

  try {
    const res = await fetchWithAuth(`${API_BASE}/v1/users/profile`, {
      headers: { 'Content-Type': 'application/json' },
    });

    if (res.status === 401 || res.status === 403) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_KEY);
      window.location.href = './index.html';
      return;
    }

    if (res.ok) {
      const user = await res.json();
      
      // Populate profile fields
      const nameEl    = document.getElementById('profile-fullname');
      const emailEl   = document.getElementById('profile-email');
      const balValEl  = document.getElementById('profile-balance-val');
      
      if (nameEl) nameEl.textContent = user.full_name || '—';
      if (emailEl) emailEl.textContent = user.email || '—';
      if (balValEl) balValEl.textContent = user.current_balance ?? '0';

    } else {
      // Fallback error UI
      const nameEl    = document.getElementById('profile-fullname');
      const emailEl   = document.getElementById('profile-email');
      const balValEl  = document.getElementById('profile-balance-val');
      if (nameEl) nameEl.textContent = 'Error loading';
      if (emailEl) emailEl.textContent = 'Error loading';
      if (balValEl) balValEl.textContent = '—';
    }
  } catch (err) {
    const nameEl  = document.getElementById('profile-fullname');
    const emailEl = document.getElementById('profile-email');
    if (nameEl) nameEl.textContent = 'Network Error';
    if (emailEl) emailEl.textContent = 'Network Error';
  }
}

/* ─────────────────────────────────────────
   Watchlists Page Logic
   ───────────────────────────────────────── */
function initWatchlistsPage() {
  const tabWl = document.getElementById('tab-watchlists');
  const tabAl = document.getElementById('tab-alerts');
  const contentWl = document.getElementById('content-watchlists');
  const contentAl = document.getElementById('content-alerts');

  // Watchlists State
  let wlData = [];
  let wlOffset = 0;
  const wlLimit = 10;
  
  // Alerts State
  let alData = [];
  let alOffset = 0;
  const alLimit = 10;

  function switchTab(tab) {
    if (tab === 'watchlists') {
      tabWl.classList.replace('text-gray-500', 'text-[#ff9900]');
      tabWl.classList.replace('border-transparent', 'border-[#ff9900]');
      tabAl.classList.replace('text-[#ff9900]', 'text-gray-500');
      tabAl.classList.replace('border-[#ff9900]', 'border-transparent');
      
      contentWl.classList.remove('hidden');
      contentAl.classList.add('hidden');
    } else {
      tabAl.classList.replace('text-gray-500', 'text-[#ff9900]');
      tabAl.classList.replace('border-transparent', 'border-[#ff9900]');
      tabWl.classList.replace('text-[#ff9900]', 'text-gray-500');
      tabWl.classList.replace('border-[#ff9900]', 'border-transparent');
      
      contentAl.classList.remove('hidden');
      contentWl.classList.add('hidden');
      
      if (alData.length === 0 && alOffset === 0) fetchAlerts();
    }
  }

  tabWl?.addEventListener('click', () => switchTab('watchlists'));
  tabAl?.addEventListener('click', () => switchTab('alerts'));

  // Load initial watchlists
  fetchWatchlists();

  // Load More Listeners
  document.getElementById('btn-more-watchlists')?.addEventListener('click', () => renderWatchlists(false));
  document.getElementById('btn-more-alerts')?.addEventListener('click', () => renderAlerts(false));
  
  // --- Watchlists Fetch & Render ---
  async function fetchWatchlists() {
    const loader = document.getElementById('loader-watchlists');
    const empty = document.getElementById('empty-watchlists');
    const container = document.getElementById('container-watchlists');
    const btnMore = document.getElementById('btn-more-watchlists');
    
    loader?.classList.remove('hidden');
    empty?.classList.add('hidden');
    btnMore?.classList.add('hidden');

    try {
      const res = await fetchWithAuth(`${API_BASE}/v1/watchlists/my`);
      if (res.ok) {
        const data = await res.json();
        wlData = data.items || [];
        wlOffset = 0;
        container.innerHTML = '';
        if (wlData.length === 0) {
          empty?.classList.remove('hidden');
        } else {
          renderWatchlists(true);
        }
      } else {
        showToast('Error', 'Failed to load watchlists', 'error');
      }
    } catch (err) {
      showToast('Error', 'Network error while loading watchlists', 'error');
    } finally {
      loader?.classList.add('hidden');
    }
  }

  function renderWatchlists(isInitial = false) {
    const container = document.getElementById('container-watchlists');
    const btnMore = document.getElementById('btn-more-watchlists');
    
    const slice = wlData.slice(wlOffset, wlOffset + wlLimit);
    
    slice.forEach(wl => {
      const card = document.createElement('div');
      card.className = 'bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all cursor-pointer group flex flex-col justify-between';
      card.innerHTML = `
        <div>
          <div class="flex justify-between items-start mb-3">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-md ${wl.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}">${wl.is_active ? 'Active' : 'Inactive'}</span>
            <span class="text-xs text-gray-400 font-medium">${new Date(wl.created_at).toLocaleDateString()}</span>
          </div>
          <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#ff9900] transition-colors truncate">Watchlist #${wl.id}</h3>
          <p class="text-sm text-gray-500 mt-1 truncate" title="${wl.url}">URL: ${wl.url}</p>
        </div>
        <div class="mt-5 pt-4 border-t border-gray-100">
          <p class="text-xs font-medium text-gray-500 mb-0.5">Target Price</p>
          <p class="text-xl font-black text-gray-900">€${(wl.last_price || 0).toLocaleString()}</p>
        </div>
      `;
      card.addEventListener('click', () => openWatchlistModal(wl));
      container.appendChild(card);
    });

    wlOffset += wlLimit;
    
    if (wlOffset < wlData.length) {
      btnMore?.classList.remove('hidden');
    } else {
      btnMore?.classList.add('hidden');
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  // --- Alerts Fetch & Render ---
  async function fetchAlerts() {
    const loader = document.getElementById('loader-alerts');
    const empty = document.getElementById('empty-alerts');
    const container = document.getElementById('container-alerts');
    const btnMore = document.getElementById('btn-more-alerts');
    
    loader?.classList.remove('hidden');
    empty?.classList.add('hidden');
    btnMore?.classList.add('hidden');

    try {
      const res = await fetchWithAuth(`${API_BASE}/v1/alerts/`);
      if (res.ok) {
        const data = await res.json();
        alData = Array.isArray(data) ? data : (data.items || (data.id ? [data] : []));
        alOffset = 0;
        container.innerHTML = '';
        if (alData.length === 0) {
          empty?.classList.remove('hidden');
        } else {
          renderAlerts(true);
        }
      } else if (res.status === 404) {
        alData = [];
        alOffset = 0;
        container.innerHTML = '';
        empty?.classList.remove('hidden');
      } else {
        showToast('Error', 'Failed to load alerts', 'error');
      }
    } catch (err) {
      showToast('Error', 'Network error while loading alerts', 'error');
    } finally {
      loader?.classList.add('hidden');
    }
  }

  function renderAlerts(isInitial = false) {
    const container = document.getElementById('container-alerts');
    const btnMore = document.getElementById('btn-more-alerts');
    
    const slice = alData.slice(alOffset, alOffset + alLimit);
    
    slice.forEach(al => {
      const card = document.createElement('div');
      card.className = 'bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex items-center justify-between gap-4';
      
      const isDrop = (al.price_diff || 0) < 0;
      const color = isDrop ? 'text-green-600' : 'text-red-600';
      const icon = isDrop ? 'trending-down' : 'trending-up';
      const diffSign = isDrop ? '' : '+';
      
      card.innerHTML = `
        <div class="flex items-center gap-4 min-w-0">
          <div class="w-10 h-10 rounded-full ${isDrop ? 'bg-green-50' : 'bg-red-50'} flex items-center justify-center flex-shrink-0">
            <i data-lucide="${icon}" class="w-5 h-5 ${color}"></i>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-bold text-gray-900 truncate">Watchlist #${al.watchlist_id}</p>
            <p class="text-xs text-gray-500 mt-0.5">${new Date(al.noticed_at).toLocaleString()}</p>
          </div>
        </div>
        <div class="text-right flex-shrink-0">
          <p class="text-base font-black ${color}">${diffSign}€${Math.abs(al.price_diff || 0).toLocaleString()}</p>
          <p class="text-xs font-semibold text-gray-500">${diffSign}${(al.price_diff_percents || 0)}%</p>
        </div>
      `;
      container.appendChild(card);
    });

    alOffset += alLimit;
    
    if (alOffset < alData.length) {
      btnMore?.classList.remove('hidden');
    } else {
      btnMore?.classList.add('hidden');
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }
}

// Watchlist Detail Modal
async function openWatchlistModal(wl) {
  openModal('modal-watchlist-detail');
  
  document.getElementById('wl-detail-badge').textContent = wl.is_active ? 'Active' : 'Inactive';
  document.getElementById('wl-detail-badge').className = `inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-md mb-3 ${wl.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`;
  
  document.getElementById('wl-detail-title').textContent = `Watchlist #${wl.id}`;
  
  const urlEl = document.getElementById('wl-detail-url');
  urlEl.innerHTML = `<a href="${wl.url}" target="_blank" rel="noopener noreferrer">${wl.url} <i data-lucide="external-link" class="inline w-3 h-3 ml-0.5"></i></a>`;
  
  document.getElementById('wl-detail-price').textContent = `€${(wl.last_price || 0).toLocaleString()}`;
  document.getElementById('wl-detail-date').textContent = new Date(wl.created_at).toLocaleDateString();
  
  // Fetch recent alerts for this watchlist
  const loader = document.getElementById('loader-wl-alerts');
  const container = document.getElementById('container-wl-alerts');
  const empty = document.getElementById('empty-wl-alerts');
  
  loader?.classList.remove('hidden');
  container.innerHTML = '';
  empty?.classList.add('hidden');
  
  try {
    const res = await fetchWithAuth(`${API_BASE}/v1/alerts/`);
    if (res.ok) {
      const data = await res.json();
      const allAlerts = Array.isArray(data) ? data : (data.items || (data.id ? [data] : []));
      const specificAlerts = allAlerts.filter(a => a.watchlist_id === wl.id).slice(0, 10);
      
      if (specificAlerts.length === 0) {
        empty?.classList.remove('hidden');
      } else {
        specificAlerts.forEach(al => {
          const row = document.createElement('div');
          row.className = 'flex items-center justify-between p-3 rounded-lg bg-white border border-gray-100 shadow-sm';
          
          const isDrop = (al.price_diff || 0) < 0;
          const color = isDrop ? 'text-green-600' : 'text-red-600';
          const icon = isDrop ? 'trending-down' : 'trending-up';
          const diffSign = isDrop ? '' : '+';
          
          row.innerHTML = `
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 rounded-full ${isDrop ? 'bg-green-50' : 'bg-red-50'} flex items-center justify-center flex-shrink-0">
                <i data-lucide="${icon}" class="w-4 h-4 ${color}"></i>
              </div>
              <div class="min-w-0 truncate">
                <p class="text-xs text-gray-500">${new Date(al.noticed_at).toLocaleString()}</p>
              </div>
            </div>
            <div class="text-right flex-shrink-0 ml-4">
              <p class="text-sm font-bold ${color}">${diffSign}€${Math.abs(al.price_diff || 0).toLocaleString()}</p>
            </div>
          `;
          container.appendChild(row);
        });
      }
    } else if (res.status === 404) {
      empty?.classList.remove('hidden');
    } else {
      empty?.classList.remove('hidden');
    }
  } catch (err) {
    empty?.classList.remove('hidden');
  } finally {
    loader?.classList.add('hidden');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }
}

document.getElementById('modal-wl-backdrop')?.addEventListener('click', () => closeModal('modal-watchlist-detail'));
document.getElementById('modal-wl-close')?.addEventListener('click', () => closeModal('modal-watchlist-detail'));
