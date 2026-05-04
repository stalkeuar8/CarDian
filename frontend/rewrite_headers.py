import os
import re

# ─── Canonical header for pages linked from root (index, etc.) ──────────────
CANONICAL_HEADER = '''  <!-- ══════════════════════════════════════════
     NAVIGATION BAR — Sticky, backdrop blur
     ══════════════════════════════════════════ -->
  <header id="navbar">
    <nav class="navbar-inner">

      <!-- Brand -->
      <a href="./index.html" id="brand-logo" class="nav-brand">
        Cardian<span>.</span>
      </a>

      <!-- Desktop Links -->
      <ul class="nav-links-desktop">
        <li><a href="./manual_lookups.html" id="nav-manual" class="nav-link">Manual</a></li>
        <li><a href="./parsed_lookups.html" id="nav-parse" class="nav-link">Parse from URL</a></li>
        <li><a href="./watchlists.html" id="nav-watchlist" class="nav-link">Watchlist</a></li>
      </ul>

      <!-- Desktop Auth Area -->
      <div class="nav-auth-desktop">
        <!-- Guest state -->
        <div class="flex items-center gap-2" id="auth-buttons-guest">
          <a href="https://t.me/CarDianAI_bot" target="_blank" rel="noopener noreferrer"
             class="px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-[#229ED9] hover:bg-[#1a8bbf] transition-all duration-200 flex items-center gap-1.5">
            <i data-lucide="send" class="w-4 h-4"></i>Bot
          </a>
          <a href="#" id="btn-signin" class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors">Sign in</a>
          <a href="#" id="btn-signup" class="px-4 py-2 text-sm font-semibold text-white rounded-lg bg-[#ff9900] hover:brightness-110 transition-all shadow-md shadow-orange-100">Sign up</a>
        </div>
        <!-- Logged-in state -->
        <div class="hidden items-center gap-2" id="auth-buttons-user">
          <button id="btn-topup" class="px-3 py-1.5 text-sm font-semibold text-[#ff9900] border border-[#ff9900] rounded-lg hover:bg-orange-50 transition-all duration-200 flex items-center gap-1.5">
            <i data-lucide="plus-circle" class="w-4 h-4"></i>Top Up
          </button>
          <span id="header-balance" class="text-sm font-bold text-gray-900 px-2">Tokens: —</span>
          <a href="https://t.me/CarDianAI_bot" target="_blank" rel="noopener noreferrer" id="btn-bot"
             class="px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-[#229ED9] hover:bg-[#1a8bbf] transition-all duration-200 flex items-center gap-1.5">
            <i data-lucide="send" class="w-4 h-4"></i>Bot
          </a>
          <a href="./profile.html" id="btn-dashboard"
             class="px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-[#ff9900] hover:brightness-110 transition-all shadow-md shadow-orange-100 flex items-center gap-1.5">
            <i data-lucide="user-circle" class="w-4 h-4"></i>My Profile
          </a>
          <button id="btn-logout" class="p-2 text-gray-500 hover:text-red-600 border border-gray-200 rounded-lg hover:border-red-200 hover:bg-red-50 transition-all duration-200 flex items-center" aria-label="Log out">
            <i data-lucide="log-out" class="w-4 h-4"></i>
          </button>
        </div>
      </div>

      <!-- Mobile right-side controls (always visible on mobile) -->
      <div class="nav-mobile-controls">
        <!-- Token count — shown when logged in (controlled by menu.js) -->
        <div id="mobile-token-badge">
          <i data-lucide="coins" class="w-3.5 h-3.5"></i>
          <span>—</span>
        </div>
        <!-- Profile icon — shown when logged in -->
        <a href="./profile.html" id="mobile-profile-btn" aria-label="My Profile">
          <i data-lucide="user-circle" class="w-4 h-4"></i>
        </a>
        <!-- Hamburger -->
        <button id="menu-btn" aria-label="Toggle menu" aria-expanded="false">
          <i data-lucide="menu" class="w-5 h-5"></i>
        </button>
      </div>

    </nav>

    <!-- Mobile Dropdown Menu -->
    <div id="mobile-menu" role="navigation" aria-label="Mobile navigation">

      <a href="./manual_lookups.html" class="mobile-nav-link">Manual</a>
      <a href="./parsed_lookups.html" class="mobile-nav-link">Parse from URL</a>
      <a href="./watchlists.html" class="mobile-nav-link">Watchlist</a>

      <div class="mobile-menu-divider"></div>

      <!-- Guest auth section -->
      <div id="mobile-auth-guest">
        <a href="#" id="btn-signin-mobile" class="mobile-guest-signin">Sign in</a>
        <a href="#" id="btn-signup-mobile" class="mobile-guest-signup">Sign up</a>
      </div>

      <!-- Logged-in auth section -->
      <div id="mobile-auth-user">
        <div class="mobile-user-row">
          <span id="header-balance-mobile" class="mobile-user-balance">Tokens: —</span>
          <button id="btn-topup-mobile" class="mobile-topup-btn">Top Up</button>
        </div>
        <a href="https://t.me/CarDianAI_bot" target="_blank" class="mobile-menu-btn mobile-btn-neutral">Bot</a>
        <a href="./profile.html" class="mobile-menu-btn mobile-btn-primary">My Profile</a>
        <button id="btn-logout-mobile" class="mobile-menu-btn mobile-btn-danger">Log out</button>
      </div>

    </div>
  </header>'''

# ─── CSS links to inject in <head> ──────────────────────────────────────────
CSS_LINKS_TO_ADD = '  <link rel="stylesheet" href="./css/header.css" />'
JS_LINKS_TO_ADD  = '  <script src="./js/menu.js"></script>'

BASE_DIR = r'\\wsl.localhost\Ubuntu\home\artem\projects\cardian\frontend'

# regex to match the entire old header block
HEADER_PATTERN = re.compile(
    r'<!--\s*[═\s]*NAVIGATION BAR.*?</header>',
    re.DOTALL | re.IGNORECASE
)

# Also catch headers that start directly with <header id="navbar"
HEADER_PATTERN2 = re.compile(
    r'<header id="navbar".*?</header>',
    re.DOTALL
)

SKIP_FILES = {'fix_headers.py', 'rewrite_headers.py'}

for root, dirs, files in os.walk(BASE_DIR):
    # don't recurse into subdirs other than root
    dirs.clear()
    for f in files:
        if not f.endswith('.html'):
            continue
        if f in SKIP_FILES:
            continue

        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()

        orig = content

        # 1. Insert header.css if not present
        if 'header.css' not in content:
            content = content.replace(
                '<link rel="stylesheet" href="./css/style.css" />',
                '<link rel="stylesheet" href="./css/style.css" />\n' + CSS_LINKS_TO_ADD
            )

        # 2. Replace old header HTML
        new_content, n1 = HEADER_PATTERN.subn(CANONICAL_HEADER, content)
        if n1 == 0:
            new_content, n2 = HEADER_PATTERN2.subn(CANONICAL_HEADER, content)
        else:
            n2 = 0

        content = new_content

        # 3. Insert menu.js before </body> if not present
        if 'menu.js' not in content:
            content = content.replace('</body>', JS_LINKS_TO_ADD + '\n</body>')

        if content != orig:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            print(f'  Updated: {f}  (header replaced: {n1+n2})')
        else:
            print(f'  Skipped: {f}  (no changes needed)')
