#!/usr/bin/env python3
# FormIA site assembler
import json, os

BASE = '/a0/usr/workdir/formia_site'

with open('/a0/usr/workdir/formations_ia_2025.json', encoding='utf-8') as f:
    raw = json.load(f)
formations = raw['formations']
json_data = json.dumps(formations, ensure_ascii=False, separators=(',',':'))
json_data = json_data.replace('</', '<\\/')

free_count = sum(1 for f in formations if 'gratuit' in str(f.get('Prix','')).lower())
certif_count = sum(1 for f in formations if str(f.get('Certifiante','')).lower().startswith('oui'))
total_count = len(formations)

with open(os.path.join(BASE,'style.css'), encoding='utf-8') as f:
    css = f.read()
# Remove the trailing </style> tag that was accidentally appended
css = css.replace('</style>\n.badge-level-deb { background: var(--green-bg); color: var(--green-text); }', '.badge-level-deb { background: var(--green-bg); color: var(--green-text); }')
# Remove </style> wrapper tags if present
css = css.replace('<style>','').replace('</style>','')

with open(os.path.join(BASE,'script.js'), encoding='utf-8') as f:
    js = f.read()

SVG_LOGO = '''<svg class="logo-icon" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="38" fill="#1e3a5f" stroke="#3B82F6" stroke-width="1.5"/>
  <circle cx="40" cy="20" r="5" fill="#60A5FA"/>
  <circle cx="40" cy="60" r="5" fill="#60A5FA"/>
  <circle cx="20" cy="40" r="5" fill="#60A5FA"/>
  <circle cx="60" cy="40" r="5" fill="#60A5FA"/>
  <circle cx="25" cy="25" r="4" fill="#93C5FD"/>
  <circle cx="55" cy="25" r="4" fill="#93C5FD"/>
  <circle cx="25" cy="55" r="4" fill="#93C5FD"/>
  <circle cx="55" cy="55" r="4" fill="#93C5FD"/>
  <circle cx="40" cy="40" r="7" fill="#3B82F6"/>
  <line x1="40" y1="25" x2="40" y2="33" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="40" y1="47" x2="40" y2="55" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="25" y1="40" x2="33" y2="40" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="47" y1="40" x2="55" y2="40" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="29" y1="29" x2="35" y2="35" stroke="#93C5FD" stroke-width="1.2"/>
  <line x1="51" y1="29" x2="45" y2="35" stroke="#93C5FD" stroke-width="1.2"/>
  <line x1="29" y1="51" x2="35" y2="45" stroke="#93C5FD" stroke-width="1.2"/>
  <line x1="51" y1="51" x2="45" y2="45" stroke="#93C5FD" stroke-width="1.2"/>
  <circle cx="40" cy="20" r="2.5" fill="#BFDBFE"/>
  <circle cx="40" cy="60" r="2.5" fill="#BFDBFE"/>
  <circle cx="20" cy="40" r="2.5" fill="#BFDBFE"/>
  <circle cx="60" cy="40" r="2.5" fill="#BFDBFE"/>
</svg>'''

SVG_LOGO_SMALL = '''<svg class="footer-logo-icon" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="40" r="38" fill="#1e3a5f" stroke="#3B82F6" stroke-width="1.5"/>
  <circle cx="40" cy="20" r="5" fill="#60A5FA"/><circle cx="40" cy="60" r="5" fill="#60A5FA"/>
  <circle cx="20" cy="40" r="5" fill="#60A5FA"/><circle cx="60" cy="40" r="5" fill="#60A5FA"/>
  <circle cx="25" cy="25" r="4" fill="#93C5FD"/><circle cx="55" cy="25" r="4" fill="#93C5FD"/>
  <circle cx="25" cy="55" r="4" fill="#93C5FD"/><circle cx="55" cy="55" r="4" fill="#93C5FD"/>
  <circle cx="40" cy="40" r="7" fill="#3B82F6"/>
  <line x1="40" y1="25" x2="40" y2="33" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="40" y1="47" x2="40" y2="55" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="25" y1="40" x2="33" y2="40" stroke="#60A5FA" stroke-width="1.5"/>
  <line x1="47" y1="40" x2="55" y2="40" stroke="#60A5FA" stroke-width="1.5"/>
</svg>'''

out = []
def W(s): out.append(s)

