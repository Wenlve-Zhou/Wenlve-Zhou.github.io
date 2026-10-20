"""Render the static academic homepage from the editable publication catalog."""
from pathlib import Path
from html import escape
from hashlib import sha256
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re
import os
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
profile = json.loads((ROOT / 'profile.json').read_text())
news = json.loads((ROOT / 'news.json').read_text())
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
shutil.copytree(ROOT / 'assets', DIST / 'assets')
for source_file in ('styles.css', 'app.js'):
    shutil.copyfile(ROOT / 'src' / source_file, DIST / source_file)
ORIGIN = (os.environ.get('SITE_URL') or profile['siteUrl']).rstrip('/')
parsed_url = urlsplit(ORIGIN)
if parsed_url.scheme not in ('https', 'http') or not parsed_url.netloc:
    raise ValueError('SITE_URL / profile.siteUrl must be an absolute website URL')
SCHOLAR = profile['scholar']
papers = json.loads((ROOT / 'publications.json').read_text())
LAST_UPDATED = datetime.now(ZoneInfo('Asia/Shanghai')).date()
paper_count = len(papers)
counts = {
    'embodied': sum(p['category'] == 'embodied' for p in papers),
    'vision': sum(p['category'] == 'vision' for p in papers),
    'world': sum(bool(p.get('world')) for p in papers),
}
seen_ids = set()
for paper in papers:
    if not re.fullmatch(r'[a-z][a-z0-9-]*', paper['id']) or paper['id'] in seen_ids:
        raise ValueError('Publication IDs must be unique lowercase slugs: ' + paper['id'])
    if paper['category'] not in ('vision', 'embodied'):
        raise ValueError('Publication category must be vision or embodied: ' + paper['id'])
    seen_ids.add(paper['id'])
e = escape

def icon(name):
    return f'<svg aria-hidden="true"><use href="#i-{name}"></use></svg>'

def link(url, label, extra=''):
    return f'<a href="{e(url, quote=True)}" target="_blank" rel="noopener noreferrer" {extra}>{label}</a>'

def bibtex(p):
    kind = p.get('bibtexType') or ('inproceedings' if p['venueShort'] == 'CVPR' else 'article')
    key = ('wang' if p['id'] == 'unitas' else 'liu' if p['id'] == 'taskanchor' else 'liang' if p['id'] == 'physdrift' else 'zhou') + str(p['year']) + p['id']
    fields = [f"  title = {{{{{p['title']}}}}}", f"  author = {{{' and '.join(p['authors'])}}}"]
    if kind == 'inproceedings':
        fields += [f"  booktitle = {{{p['venue']}}}"]
    elif p['venueShort'] == 'Preprint':
        fields += [f"  journal = {{arXiv preprint arXiv:{p['arxiv']}}}", f"  eprint = {{{p['arxiv']}}}", '  archivePrefix = {arXiv}']
    else:
        fields += [f"  journal = {{{p['venue']}}}"]
    for optional_field in ('volume', 'number', 'pages'):
        if p.get(optional_field):
            fields += [f"  {optional_field} = {{{p[optional_field]}}}"]
    fields += [f"  year = {{{p['year']}}}"]
    if p.get('doi'):
        fields += [f"  doi = {{{p['doi']}}}"]
    fields += [f"  url = {{{p['paper']}}}"]
    return '@' + kind + '{' + key + ',\n' + ',\n'.join(fields) + '\n}\n'

