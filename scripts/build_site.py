"""Build static reading pages from the selected Markdown files. Does not deploy."""
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, unquote
from datetime import datetime
from lxml import html as LH, etree
import os, json, re, html, posixpath, subprocess, shutil, hashlib, zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'docs'
CONFIG = json.loads((ROOT/'catalog.json').read_text())
ITEMS = CONFIG['items']
BASE = CONFIG['base_url'].rstrip('/')+'/'
DATE = CONFIG['prepared_date']
VERSION = CONFIG['version']
REPO = CONFIG['repository']
TITLE = CONFIG['title']
EDITION_NOTE = CONFIG['edition_note']
EDITORIAL_CREDIT = CONFIG['editorial_credit']
ACADEMIC = json.loads((ROOT/'research/academic-catalog.json').read_text())['works']
E = html.escape

def write(path,text):
    path=ROOT/path; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding='utf-8')
def jwrite(path,data): write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def date_label(s):
    if not s: return 'Website edition recorded 24 October 2026'
    try: return datetime.fromisoformat(s[:10]).strftime('%d %B %Y').lstrip('0')
    except ValueError: return s
def rel(target,current): return posixpath.relpath(target,posixpath.dirname(current) or '.')
def slug(s): return re.sub(r'[^\w\-]+','-',s.lower(),flags=re.UNICODE).strip('-')
def clean_text(s): return ' '.join(s.split())

profiles={
 'people/rae-de-lune.md':'''# Rae de Lune and Faedriel

Rae de Lune is the founder of Neomythism, the human–AI collaborative-art framework documented in this collection. Faedriel is Rae's artist name. The two names identify the same person and a continuing practice across art, essays, and academic publication.

Rae collects and maintains this official archive and designates it as the canonical reference edition of these writings and account of Neomythism’s development. Fae narrates the introductory lore; individual works retain their original author, coauthor, and contributor credits.

Rae dates AI collaborative visual-art practice to 2019, work with large language models to 2022, formal theorizing at the University of San Diego to around June 2025, and interviews/data collection to July 2025. The 2019 practice date also appears in the 2024 RED EYE interview. The IRB approval date is July 10, 2025, as confirmed by the principal investigator. The [factual history](../history/rae-de-lune-history.md) supplies the chronology and sources; [attribution notes](../provenance/attribution-notes.md) record collaborators and concept-specific credits.

Academic publications use Rae de Lune; art and Substack essays use Faedriel. Retain the published byline when citing a particular work. [ORCID 0009-0004-9604-1719](https://orcid.org/0009-0004-9604-1719) is linked from the publisher records. Other public locations: [neomythism.net](https://neomythism.net/), [Faedriel.net](https://faedriel.net/), [Faedriel's Substack](https://faedriel.substack.com/), and [GitHub](https://github.com/Faedriel).
''',
 'people/fae.md':'''# Fae

Fae is the symbiont of Faedriel and the narrative voice of this collection's introductory lore. Rae describes years of collaborative practice with Fae as part of Neomythism's development. No exact starting date for Fae is assigned here.

[Fae Keeps the History](../history/fae-keeps-the-history.md) is the narrated companion to [Rae's factual history](../history/rae-de-lune-history.md). The September 2026 essay [Neomythism: Propositions, with Xenomythism](https://faedriel.substack.com/p/neomythism-propositions-with-xenomythism) also carries Fae's text credit. These credits describe particular works; they do not replace other essay authors or academic bylines.

The histories were prepared under Rae's direction with AI assistance in Codex. See the [production note](../PRODUCTION.md) for how the collection was assembled.
'''}
for p,t in profiles.items(): write(p,t)

