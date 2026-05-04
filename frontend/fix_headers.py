import os
import re

header_desktop_guest_user_menu = """      <!-- Desktop Auth Container -->
      <div class="hidden lg:flex items-center gap-3">
        <div class="flex items-center gap-3" id="auth-buttons-guest">
          <a href="https://t.me/CarDianAI_bot" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-[#229ED9] hover:bg-[#1a8bbf] hover:scale-105 transition-all duration-200 flex items-center gap-1.5">
            <i data-lucide="send" class="w-4 h-4"></i>Bot
          </a>
          <a href="#" id="btn-signin" class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors">Sign in</a>
          <a href="#" id="btn-signup" class="px-4 py-2 text-sm font-semibold text-white rounded-lg bg-[#ff9900] hover:scale-105 hover:shadow-lg hover:shadow-orange-200 transition-all duration-200 shadow-md shadow-orange-100">Sign up</a>
        </div>
        <div class="hidden items-center gap-2" id="auth-buttons-user">
          <button id="btn-topup" class="px-3 py-1.5 text-sm font-semibold text-[#ff9900] border border-[#ff9900] rounded-lg hover:bg-orange-50 transition-all duration-200 flex items-center gap-1.5">
            <i data-lucide="plus-circle" class="w-4 h-4"></i>Top Up
          </button>
          <span id="header-balance" class="text-sm font-bold text-gray-900 px-2">Tokens: —</span>
          <a href="https://t.me/CarDianAI_bot" target="_blank" rel="noopener noreferrer" id="btn-bot" class="px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-[#229ED9] hover:bg-[#1a8bbf] hover:scale-105 transition-all duration-200 flex items-center gap-1.5">
            <i data-lucide="send" class="w-4 h-4"></i>Bot
          </a>
          <a href="./profile.html" id="btn-dashboard" class="px-3 py-1.5 text-sm font-semibold text-white rounded-lg bg-[#ff9900] hover:scale-105 hover:shadow-lg hover:shadow-orange-200 transition-all duration-200 shadow-md shadow-orange-100 flex items-center gap-1.5">
            <i data-lucide="user-circle" class="w-4 h-4"></i>My Profile
          </a>
          <button id="btn-logout" class="p-2 text-gray-500 hover:text-red-600 border border-gray-200 rounded-lg hover:border-red-200 hover:bg-red-50 transition-all duration-200 flex items-center" aria-label="Log out">
            <i data-lucide="log-out" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
      <button id="menu-btn" class="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors" aria-label="Toggle menu" aria-expanded="false">
        <i data-lucide="menu" class="w-5 h-5"></i>
      </button>
    </nav>"""

header_mobile_menu = """    <div id="mobile-menu" class="hidden lg:hidden border-t border-gray-100 bg-white/95 backdrop-blur-md px-6 py-4 space-y-1">
      <a href="./manual_lookups.html" class="block text-sm font-medium text-gray-700 hover:text-[#ff9900] py-2.5 transition-colors">Manual</a>
      <a href="./parsed_lookups.html" class="block text-sm font-medium text-gray-700 hover:text-[#ff9900] py-2.5 transition-colors">Parse from URL</a>
      <a href="./watchlists.html" class="block text-sm font-medium text-gray-700 hover:text-[#ff9900] py-2.5 transition-colors">Watchlist</a>
      
      <!-- Mobile Auth Guest -->
      <div id="mobile-auth-guest" class="flex gap-3 pt-3 border-t border-gray-100 mt-3">
        <a href="#" id="btn-signin-mobile" class="flex-1 text-center px-4 py-2.5 text-sm font-medium border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">Sign in</a>
        <a href="#" id="btn-signup-mobile" class="flex-1 text-center px-4 py-2.5 text-sm font-semibold text-white rounded-lg bg-[#ff9900] hover:brightness-110 transition-all">Sign up</a>
      </div>
      
      <!-- Mobile Auth User -->
      <div id="mobile-auth-user" class="hidden flex-col gap-2 pt-3 border-t border-gray-100 mt-3">
        <div class="flex items-center justify-between px-2 mb-2">
           <span id="header-balance-mobile" class="text-sm font-bold text-gray-900">Tokens: —</span>
           <button id="btn-topup-mobile" class="text-sm font-semibold text-[#ff9900]">Top Up</button>
        </div>
        <a href="https://t.me/CarDianAI_bot" target="_blank" class="block text-center px-4 py-2.5 text-sm font-medium border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">Bot</a>
        <a href="./profile.html" class="block text-center px-4 py-2.5 text-sm font-semibold text-white rounded-lg bg-[#ff9900] transition-colors">My Profile</a>
        <button id="btn-logout-mobile" class="block w-full text-center px-4 py-2.5 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors">Log out</button>
      </div>
    </div>
  </header>"""

base_dir = r"\\wsl.localhost\Ubuntu\home\artem\projects\cardian\frontend"
modified = 0

for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            orig_content = content
            content = content.replace('<ul class="hidden md:flex', '<ul class="hidden lg:flex')
            content = re.sub(r'<!-- Desktop Auth Buttons -->.*?</nav>', header_desktop_guest_user_menu, content, flags=re.DOTALL|re.IGNORECASE)
            content = re.sub(r'<!-- Mobile Dropdown Menu -->.*?</header>', header_mobile_menu, content, flags=re.DOTALL|re.IGNORECASE)
            
            if content != orig_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                modified += 1
                print(f"Modified {f}")
print(f"Total modified: {modified}")
