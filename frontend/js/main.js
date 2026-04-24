/* ═══════════════════════════════════════════
   Cardian — main.js
   Lucide init · Mobile menu · Scroll effects
   Floating card animation · Auth modals
   ═══════════════════════════════════════════ */

/* ─────────────────────────────────────────
   Auth — Constants
   ───────────────────────────────────────── */
const API_BASE = 'http://localhost:8008';
const TOKEN_KEY = 'cardian_token';
const REFRESH_KEY = 'cardian_refresh_token';

/* ─────────────────────────────────────────
   Auth — UI State: checkAuthState()
   Shows guest buttons OR My Profile + Logout
   ───────────────────────────────────────── */
function checkAuthState() {
    const token = localStorage.getItem(TOKEN_KEY);
    const guestNav = document.getElementById('auth-buttons-guest');
    const userNav = document.getElementById('auth-buttons-user');

    if (!guestNav || !userNav) return;

    if (token) {
        guestNav.classList.remove('md:flex');
        guestNav.classList.add('hidden');
        userNav.classList.remove('hidden');
        userNav.classList.add('flex');
    } else {
        userNav.classList.remove('flex');
        userNav.classList.add('hidden');
        guestNav.classList.remove('hidden');
        guestNav.classList.add('md:flex');
    }

    // Re-render Lucide icons for the newly shown buttons
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/* ─────────────────────────────────────────
   Auth — Modal helpers
   ───────────────────────────────────────── */
function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    // Focus first focusable element inside the panel
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

/* ─────────────────────────────────────────
   Auth — Extract a human-readable error
   from various API response shapes
   ───────────────────────────────────────── */
function extractErrorMessage(data) {
    // FastAPI validation error array
    if (data?.detail && Array.isArray(data.detail)) {
        return data.detail.map(e => e.msg).join(', ');
    }
    // FastAPI string detail
    if (typeof data?.detail === 'string') return data.detail;
    // Generic message field
    if (typeof data?.message === 'string') return data.message;
    return 'Something went wrong. Please try again.';
}

/* ─────────────────────────────────────────
   Auth — Sign In fetch
   POST /v1/auth/login  { email, password }
   Response: UserAuthResponseSchema
     { access_token, refresh_token, ... }
   ───────────────────────────────────────── */
async function handleSignIn(e) {
    e.preventDefault();
    clearError('signin-error');

    const btn = document.getElementById('signin-submit');
    const email = document.getElementById('signin-email').value.trim();
    const password = document.getElementById('signin-password').value;

    if (!email || !password) {
        showError('signin-error', 'Please fill in all fields.');
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Signing in…';

    try {
        const res = await fetch(`${API_BASE}/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            showError('signin-error', extractErrorMessage(data));
            return;
        }

        // Persist tokens
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);

        closeModal('modal-signin');
        checkAuthState();

        // Reset form
        document.getElementById('form-signin').reset();

    } catch (err) {
        showError('signin-error', 'Network error — is the server running?');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Sign in';
    }
}

/* ─────────────────────────────────────────
   Auth — Sign Up fetch
   POST /v1/auth/register  { full_name, email, password }
   Response: UserAuthResponseSchema
     { access_token, refresh_token, ... }
   ───────────────────────────────────────── */
async function handleSignUp(e) {
    e.preventDefault();
    clearError('signup-error');

    const btn = document.getElementById('signup-submit');
    const full_name = document.getElementById('signup-fullname').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;

    if (!full_name || !email || !password) {
        showError('signup-error', 'Please fill in all fields.');
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Creating account…';

    try {
        const res = await fetch(`${API_BASE}/v1/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name, email, password }),
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            showError('signup-error', extractErrorMessage(data));
            return;
        }

        // Persist tokens
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);

        closeModal('modal-signup');
        checkAuthState();

        // Reset form
        document.getElementById('form-signup').reset();

    } catch (err) {
        showError('signup-error', 'Network error — is the server running?');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Create account';
    }
}

/* ─────────────────────────────────────────
   Auth — Log out
   POST /v1/auth/logout (Bearer token)
   Clears storage + redirects regardless of response
   ───────────────────────────────────────── */