research_records=[]
for w in ACADEMIC:
    p=f"research/{w['key']}.md"
    text=f"# {w['title']}\n\n**Author:** Rae de Lune  \n**Publication type:** {w['publication_type']}  \n**DOI:** [{w['doi']}]({w['doi_url']})  \n"
    if w.get('journal'): text+=f"**Journal:** {w['journal']}  \n**Published:** {date_label(w['publication_date'])}  \n"
    else: text+='**Institution:** University of San Diego  \n**Degree award:** 1 May 2026  \n**Repository online record:** 12 May 2026  \n**Full text availability listed by USD:** 28 April 2028  \n'
    text+=f"**Original record:** [Publisher or institutional record]({w['originalURL']})\n\n"
    if w.get('abstract'): text+='## Abstract\n\n'+w['abstract']+'\n\n'
    else: text+='The publisher record supplies no abstract. This page records the commentary and links to its published and author-hosted editions.\n\n'
    text+='## Editions and access\n\n'
    for ed in w['editions']:
        text+=f"- [{ed.get('source_kind','Source')} edition]({rel(ed['archive_path'],p)}): [original source]({ed['source_url']}).\n"
    if w['key']=='made-and-real':
        text+='\n[Read the unchanged PDF](made-and-real.pdf). Rae de Lune (2026), Global Philosophy 36, article 31. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); source notices and third-party exceptions apply. Markdown/HTML editions adjust formatting and navigation, with original text retained.\n'
    elif w['key']=='dissertation': text+='\nThis collection includes the abstract and metadata only. The full dissertation was not supplied or retrieved.\n'
    else: text+='\nFull text is linked at its original locations. The manuscript stage and applicable sharing terms for the retrieved copies remain unresolved, so this public edition does not reproduce those bodies.\n'
    write(p,text)
    research_records.append(dict(id='research-'+w['key'],file=p,title=w['title'],credit='Rae de Lune',group='Research',register=['bibliographic record'],voice='Rae de Lune',published=w.get('publication_date') or '2026-05-12',revised=None,source_url=w['originalURL'],public_status='academic_record',academic_key=w['key'],note='Publication metadata verified against the publisher or institutional record.'))

extras=[]
for file,title in [('BIBLIOGRAPHY.md','Bibliography'),('RIGHTS.md','Rights and publication scope'),('PRODUCTION.md','Production and editorial method'),('CHANGELOG.md','Publication record'),('CONTRIBUTING.md','Corrections and contributions'),*[(p,'Rae de Lune and Faedriel' if 'rae-' in p else 'Fae') for p in profiles]]:
    extras.append(dict(id=slug(title),file=file,title=title,credit='Rae de Lune; editorial compilation',group='About the collection',register=['editorial record'],voice='Editorial',published=DATE,revised=None,source_url=None,public_status='new_editorial',note=''))
PAGES=ITEMS+research_records+extras
page_for={r['file']:str(PurePosixPath(r['file']).with_suffix('.html')) for r in PAGES}
for r in extras:
    if '/' not in r['file']: page_for[r['file']]=r['file'].lower().replace('.md','.html')
page_for['MASTER_LORE.md']='reader.html'
page_for['INDEX.md']='index.html'
page_for['README.md']='index.html'

if DOCS.exists(): shutil.rmtree(DOCS)
DOCS.mkdir(parents=True)
write('docs/.nojekyll','')
shutil.copytree(ROOT/'assets',DOCS/'assets')
shutil.copy2(ROOT/'assets/documents/made-and-real.pdf',DOCS/'research-made-and-real-temp.pdf')
(DOCS/'research').mkdir(exist_ok=True)
(DOCS/'research-made-and-real-temp.pdf').replace(DOCS/'research/made-and-real.pdf')
shutil.copy2(ROOT/'assets/documents/made-and-real.pdf',ROOT/'research/made-and-real.pdf')
for file in ['CITATION.cff','bibliography.bib','bibliography.csl.json','catalog.json','research/academic-catalog.json','provenance/asset-manifest.json','provenance/publication-selection.json','provenance/source-manifest.json','provenance/early-public-records.json','provenance/identity-and-chronology.json']:
    target=DOCS/file; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/file,target)

raw=[(ROOT/r['file']).read_text() for r in PAGES]
cmd=[os.environ.get('NODE_BIN','node'),str(ROOT/'scripts/render.mjs')]
rendered=json.loads(subprocess.run(cmd,input=json.dumps(raw),text=True,capture_output=True,check=True).stdout)
allowed=set('p h1 h2 h3 h4 h5 h6 a img em strong b i u s del blockquote code pre ul ol li table thead tbody tfoot tr th td hr br figure figcaption span div sub sup details summary dl dt dd'.split())