W('<!DOCTYPE html>')
W('<html lang="fr">')
W('<head>')
W('<meta charset="UTF-8">')
W('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
W('<title>FormIA \u2014 Trouvez la formation IA qui vous correspond</title>')
W('<meta name="description" content="Annuaire de ' + str(total_count) + ' formations en intelligence artificielle 2025-2026. Filtrez par cat\u00e9gorie, niveau, langue et trouvez la formation IA qui vous correspond.">')
W('<style>' + css + '</style>')
W('</head>')
W('<body>')

# HERO
W('<header class="hero">')
W('<div class="hero-bg"></div>')
W('<div class="hero-grid"></div>')
W('<div class="hero-content">')
W('<div class="logo-wrap">')
W(SVG_LOGO)
W('<div class="logo-textblock">')
W('<span class="logo-name">FormIA</span>')
W('<span class="logo-badge">Annuaire formations IA 2025&#8209;2026</span>')
W('</div></div>')
W('<p class="hero-tagline">Trouvez la formation IA qui vous correspond</p>')
W('<p class="hero-sub">' + str(total_count) + ' formations s\u00e9lectionn\u00e9es &bull; Toutes cat\u00e9gories &bull; Tous niveaux</p>')
W('<div class="hero-dots"><span class="hero-dot"></span><span class="hero-dot"></span><span class="hero-dot"></span></div>')
W('</div></header>')

# STATS
W('<section class="stats-banner">')
W('<div class="stats-inner">')
W('<div class="stat-item"><span class="stat-icon">\U0001F9E0</span><div class="stat-num">' + str(total_count) + '</div><div class="stat-label">Formations r\u00e9pertori\u00e9es</div></div>')
W('<div class="stat-item"><span class="stat-icon">\U0001F7E2</span><div class="stat-num">' + str(free_count) + '</div><div class="stat-label">Formations gratuites</div></div>')
W('<div class="stat-item"><span class="stat-icon">\U0001F3AB</span><div class="stat-num">' + str(certif_count) + '</div><div class="stat-label">Formations certifiantes</div></div>')
W('</div></section>')

# FILTERS
W('<nav class="filters-section">')
W('<div class="filters-inner">')
W('<div class="search-row">')
W('<div class="search-wrap">')
W('<span class="search-ico"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg></span>')
W('<input type="search" id="searchInput" class="search-input" placeholder="Rechercher par nom, cr\u00e9ateur, th\u00e9matique..." autocomplete="off">')
W('</div>')
W('<span class="results-count" id="resultsCount">72 formations</span>')
W('</div>')
W('<div class="pills-row" id="pillsContainer"></div>')
W('</div></nav>')

# MAIN
W('<main class="main-content">')
W('<div class="section-header">')
W('<p class="section-title">Affichage de <strong id="countDisplay">72 formations</strong></p>')
W('</div>')
W('<div class="empty-state" id="emptyState">')
W('<div class="empty-icon">\U0001F50D</div>')
W('<h3>Aucune formation trouv\u00e9e</h3>')
W('<p>Essayez d\u2019autres mots-cl\u00e9s ou s\u00e9lectionnez une autre cat\u00e9gorie.</p>')
W('</div>')
W('<div class="cards-grid" id="cardsGrid"></div>')
W('</main>')

# FOOTER
W('<footer class="footer">')
W('<div class="footer-logo">')
W(SVG_LOGO_SMALL)
W('<span class="footer-logo-name">FormIA</span>')
W('</div>')
W('<div class="footer-text">')
W('<p>L\u2019annuaire de r\u00e9f\u00e9rence des formations en Intelligence Artificielle &mdash; 2025-2026</p>')
W('<p style="margin-top:6px;font-size:0.75rem;opacity:0.6;">' + str(total_count) + ' formations &bull; ' + str(free_count) + ' gratuites &bull; ' + str(certif_count) + ' certifiantes</p>')
W('</div>')
W('</footer>')

# SCRIPTS
W('<script>var FORMATIONS=' + json_data + ';</script>')
W('<script>' + js + '</script>')
W('</body>')
W('</html>')

result = '\n'.join(out)
out_path = os.path.join(BASE, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(result)

size = os.path.getsize(out_path)
print('SUCCESS: index.html written')
print('Size: {:,} bytes ({:.1f} KB)'.format(size, size/1024))
print('Lines:', result.count('\n'))
