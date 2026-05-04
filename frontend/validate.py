import os
base = r'\\wsl.localhost\Ubuntu\home\artem\projects\cardian\frontend'
files = [f for f in os.listdir(base) if f.endswith('.html')]
print(f"{'FILE':32s}  {'resp.css':9s}  {'menu.js':8s}  {'navbar':7s}  {'mob-badge':10s}  {'mob-auth':9s}")
all_ok = True
for f in sorted(files):
    path = os.path.join(base, f)
    content = open(path, encoding='utf-8').read()
    checks = [
        'responsive.css' in content,
        'menu.js' in content and 'src="./js/menu.js"' in content,
        'id="navbar"' in content,
        'mobile-token-badge' in content,
        'mobile-auth-guest' in content,
    ]
    row = '  '.join(['OK ' if c else 'MISSING' for c in checks])
    if not all(checks):
        all_ok = False
    print(f"{f:32s}  {row}")
print()
print('ALL OK' if all_ok else 'ISSUES FOUND')