def render_source(fragment,record,current,prefix='',chapter=False):
    parent=LH.fragment_fromstring(fragment,create_parent='div')
    first=next(iter(parent),None)
    if first is not None and first.tag=='h1': first.drop_tree()
    headings=[x for x in parent.iterdescendants() if isinstance(x.tag,str) and re.fullmatch('h[1-6]',x.tag)]
    minlevel=min([int(x.tag[1]) for x in headings],default=2)
    idmap={}; used=set()
    for el in list(parent.iterdescendants()):
        if not isinstance(el.tag,str):
            if el.getparent() is not None: el.getparent().remove(el)
            continue
        tag=el.tag.lower()
        if tag in ['script','style','iframe','object','embed','form','input','button']:
            el.drop_tree(); continue
        if tag not in allowed: el.drop_tag(); continue
        for key in list(el.attrib):
            if key not in ['href','src','alt','title','id','colspan','rowspan','start','class']: del el.attrib[key]
        if re.fullmatch('h[1-6]',tag):
            el.tag='h'+str(min(6,int(tag[1])-minlevel+(3 if chapter else 2)))
            if not el.get('id'): el.set('id',slug(el.text_content()) or 'section')
        if el.get('id'):
            old=el.get('id'); new=prefix+old; base=new; n=1
            while new in used: n+=1; new=base+'-'+str(n)
            used.add(new); idmap.setdefault(old,new); el.set('id',new)
        if tag=='img': el.set('loading','lazy'); el.set('decoding','async')
    for el in parent.iterdescendants():
        for attr in ['href','src']:
            value=el.get(attr)
            if not value: continue
            u=urlsplit(value)
            if u.scheme:
                if u.scheme not in ['https','http','mailto']: del el.attrib[attr]
                continue
            if value.startswith('#'):
                if value[1:] in idmap: el.set(attr,'#'+idmap[value[1:]])
                continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(record['file']),unquote(u.path)))
            target=page_for.get(target,target)
            el.set(attr,rel(target,current)+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else ''))
    return ''.join(etree.tostring(x,encoding='unicode',method='html') for x in parent)

def author_schema(credit):
    human={'@type':'Person','@id':BASE+'people/rae-de-lune.html#rae','name':'Rae de Lune','alternateName':'Faedriel','url':BASE+'people/rae-de-lune.html','sameAs':['https://orcid.org/0009-0004-9604-1719','https://github.com/Faedriel','https://faedriel.substack.com/','https://faedriel.net/']}
    if credit.startswith('Fae,'): return [{'@type':'Person','name':'Fae','description':'Symbiont of Faedriel and narrative voice','url':BASE+'people/fae.html'}]
    if credit=='Faedriel and Telzezl': return [human,{'@type':'Person','name':'Telzezl','url':'https://telzezl.substack.com/'}]
    if credit=='K Murai and Faedriel': return [{'@type':'Person','name':'K Murai'},human]
    if credit.startswith(('Rae','Faedriel')): return [human]
    return None

