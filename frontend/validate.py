import os
base = r'\\wsl.localhost\Ubuntu\home\artem\projects\cardian\frontend'
files = [f for f in os.listdir(base) if f.endswith('.html')]
for f in sorted(files):
    path = os.path.join(base, f)
    content = open(path, encoding='utf-8').read()
    checks = {
        'header.css': 'header.css' in content,
        'menu.js':    'menu.js' in content,
        'navbar':     'id="navbar"' in content,
        'mob_token':  'mobile-token-badge' in content,
        'mob_auth':   'mobile-auth-guest' in content,
    }
    status = '  '.join(f'{k}={v}' for k,v in checks.items())
    print(f'{f:30s}  {status}')
