/* ═══════════════════════════════════════════
   Cardian — main.js
   Lucide init · Mobile menu · Scroll effects
   Floating card animation · Auth modals
   ═══════════════════════════════════════════ */

/* ─────────────────────────────────────────
   Auth — Constants
   ───────────────────────────────────────── */
const API_BASE    = 'http://localhost:8008';
const TOKEN_KEY   = 'cardian_token';
const REFRESH_KEY = 'cardian_refresh_token';

// Simplified RateTypes string
// RateTypes from OpenAPI spec is now an enum: "starter" or "pro"

/* ─────────────────────────────────────────
   Auth — fetchWithAuth Wrapper
   ───────────────────────────────────────── */
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
        
        options.headers['Authorization'] = `Bearer ${data.access_token}`;
        response = await fetch(url, options);
      } else {
        await handleLogout();
      }
    } catch (err) {
      await handleLogout();
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

  if (!guestNav || !userNav) return;

  if (token) {
    guestNav.classList.remove('md:flex');
    guestNav.classList.add('hidden');
    userNav.classList.remove('hidden');
    userNav.classList.add('flex');

    // Fetch profile to get current_balance
    try {
      const res = await fetchWithAuth(`${API_BASE}/v1/users/profile`);
      if (res.ok) {
        const user = await res.json();
        updateHeaderBalance(user.current_balance ?? '—');
        // Cache user_id for top-up
        window._cardianUserId = user.id;
      } else if (res.status === 401 || res.status === 403) {
        // Token invalid — force logout
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        guestNav.classList.remove('hidden');
        guestNav.classList.add('md:flex');
        userNav.classList.remove('flex');
        userNav.classList.add('hidden');
      }
    } catch (_) { /* network error, leave balance as — */ }

  } else {
    userNav.classList.remove('flex');
    userNav.classList.add('hidden');
    guestNav.classList.remove('hidden');
    guestNav.classList.add('md:flex');
  }

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function updateHeaderBalance(balance) {
  const el = document.getElementById('header-balance');
  if (el) el.textContent = `Tokens: ${balance}`;
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
    window.location.href = './index.html';
  }
}

/* ─────────────────────────────────────────
   Top Up — PATCH /v1/users/payments/
   Body: { rate: { price, tokens }, user_id }
   ───────────────────────────────────────── */