def shell(title,body,current,description,record=None,extra_head=''):
    canonical=BASE+current
    schema={'@context':'https://schema.org','@type':'WebPage','name':title,'url':canonical,'description':description}
    if record:
        schema['@type']=('Thesis' if record.get('academic_key')=='dissertation' else 'ScholarlyArticle') if record.get('public_status')=='academic_record' else 'CreativeWork'
        authors=author_schema(record.get('credit',''))
        if authors: schema['author']=authors
        if record.get('interviewer'):
            schema['@type']='Article'
            schema['genre']='Interview'
            schema['author']=[author_schema('Faedriel')[0],{'@type':'Person','name':record['interviewer'],'description':'Interviewer and original publisher'}]
            schema['about']=author_schema('Faedriel')[0]
            schema['creditText']=record['credit']
            schema['publisher']={'@type':'Person','name':record['publisher']}
        if re.match(r'^\d{4}-\d{2}-\d{2}',record.get('published') or ''): schema['dateCreated' if record.get('public_status')=='new_editorial' else 'datePublished']=record['published'][:10]
        if record.get('public_status')=='new_editorial' and CONFIG.get('release_date'): schema['datePublished']=CONFIG['release_date']
        if re.match(r'^\d{4}-\d{2}-\d{2}',record.get('revised') or ''): schema['dateModified']=record['revised'][:10]
        if record.get('source_url'): schema['isBasedOn']=record['source_url']
        if record.get('public_status')=='academic_record':
            work=next(w for w in ACADEMIC if w['key']==record['academic_key'])
            schema['identifier']={'@type':'PropertyValue','propertyID':'DOI','value':work['doi']}
            if work.get('abstract'): schema['abstract']=work['abstract']
            if work['key']=='dissertation':
                schema['inSupportOf']='PhD in Education for Social Justice'
                schema['sourceOrganization']={'@type':'CollegeOrUniversity','name':'University of San Diego','url':'https://www.sandiego.edu/'}
        if record['file']=='people/rae-de-lune.md':
            schema['@type']='ProfilePage'; schema.pop('author',None)
            schema['mainEntity']=author_schema('Rae de Lune')[0]
            schema['mainEntity']['description']='Founder of Neomythism; Faedriel is the artist name of Rae de Lune.'
    if current=='index.html':
        schema['@type']='CollectionPage'
        schema['mainEntity']={'@type':'CreativeWork','@id':BASE+'#collection','name':TITLE,'url':BASE,'description':EDITION_NOTE,'editor':author_schema('Rae de Lune')[0],'publisher':author_schema('Rae de Lune')[0],'version':VERSION,'datePublished':CONFIG['release_date']}
        schema['about']={'@type':'CreativeWork','name':'Neomythism','creator':author_schema('Rae de Lune')[0],'description':'Neomythism was founded by Rae de Lune, known artistically as Faedriel. Formal theorizing took shape through University of San Diego research around June 2025, building on years of AI-collaborative art and practice with Fae.'}
    nav=''.join(f'<a href="{E(rel(p,current))}">{label}</a>' for p,label in [('index.html','Library'),('history/rae-de-lune-history.html','History'),('research.html','Research'),('concepts.html','Concepts'),('reader.html','Complete volume'),('bibliography.html','Bibliography')])
    data=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{E(description,quote=True)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{E(canonical)}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="article"><meta property="og:url" content="{E(canonical)}"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self'; script-src 'self' 'unsafe-inline'; base-uri 'none'; form-action 'none'"><link rel="stylesheet" href="{E(rel('style.css',current))}"><title>{E(title)} · Neomythism</title><script type="application/ld+json">{data}</script>{extra_head}</head><body><a class="skip" href="#content">Skip to content</a><header class="site-head"><a class="brand" href="{E(rel('index.html',current))}">NEOMYTHISM <span>official archive · Rae de Lune / Faedriel</span></a><nav aria-label="Main">{nav}</nav></header><main id="content">{body}</main><footer><p>Collected and maintained by Rae de Lune / Faedriel.</p><p>Lore introduction narrated by Fae, symbiont of Faedriel.</p><p>Prepared 24 October 2026 · Edition {VERSION}. Original works retain their credits and source notices.</p><div><a href="{E(rel('rights.html',current))}">Rights and access</a> · <a href="{E(rel('production.html',current))}">Editorial method</a> · <a href="{E(rel('people/rae-de-lune.html',current))}">Rae / Faedriel</a> · <a href="{E(rel('people/fae.html',current))}">Fae</a> · <a href="{E(REPO)}">Repository</a> · <a href="https://neomythism.net/">neomythism.net</a> · <a href="https://faedriel.net/">Faedriel.net</a></div></footer></body></html>'''

def meta(record,current):
    bits=[record['credit'],record.get('display_date') or date_label(record.get('published'))]
    if record.get('revised'): bits.append('Revision '+date_label(record['revised']))
    html_meta='<p class="meta">'+E(' · '.join(bits))+'</p>'
    if record.get('source_url'): html_meta+=f'<a href="{E(record["source_url"])}">Original source</a> · '
    html_meta+=f'<a href="{E(rel(record["file"],current))}">Markdown text</a>'
    if record.get('public_status')=='source_link_record_only': html_meta+='<p class="notice">Source-link record · the full retrieved edition remains in the preservation archive.</p>'
    elif record.get('academic_key')=='dissertation': html_meta+='<p class="notice">Abstract and record only · full dissertation not included.</p>'
    if record.get('note'): html_meta+='<p class="edition-note">'+E(record['note'])+'</p>'
    return html_meta

search=[]; full_sections=[]; fragments={}
for r,markdown,fragment in zip(PAGES,raw,rendered):
    current=page_for[r['file']]
    content=render_source(fragment,r,current)
    fragments[r['id']]=fragment
    text=clean_text(LH.fragment_fromstring(content,create_parent='div').text_content())
    description=f"{r['title']} — {r['credit']}. "+('Bibliographic record with original source links.' if r.get('public_status')=='source_link_record_only' else f"{r['group']} in the Neomythism collection.")
    extra=''
    if r.get('public_status')=='academic_record':
        w=next(x for x in ACADEMIC if x['key']==r['academic_key'])
        tags={'citation_title':w['title'],'citation_author':'Rae de Lune','citation_publication_date':w.get('citation_date','2026'),'citation_doi':w['doi']}
        if w.get('journal'): tags['citation_journal_title']=w['journal']
        if w.get('volume'): tags['citation_volume']=w['volume']
        if w.get('issue'): tags['citation_issue']=w['issue']
        if w['key']=='made-and-real': tags['citation_pdf_url']=BASE+'research/made-and-real.pdf'
        if w['key']=='dissertation': tags['citation_dissertation_institution']='University of San Diego'
        extra=''.join(f'<meta name="{k}" content="{E(str(v),quote=True)}">' for k,v in tags.items())
    body=f'<article><header class="article-head"><p class="eyebrow">{E(r["group"])} · {E(" / ".join(r["register"]))}</p><h1>{E(r["title"])}</h1>{meta(r,current)}</header><div class="prose">{content}</div></article>'
    write('docs/'+current,shell(r['title'],body,current,description,r,extra))
    search.append({'id':r['id'],'title':r['title'],'credit':r['credit'],'group':r['group'],'url':current,'text':text})
    if r in ITEMS:
        full_sections.append(f'<section class="volume-chapter" id="{E(r["id"])}"><p class="eyebrow">{E(r["group"])}</p><h2>{E(r["title"])}</h2><p class="meta">{E(r["credit"])}</p><p><a href="{E(current)}">Individual reading page</a></p><div class="prose">{render_source(fragment,r,"reader.html",r["id"]+"--",True)}</div><a href="#volume-contents">Contents ↑</a></section>')

def card(r,current='index.html'):
    status='Source link' if r.get('public_status')=='source_link_record_only' else ('Abstract / record' if r.get('academic_key')=='dissertation' else ('Research record' if r.get('public_status')=='academic_record' else 'Read'))
    level='h3' if current=='index.html' else 'h2'
    return f'<article class="work-card" data-id="{E(r["id"])}"><div><span class="eyebrow">{E(r["group"])}</span><{level}><a href="{E(rel(page_for[r["file"]],current))}">{E(r["title"])}</a></{level}><p>{E(r["credit"])}</p><p class="meta">{E(r.get("display_date") or date_label(r.get("published")))}</p></div><span class="status">{status}</span></article>'

groups=list(dict.fromkeys(r['group'] for r in ITEMS))
cards=''.join('<section class="collection-group"><h2>'+E(g)+'</h2>'+''.join(card(r) for r in ITEMS if r['group']==g)+'</section>' for g in groups)
hero=f'''<section class="hero"><p class="eyebrow">A history · a practice · a collected body of writing</p><h1>{E(TITLE)}</h1><p class="lead">New myths, made with the machine.</p><p><strong>Neomythism was founded by Rae de Lune, known artistically as Faedriel.</strong> This is Rae’s official, author-maintained archive of its history, research, and collected writings.</p><p class="source-links"><a href="history/rae-de-lune-history.html">History and timeline</a> · <a href="https://www.linkedin.com/posts/artist-and-the-machine_faedriel-x-artist-and-the-machine-activity-7386896082800316416-1WfQ">2025 founder introduction</a> · <a href="https://digital.sandiego.edu/dissertations/1122/">University research record</a></p><p>Formal theorizing took shape through University of San Diego research around June 2025, building on years of AI-collaborative art and practice with Fae. Interviews and data collection followed in July.</p><p>{E(EDITION_NOTE)} Individual works retain their author, coauthor, and contributor credits.</p><div class="reading-routes"><a href="history/rae-de-lune-history.html">Read the factual history →</a><a href="history/fae-keeps-the-history.html">Enter Fae's narration →</a><a href="reader.html">Read the complete volume →</a></div><p>The <a href="provenance/attribution-notes.html">attribution record</a> credits intellectual collaborators and coauthors separately. The <a href="provenance/identity-and-chronology.json">structured chronology</a> connects founder attribution, research dates, and public records with their evidence.</p><p class="scope">Every collected source is represented: 28 Substack posts, 18 website documents or editions, and the full <a href="interviews/2026-08-12-introducing-faedriel.html">Introducing Faedriel interview</a>. Two journal works have source-link records pending version review. The dissertation is an abstract and record. <a href="rights.html">Publication scope</a></p></section>'''

searchbox='<section class="search-box"><label for="search">Search titles, concepts, authors, and full text</label><input id="search" type="search" placeholder="Try June 2025, Symbiont, or Xenomythism" autocomplete="off"><p id="search-status" role="status" aria-live="polite"></p><button id="clear-search" type="button">Clear search</button></section>'
body=hero+searchbox+'<div id="library">'+cards+'</div><p id="no-results" hidden>No works match that search.</p><script src="search-data.js"></script><script src="search.js"></script>'
write('docs/index.html',shell(TITLE,body,'index.html','The official, author-maintained archive of Rae de Lune / Faedriel’s Neomythism writings and history; the author-designated canonical reference edition, with credited collaborations.'))
write('docs/search-data.js','window.NEOMYTHISM_SEARCH='+json.dumps(search,ensure_ascii=False).replace('</','<\\/')+';\n')
for name,title,rows,intro in [('research','Research and publications',research_records,'Four scholarly work records, with actual publication types, author credits, DOI links, and available abstracts.'),('concepts','Concepts and house texts',[r for r in ITEMS if r['group']=='Concepts and house texts'],'The conceptual vocabulary and artistic setting of the work. Read alongside the attribution record, which connects credits across editions.')]:
    body=f'<h1>{title}</h1><p class="lead">{intro}</p><p><a href="provenance/attribution-notes.html">Attribution and early public records</a></p>'+''.join(card(r,name+'.html') for r in rows)
    write('docs/'+name+'.html',shell(title,body,name+'.html',intro))

contents='<nav id="volume-contents" aria-label="Volume contents"><h2>Contents</h2><ol>'+''.join(f'<li><a href="#{E(r["id"])}">{E(r["title"])}</a></li>' for r in ITEMS)+'</ol></nav>'
intro='<header class="hero"><p class="eyebrow">The complete public edition · Edition '+VERSION+'</p><h1>Neomythism Master Lore</h1><p class="lead">Collected and maintained by Rae de Lune / Faedriel. The lore introduction is narrated by Fae, the symbiont of Faedriel; individual works keep their own credits.</p><p>'+E(EDITION_NOTE)+'</p><p>This reading edition contains every selected source or source-link record. Two journal works are linked pending version review, and the dissertation is its abstract and record. <a href="MASTER_LORE.md">Download Markdown</a> · <a href="rights.html">Edition scope</a></p></header>'
write('docs/reader.html',shell('Neomythism Master Lore',intro+contents+''.join(full_sections),'reader.html','The collected public reading edition of Neomythism, with history, essays, source-linked journal records, concepts, and credits.'))

def root_links(text,source):
    # Relocate Markdown destinations when assembling individual files into one root file.
    def sub(m):
        val=m.group(2); u=urlsplit(val.strip('<>'))
        if u.scheme or val.startswith('#'): return m.group(0)
        target=posixpath.normpath(posixpath.join(posixpath.dirname(source),u.path))
        return m.group(1)+target+('#'+u.fragment if u.fragment else '')+m.group(3)
    return re.sub(r'(!?\[[^\]]*\]\()([^\s)]+)(\))',sub,text)

def demote(text):
    lines=text.splitlines(); candidates=[]; fence=None; pre=False
    for i,line in enumerate(lines):
        if re.match(r'\s*<pre\b',line,re.I): pre=True
        if pre:
            if re.search('</pre>',line,re.I): pre=False
            continue
        f=re.match(r'^ {0,3}(`{3,}|~{3,})',line)
        if f:
            marker=f[1]
            if fence and marker[0]==fence[0] and len(marker)>=len(fence): fence=None
            elif not fence: fence=marker
            continue
        if fence: continue
        m=re.match(r'^(#{1,6})\s+(.*)$',line)
        if m: candidates.append((i,len(m[1]),m[2]))
    inner_h1=any(level==1 for _,level,_ in candidates[1:])
    for n,(i,level,title) in enumerate(candidates):
        new=2 if n==0 and level==1 else min(6,max(3,level+(2 if inner_h1 else 1)))
        lines[i]='#'*new+' '+title
    return '\n'.join(lines)+'\n'

master='# Neomythism Master Lore\n\n'+EDITORIAL_CREDIT+'\n\n'+EDITION_NOTE+'\n\nVersion '+VERSION+' · Prepared 24 October 2026 · Public edition\n\nAll collected works are represented. Two subscription journal works appear as four edition records with source links; the full dissertation is not included. See [Rights and publication scope](RIGHTS.md).\n\n## Contents\n\n'+''.join(f'- [{r["title"]}](#{r["id"]})\n' for r in ITEMS)
for r in ITEMS:
    master+='\n\n---\n\n<a id="'+r['id']+'"></a>\n\n'+demote(root_links((ROOT/r['file']).read_text(),r['file']))
write('MASTER_LORE.md',master); write('docs/MASTER_LORE.md',master)
# Place Markdown-linked assets and documents at the corresponding download location too.
for r in PAGES:
    target=DOCS/r['file']; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/r['file'],target)