def paper_html(p):
    authors = ', '.join(f'<strong>{e(profile["name"])}</strong>' if a == profile['name'] else e(a) for a in p['authors'])
    venue_cls = ' is-cvpr' if p['venueShort'] == 'CVPR' else ''
    role = f'<span class="role">{e(p["role"])}</span>' if p.get('role') else ''
    lead = '<span class="lead-role">Project lead</span>' if p.get('lead') else ''
    links = [link(p['paper'], icon('paper') + 'Paper', f'aria-label="Read {e(p["title"], quote=True)}"')]
    for key, label, sym in [('preprint','arXiv','external'),('project','Project','globe'),('code','Code','code')]:
        if p.get(key):
            links.append(link(p[key], icon(sym) + label))
    links += [f'<button type="button" class="bib-button" data-paper="{p["id"]}" aria-haspopup="dialog" aria-label="BibTeX for {e(p["title"], quote=True)}">{icon("quote")}BibTeX</button>', f'<a class="bib-fallback" href="assets/citations/{p["id"]}.bib" download>BibTeX</a>']
    if p.get('image'):
        teaser = f'<a href="{p["image"]}" class="teaser" data-image="{p["id"]}" aria-label="Enlarge figure for {e(p["title"], quote=True)}"><img src="{p["image"]}" alt="{e(p["imageAlt"], quote=True)}" width="600" height="420" loading="lazy"><span class="zoom-hint">{icon("expand")}</span></a>'
    else:
        cover_name = p.get('shortTitle') or (p['id'].upper() if len(p['id']) <= 6 else 'PAPER')
        cover_topic = '<br>'.join(e(tag) for tag in p.get('tags', [])[:2])
        teaser = f'<a class="teaser paper-cover" href="{e(p["paper"], quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Read {e(p["title"], quote=True)}"><span class="cover-journal">{e(p["venue"].upper())}</span><span class="cover-abbreviation">{e(cover_name)}</span><span class="cover-topic">{cover_topic}</span><span class="cover-year">{p["year"]} {icon("external")}</span></a>'
    lead_class = ' lead-publication' if p.get('lead') else ''
    return f'''<article class="publication{lead_class}" id="paper-{p['id']}" data-category="{p['category']}" data-world="{str(p.get('world', False)).lower()}">
      {teaser}
      <div class="paper-content">
        <div class="paper-meta"><span class="venue{venue_cls}" title="{e(p['venue'], quote=True)}">{e(p['venueShort'])} {p['year']}</span>{role}{lead}</div>
        <h4 class="paper-title">{link(p['paper'], e(p['title']))}</h4>
        <p class="authors">{authors}</p>
        <p class="paper-summary">{e(p['summary'])}</p>
        <div class="paper-links">{''.join(links)}</div>
      </div>
    </article>'''

years = sorted({p['year'] for p in papers}, reverse=True)
publication_html = '\n'.join(f'<div class="year-group" data-year="{year}"><h3 class="year-label">{year}</h3>' + '\n'.join(paper_html(p) for p in papers if p['year'] == year) + '</div>' for year in years)

symbols = '''
<svg xmlns="http://www.w3.org/2000/svg" class="icon-defs" aria-hidden="true"><defs>
<symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/></symbol>
<symbol id="i-scholar" viewBox="0 0 24 24"><path d="m2 9 10-5 10 5-10 5-10-5Z"/><path d="M6 11v6c4 3 8 3 12 0v-6M22 9v7"/></symbol>
<symbol id="i-code" viewBox="0 0 24 24"><path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-16-2 20"/></symbol>
<symbol id="i-github" viewBox="0 0 24 24"><path d="M9 19c-4 1-4-2-6-2m12 5v-4c0-1.1-.4-1.8-1-2 3-.4 6-1.4 6-6a4.7 4.7 0 0 0-1.2-3.3A4.4 4.4 0 0 0 18.7 3S17.6 2.6 15 4a12.5 12.5 0 0 0-6 0C6.4 2.6 5.3 3 5.3 3a4.4 4.4 0 0 0-.1 3.7A4.7 4.7 0 0 0 4 10c0 4.6 3 5.6 6 6-.6.3-1 1-1 2v4"/></symbol>
<symbol id="i-external" viewBox="0 0 24 24"><path d="M7 17 17 7M7 7h10v10"/></symbol>
<symbol id="i-paper" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8m-8 4h5"/></symbol>
<symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c5 5 5 13 0 18-5-5-5-13 0-18Z"/></symbol>
<symbol id="i-eye" viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></symbol>
<symbol id="i-robot" viewBox="0 0 24 24"><rect x="4" y="7" width="16" height="13" rx="3"/><path d="M12 3v4M9 16h6M1 12v4m22-4v4M8 11v1m8-1v1"/><circle cx="12" cy="2" r="1"/></symbol>
<symbol id="i-layers" viewBox="0 0 24 24"><path d="m12 3 10 5-10 5L2 8l10-5Zm-10 9 10 5 10-5M2 16l10 5 10-5"/></symbol>
<symbol id="i-box" viewBox="0 0 24 24"><path d="m12 2 10 5v10l-10 5-10-5V7l10-5Zm0 10 10-5M12 12 2 7m10 5v10M7 4.5l10 5"/></symbol>
<symbol id="i-update" viewBox="0 0 24 24"><path d="M3 11a9 9 0 1 1 2.5 7M3 4v7h7M12 7v5l3 2"/></symbol>
<symbol id="i-quote" viewBox="0 0 24 24"><path d="M3 12h6v7H3v-7Zm0 0c0-5 2-7 5-7m7 7h6v7h-6v-7Zm0 0c0-5 2-7 5-7"/></symbol>
<symbol id="i-expand" viewBox="0 0 24 24"><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/></symbol>
<symbol id="i-close" viewBox="0 0 24 24"><path d="m6 6 12 12M6 18 18 6"/></symbol>
<symbol id="i-up" viewBox="0 0 24 24"><path d="m6 12 6-6 6 6M12 6v15"/></symbol>
</defs></svg>'''