async function handleLogout() {
    const token = localStorage.getItem(TOKEN_KEY);

    // Fire logout request — do not await success, always clean up
    try {
        await fetch(`${API_BASE}/v1/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });
    } catch (_) {
        // Network error is acceptable — we still log out locally
    } finally {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        window.location.href = './index.html';
    }
}

/* ─────────────────────────────────────────
   Auth — Password visibility toggle
   ───────────────────────────────────────── */
function initPasswordToggles() {
    document.querySelectorAll('.pw-toggle').forEach((btn) => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = btn.querySelector('i');
            if (!input || !icon) return;

            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
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
document.addEventListener('DOMContentLoaded', () => {

    /* ─────────────────────────────────────────
       1. Initialize Lucide Icons
       ───────────────────────────────────────── */
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    /* ─────────────────────────────────────────
       2. Mobile Menu Toggle
       ───────────────────────────────────────── */
    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            const isOpen = !mobileMenu.classList.contains('hidden');

            // Toggle visibility
            mobileMenu.classList.toggle('hidden', isOpen);

            // Swap hamburger ↔ X icon
            const icon = menuBtn.querySelector('i');
            if (icon) {
                icon.setAttribute('data-lucide', isOpen ? 'menu' : 'x');
                lucide.createIcons();
            }

            // Update ARIA state
            menuBtn.setAttribute('aria-expanded', String(!isOpen));
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add('hidden');

                const icon = menuBtn.querySelector('i');
                if (icon) {
                    icon.setAttribute('data-lucide', 'menu');
                    lucide.createIcons();
                }
                menuBtn.setAttribute('aria-expanded', 'false');
            }
        });

        // Close menu on resize back to desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768) {
                mobileMenu.classList.add('hidden');
                const icon = menuBtn.querySelector('i');
                if (icon) {
                    icon.setAttribute('data-lucide', 'menu');
                    lucide.createIcons();
                }
                menuBtn.setAttribute('aria-expanded', 'false');
            }
        }, { passive: true });
    }

    /* ─────────────────────────────────────────
       3. Navbar — elevated shadow on scroll
       ───────────────────────────────────────── */
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('shadow-md', window.scrollY > 8);
        }, { passive: true });
    }

    /* ─────────────────────────────────────────
       4. Floating Cards — asynchronous JS-driven
          vertical levitation (augments CSS float)
       ───────────────────────────────────────── */
    const floatCards = document.querySelectorAll('[data-float]');

    /**
     * Each card gets its own independent rAF loop with randomised
     * amplitude, frequency, and phase so they never move in sync.
     */
    floatCards.forEach((card, index) => {
        // Randomise parameters per card so motion is fully asynchronous
        const amplitude = 10 + Math.random() * 10;   // px (10–20)
        const frequency = 0.0004 + Math.random() * 0.0003; // cycles/ms
        const phaseShift = (index / floatCards.length) * Math.PI * 2;
        const rotRange = 2 + Math.random() * 3;      // degrees (2–5)

        let startTime = null;

        function animate(timestamp) {
            if (!startTime) startTime = timestamp;
            const elapsed = timestamp - startTime;

            const y = Math.sin(elapsed * frequency * Math.PI * 2 + phaseShift) * amplitude;
            const rot = Math.sin(elapsed * frequency * Math.PI * 2 + phaseShift + 1) * rotRange;

            card.style.transform = `translateY(${y.toFixed(2)}px) rotate(${rot.toFixed(2)}deg)`;

            requestAnimationFrame(animate);
        }

        // Stagger the start of each card's loop for even more variety
        setTimeout(() => requestAnimationFrame(animate), index * 180);
    });

    /* ─────────────────────────────────────────
       5. Pricing Cards — scroll-reveal via
          IntersectionObserver
       ───────────────────────────────────────── */
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    document.querySelectorAll('.pricing-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(36px)';
        card.style.transition = `opacity .6s ease ${i * 0.12}s, transform .6s cubic-bezier(.22,1,.36,1) ${i * 0.12}s`;
        revealObserver.observe(card);
    });

    /* ─────────────────────────────────────────
       6. Smooth scroll for any # anchor links
       ───────────────────────────────────────── */
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', (e) => {
            const targetId = anchor.getAttribute('href');
            if (targetId === '#') return;
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    /* ─────────────────────────────────────────
       7. Auth — Modal trigger bindings
       ───────────────────────────────────────── */

    // Open Sign In modal
    document.getElementById('btn-signin')?.addEventListener('click', (e) => {
        e.preventDefault();
        clearError('signin-error');
        openModal('modal-signin');
    });

    // Open Sign Up modal
    document.getElementById('btn-signup')?.addEventListener('click', (e) => {
        e.preventDefault();
        clearError('signup-error');
        openModal('modal-signup');
    });

    // Close Sign In modal (× button)
    document.getElementById('modal-signin-close')?.addEventListener('click', () => closeModal('modal-signin'));

    // Close Sign Up modal (× button)
    document.getElementById('modal-signup-close')?.addEventListener('click', () => closeModal('modal-signup'));

    // Close on backdrop click
    document.getElementById('modal-signin-backdrop')?.addEventListener('click', () => closeModal('modal-signin'));
    document.getElementById('modal-signup-backdrop')?.addEventListener('click', () => closeModal('modal-signup'));

    // ESC key closes any open modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAllModals();
    });

    // Switch: Sign In → Sign Up
    document.getElementById('switch-to-signup')?.addEventListener('click', () => {
        closeModal('modal-signin');
        clearError('signup-error');
        openModal('modal-signup');
    });

    // Switch: Sign Up → Sign In
    document.getElementById('switch-to-signin')?.addEventListener('click', () => {
        closeModal('modal-signup');
        clearError('signin-error');
        openModal('modal-signin');
    });

    // Log out
    document.getElementById('btn-logout')?.addEventListener('click', handleLogout);

    /* ─────────────────────────────────────────
       8. Auth — Form submission
       ───────────────────────────────────────── */
    document.getElementById('form-signin')?.addEventListener('submit', handleSignIn);
    document.getElementById('form-signup')?.addEventListener('submit', handleSignUp);

    /* ─────────────────────────────────────────
       9. Password visibility toggles
       ───────────────────────────────────────── */
    initPasswordToggles();

    /* ─────────────────────────────────────────
       10. Initial auth state check on page load
       ───────────────────────────────────────── */
    checkAuthState();

});