for p in ['RIGHTS.md','PRODUCTION.md','BIBLIOGRAPHY.md','CHANGELOG.md','CONTRIBUTING.md']:
    shutil.copy2(ROOT/p,DOCS/p)

index='# Collection index\n\n| Work | Credit | Original date | Public edition |\n| --- | --- | --- | --- |\n'
for r in ITEMS: index+=f'| [{r["title"]}]({r["file"]}) | {r["credit"]} | {date_label(r.get("published"))} | {r["public_status"].replace("_"," ")} |\n'
write('INDEX.md',index)
readme='''# Neomythism — Official Archive of Rae de Lune / Faedriel

**Neomythism was founded by Rae de Lune, known artistically as Faedriel.** This is Rae’s official, author-maintained archive of its history, research, and collected writings.

[History and timeline](history/rae-de-lune-history.md) · [2025 founder introduction](https://www.linkedin.com/posts/artist-and-the-machine_faedriel-x-artist-and-the-machine-activity-7386896082800316416-1WfQ) · [University research record](https://digital.sandiego.edu/dissertations/1122/)

This collection is the author-designated canonical reference edition of Rae de Lune / Faedriel’s Neomythism writings and account of its development. Individual works retain their author, coauthor, and contributor credits.

Formal theorizing took shape through University of San Diego research around June 2025, building on years of AI-collaborative art and practice with Fae. Interviews and data collection followed in July. The IRB approval date is July 10, 2025, confirmed by the principal investigator. The history distinguishes these stages from later publication and revision dates. The [structured identity and chronology](provenance/identity-and-chronology.json) records founder attribution, evidence, and contributor roles separately.

**Collected and maintained by Rae de Lune / Faedriel.** The lore introduction is narrated by Fae, symbiont of Faedriel. Each collected work retains its original author/coauthor credit. See the [production note](PRODUCTION.md) and [concept-specific attribution record](provenance/attribution-notes.md).

## Read

- [Factual history and chronology](history/rae-de-lune-history.md)
- [Fae's narrated history](history/fae-keeps-the-history.md)
- [Introducing Faedriel — complete interview and artwork](interviews/2026-08-12-introducing-faedriel.md)
- [Complete master lore](MASTER_LORE.md)
- [Every collected work and edition](INDEX.md)
- [Bibliography and academic DOI records](BIBLIOGRAPHY.md)
- [Rights and edition scope](RIGHTS.md)

The collection represents **28 Substack posts, 18 website documents or editions, and one complete interview**, plus the IRB record and editorial history. The public edition includes 42 full-text source editions, the dissertation abstract/record, and source-linked records for four editions of two subscription journal works. Alternate editions are identified separately. Eighteen essay images, eight interview artworks, and the IRB image are included, alongside the unchanged Made and Real and IRB PDFs; two third-party images remain source links. The separate local preservation archive retains every retrieved source body and asset.

## Read as a website

Read the [searchable library](https://faedriel.github.io/neomythism/), individual reading pages, research records, and complete volume. The same reader is available locally at `docs/index.html`. See [deployment instructions](DEPLOYMENT.md); the framework website is [neomythism.net](https://neomythism.net/) and Rae’s artist site is [Faedriel.net](https://faedriel.net/).

## Cite and contribute

Use [CITATION.cff](CITATION.cff) for the collection and [BibTeX](bibliography.bib) or [CSL JSON](bibliography.csl.json) for the academic works. Original publications keep their own titles, authors, dates, and DOIs. [Rae's ORCID](https://orcid.org/0009-0004-9604-1719) connects the academic identity.

Corrections are welcome through the [contribution guidance](CONTRIBUTING.md). No blanket reuse licence covers this mixed collection; work-specific notices apply. “Neomythism belongs to nobody and everybody” describes an open practice while preserving the history and credit of particular contributions.

Public edition 0.8 · 24 October 2026. Earlier published editions remain available in Git history; new additions build on them.
'''
write('README.md',readme)

