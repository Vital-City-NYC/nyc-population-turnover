#!/usr/bin/env python3
"""Inline docs/data.json into build/template.html and write docs/index.html (one self-contained
file that can be pasted whole into a Ghost HTML card), and render METHODOLOGY.md as
docs/methodology.html with a small purpose-built Markdown converter (headings, paragraphs,
bullet and numbered lists, pipe tables, fenced code, inline code, bold, links)."""
import html, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
data = open(os.path.join(ROOT, 'docs', 'data.json')).read()
tpl = open(os.path.join(ROOT, 'build', 'template.html')).read()
assert tpl.count('/*DATA*/') == 1
out = tpl.replace('/*DATA*/', data)
open(os.path.join(ROOT, 'docs', 'index.html'), 'w').write(out)
print('wrote docs/index.html', len(out), 'bytes')

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s
md = open(os.path.join(ROOT, 'METHODOLOGY.md')).read().splitlines()
body = []; i = 0; para = []
def flush():
    global para
    if para: body.append('<p>' + inline(' '.join(para)) + '</p>'); para = []
while i < len(md):
    line = md[i]
    if line.startswith('```'):
        flush(); j = i + 1; code = []
        while not md[j].startswith('```'): code.append(md[j]); j += 1
        body.append('<pre>' + html.escape('\n'.join(code)) + '</pre>'); i = j + 1; continue
    if line.startswith('|'):
        flush(); rows = []
        while i < len(md) and md[i].startswith('|'):
            if not re.match(r'^\|[\s\-|]+\|$', md[i]): rows.append([c.strip() for c in md[i].strip('|').split('|')])
            i += 1
        t = '<div class="twrap"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
        for r in rows[1:]: t += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
        body.append(t + '</tbody></table></div>'); continue
    m = re.match(r'^(#{1,3}) (.*)', line)
    if m: flush(); body.append(f'<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>'); i += 1; continue
    if re.match(r'^- ', line):
        flush(); items = []
        while i < len(md) and re.match(r'^- ', md[i]): items.append(md[i][2:]); i += 1
        body.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>'); continue
    if re.match(r'^\d+\. ', line):
        flush(); items = []
        while i < len(md) and re.match(r'^\d+\. ', md[i]): items.append(re.sub(r'^\d+\. ', '', md[i])); i += 1
        body.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ol>'); continue
    if not line.strip(): flush(); i += 1; continue
    para.append(line); i += 1
flush()
page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Methodology: New York City's population since 1970</title>
<link rel="stylesheet" href="https://use.typekit.net/qqk2vto.css">
<style>
body{margin:0;background:#fff;color:#050507;font-family:"halyard-text","Inter","Helvetica Neue",Arial,sans-serif;font-weight:300;line-height:1.5}
main{max-width:760px;margin:0 auto;padding:24px 16px 48px}
a.back{font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#707175;text-decoration:none}
h1{font-weight:900;font-size:1.7rem;line-height:1.15;margin:.6rem 0 1rem}
h2{font-weight:900;font-size:1.2rem;margin:2rem 0 .5rem;border-top:2px solid #050507;padding-top:.8rem}
h3{font-weight:700;font-size:1rem;margin:1.3rem 0 .3rem}
p,li{font-size:.95rem}
code{font-family:ui-monospace,Menlo,monospace;font-size:.82rem;background:#f7f7f4;padding:1px 4px}
pre{background:#f7f7f4;padding:.8rem 1rem;font-size:.82rem;overflow-x:auto}
.twrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.8rem;margin:.6rem 0}
th,td{padding:.45rem .5rem;border-bottom:1px solid #ddd;text-align:left;vertical-align:top;line-height:1.35}
th{background:#050507;color:#fff;font-weight:700}
th code{background:transparent;color:#fff}
a{color:#217ebe}
</style></head><body><main><a class="back" href="index.html">&larr; Back to the page</a>
''' + '\n'.join(body) + '\n</main></body></html>\n'
open(os.path.join(ROOT, 'docs', 'methodology.html'), 'w').write(page)
print('wrote docs/methodology.html', len(page), 'bytes')
