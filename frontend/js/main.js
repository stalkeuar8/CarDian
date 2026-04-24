/* ═══════════════════════════════════════════
   Cardian — main.js
   Lucide init · Mobile menu · Scroll effects
   Floating card animation management
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

});