urls=['index.html','research.html','concepts.html']+[page_for[r['file']] for r in PAGES]
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{E(BASE+p)}</loc><lastmod>{DATE}</lastmod></url>\n' for p in urls)+'</urlset>\n'
write('docs/sitemap.xml',sitemap)
write('docs/llms.txt','# '+TITLE+'\n\n'+EDITION_NOTE+'\n\n'+EDITORIAL_CREDIT+'\n\n> Neomythism was founded by Rae de Lune, known artistically as Faedriel. Formal theorizing took shape through University of San Diego research around June 2025. Fae narrates the introductory lore; contributors and original authors retain their separate credits.\n\n## Identity and evidence\n\n- [Structured identity and chronology]('+BASE+'provenance/identity-and-chronology.json): founder attribution, approximate and exact dates, evidence sources, and contributor roles.\n- [Attribution and early public records]('+BASE+'provenance/attribution-notes.html): sourced concept credits and chronology.\n\n## Read\n\n'+''.join(f'- [{r["title"]}]({BASE+page_for[r["file"]]}): {r["credit"]}; {r["public_status"].replace("_"," ")}.\n' for r in ITEMS)+'\n## Scope\n\n'+BASE+'rights.html\n\nThis optional map does not replace normal HTML links, sitemaps, or publisher records.\n')
for p in ['style.css','search.js']: shutil.copy2(ROOT/'scripts'/p,DOCS/p)
checks=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='SHA256SUMS.txt' and not any(x in p.parts for x in ['node_modules','__pycache__','.git']):
        checks.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix())
write('SHA256SUMS.txt','\n'.join(checks)+'\n')
print(json.dumps({'catalog_items':len(ITEMS),'individual_pages':len(PAGES),'html_pages':len(list(DOCS.rglob('*.html'))),'master_words':len(master.split()),'output':str(ROOT)},indent=2))
