"""Turn a wget mirror of the live WordPress site into the static backup.

Adds a banner to every page saying it is a backup with a link to the live site, points search engines at the
live site (canonical + noindex) so the backup never competes with it, and removes leftover WordPress-only links.
Usage: python3 make_static.py <mirror_dir> <live_url>
"""
import os, re, sys

root, live = sys.argv[1], sys.argv[2].rstrip('/')
BANNER = (
    '<div id="backup-banner" role="note" style="position:sticky;top:0;z-index:99999;background:#6AA821;color:#fff;'
    'font:600 15px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;text-align:center;padding:10px 16px">'
    'You are viewing a static backup of this site, saved {date}. Forms, search and live content may not work. '
    '<a href="{live}{path}" style="color:#fff;text-decoration:underline">Go to the live site at DannoPeters.ca &rarr;</a></div>'
)
date = os.environ.get('BACKUP_DATE', '')
n = 0
for dirpath, _, files in os.walk(root):
    for f in files:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dirpath, f)
        html = open(p, encoding='utf-8', errors='replace').read()
        if 'id="backup-banner"' in html:
            continue
        rel = '/' + os.path.relpath(p, root).replace(os.sep, '/')
        path = re.sub(r'index\.html$', '', rel)
        head = (f'<link rel="canonical" href="{live}{path}">'
                '<meta name="robots" content="noindex, follow">')
        html = re.sub(r'<link rel=["\']canonical["\'][^>]*>', '', html, flags=re.I)
        html = re.sub(r'<meta name=["\']robots["\'][^>]*>', '', html, flags=re.I)
        html = re.sub(r'(<head[^>]*>)', r'\1' + head, html, count=1, flags=re.I)
        html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + BANNER.format(date=date, live=live, path=path), html, count=1, flags=re.I)
        open(p, 'w', encoding='utf-8').write(html)
        n += 1
print('pages updated:', n)
