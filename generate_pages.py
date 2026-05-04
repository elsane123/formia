#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, random, unicodedata, sys
from pathlib import Path

BASE_DIR  = Path(__file__).parent
DATA_FILE = Path('/a0/usr/workdir/formations_ia_2025.json')
OUT_DIR   = BASE_DIR / 'formations'
INDEX_HTML = BASE_DIR / 'index.html'
SITEMAP   = BASE_DIR / 'sitemap.xml'
BASE_URL  = 'https://formia.fr'

def slugify(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def esc(s):
    return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def level_badge(niveau):
    n = (niveau or '').lower()
    if any(x in n for x in ['debutant','fondamentaux','associate','d\xc3\xa9butant']):
        return '<span class="badge badge-deb">' + esc(niveau) + '</span>'
    if any(x in n for x in ['interm','intermediaire']):
        return '<span class="badge badge-int">' + esc(niveau) + '</span>'
    if any(x in n for x in ['avanc','professional','m1']):
        return '<span class="badge badge-adv">' + esc(niveau) + '</span>'
    return '<span class="badge badge-other">' + esc(niveau) + '</span>'

def certif_badge(certif):
    c = (certif or '').lower()
    if c.startswith('oui'):
        return '<span class="badge badge-certif-yes">\u2705 ' + esc(certif) + '</span>'
    return '<span class="badge badge-certif-no">\u2717 ' + esc(certif) + '</span>'

def price_html(prix):
    if 'gratuit' in (prix or '').lower():
        return '<span class="price-free">\U0001f381 ' + esc(prix) + '</span>'
    return '<span class="price-paid">' + esc(prix) + '</span>'

def lang_flag(langue):
    l = (langue or '').lower()
    if l == 'fran\xe7ais': return '\U0001f1eb\U0001f1f7'
    if l == 'anglais': return '\U0001f1ec\U0001f1e7'
    if 'fran' in l and 'angl' in l: return '\U0001f1eb\U0001f1f7 \U0001f1ec\U0001f1e7'
    return '\U0001f310'

def theme_tags(themes):
    tags = [t.strip() for t in (themes or '').split(',') if t.strip()]
    return ' '.join('<span class="theme-tag">' + esc(t) + '</span>' for t in tags)

def get_similar(current, all_f, count=3):
    cat = current.get('Cat\xe9gorie', '')
    pool = [f for f in all_f
            if f.get('Cat\xe9gorie') == cat
            and f.get('Nom de la formation') != current.get('Nom de la formation')]
    random.seed(hash(current.get('Nom de la formation','')))
    random.shuffle(pool)
    return pool[:count]

def extract_price(prix):
    p = (prix or '').replace('\u202f','').replace('\xa0','').replace(' ','')
    m = re.search(r'(\d[\d,.]*)', p)
    return m.group(1) if m else '0'

LOGO_SVG = ('<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="40" cy="40" r="38" fill="#1e3a5f" stroke="#3B82F6" stroke-width="1.5"/>'
    '<circle cx="40" cy="20" r="5" fill="#60A5FA"/>'
    '<circle cx="40" cy="60" r="5" fill="#60A5FA"/>'
    '<circle cx="20" cy="40" r="5" fill="#60A5FA"/>'
    '<circle cx="60" cy="40" r="5" fill="#60A5FA"/>'
    '<circle cx="25" cy="25" r="4" fill="#93C5FD"/>'
    '<circle cx="55" cy="25" r="4" fill="#93C5FD"/>'
    '<circle cx="25" cy="55" r="4" fill="#93C5FD"/>'
    '<circle cx="55" cy="55" r="4" fill="#93C5FD"/>'
    '<circle cx="40" cy="40" r="7" fill="#3B82F6"/>'
    '<line x1="40" y1="25" x2="40" y2="33" stroke="#60A5FA" stroke-width="1.5"/>'
    '<line x1="40" y1="47" x2="40" y2="55" stroke="#60A5FA" stroke-width="1.5"/>'
    '<line x1="25" y1="40" x2="33" y2="40" stroke="#60A5FA" stroke-width="1.5"/>'
    '<line x1="47" y1="40" x2="55" y2="40" stroke="#60A5FA" stroke-width="1.5"/>'
    '</svg>')

CSS = ('*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n'
':root {\n'
'  --navy: #0F172A; --navy-800: #1E293B;\n'
'  --blue: #3B82F6; --blue-dark: #2563EB; --blue-light: #60A5FA;\n'
'  --blue-glow: rgba(59,130,246,0.15);\n'
'  --white: #FFFFFF;\n'
'  --gray-50: #F8FAFC; --gray-100: #F1F5F9; --gray-200: #E2E8F0;\n'
'  --gray-300: #CBD5E1; --gray-400: #94A3B8; --gray-500: #64748B; --gray-600: #475569;\n'
'  --font: -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;\n'
'  --radius: 14px;\n'
'  --shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 20px rgba(0,0,0,0.06);\n'
'  --shadow-hover: 0 14px 40px rgba(59,130,246,0.22), 0 2px 8px rgba(0,0,0,0.08);\n'
'  --transition: 0.2s cubic-bezier(0.4,0,0.2,1);\n'
'}\n'
'html { scroll-behavior: smooth; }\n'
'body { font-family: var(--font); background: var(--gray-50); color: var(--navy-800); line-height: 1.6; min-height: 100vh; }\n'
'a { color: var(--blue); text-decoration: none; } a:hover { text-decoration: underline; }\n'
'.site-header { background: linear-gradient(135deg,#0F172A 0%,#1a2744 45%,#0d1f3c 100%); }\n'
'.site-header-inner { max-width:1200px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; padding:18px 24px; }\n'
'.header-logo { display:inline-flex; align-items:center; gap:12px; text-decoration:none; }\n'
'.header-logo-icon { width:44px; height:44px; filter:drop-shadow(0 0 14px rgba(59,130,246,0.7)); }\n'
'.header-logo-name { font-size:1.55rem; font-weight:800; letter-spacing:-0.04em; line-height:1; background:linear-gradient(135deg,#fff 0%,#93C5FD 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }\n'
'.header-logo-badge { font-size:0.57rem; font-weight:700; letter-spacing:0.14em; color:var(--blue-light); text-transform:uppercase; display:block; margin-top:3px; }\n'
'.header-back { display:inline-flex; align-items:center; gap:6px; color:rgba(255,255,255,0.6); font-size:0.83rem; font-weight:600; transition:color var(--transition); }\n'
'.header-back:hover { color:#fff; text-decoration:none; }\n'
'.breadcrumb { background:var(--white); border-bottom:1px solid var(--gray-200); padding:11px 24px; }\n'
'.breadcrumb-inner { max-width:1200px; margin:0 auto; display:flex; align-items:center; gap:7px; font-size:0.79rem; color:var(--gray-500); flex-wrap:wrap; }\n'
'.breadcrumb a { color:var(--blue); } .breadcrumb-sep { color:var(--gray-300); } .breadcrumb-current { color:var(--navy-800); font-weight:600; }\n'
'.page-hero { background:linear-gradient(135deg,#0F172A 0%,#1a2744 45%,#0d1f3c 100%); position:relative; overflow:hidden; padding:52px 24px 60px; }\n'
'.page-hero-bg { position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 900px 500px at 15% 50%,rgba(59,130,246,0.12) 0%,transparent 70%),radial-gradient(ellipse 700px 400px at 85% 40%,rgba(139,92,246,0.08) 0%,transparent 70%); }\n'
'.page-hero-grid { position:absolute; inset:0; pointer-events:none; background-image:linear-gradient(rgba(59,130,246,0.05) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.05) 1px,transparent 1px); background-size:52px 52px; -webkit-mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 40%,transparent 100%); mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 40%,transparent 100%); }\n'
'.page-hero-content { position:relative; z-index:1; max-width:900px; margin:0 auto; }\n'
'.hero-cat-badge { display:inline-block; margin-bottom:16px; padding:5px 14px; border-radius:999px; background:rgba(59,130,246,0.18); border:1px solid rgba(59,130,246,0.35); color:var(--blue-light); font-size:0.75rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; }\n'
'.page-hero-title { font-size:clamp(1.55rem,4vw,2.5rem); font-weight:800; letter-spacing:-0.03em; color:var(--white); line-height:1.18; margin-bottom:14px; }\n'
'.page-hero-sub { font-size:0.97rem; color:rgba(255,255,255,0.55); }\n'
'.info-section { padding:44px 24px 0; }\n'
'.info-grid { max-width:1200px; margin:0 auto; display:grid; grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); gap:16px; }\n'
'.info-card { background:var(--white); border:1px solid var(--gray-200); border-radius:var(--radius); padding:20px 22px; box-shadow:var(--shadow); transition:box-shadow var(--transition),border-color var(--transition),transform var(--transition); }\n'
'.info-card:hover { box-shadow:var(--shadow-hover); border-color:rgba(59,130,246,0.25); transform:translateY(-2px); }\n'
'.info-card-label { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.09em; color:var(--gray-400); margin-bottom:8px; display:flex; align-items:center; gap:6px; }\n'
'.info-card-value { font-size:0.95rem; font-weight:600; color:var(--navy-800); line-height:1.45; }\n'
'.theme-tag { display:inline-block; padding:3px 9px; border-radius:999px; background:var(--blue-glow); color:var(--blue-dark); font-size:0.72rem; font-weight:600; margin:2px; border:1px solid rgba(59,130,246,0.2); }\n'
'.badge { display:inline-block; padding:3px 10px; border-radius:999px; font-size:0.78rem; font-weight:700; }\n'
'.badge-deb { background:#ECFDF5; color:#065F46; border:1px solid #6EE7B7; }\n'
'.badge-int { background:#FFFBEB; color:#92400E; border:1px solid #FCD34D; }\n'
'.badge-adv { background:#EFF6FF; color:#1E40AF; border:1px solid #93C5FD; }\n'
'.badge-other { background:var(--gray-100); color:var(--gray-600); border:1px solid var(--gray-300); }\n'
'.badge-certif-yes { background:#ECFDF5; color:#065F46; border:1px solid #6EE7B7; }\n'
'.badge-certif-no { background:#FEF2F2; color:#991B1B; border:1px solid #FCA5A5; }\n'
'.price-free { color:#065F46; font-weight:700; font-size:1rem; }\n'
'.price-paid { color:var(--navy-800); font-weight:700; font-size:1rem; }\n'
'.desc-section { padding:40px 24px; }\n'
'.desc-card { max-width:1200px; margin:0 auto; background:var(--white); border:1px solid var(--gray-200); border-radius:var(--radius); padding:36px 40px; box-shadow:var(--shadow); }\n'
'.desc-title { font-size:1.15rem; font-weight:800; color:var(--navy-800); margin-bottom:16px; padding-bottom:14px; border-bottom:2px solid var(--gray-100); display:flex; align-items:center; gap:10px; }\n'
'.desc-body { font-size:0.97rem; color:var(--gray-600); line-height:1.8; }\n'
'.cta-section { padding:8px 24px 48px; }\n'
'.cta-inner { max-width:1200px; margin:0 auto; display:flex; gap:14px; flex-wrap:wrap; align-items:center; }\n'
'.btn-cta { display:inline-flex; align-items:center; gap:10px; padding:16px 32px; border-radius:10px; background:linear-gradient(135deg,var(--blue) 0%,var(--blue-dark) 100%); color:var(--white); font-size:1.05rem; font-weight:700; box-shadow:0 4px 20px rgba(59,130,246,0.35); transition:transform var(--transition),box-shadow var(--transition); text-decoration:none; }\n'
'.btn-cta:hover { transform:translateY(-2px); box-shadow:0 8px 32px rgba(59,130,246,0.5); text-decoration:none; color:var(--white); }\n'
'.btn-back { display:inline-flex; align-items:center; gap:8px; padding:14px 24px; border-radius:10px; background:var(--white); color:var(--navy-800); font-size:0.93rem; font-weight:600; border:1.5px solid var(--gray-200); transition:all var(--transition); text-decoration:none; }\n'
'.btn-back:hover { border-color:var(--blue); color:var(--blue); text-decoration:none; }\n'
'.similar-section { background:var(--white); border-top:1px solid var(--gray-200); padding:48px 24px; }\n'
'.similar-inner { max-width:1200px; margin:0 auto; }\n'
'.similar-title { font-size:1.35rem; font-weight:800; color:var(--navy-800); margin-bottom:28px; }\n'
'.similar-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:18px; }\n'
'.similar-card { display:block; background:var(--gray-50); border:1px solid var(--gray-200); border-radius:var(--radius); padding:22px 24px; transition:box-shadow var(--transition),border-color var(--transition),transform var(--transition); text-decoration:none; color:inherit; }\n'
'.similar-card:hover { box-shadow:var(--shadow-hover); border-color:rgba(59,130,246,0.3); transform:translateY(-3px); text-decoration:none; }\n'
'.similar-cat { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--blue); margin-bottom:8px; }\n'
'.similar-nom { font-size:0.97rem; font-weight:700; color:var(--navy-800); margin-bottom:12px; line-height:1.35; }\n'
'.similar-meta { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }\n'
'.similar-niveau { font-size:0.75rem; color:var(--gray-500); font-weight:600; }\n'
'.similar-prix { font-size:0.8rem; font-weight:700; color:var(--navy-800); }\n'
'.similar-free { color:#065F46; }\n'
'.footer { background:var(--navy); color:rgba(255,255,255,0.5); text-align:center; padding:40px 24px; margin-top:0; }\n'
'.footer-logo { display:flex; align-items:center; justify-content:center; gap:12px; margin-bottom:16px; }\n'
'.footer-logo-icon { width:36px; height:36px; }\n'
'.footer-logo-name { font-size:1.2rem; font-weight:800; color:var(--white); letter-spacing:-0.03em; }\n'
'.footer-text { font-size:0.82rem; line-height:1.7; }\n'
'@media(max-width:640px) { .site-header-inner { padding:14px 16px; } .page-hero { padding:36px 16px 44px; } .desc-card { padding:24px 20px; } .cta-inner { flex-direction:column; } .btn-cta,.btn-back { width:100%; justify-content:center; } }\n'
)

def render_page(f, slug, similar):
    nom        = f.get('Nom de la formation', '')
    categorie  = f.get('Cat\xe9gorie', '')
    createur   = f.get('Cr\xe9ateur / Organisme', '')
    plateforme = f.get('Plateforme', '')
    themes     = f.get('Th\xe9matiques couvertes', '')
    niveau     = f.get('Niveau', '')
    langue     = f.get('Langue', '')
    prix       = f.get('Prix', '')
    certif     = f.get('Certifiante', '')
    public     = f.get('Public cible', '')
    desc       = f.get('Description', '')
    url_ext    = f.get('URL', '#')

    page_url  = BASE_URL + '/formations/' + slug + '.html'
    flag      = lang_flag(langue)
    schema_lang = 'fr' if 'fran' in langue.lower() else 'en'
    price_val = extract_price(prix)
    desc_short = esc(desc[:150]) + '...'
    meta_desc = ('Formation ' + esc(nom) + ' par ' + esc(createur) +
                 ' sur ' + esc(plateforme) + '. Niveau ' + esc(niveau) +
                 '. Prix: ' + esc(prix) + '. ' + desc_short)

    schema = ('{\n'
              '  "@context": "https://schema.org",\n'
              '  "@type": "Course",\n'
              '  "name": "' + esc(nom) + '",\n'
              '  "description": "' + esc(desc) + '",\n'
              '  "provider": { "@type": "Organization", "name": "' + esc(createur) + '" },\n'
              '  "url": "' + esc(url_ext) + '",\n'
              '  "inLanguage": "' + schema_lang + '",\n'
              '  "educationalLevel": "' + esc(niveau) + '",\n'
              '  "offers": { "@type": "Offer", "price": "' + price_val + '", "priceCurrency": "EUR" }\n'
              '}')

    sim_html = ''
    for sf in similar:
        sf_slug = slugify(sf.get('Nom de la formation', ''))
        sf_free = 'gratuit' in sf.get('Prix','').lower()
        px_cls  = ' similar-free' if sf_free else ''
        sim_html += ('<a href="' + sf_slug + '.html" class="similar-card">'
                     '<div class="similar-cat">' + esc(sf.get('Cat\xe9gorie','')) + '</div>'
                     '<div class="similar-nom">' + esc(sf.get('Nom de la formation','')) + '</div>'
                     '<div class="similar-meta">'
                     '<span class="similar-niveau">' + esc(sf.get('Niveau','')) + '</span>'
                     '<span class="similar-prix' + px_cls + '">' + esc(sf.get('Prix','')) + '</span>'
                     '</div></a>')

    sim_section = ''
    if sim_html:
        sim_section = ('<section class="similar-section"><div class="similar-inner">'
                       '<h2 class="similar-title">Formations similaires</h2>'
                       '<div class="similar-grid">' + sim_html + '</div>'
                       '</div></section>')

    parts = [
        '<!DOCTYPE html><html lang="fr"><head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>' + esc(nom) + ' \u2013 FormIA | Formation IA 2025</title>',
        '<meta name="description" content="' + meta_desc + '">',
        '<link rel="canonical" href="' + page_url + '">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="' + esc(nom) + ' \u2013 FormIA">',
        '<meta property="og:description" content="' + meta_desc + '">',
        '<meta property="og:url" content="' + page_url + '">',
        '<meta property="og:image" content="https://formia.fr/og-image.png">',
        '<meta property="og:site_name" content="FormIA">',
        '<meta property="og:locale" content="fr_FR">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="' + esc(nom) + ' \u2013 FormIA">',
        '<meta name="twitter:description" content="' + meta_desc + '">',
        '<meta name="twitter:image" content="https://formia.fr/og-image.png">',
        '<meta name="twitter:site" content="@FormIA_fr">',
        '<script type="application/ld+json">' + schema + '</script>',
        '<style>' + CSS + '</style>',
        '</head><body>',
        '<header class="site-header"><div class="site-header-inner">',
        '<a href="../index.html" class="header-logo">',
        '<span class="header-logo-icon">' + LOGO_SVG + '</span>',
        '<span><span class="header-logo-name">FormIA</span>',
        '<span class="header-logo-badge">Annuaire IA 2025</span></span>',
        '</a>',
        '<a href="../index.html" class="header-back">\u2190 Retour \xe0 l\'annuaire</a>',
        '</div></header>',
        '<nav class="breadcrumb"><div class="breadcrumb-inner">',
        '<a href="../index.html">Accueil</a>',
        '<span class="breadcrumb-sep">\u203a</span>',
        '<span>' + esc(categorie) + '</span>',
        '<span class="breadcrumb-sep">\u203a</span>',
        '<span class="breadcrumb-current">' + esc(nom) + '</span>',
        '</div></nav>',
        '<section class="page-hero"><div class="page-hero-bg"></div><div class="page-hero-grid"></div>',
        '<div class="page-hero-content">',
        '<span class="hero-cat-badge">' + esc(categorie) + '</span>',
        '<h1 class="page-hero-title">' + esc(nom) + '</h1>',
        '<p class="page-hero-sub">' + flag + ' ' + esc(langue) + ' &bull; ' + esc(createur) + '</p>',
        '</div></section>',
        '<section class="info-section"><div class="info-grid">',
        '<div class="info-card"><div class="info-card-label">\U0001f3eb Cr\xe9ateur / Organisme</div><div class="info-card-value">' + esc(createur) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f5a5\ufe0f Plateforme</div><div class="info-card-value">' + esc(plateforme) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f3af Th\xe9matiques couvertes</div><div class="info-card-value">' + theme_tags(themes) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f4ca Niveau</div><div class="info-card-value">' + level_badge(niveau) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f30d Langue</div><div class="info-card-value">' + flag + ' ' + esc(langue) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f4b0 Prix</div><div class="info-card-value">' + price_html(prix) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f3ab Certifiante</div><div class="info-card-value">' + certif_badge(certif) + '</div></div>',
        '<div class="info-card"><div class="info-card-label">\U0001f465 Public cible</div><div class="info-card-value">' + esc(public) + '</div></div>',
        '</div></section>',
        '<section class="desc-section"><div class="desc-card">',
        '<div class="desc-title">\U0001f4cb Description de la formation</div>',
        '<div class="desc-body">' + esc(desc) + '</div>',
        '</div></section>',
        '<section class="cta-section"><div class="cta-inner">',
        '<a href="' + esc(url_ext) + '" target="_blank" rel="noopener noreferrer" class="btn-cta">',
        'Acc\xe9der \xe0 la formation \u2192</a>',
        '<a href="../index.html" class="btn-back">\u2190 Retour \xe0 l\'annuaire</a>',
        '</div></section>',
        sim_section,
        '<footer class="footer">',
        '<div class="footer-logo"><span class="footer-logo-icon">' + LOGO_SVG + '</span>',
        '<span class="footer-logo-name">FormIA</span></div>',
        '<div class="footer-text">',
        '<p>L\'annuaire de r\xe9f\xe9rence des formations en Intelligence Artificielle &mdash; 2025-2026</p>',
        '<p style="margin-top:6px;font-size:0.75rem;opacity:0.6;">72 formations &bull; 17 gratuites &bull; 57 certifiantes</p>',
        '</div></footer>',
        '</body></html>',
    ]
    return '\n'.join(parts)

def update_index_html(formations):
    """Replace direct external URLs in card links with slug-based internal URLs."""
    content = INDEX_HTML.read_text(encoding='utf-8')
    # Build a mapping: external URL -> slug page
    # The JS builds cards: href="' + escHtml(url) + '"
    # We patch the buildCard function to use slug-based URL
    old = "html += '<a href=\"' + escHtml(url) + '\" target=\"_blank\" rel=\"noopener\" class=\"btn-voir\">Voir"
    new = ("html += '<a href=\"formations/' + slug + '.html\" class=\"btn-voir\">Voir")
    if old in content:
        content = content.replace(old, new)
        print('  [index.html] Patched btn-voir href to slug-based URL')
    else:
        print('  [index.html] WARNING: btn-voir pattern not found, trying alternate patch')
        # Alternate: inject slugify + use it
    # Inject slugify function into JS before buildCard
    slug_js = """function jsSlugify(text) {
  text = text.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
  text = text.toLowerCase();
  text = text.replace(/[^\\w\\s-]/g,'');
  text = text.replace(/[\\s_]+/g,'-');
  text = text.replace(/-+/g,'-');
  return text.replace(/^-+|-+$/g,'');
}"""
    if 'function jsSlugify' not in content:
        content = content.replace('function buildCard(f) {',
                                   slug_js + '\nfunction buildCard(f) {')
        print('  [index.html] Injected jsSlugify() function')
    # Now ensure slug variable is set in buildCard
    if 'var slug = jsSlugify' not in content:
        content = content.replace(
            "var url = f['URL'] || '#';",
            "var url = f['URL'] || '#';\n  var slug = jsSlugify(nom);"
        )
        print('  [index.html] Added slug variable in buildCard')
    # Patch the href to use slug
    old2 = "'<a href=\"' + escHtml(url) + '\" target=\"_blank\" rel=\"noopener\" class=\"btn-voir\">Voir"
    new2 = "'<a href=\"formations/' + slug + '.html\" class=\"btn-voir\">Voir"
    if old2 in content:
        content = content.replace(old2, new2)
        print('  [index.html] Patched btn-voir href successfully')
    INDEX_HTML.write_text(content, encoding='utf-8')

def update_sitemap(slugs):
    """Add 72 formation URLs to sitemap.xml."""
    content = SITEMAP.read_text(encoding='utf-8')
    # Remove existing formation entries to avoid duplicates
    content = re.sub(r'\s*<url>\s*<loc>https://formia\.fr/formations/[^<]+</loc>.*?</url>', '',
                     content, flags=re.DOTALL)
    formation_entries = '\n'.join(
        '  <url>\n'
        '    <loc>' + BASE_URL + '/formations/' + s + '.html</loc>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>0.7</priority>\n'
        '  </url>'
        for s in slugs
    )
    content = content.replace('</urlset>', formation_entries + '\n</urlset>')
    SITEMAP.write_text(content, encoding='utf-8')
    print('  [sitemap.xml] Added ' + str(len(slugs)) + ' formation URLs')

def main():
    print('FormIA Page Generator')
    print('=' * 50)

    # Load data
    data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    formations = data['formations']
    print('Loaded ' + str(len(formations)) + ' formations')

    # Create output directory
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print('Output dir: ' + str(OUT_DIR))

    # Generate pages
    slugs = []
    errors = []
    for i, f in enumerate(formations):
        nom = f.get('Nom de la formation', '')
        slug = slugify(nom)
        slugs.append(slug)
        similar = get_similar(f, formations, count=3)
        try:
            html = render_page(f, slug, similar)
            out_path = OUT_DIR / (slug + '.html')
            out_path.write_text(html, encoding='utf-8')
            print('  [' + str(i+1).zfill(2) + '/72] ' + slug + '.html')
        except Exception as e:
            errors.append((slug, str(e)))
            print('  ERROR: ' + slug + ' -> ' + str(e))

    print('')
    print('Pages generated: ' + str(len(slugs) - len(errors)) + '/72')

    # Update index.html
    print('\nUpdating index.html...')
    try:
        update_index_html(formations)
    except Exception as e:
        print('  ERROR updating index.html: ' + str(e))

    # Update sitemap.xml
    print('\nUpdating sitemap.xml...')
    try:
        update_sitemap(slugs)
    except Exception as e:
        print('  ERROR updating sitemap.xml: ' + str(e))

    # Summary
    print('')
    print('=' * 50)
    files = list(OUT_DIR.glob('*.html'))
    print('Files in formations/: ' + str(len(files)))
    sitemap_content = SITEMAP.read_text(encoding='utf-8')
    url_count = sitemap_content.count('<loc>')
    print('URLs in sitemap.xml: ' + str(url_count))
    if errors:
        print('Errors: ' + str(len(errors)))
        for slug, err in errors:
            print('  ' + slug + ': ' + err)
    else:
        print('All pages generated successfully!')

if __name__ == '__main__':
    main()