university = profile['university']
education = profile['education']
interest_names = [item['label'] for item in profile['interests']]
bold_interests = [f'<strong>{e(label.lower())}</strong>' for label in interest_names]
if len(bold_interests) > 1:
    joined_interests = ', '.join(bold_interests[:-1]) + ', and ' + bold_interests[-1]
else:
    joined_interests = ''.join(bold_interests)
about_html = (
    f'<p>I am a <strong>{e(profile["role"])}</strong> at the {e(profile["department"])}, '
    + link(university['url'], e(university['name']))
    + f'. I received my {e(education["degree"])} from '
    + link(education['url'], e(education['university']))
    + (f' ({e(education["abbreviation"])})' if education.get('abbreviation') else '')
    + '.</p>'
    + f'<p>My research spans {joined_interests}. {e(profile["researchStatement"])}</p>'
    + ''.join(f'<p>{e(paragraph)}</p>' for paragraph in profile.get('extraBiography', []))
)
interests_html = ''.join(f'<span class="interest">{icon(item["icon"])}{e(item["label"])}</span>' for item in profile['interests'])
rail_focus = '<br>'.join(e(item['label']) for item in profile['interests'][:2])
news_parts = []
for item in sorted(news, key=lambda x: x['date'], reverse=True):
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', item['date']):
        raise ValueError('News dates must use YYYY-MM format')
    date = datetime.strptime(item['date'], '%Y-%m')
    text = item['text']
    paper_id = item.get('paperId')
    highlight = item.get('highlight')
    rendered_text = e(text)
    if paper_id:
        if paper_id not in seen_ids or not highlight or highlight not in text:
            raise ValueError('News paperId/highlight does not match an existing publication and text')
        pos = text.index(highlight)
        rendered_text = e(text[:pos]) + f'<a href="#paper-{e(paper_id)}">{e(highlight)}</a>' + e(text[pos + len(highlight):])
    news_parts.append(f'<li><time datetime="{e(item["date"])}">{date.strftime("%b %Y")}</time><p>{rendered_text}</p></li>')
news_html = ''.join(news_parts)
experience_rows = [
    {'period': 'Current', 'role': profile['role'], 'institution': university['name'], 'url': university['url'], 'description': profile['department']},
    {'period': education['degree'], 'institution': education['university'], 'url': education['url']},
] + profile.get('additionalExperience', [])
experience_parts = []
for item in experience_rows:
    institution = link(item['url'], e(item['institution'])) if item.get('url') else e(item['institution'])
    title = (e(item['role']) + ' · ' if item.get('role') else '') + institution
    description = f'<p>{e(item["description"])}</p>' if item.get('description') else ''
    experience_parts.append(f'<li class="experience-item"><span class="period">{e(item["period"])}</span><div><strong>{title}</strong>{description}</div></li>')
