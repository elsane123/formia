#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, random, unicodedata, sys
from pathlib import Path

BASE_DIR  = Path(__file__).parent
DATA_FILE = Path('/a0/usr/workdir/formations_ia_2025.json')
OUT_DIR   = BASE_DIR / 'formations'
INDEX_HTML = BASE_DIR / 'index.html'
SITEMAP   = BASE_DIR / 'sitemap.xml'
BASE_URL  = 'https://academy.cyberquantic.com'

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

LOGO_SVG = (
    '<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">''<circle cx="40" cy="40" r="36" fill="#e8f0fe" stroke="#0066CC" stroke-width="1.5"/>''<circle cx="28" cy="30" r="15" fill="none" stroke="#0066CC" stroke-width="2" opacity="0.65"/>''<circle cx="52" cy="30" r="15" fill="none" stroke="#1a4fa8" stroke-width="2" opacity="0.65"/>''<circle cx="40" cy="47" r="15" fill="none" stroke="#0099ff" stroke-width="2" opacity="0.65"/>''<text x="40" y="38" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="800" fill="#0066CC">CQ</text>''</svg>')

CSS = (
'*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n'
':root {\n'
'  --bg-primary: #ffffff;\n'
'  --bg-secondary: #f4f6fb;\n'
'  --bg-card: #ffffff;\n'
'  --text-primary: #1B2B4B;\n'
'  --text-secondary: #4a5568;\n'
'  --accent: #0066CC;\n'
'  --accent-hover: #0052a3;\n'
'  --border: #e2e8f0;\n'
'  --shadow: 0 2px 12px rgba(0,0,0,0.08);\n'
'  --shadow-hover: 0 8px 32px rgba(0,102,204,0.16), 0 2px 8px rgba(0,0,0,0.08);\n'
'  --nav-bg: #ffffff;\n'
'  --hero-bg: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);\n'
'  --navy: #1B2B4B;\n'
'  --navy-800: #1B2B4B;\n'
'  --blue: #0066CC;\n'
'  --blue-dark: #0052a3;\n'
'  --blue-light: #4d94e0;\n'
'  --blue-glow: rgba(0,102,204,0.12);\n'
'  --white: #ffffff;\n'
'  --gray-50: #f4f6fb;\n'
'  --gray-100: #eef1f7;\n'
'  --gray-200: #e2e8f0;\n'
'  --gray-300: #cbd5e1;\n'
'  --gray-400: #94a3b8;\n'
'  --gray-500: #64748b;\n'
'  --gray-600: #475569;\n'
'  --gray-700: #334155;\n'
'  --green: #10B981; --green-bg: #ECFDF5; --green-text: #065F46;\n'
'  --orange: #F59E0B; --orange-bg: #FFFBEB; --orange-text: #92400E;\n'
'  --red: #EF4444; --red-bg: #FEF2F2; --red-text: #991B1B;\n'
"  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;\n"
'  --radius: 14px; --radius-sm: 8px;\n'
'  --transition: 0.2s cubic-bezier(0.4,0,0.2,1);\n'
'}\n'
'html { scroll-behavior: smooth; }\n'
'body { font-family: var(--font); background: var(--bg-secondary); color: var(--text-primary); line-height: 1.6; min-height: 100vh; }\n'
'\n'
'/* ===== SITE HEADER ===== */\n'
'.site-header {\n'
'  background: #ffffff;\n'
'  border-bottom: 1.5px solid var(--border);\n'
'  position: sticky; top: 0; z-index: 200;\n'
'  box-shadow: 0 1px 8px rgba(0,0,0,0.06);\n'
'}\n'
'.site-header-inner {\n'
'  max-width: 1200px; margin: 0 auto;\n'
'  display: flex; align-items: center; justify-content: space-between;\n'
'  padding: 0 24px; height: 64px;\n'
'}\n'
'.header-logo { display: inline-flex; align-items: center; gap: 10px; text-decoration: none; flex-shrink: 0; }\n'
'.header-logo-icon { width: 40px; height: 40px; flex-shrink: 0; }\n'
'.header-logo-text { display: inline-flex; align-items: baseline; gap: 0; line-height: 1; }\n'
'.header-logo-brand { font-size: 1.25rem; font-weight: 400; color: #1B2B4B; letter-spacing: -0.02em; }\n'
'.header-logo-brand strong { font-weight: 800; }\n'
'.header-logo-academy { font-size: 1.25rem; font-weight: 800; color: #0066CC; letter-spacing: -0.02em; }\n'
'.header-nav { display: flex; align-items: center; gap: 8px; }\n'
'.header-nav-link {\n'
'  color: #4a5568; font-size: 0.9rem; font-weight: 500;\n'
'  text-decoration: none; padding: 6px 14px; border-radius: 6px;\n'
'  transition: color var(--transition), background var(--transition);\n'
'}\n'
'.header-nav-link:hover { color: #0066CC; background: rgba(0,102,204,0.06); }\n'
'.header-nav-cta {\n'
'  display: inline-flex; align-items: center;\n'
'  padding: 8px 18px; border-radius: 8px;\n'
'  background: #0066CC; color: #ffffff;\n'
'  font-size: 0.88rem; font-weight: 700; text-decoration: none;\n'
'  transition: background var(--transition), box-shadow var(--transition);\n'
'  box-shadow: 0 2px 8px rgba(0,102,204,0.3);\n'
'}\n'
'.header-nav-cta:hover { background: #0052a3; box-shadow: 0 4px 16px rgba(0,102,204,0.4); }\n'
'.header-menu-btn {\n'
'  display: none; background: none; border: none; cursor: pointer;\n'
'  color: #1B2B4B; padding: 4px;\n'
'}\n'
'@media (max-width: 768px) {\n'
'  .header-nav { display: none; }\n'
'  .header-menu-btn { display: flex; }\n'
'}\n'
'\n'
'/* ===== HERO ===== */\n'
'.hero {\n'
'  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);\n'
'  position: relative; overflow: hidden;\n'
'  padding: 72px 24px 80px; text-align: center;\n'
'  border-bottom: 1px solid var(--border);\n'
'}\n'
'.hero-deco { position: absolute; inset: 0; pointer-events: none; }\n'
'.hero-hex {\n'
'  position: absolute; width: 320px; height: 320px;\n'
'  top: -60px; right: -60px; opacity: 0.6;\n'
'}\n'
'.hero-hex-2 {\n'
'  position: absolute; width: 200px; height: 200px;\n'
'  bottom: -40px; left: -40px; opacity: 0.4;\n'
'}\n'
'.hero-content { position: relative; z-index: 1; max-width: 760px; margin: 0 auto; }\n'
'.hero-badge {\n'
'  display: inline-block; margin-bottom: 20px;\n'
'  padding: 6px 16px; border-radius: 999px;\n'
'  background: rgba(0,102,204,0.1); border: 1px solid rgba(0,102,204,0.25);\n'
'  color: #0066CC; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;\n'
'}\n'
'.hero-title {\n'
'  font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 800;\n'
'  letter-spacing: -0.04em; line-height: 1.1;\n'
'  color: #1B2B4B; margin-bottom: 20px;\n'
'}\n'
'.hero-tagline {\n'
'  font-size: 1.1rem; color: #4a5568;\n'
'  line-height: 1.65; margin-bottom: 44px; font-weight: 400;\n'
'}\n'
'.hero-stats {\n'
'  display: flex; gap: 0; justify-content: center;\n'
'  background: #ffffff; border-radius: 16px;\n'
'  border: 1px solid var(--border);\n'
'  box-shadow: 0 2px 12px rgba(0,0,0,0.08);\n'
'  overflow: hidden; max-width: 600px; margin: 0 auto;\n'
'}\n'
'.hero-stat {\n'
'  flex: 1; padding: 24px 20px; text-align: center;\n'
'  border-right: 1px solid var(--border);\n'
'  position: relative;\n'
'}\n'
'.hero-stat:last-child { border-right: none; }\n'
'.hero-stat-num {\n'
'  display: block; font-size: 2.4rem; font-weight: 800;\n'
'  line-height: 1; margin-bottom: 6px;\n'
'  color: #0066CC;\n'
'}\n'
'.hero-stat-label {\n'
'  display: block; font-size: 0.75rem; color: #64748b;\n'
'  text-transform: uppercase; letter-spacing: 0.07em; font-weight: 600;\n'
'}\n'
'\n'
'/* ===== FILTERS ===== */\n'
'.filters-section {\n'
'  background: rgba(255,255,255,0.97); backdrop-filter: blur(16px);\n'
'  border-bottom: 1px solid var(--border);\n'
'  position: sticky; top: 64px; z-index: 100;\n'
'  box-shadow: 0 2px 12px rgba(0,0,0,0.06);\n'
'}\n'
'.filters-inner { max-width: 1200px; margin: 0 auto; padding: 14px 24px; display: flex; flex-direction: column; gap: 10px; }\n'
'.search-row { display: flex; align-items: center; gap: 12px; }\n'
'.search-wrap { flex: 1; position: relative; }\n'
'.search-ico { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--gray-400); pointer-events: none; }\n'
'.search-input {\n'
'  width: 100%; padding: 10px 14px 10px 42px;\n'
'  border: 1.5px solid var(--border); border-radius: var(--radius-sm);\n'
'  font-size: 0.93rem; font-family: var(--font); background: var(--bg-secondary);\n'
'  color: var(--text-primary); transition: border-color var(--transition), box-shadow var(--transition); outline: none;\n'
'}\n'
'.search-input:focus { border-color: #0066CC; box-shadow: 0 0 0 3px rgba(0,102,204,0.12); background: #ffffff; }\n'
'.search-input::placeholder { color: var(--gray-400); }\n'
'.results-count { font-size: 0.82rem; color: var(--gray-500); white-space: nowrap; font-weight: 600; min-width: 90px; text-align: right; }\n'
'.pills-row { display: flex; flex-wrap: wrap; gap: 7px; align-items: center; }\n'
'.pills-label { font-size: 0.72rem; font-weight: 700; color: var(--gray-400); text-transform: uppercase; letter-spacing: 0.08em; margin-right: 2px; white-space: nowrap; }\n'
'.pill {\n'
'  display: inline-flex; align-items: center; gap: 5px;\n'
'  padding: 4px 11px; border-radius: 999px;\n'
'  font-size: 0.74rem; font-weight: 600; cursor: pointer;\n'
'  border: 1.5px solid transparent; transition: all var(--transition);\n'
'  background: var(--gray-100); color: var(--gray-600); user-select: none;\n'
'}\n'
'.pill:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }\n'
'.pill.active { border-color: currentColor; filter: saturate(1.2); box-shadow: 0 2px 10px rgba(0,0,0,0.12); }\n'
'.pill-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }\n'
'.pill-all { background: #1B2B4B; color: #ffffff; }\n'
'.pill-all.active { background: #0066CC; border-color: #0066CC; }\n'
'\n'
'/* ===== MAIN ===== */\n'
'.main-content { max-width: 1200px; margin: 0 auto; padding: 40px 24px 72px; }\n'
'.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; flex-wrap: wrap; gap: 12px; }\n'
'.section-title { font-size: 0.93rem; color: var(--gray-500); font-weight: 500; }\n'
'.section-title strong { color: #1B2B4B; font-size: 1rem; font-weight: 700; }\n'
'.empty-state { text-align: center; padding: 80px 24px; color: var(--gray-500); display: none; }\n'
'.empty-icon { font-size: 3.5rem; margin-bottom: 16px; }\n'
'.empty-state h3 { font-size: 1.2rem; color: var(--gray-600); margin-bottom: 8px; font-weight: 600; }\n'
'.empty-state p { font-size: 0.9rem; }\n'
'.cards-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 24px; }\n'
'\n'
'/* ===== CARD ===== */\n'
'.card {\n'
'  background: #ffffff; border-radius: var(--radius);\n'
'  box-shadow: 0 2px 12px rgba(0,0,0,0.08); display: flex; flex-direction: column;\n'
'  border: 1px solid var(--border);\n'
'  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);\n'
'  overflow: hidden;\n'
'}\n'
'.card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,102,204,0.16); border-color: rgba(0,102,204,0.28); }\n'
'.card-accent { height: 4px; width: 100%; flex-shrink: 0; }\n'
'.card-body { padding: 18px 18px 14px; flex: 1; display: flex; flex-direction: column; gap: 10px; }\n'
'.card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; flex-wrap: wrap; }.badge {\n'
'  display: inline-flex; align-items: center; gap: 4px;\n'
'  padding: 3px 9px; border-radius: 999px;\n'
'  font-size: 0.69rem; font-weight: 700; letter-spacing: 0.02em; white-space: nowrap;\n'
'}\n'
'.badge-level-deb { background: var(--green-bg); color: var(--green-text); }\n'
'.badge-level-int { background: var(--orange-bg); color: var(--orange-text); }\n'
'.badge-level-adv { background: var(--red-bg); color: var(--red-text); }\n'
'.badge-level-other { background: #EEF2FF; color: #3730A3; }\n'
'.badge-certif { background: #F0FDF4; color: #166534; }\n'
'.badge-free { background: #ECFDF5; color: #065F46; }\n'
'.card-title { font-size: 0.98rem; font-weight: 700; color: #1B2B4B; line-height: 1.35; }\n'
'.card-meta { display: flex; flex-direction: column; gap: 4px; }\n'
'.card-meta-row { display: flex; align-items: center; gap: 7px; font-size: 0.8rem; color: var(--gray-500); }\n'
'.card-meta-row svg { width: 13px; height: 13px; flex-shrink: 0; color: var(--gray-400); }\n'
'.card-meta-val { color: var(--gray-600); font-weight: 500; }\n'
'.card-themes { display: flex; flex-wrap: wrap; gap: 5px; }\n'
'.theme-tag {\n'
'  padding: 2px 8px; border-radius: 999px;\n'
'  font-size: 0.67rem; font-weight: 600;\n'
'  background: rgba(0,102,204,0.07); color: #0066CC;\n'
'  border: 1px solid rgba(0,102,204,0.15);\n'
'}\n'
'.card-desc { font-size: 0.82rem; color: var(--gray-500); line-height: 1.5; flex: 1; }\n'
'.card-footer { padding: 12px 18px 16px; border-top: 1px solid var(--gray-100); display: flex; align-items: center; justify-content: space-between; gap: 8px; }\n'
'.card-price { font-size: 0.9rem; font-weight: 700; color: #1B2B4B; }\n'
'.card-price.free { color: var(--green); }\n'
'.card-lang { font-size: 1rem; }\n'
'.btn-voir {\n'
'  display: inline-flex; align-items: center; gap: 5px;\n'
'  padding: 7px 14px; border-radius: var(--radius-sm);\n'
'  background: transparent; color: #0066CC;\n'
'  font-size: 0.78rem; font-weight: 700; text-decoration: none;\n'
'  border: 1.5px solid #0066CC;\n'
'  transition: background var(--transition), color var(--transition), transform var(--transition);\n'
'  white-space: nowrap;\n'
'}\n'
'.btn-voir:hover { background: #0066CC; color: #ffffff; transform: translateY(-1px); }\n'
'.btn-voir svg { width: 12px; height: 12px; }\n'
'\n'
'/* ===== CATEGORY COLORS ===== */\n'
'.cat-influenceurs { background: #F3E8FF; color: #6B21A8; }\n'
'.cat-mooc-plateformes { background: #DBEAFE; color: #1E40AF; }\n'
'.cat-mooc-gratuits { background: #DCFCE7; color: #14532D; }\n'
'.cat-bootcamp-fr { background: #FEF3C7; color: #92400E; }\n'
'.cat-bootcamp-en { background: #FEE2E2; color: #991B1B; }\n'
'.cat-certif-gafam { background: #EDE9FE; color: #4C1D95; }\n'
'.cat-certif-cloud { background: #CFFAFE; color: #164E63; }\n'
'.cat-formations-acad { background: #E0F2FE; color: #0C4A6E; }\n'
'.cat-univ { background: #FEF9C3; color: #713F12; }\n'
'.cat-metiers { background: #FCE7F3; color: #831843; }\n'
'\n'
'/* Accent colors per category */\n'
'.accent-influenceurs { background: linear-gradient(90deg,#8B5CF6,#A855F7); }\n'
'.accent-mooc-plateformes { background: linear-gradient(90deg,#0066CC,#0052a3); }\n'
'.accent-mooc-gratuits { background: linear-gradient(90deg,#10B981,#059669); }\n'
'.accent-bootcamp-fr { background: linear-gradient(90deg,#F59E0B,#D97706); }\n'
'.accent-bootcamp-en { background: linear-gradient(90deg,#EF4444,#DC2626); }\n'
'.accent-certif-gafam { background: linear-gradient(90deg,#6366F1,#4F46E5); }\n'
'.accent-certif-cloud { background: linear-gradient(90deg,#06B6D4,#0891B2); }\n'
'.accent-formations-acad { background: linear-gradient(90deg,#0066CC,#0052a3); }\n'
'.accent-univ { background: linear-gradient(90deg,#F59E0B,#B45309); }\n'
'.accent-metiers { background: linear-gradient(90deg,#EC4899,#DB2777); }\n'
'\n'
'/* ===== BLOG SECTION ===== */\n'
'.blog-section {\n'
'  background: #ffffff;\n'
'  border-top: 1px solid var(--border);\n'
'  padding: 64px 24px;\n'
'}\n'
'.blog-inner { max-width: 1200px; margin: 0 auto; }\n'
'.blog-header { text-align: center; margin-bottom: 40px; }\n'
'.blog-title { font-size: 1.8rem; font-weight: 800; color: #1B2B4B; margin-bottom: 8px; }\n'
'.blog-subtitle { font-size: 0.95rem; color: var(--gray-500); }\n'
'.blog-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 28px; }\n'
'.blog-card {\n'
'  background: var(--bg-secondary);\n'
'  border: 1px solid var(--border);\n'
'  border-radius: var(--radius);\n'
'  overflow: hidden;\n'
'  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);\n'
'}\n'
'.blog-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0,102,204,0.14); border-color: rgba(0,102,204,0.3); }\n'
'.blog-card-accent { height: 4px; background: linear-gradient(90deg, #0066CC, #0099ff); }\n'
'.blog-card-body { padding: 24px; }\n'
'.blog-card-meta { display: flex; gap: 16px; margin-bottom: 12px; }\n'
'.blog-date, .blog-read { font-size: 0.75rem; color: var(--gray-400); font-weight: 600; }\n'
'.blog-card-title { font-size: 1.15rem; font-weight: 700; color: #1B2B4B; margin-bottom: 10px; line-height: 1.35; }\n'
'.blog-card-excerpt { font-size: 0.87rem; color: var(--gray-500); line-height: 1.6; margin-bottom: 20px; }\n'
'.blog-card-link {\n'
'  display: inline-flex; align-items: center; gap: 6px;\n'
'  font-size: 0.83rem; font-weight: 700; color: #0066CC; text-decoration: none;\n'
'  transition: gap var(--transition), color var(--transition);\n'
'}\n'
'.blog-card-link:hover { color: #0052a3; gap: 10px; }\n'
'\n'
'/* ===== FOOTER ===== */\n'
'.footer {\n'
'  background: #1B2B4B;\n'
'  color: rgba(255,255,255,0.6);\n'
'  text-align: center; padding: 48px 24px;\n'
'  border-top: 1px solid rgba(255,255,255,0.08);\n'
'}\n'
'.footer-inner { max-width: 800px; margin: 0 auto; }\n'
'.footer-brand {\n'
'  display: flex; align-items: center; justify-content: center;\n'
'  gap: 10px; margin-bottom: 16px;\n'
'}\n'
'.footer-logo-icon { width: 32px; height: 32px; }\n'
'.footer-logo-name {\n'
'  font-size: 1.15rem; font-weight: 400; color: rgba(255,255,255,0.85);\n'
'  letter-spacing: -0.02em;\n'
'}\n'
'.footer-logo-name strong { font-weight: 800; }\n'
'.footer-logo-academy { color: #4d94e0; font-weight: 800; }\n'
'.footer-text { font-size: 0.85rem; line-height: 1.7; margin-bottom: 6px; }\n'
'.footer-sub { font-size: 0.75rem; opacity: 0.55; margin-bottom: 16px; }\n'
'.footer-copy { font-size: 0.78rem; opacity: 0.5; }\n'
'.footer-copy a { color: #4d94e0; text-decoration: none; }\n'
'.footer-copy a:hover { text-decoration: underline; }\n'
'\n'
'/* ===== RESPONSIVE ===== */\n'
'@media (max-width: 1024px) {\n'
'  .cards-grid { grid-template-columns: repeat(2,1fr); }\n'
'}\n'
'@media (max-width: 640px) {\n'
'  .cards-grid { grid-template-columns: 1fr; gap: 16px; }\n'
'  .hero { padding: 56px 16px 64px; }\n'
'  .hero-stats { flex-direction: column; max-width: 100%; }\n'
'  .hero-stat { border-right: none; border-bottom: 1px solid var(--border); }\n'
'  .hero-stat:last-child { border-bottom: none; }\n'
'  .filters-inner { padding: 12px 16px; }\n'
'  .main-content { padding: 24px 16px 56px; }\n'
'  .section-header { flex-direction: column; align-items: flex-start; }\n'
'  .card-footer { flex-wrap: wrap; }\n'
'  .blog-section { padding: 40px 16px; }\n'
'  .blog-title { font-size: 1.4rem; }\n'
'  .blog-grid { grid-template-columns: 1fr; }\n'
'}\n'
'@media (max-width: 400px) {\n'
'  .pills-row { gap: 5px; }\n'
'  .pill { font-size: 0.7rem; padding: 3px 8px; }\n'
'}\n'
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
        '<title>' + esc(nom) + ' \u2013 Cyberquantic Academy | Formation IA 2025</title>',
        '<meta name="description" content="' + meta_desc + '">',
        '<link rel="canonical" href="' + page_url + '">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="' + esc(nom) + ' \u2013 Cyberquantic Academy">',
        '<meta property="og:description" content="' + meta_desc + '">',
        '<meta property="og:url" content="' + page_url + '">',
        '<meta property="og:image" content="https://academy.cyberquantic.com/og-image.png">',
        '<meta property="og:site_name" content="Cyberquantic Academy">',
        '<meta property="og:locale" content="fr_FR">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="' + esc(nom) + ' \u2013 Cyberquantic Academy">',
        '<meta name="twitter:description" content="' + meta_desc + '">',
        '<meta name="twitter:image" content="https://academy.cyberquantic.com/og-image.png">',
        '<meta name="twitter:site" content="@CyberQuantic">',
        '<script type="application/ld+json">' + schema + '</script>',
        '<style>' + CSS + '</style>',
        '</head><body>',
        '<header class="site-header"><div class="site-header-inner">',
        '<a href="../index.html" class="header-logo">''<span class="header-logo-icon">' + LOGO_SVG + '</span>''<span class="header-logo-text">''<span class="header-logo-brand">Cyber<strong>Quantic</strong></span>''<span class="header-logo-academy"> Academy</span>''</span></a>',
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
        '<span class="footer-logo-name">Cyber<strong>Quantic</strong> <span class="footer-logo-academy">Academy</span></span></div>',
        '<div class="footer-text">',
        '<p class="footer-text">L\'annuaire de r\xe9f\xe9rence des formations en Intelligence Artificielle &mdash; 2025-2026</p>',
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
