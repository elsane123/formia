#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyberquantic Academy rebrand script.
FormIA -> Cyberquantic Academy, CyberQuantic light theme.
"""
import re
from pathlib import Path

BASE = Path('/a0/usr/workdir/formia_site')
NEW_URL = 'https://academy.cyberquantic.com'

# ─────────────────────────────────────────────────────────────────
# LOGO SVG (geometric hexagonal overlapping circles, CQ mark)
# ─────────────────────────────────────────────────────────────────
LOGO_SVG = (
    '<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="40" cy="40" r="36" fill="#e8f0fe" stroke="#0066CC" stroke-width="1.5"/>'
    '<circle cx="28" cy="30" r="15" fill="none" stroke="#0066CC" stroke-width="2" opacity="0.65"/>'
    '<circle cx="52" cy="30" r="15" fill="none" stroke="#1a4fa8" stroke-width="2" opacity="0.65"/>'
    '<circle cx="40" cy="47" r="15" fill="none" stroke="#0099ff" stroke-width="2" opacity="0.65"/>'
    '<circle cx="40" cy="34" r="8" fill="#0066CC" opacity="0.12"/>'
    '<text x="40" y="39" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="800" fill="#0066CC">CQ</text>'
    '</svg>'
)

LOGO_SVG_INLINE = LOGO_SVG  # same logo used everywhere

# ─────────────────────────────────────────────────────────────────
# SHARED HEADER/FOOTER for formation pages (generate_pages.py)
# ─────────────────────────────────────────────────────────────────
PAGE_HEADER_LOGO_A = '<a href="../index.html" class="header-logo">'
PAGE_HEADER_LOGO_B = (
    '<span class="header-logo-icon">' + LOGO_SVG + '</span>'
    '<span class="header-logo-text">'
    '<span class="header-logo-brand">Cyber<strong>Quantic</strong></span>'
    '<span class="header-logo-academy"> Academy</span>'
    '</span>'
)

# ─────────────────────────────────────────────────────────────────
# CSS for generate_pages.py (formation detail pages)
# ─────────────────────────────────────────────────────────────────
PAGE_CSS = (
'*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n'
':root {\n'
'  --bg-primary: #ffffff;\n'
'  --bg-secondary: #f4f6fb;\n'
'  --text-primary: #1B2B4B;\n'
'  --text-secondary: #4a5568;\n'
'  --accent: #0066CC;\n'
'  --accent-hover: #0052a3;\n'
'  --border: #e2e8f0;\n'
'  --navy: #1B2B4B; --navy-800: #1B2B4B;\n'
'  --blue: #0066CC; --blue-dark: #0052a3; --blue-light: #4d94e0;\n'
'  --blue-glow: rgba(0,102,204,0.12);\n'
'  --white: #ffffff;\n'
'  --gray-50: #f4f6fb; --gray-100: #eef1f7; --gray-200: #e2e8f0;\n'
'  --gray-300: #cbd5e1; --gray-400: #94a3b8; --gray-500: #64748b; --gray-600: #475569;\n'
'  --font: -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;\n'
'  --radius: 14px;\n'
'  --shadow: 0 2px 12px rgba(0,0,0,0.08);\n'
'  --shadow-hover: 0 8px 32px rgba(0,102,204,0.16), 0 2px 8px rgba(0,0,0,0.08);\n'
'  --transition: 0.2s cubic-bezier(0.4,0,0.2,1);\n'
'}\n'
'html { scroll-behavior: smooth; }\n'
'body { font-family: var(--font); background: var(--bg-secondary); color: var(--text-primary); line-height: 1.6; min-height: 100vh; }\n'
'a { color: var(--blue); text-decoration: none; } a:hover { text-decoration: underline; }\n'
'/* SITE HEADER */\n'
'.site-header { background: #ffffff; border-bottom: 1.5px solid var(--border); box-shadow: 0 1px 8px rgba(0,0,0,0.06); }\n'
'.site-header-inner { max-width:1200px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; padding:0 24px; height:64px; }\n'
'.header-logo { display:inline-flex; align-items:center; gap:10px; text-decoration:none; }\n'
'.header-logo-icon { width:40px; height:40px; flex-shrink:0; }\n'
'.header-logo-text { display:flex; align-items:baseline; gap:0; line-height:1; }\n'
'.header-logo-brand { font-size:1.25rem; font-weight:400; color:#1B2B4B; letter-spacing:-0.02em; }\n'
'.header-logo-brand strong { font-weight:800; }\n'
'.header-logo-academy { font-size:1.25rem; font-weight:800; color:#0066CC; letter-spacing:-0.02em; }\n'
'.header-back { display:inline-flex; align-items:center; gap:6px; color:#4a5568; font-size:0.83rem; font-weight:600; transition:color var(--transition); }\n'
'.header-back:hover { color:#0066CC; text-decoration:none; }\n'
'/* BREADCRUMB */\n'
'.breadcrumb { background:var(--white); border-bottom:1px solid var(--border); padding:11px 24px; }\n'
'.breadcrumb-inner { max-width:1200px; margin:0 auto; display:flex; align-items:center; gap:7px; font-size:0.79rem; color:var(--gray-500); flex-wrap:wrap; }\n'
'.breadcrumb a { color:var(--blue); } .breadcrumb-sep { color:var(--gray-300); } .breadcrumb-current { color:var(--navy-800); font-weight:600; }\n'
'/* PAGE HERO */\n'
'.page-hero { background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%); position:relative; overflow:hidden; padding:52px 24px 60px; border-bottom:1px solid var(--border); }\n'
'.page-hero-bg { position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 700px 400px at 85% 50%, rgba(0,102,204,0.06) 0%, transparent 70%); }\n'
'.page-hero-grid { position:absolute; inset:0; pointer-events:none; background-image:linear-gradient(rgba(0,102,204,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,102,204,0.04) 1px,transparent 1px); background-size:52px 52px; }\n'
'.page-hero-content { position:relative; z-index:1; max-width:900px; margin:0 auto; }\n'
'.hero-cat-badge { display:inline-block; margin-bottom:16px; padding:5px 14px; border-radius:999px; background:rgba(0,102,204,0.1); border:1px solid rgba(0,102,204,0.25); color:#0066CC; font-size:0.75rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; }\n'
'.page-hero-title { font-size:clamp(1.55rem,4vw,2.5rem); font-weight:800; letter-spacing:-0.03em; color:#1B2B4B; line-height:1.18; margin-bottom:14px; }\n'
'.page-hero-sub { font-size:0.97rem; color:#4a5568; }\n'
'/* INFO CARDS */\n'
'.info-section { padding:44px 24px 0; }\n'
'.info-grid { max-width:1200px; margin:0 auto; display:grid; grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); gap:16px; }\n'
'.info-card { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); padding:20px 22px; box-shadow:var(--shadow); transition:box-shadow var(--transition),border-color var(--transition),transform var(--transition); }\n'
'.info-card:hover { box-shadow:var(--shadow-hover); border-color:rgba(0,102,204,0.25); transform:translateY(-2px); }\n'
'.info-card-label { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.09em; color:var(--gray-400); margin-bottom:8px; display:flex; align-items:center; gap:6px; }\n'
'.info-card-value { font-size:0.95rem; font-weight:600; color:var(--navy-800); line-height:1.45; }\n'
'.theme-tag { display:inline-block; padding:3px 9px; border-radius:999px; background:rgba(0,102,204,0.08); color:#0066CC; font-size:0.72rem; font-weight:600; margin:2px; border:1px solid rgba(0,102,204,0.18); }\n'
'.badge { display:inline-block; padding:3px 10px; border-radius:999px; font-size:0.78rem; font-weight:700; }\n'
'.badge-deb { background:#ECFDF5; color:#065F46; border:1px solid #6EE7B7; }\n'
'.badge-int { background:#FFFBEB; color:#92400E; border:1px solid #FCD34D; }\n'
'.badge-adv { background:#EFF6FF; color:#1E40AF; border:1px solid #93C5FD; }\n'
'.badge-other { background:var(--gray-100); color:var(--gray-600); border:1px solid var(--gray-300); }\n'
'.badge-certif-yes { background:#ECFDF5; color:#065F46; border:1px solid #6EE7B7; }\n'
'.badge-certif-no { background:#FEF2F2; color:#991B1B; border:1px solid #FCA5A5; }\n'
'.price-free { color:#065F46; font-weight:700; font-size:1rem; }\n'
'.price-paid { color:var(--navy-800); font-weight:700; font-size:1rem; }\n'
'/* DESCRIPTION */\n'
'.desc-section { padding:40px 24px; }\n'
'.desc-card { max-width:1200px; margin:0 auto; background:var(--white); border:1px solid var(--border); border-radius:var(--radius); padding:36px 40px; box-shadow:var(--shadow); }\n'
'.desc-title { font-size:1.15rem; font-weight:800; color:var(--navy-800); margin-bottom:16px; padding-bottom:14px; border-bottom:2px solid var(--gray-100); display:flex; align-items:center; gap:10px; }\n'
'.desc-body { font-size:0.97rem; color:var(--gray-600); line-height:1.8; }\n'
'/* CTA */\n'
'.cta-section { padding:8px 24px 48px; }\n'
'.cta-inner { max-width:1200px; margin:0 auto; display:flex; gap:14px; flex-wrap:wrap; align-items:center; }\n'
'.btn-cta { display:inline-flex; align-items:center; gap:10px; padding:16px 32px; border-radius:10px; background:#0066CC; color:#ffffff; font-size:1.05rem; font-weight:700; box-shadow:0 4px 20px rgba(0,102,204,0.3); transition:transform var(--transition),box-shadow var(--transition),background var(--transition); text-decoration:none; }\n'
'.btn-cta:hover { transform:translateY(-2px); box-shadow:0 8px 32px rgba(0,102,204,0.45); text-decoration:none; color:#ffffff; background:#0052a3; }\n'
'.btn-back { display:inline-flex; align-items:center; gap:8px; padding:14px 24px; border-radius:10px; background:var(--white); color:var(--navy-800); font-size:0.93rem; font-weight:600; border:1.5px solid var(--border); transition:all var(--transition); text-decoration:none; }\n'
'.btn-back:hover { border-color:#0066CC; color:#0066CC; text-decoration:none; }\n'
'/* SIMILAR */\n'
'.similar-section { background:var(--bg-secondary); border-top:1px solid var(--border); padding:48px 24px; }\n'
'.similar-inner { max-width:1200px; margin:0 auto; }\n'
'.similar-title { font-size:1.35rem; font-weight:800; color:var(--navy-800); margin-bottom:28px; }