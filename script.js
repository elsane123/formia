(function(){
'use strict';

// Category -> CSS class mapping
var CAT_CLASS = {
  'Influenceurs FR': 'influenceurs',
  'MOOC & Plateformes': 'mooc-plateformes',
  'MOOCs gratuits': 'mooc-gratuits',
  'Bootcamps intensifs': 'bootcamp-fr',
  'Bootcamps anglophones': 'bootcamp-en',
  'Certifications GAFAM': 'certif-gafam',
  'Certifications cloud & tech': 'certif-cloud',
  'Formations académiques françaises': 'formations-acad',
  'Universités & Grandes écoles': 'univ',
  'Formations spécialisées par métier': 'metiers'
};

// Category display labels (shortened for pills)
var CAT_LABELS = {
  'Influenceurs FR': 'Influenceurs FR',
  'MOOC & Plateformes': 'MOOC & Plateformes',
  'MOOCs gratuits': 'MOOCs gratuits',
  'Bootcamps intensifs': 'Bootcamps FR',
  'Bootcamps anglophones': 'Bootcamps EN',
  'Certifications GAFAM': 'Certif. GAFAM',
  'Certifications cloud & tech': 'Cloud & Tech',
  'Formations académiques françaises': 'Académiques FR',
  'Universités & Grandes écoles': 'Universités',
  'Formations spécialisées par métier': 'Par métier'
};

function getLevelClass(niveau) {
  var n = (niveau||'').toLowerCase();
  if (n.indexOf('débutant') !== -1 || n.indexOf('debutant') !== -1 || n.indexOf('fondamentaux') !== -1) return 'deb';
  if (n.indexOf('intermédiaire') !== -1 || n.indexOf('intermediaire') !== -1) return 'int';
  if (n.indexOf('avancé') !== -1 || n.indexOf('avance') !== -1) return 'adv';
  return 'other';
}

function getLangFlag(langue) {
  var l = (langue||'').toLowerCase();
  if (l === 'français') return '🇫🇷';
  if (l === 'anglais') return '🇬🇧';
  if (l.indexOf('français') !== -1 && l.indexOf('anglais') !== -1) return '🇫🇷 🇬🇧';
  return '🌐';
}

function isFree(prix) {
  return prix && prix.toLowerCase().indexOf('gratuit') !== -1;
}

function isCertif(certif) {
  return certif && certif.toLowerCase().startsWith('oui');
}

function escHtml(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function truncate(s, n) {
  s = s||'';
  return s.length > n ? s.slice(0,n) + '\u2026' : s;
}

function catClass(cat) {
  return CAT_CLASS[cat] || 'mooc-plateformes';
}

function buildCard(f) {
  var cat = f['\u0043at\u00e9gorie'] || '';
  var nom = f['Nom de la formation'] || '';
  var createur = f['Cr\u00e9ateur / Organisme'] || '';
  var plateforme = f['Plateforme'] || '';
  var themes = f['Th\u00e9matiques couvertes'] || '';
  var niveau = f['Niveau'] || '';
  var langue = f['Langue'] || '';
  var prix = f['Prix'] || '';
  var certif = f['Certifiante'] || '';
  var desc = f['Description'] || '';
  var url = f['URL'] || '#';

  var cc = catClass(cat);
  var levelCls = getLevelClass(niveau);
  var flag = getLangFlag(langue);
  var free = isFree(prix);
  var certifOui = isCertif(certif);

  var themeList = themes.split(',').map(function(t){ return t.trim(); }).filter(Boolean).slice(0,3);
  var themeHtml = themeList.map(function(t){
    return '<span class="theme-tag">' + escHtml(t) + '</span>';
  }).join('');

  var html = '<div class="card" data-cat="' + escHtml(cat) + '">';
  html += '<div class="card-accent accent-' + cc + '"></div>';
  html += '<div class="card-body">';
  html += '<div class="card-top">';
  html += '<span class="badge cat-' + cc + '">' + escHtml(CAT_LABELS[cat]||cat) + '</span>';
  html += '<span class="badge badge-level-' + levelCls + '">' + escHtml(niveau||'N/A') + '</span>';
  html += '</div>';
  html += '<div class="card-title">' + escHtml(nom) + '</div>';
  html += '<div class="card-meta">';
  html += '<div class="card-meta-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg><span class="card-meta-val">' + escHtml(createur) + '</span></div>';
  html += '<div class="card-meta-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg><span class="card-meta-val">' + escHtml(plateforme) + '</span></div>';
  html += '</div>';
  if (themeHtml) html += '<div class="card-themes">' + themeHtml + '</div>';
  html += '<div class="card-desc">' + escHtml(truncate(desc, 160)) + '</div>';
  html += '</div>';
  html += '<div class="card-footer">';
  html += '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">';
  html += '<span class="card-price' + (free?' free':'') + '">' + escHtml(prix) + '</span>';
  if (certifOui) html += '<span class="badge badge-certif">\u2713 Certifiante</span>';
  html += '</div>';
  html += '<div style="display:flex;align-items:center;gap:8px">';
  html += '<span class="card-lang" title="' + escHtml(langue) + '">' + flag + '</span>';
  html += '<a href="' + escHtml(url) + '" target="_blank" rel="noopener" class="btn-voir">Voir <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg></a>';
  html += '</div>';
  html += '</div></div>';
  return html;
}

var activeCategory = 'all';
var searchQuery = '';

function normalize(s) {
  return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
}

function filterAndRender() {
  var grid = document.getElementById('cardsGrid');
  var empty = document.getElementById('emptyState');
  var countEl = document.getElementById('resultsCount');
  var q = normalize(searchQuery);
  var count = 0;
  var html = '';

  for (var i=0; i<FORMATIONS.length; i++) {
    var f = FORMATIONS[i];
    var cat = f['\u0043at\u00e9gorie']||'';
    if (activeCategory !== 'all' && cat !== activeCategory) continue;
    if (q) {
      var haystack = normalize(
        (f['Nom de la formation']||'') + ' ' +
        (f['Cr\u00e9ateur / Organisme']||'') + ' ' +
        (f['Th\u00e9matiques couvertes']||'') + ' ' +
        (f['Plateforme']||'') + ' ' +
        (f['Description']||'')
      );
      if (haystack.indexOf(q) === -1) continue;
    }
    html += buildCard(f);
    count++;
  }

  grid.innerHTML = html;
  if (count === 0) {
    empty.style.display = 'block';
    grid.style.display = 'none';
  } else {
    empty.style.display = 'none';
    grid.style.display = 'grid';
  }
  countEl.textContent = count + ' formation' + (count > 1 ? 's' : '');
}

function initPills() {
  var container = document.getElementById('pillsContainer');
  var cats = [];
  var seen = {};
  for (var i=0; i<FORMATIONS.length; i++) {
    var c = FORMATIONS[i]['\u0043at\u00e9gorie']||'';
    if (c && !seen[c]) { cats.push(c); seen[c]=true; }
  }

  var html = '<span class="pills-label">Cat\u00e9gorie :</span>';
  html += '<button class="pill pill-all active" data-cat="all" onclick="setCat(this,\'all\')">Toutes les formations</button>';
  for (var j=0; j<cats.length; j++) {
    var cat = cats[j];
    var cc = catClass(cat);
    var label = CAT_LABELS[cat]||cat;
    html += '<button class="pill cat-'+cc+'" data-cat="'+escHtml(cat)+'" onclick="setCat(this,\''+escHtml(cat).replace(/'/g,"\\'")+'\')">';
    html += '<span class="pill-dot" style="background:currentColor"></span>';
    html += escHtml(label)+'</button>';
  }
  container.innerHTML = html;
}

window.setCat = function(el, cat) {
  activeCategory = cat;
  var pills = document.querySelectorAll('.pill');
  for (var i=0; i<pills.length; i++) pills[i].classList.remove('active');
  el.classList.add('active');
  filterAndRender();
};

document.addEventListener('DOMContentLoaded', function(){
  initPills();
  filterAndRender();
  var inp = document.getElementById('searchInput');
  inp.addEventListener('input', function(){
    searchQuery = inp.value;
    filterAndRender();
  });
});

})();