experience_html = ''.join(experience_parts)
site_description = f'{profile["name"]}, {profile["role"]} at {university["name"]}. Research in ' + ', '.join(label.lower() for label in interest_names) + '.'
structured = {'@context':'https://schema.org','@type':'Person','name':profile['name'],'jobTitle':profile['role'],'email':'mailto:'+profile['email'],'url':ORIGIN,'image':ORIGIN+'/'+profile['portrait'],'affiliation':{'@type':'CollegeOrUniversity','name':university['name'],'department':{'@type':'Organization','name':profile['department']}},'alumniOf':{'@type':'CollegeOrUniversity','name':education['university']},'sameAs':[SCHOLAR,profile['github']],'knowsAbout':interest_names}


html = f'''<!doctype html>
<html lang="en" class="no-js">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{e(profile["name"])} | {e(profile["role"])} at {e(university["name"])}</title>
  <meta name="description" content="{e(site_description, quote=True)}">
  <meta name="theme-color" content="#142a3d">
  <meta property="og:type" content="profile"><meta property="og:title" content="{e(profile["name"], quote=True)} — Academic Homepage">
  <meta property="og:description" content="{e(" · ".join(interest_names), quote=True)}">
  <meta property="og:url" content="{ORIGIN}"><meta property="og:image" content="{ORIGIN}/{e(profile["portrait"], quote=True)}">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg"><link rel="stylesheet" href="styles.css?v={sha256((DIST / 'styles.css').read_bytes()).hexdigest()[:12]}">
  <link rel="canonical" href="{ORIGIN}/">
  <script type="application/ld+json">{json.dumps(structured)}</script>
  <script>document.documentElement.classList.remove('no-js');</script>
  <script src="app.js?v={sha256((DIST / 'app.js').read_bytes()).hexdigest()[:12]}" defer></script>
</head>
<body id="top">
{symbols}
<a class="skip-link" href="#main-content">Skip to content</a>
<aside class="sidebar" aria-label="Profile and navigation">
  <div class="site-label"><span class="site-mark">wz.</span> Academic homepage</div>
  <div class="profile">
    <div class="portrait-frame"><img class="portrait" src="{e(profile["portrait"], quote=True)}" alt="Portrait of {e(profile["name"], quote=True)}" width="156" height="196" fetchpriority="high"></div>
    <h1>{e(profile["name"])}</h1><p class="position"><span class="position-mark" aria-hidden="true"></span>{e(profile["role"])} · {e(profile["credential"])}</p>
    <p class="affiliation">{link(university['url'], e(university['name']))}<br>{e(profile['department'])}</p>
  </div>
  <div class="profile-links">
    <a href="mailto:{e(profile["email"], quote=True)}" class="email">{icon('mail')}{e(profile["email"])}</a>
    {link(SCHOLAR,icon('scholar')+'Google Scholar')}
    {link(profile['github'],icon('github')+'GitHub')}
  </div>
  <nav class="side-nav" aria-label="Sections">
    <a href="#about" aria-current="location"><span>01</span>About</a>
    <a href="#updates"><span>02</span>Updates</a>
    <a href="#publications"><span>03</span>Publications</a>
    <a href="#experience"><span>04</span>Experience</a>
    <a href="#contact"><span>05</span>Contact</a>
  </nav>
  <div class="rail-footer"><span>Research profile</span>{rail_focus}</div>
</aside>
<div class="main-shell">
  <header class="topbar"><div class="breadcrumb">{e(profile["name"])} <span class="slash">/</span><strong>Academic homepage</strong></div><a href="mailto:{e(profile["email"], quote=True)}">Get in touch {icon('external')}</a></header>
  <main id="main-content">
    <section id="about" aria-labelledby="about-title">
      <p class="section-kicker">Profile &amp; research</p>
      <h2 id="about-title">About me</h2>
      <div class="about-body">{about_html}</div>
      <div class="interests" aria-label="Research interests">{interests_html}</div>
    </section>
    <section id="updates" class="updates" aria-labelledby="updates-title">
      <div class="updates-heading"><h2 id="updates-title">{icon('update')}Recent updates</h2></div>
      <ul class="news-list">{news_html}</ul>
    </section>
    <section id="publications" class="publications" aria-labelledby="publications-title">
      <p class="section-kicker">Research &amp; publications</p>
      <div class="section-heading"><h2 id="publications-title">Selected publications <span class="count-badge" id="paper-count">{paper_count}</span></h2>{link(SCHOLAR,'<span class="long-label">Full list on </span>Google Scholar'+icon('external'),'class="scholar-link"')}</div>
      <p class="publication-note">My name is underlined. Author contributions are noted where applicable.</p>
      <div class="filters" role="group" aria-label="Filter publications by research area">
        <button type="button" class="filter" data-filter="all" aria-pressed="true">All <span>{paper_count}</span></button>
        <button type="button" class="filter" data-filter="embodied" aria-pressed="false">Embodied intelligence <span>{counts['embodied']}</span></button>
        <button type="button" class="filter" data-filter="vision" aria-pressed="false">Computer vision <span>{counts['vision']}</span></button>
        <button type="button" class="filter" data-filter="world" aria-pressed="false">World models <span>{counts['world']}</span></button>
      </div>
      <div class="visually-hidden" id="filter-status" role="status" aria-live="polite"></div>
      <div id="publication-list">{publication_html}</div>
    </section>
    <section id="experience" class="experience" aria-labelledby="experience-title">
      <p class="section-kicker">Academic journey</p><h2 id="experience-title">Experience &amp; education</h2>
      <ol class="experience-list">{experience_html}</ol>
    </section>
    <section id="contact" class="contact-section" aria-labelledby="contact-title"><div><h2 id="contact-title">Get in touch</h2><p>{e(profile["contactText"])}</p></div><a class="contact-button" href="mailto:{e(profile["email"], quote=True)}">{icon('mail')}{e(profile["email"])} {icon('external')}</a></section>
  </main>
  <footer class="footer"><div>© {LAST_UPDATED.year} {e(profile["name"])} <span class="footer-update">· Updated {LAST_UPDATED.strftime('%B %Y')}</span></div><a href="#top">Back to top {icon('up')}</a></footer>
</div>
<dialog id="citation-dialog" aria-labelledby="citation-heading"><div class="dialog-heading"><h2 id="citation-heading">Cite this work</h2><button type="button" class="dialog-close" data-close aria-label="Close citation">{icon('close')}</button></div><p class="citation-title" id="citation-title"></p><pre id="citation-code" tabindex="0"></pre><div class="dialog-actions"><button type="button" id="copy-citation">Copy BibTeX</button><a id="download-citation" download>Download .bib</a><span class="copy-status" id="copy-status" role="status" aria-live="polite"></span></div></dialog>
<dialog id="image-dialog" class="image-dialog" aria-labelledby="image-heading"><div class="dialog-heading"><h2 id="image-heading"></h2><button type="button" class="dialog-close" data-close aria-label="Close figure">{icon('close')}</button></div><img id="full-figure" alt=""><p class="image-source">Figure from the original research paper or project.</p></dialog>
</body>
</html>'''

(DIST / 'index.html').write_text(html)
(DIST / 'assets/citations').mkdir(exist_ok=True)
for p in papers:
    p['bibtex'] = bibtex(p)
    (DIST / f"assets/citations/{p['id']}.bib").write_text(p['bibtex'])
(DIST / 'publications.json').write_text(json.dumps(papers, indent=2))
(DIST / '.nojekyll').write_text('')
(DIST / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+ORIGIN+'/</loc><lastmod>'+LAST_UPDATED.isoformat()+'</lastmod></url></urlset>')
print(f'Rendered {len(papers)} publications with static HTML and BibTeX.')
