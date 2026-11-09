import os, sys
base = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend'
sys.path.insert(0, base)
from app.main import app

routes = []
for r in app.routes:
    methods = getattr(r, 'methods', None)
    path = getattr(r, 'path', None)
    name = getattr(r, 'name', None)
    if path:
        routes.append((path, ', '.join(methods or []), name or ''))

print(f"Total API Routes: {len(routes)}")
for p, m, n in sorted(routes):
    if any(k in p for k in ['invoice', 'bill', 'purchase', 'sale', 'payment', 'report', 'pdf', 'customer', 'seller', 'setting', 'exchange', 'gold', 'silver', 'stock']):
        print(f"  {m:10} {p:45} -> {n}")