async function handleTopUp() {
  const btn = document.getElementById('topup-submit');
  const errorEl   = document.getElementById('topup-error');

  // Hide previous messages
  errorEl.classList.add('hidden');

   const isPro     = document.getElementById('topup-pro')?.checked;
   const rate      = isPro ? 'pro' : 'starter';
   const tokensAdded = isPro ? 100 : 8;
   const token     = localStorage.getItem(TOKEN_KEY);
   const userId    = window._cardianUserId;

  if (!token) { openModal('modal-signin'); closeModal('modal-topup'); return; }
  if (!userId) { errorEl.textContent = 'Could not determine user ID. Please refresh.'; errorEl.classList.remove('hidden'); return; }

  btn.disabled    = true;
  btn.textContent = 'Processing…';

  try {
    const res = await fetchWithAuth(`${API_BASE}/v1/users/payments/`, {
      method:  'PATCH',
      headers: { 'Content-Type':  'application/json' },
      body: JSON.stringify({ rate, user_id: userId }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      errorEl.textContent = extractErrorMessage(data);
      errorEl.classList.remove('hidden');
      return;
    }

    // Refresh balance in header
    await checkAuthState();
    closeModal('modal-topup');
    
    const pkgName = rate === 'pro' ? 'Pro' : 'Starter';
    showToast('Payment Successful', `Successfully activated the ${pkgName} package!`);
  } catch (err) {
    errorEl.textContent = 'Network error — is the server running?';
    errorEl.classList.remove('hidden');
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Pay Now';
  }
}

/* ─────────────────────────────────────────
   Profile — Edit Functions
   ───────────────────────────────────────── */

// Global Dynamic Toast System
function showToast(title, message, type = 'success') {
  const toastId = 'toast-' + Date.now();
  const icon = type === 'success' ? 'check-circle' : 'x-circle';
  const color = type === 'success' ? 'border-green-500 text-green-600' : 'border-red-500 text-red-600';
  
  const toastHTML = `
    <div id="${toastId}" class="fixed bottom-6 right-6 z-[100] bg-white shadow-2xl rounded-xl border-l-4 ${color} p-4 flex items-start gap-3 transform translate-x-full opacity-0 transition-all duration-300">
      <i data-lucide="${icon}" class="w-5 h-5 flex-shrink-0 mt-0.5"></i>
      <div>
        <p class="text-sm font-bold text-gray-900">${title}</p>
        <p class="text-sm text-gray-500 mt-0.5">${message}</p>
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

  // Pricing buttons
  document.getElementById('pricing-starter-cta')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (localStorage.getItem(TOKEN_KEY)) {
      const topupStarter = document.getElementById('topup-starter');
      if (topupStarter) topupStarter.checked = true;
      openModal('modal-topup');
    } else {
      clearError('signin-error');
      openModal('modal-signin');
    }
  });

  document.getElementById('pricing-pro-cta')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (localStorage.getItem(TOKEN_KEY)) {
      const topupPro = document.getElementById('topup-pro');
      if (topupPro) topupPro.checked = true;
      openModal('modal-topup');
    } else {
      clearError('signin-error');
      openModal('modal-signin');
    }
  });

  /* 8. Top Up Modal */
  document.getElementById('btn-topup')?.addEventListener('click', () => {
    // Reset state
    document.getElementById('topup-error')?.classList.add('hidden');
    document.getElementById('topup-success')?.classList.add('hidden');
    openModal('modal-topup');
  });
  document.getElementById('modal-topup-close')?.addEventListener('click', () => closeModal('modal-topup'));
  document.getElementById('modal-topup-backdrop')?.addEventListener('click', () => closeModal('modal-topup'));
  document.getElementById('topup-submit')?.addEventListener('click', handleTopUp);

  /* 9. Auth & Profile Form submission */
  document.getElementById('form-signin')?.addEventListener('submit', handleSignIn);
  document.getElementById('form-signup')?.addEventListener('submit', handleSignUp);
  document.getElementById('form-edit-name')?.addEventListener('submit', handleEditName);
  document.getElementById('form-edit-email')?.addEventListener('submit', handleEditEmail);
  document.getElementById('form-change-password')?.addEventListener('submit', handleChangePassword);

  /* 10. Password visibility toggles */
  initPasswordToggles();

  /* 11. Initial auth state check */
  await checkAuthState();

  /* 12. Navigation Logic (Auth Guards) */
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
        
        // Fun text cycling
        const texts = [
          "Scanning photos...", 
          "Extracting technical data...", 
          "Evaluating condition...", 
          "Calculating market price...", 
          "Finalizing AI verdict..."
        ];
        let textIdx = 0;
        const textInt = setInterval(() => {
          textIdx = (textIdx + 1) % texts.length;
          loadingText.textContent = texts[textIdx];
        }, 2000);

        // Polling
        const pollInt = setInterval(async () => {
          try {
            const verdictRes = await fetchWithAuth(`${API_BASE}/v1/lookups/parsed/${lookupId}/verdict`);
            if (verdictRes.status === 202) {
              // still processing
              return;
            }
            
            clearInterval(pollInt);
            clearInterval(textInt);
            
            if (!verdictRes.ok) {
              const errData = await verdictRes.json().catch(() => ({}));
              showToast('Prediction Failed', extractErrorMessage(errData), 'error');
              resetParseUI();
              return;
            }
            
            const verdictData = await verdictRes.json();
            
            // Now fetch car details
            const carRes = await fetchWithAuth(`${API_BASE}/v1/lookups/parsed/${lookupId}`);
            const carData = carRes.ok ? await carRes.json() : {};
            
            renderCarResult(verdictData, carData);
            
          } catch (pollErr) {
            clearInterval(pollInt);
            clearInterval(textInt);
            showToast('Network Error', 'Lost connection while analyzing.', 'error');
            resetParseUI();
          }
        }, 1500);

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
      
      const btn = document.getElementById('btn-predict-price');
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="search" class="w-5 h-5"></i> Predict Price';
      }
      if (typeof lucide !== 'undefined') lucide.createIcons();
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
    }
  }

  /* 14. Manual Parser Logic */
  const manualForm = document.getElementById('form-manual-lookup');
  if (manualForm) {
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
      
      const payload = {
        brand: document.getElementById('manual-brand').value.trim(),
        model: document.getElementById('manual-model').value.trim(),
        year: parseInt(document.getElementById('manual-year').value, 10),
        mileage_km: parseInt(document.getElementById('manual-mileage').value, 10),
        power_kw: parseInt(document.getElementById('manual-power').value, 10),
        previous_owners_qty: parseInt(document.getElementById('manual-owners').value, 10),
        fuel_category: document.getElementById('manual-fuel').value,
        condition: document.getElementById('manual-condition').value,
        transmission: document.getElementById('manual-transmission').value,
        body_type: document.getElementById('manual-body').value,
        drive_train: document.getElementById('manual-drivetrain').value,
        had_accident: parseInt(document.getElementById('manual-had-accident').value, 10),
        has_full_service_history: parseInt(document.getElementById('manual-service-history').value, 10),
        seller_is_dealer: parseInt(document.getElementById('manual-seller-dealer').value, 10)
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
        
        const initData = await initRes.json().catch(() => ({}));
        
        if (!initRes.ok) {
          showToast('Validation Error', extractErrorMessage(initData), 'error');
          resetManualUI();
          return;
        }

        const lookupId = initData.lookup_id;
        
        manualForm.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        loadingEl.classList.add('flex');
        
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
          loadingText.textContent = texts[textIdx];
        }, 2000);

        const pollInt = setInterval(async () => {
          try {
            const verdictRes = await fetchWithAuth(`${API_BASE}/v1/lookups/manual/${lookupId}/verdict`);
            if (verdictRes.status === 202) {
              return;
            }
            
            clearInterval(pollInt);
            clearInterval(textInt);
            
            if (!verdictRes.ok) {
              const errData = await verdictRes.json().catch(() => ({}));
              showToast('Prediction Failed', extractErrorMessage(errData), 'error');
              resetManualUI();
              return;
            }
            
            const verdictData = await verdictRes.json();
            
            renderCarResultManual(verdictData, payload);
            
          } catch (pollErr) {
            clearInterval(pollInt);
            clearInterval(textInt);
            showToast('Network Error', 'Lost connection while analyzing.', 'error');
            resetManualUI();
          }
        }, 1500);

      } catch (err) {
        showToast('Network Error', 'Failed to start parsing. Is the server running?', 'error');
        resetManualUI();
      }
    });

    document.getElementById('btn-parse-another')?.addEventListener('click', () => {
      document.getElementById('parse-result').classList.add('hidden');
      document.getElementById('form-manual-lookup').classList.remove('hidden');
      // Intentionally not clearing all inputs to allow easy tweaking
    });

    function resetManualUI() {
      document.getElementById('form-manual-lookup').classList.remove('hidden');
      
      const loadingEl = document.getElementById('parse-loading');
      loadingEl.classList.add('hidden');
      loadingEl.classList.remove('flex');
      
      document.getElementById('parse-result').classList.add('hidden');
      
      const btn = document.getElementById('btn-manual-predict');
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="zap" class="w-5 h-5"></i> Predict Price';
      }
      if (typeof lucide !== 'undefined') lucide.createIcons();
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
