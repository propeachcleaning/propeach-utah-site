"""Give every Utah inner page the GA (propeachcleaning.com) design.

Each page = GA's Webflow page frame (head CSS/JS, nav, footer, popups, animations) around the page's OWN Utah
content, restyled into GA's text format (loc-h1 / loc-h2 / loc-p / loc-list / loc-cta), plus the page's Utah
price tables and Utah before/after photos. Utah facts, prices, FAQs and schema are kept; nothing Atlanta-specific
is copied in.

Content source = the hand-built pages saved in tools/legacy/ (created on first run). Edit those to change a
page's words, then re-run:

    python3 tools/build_pages_from_ga.py
"""
import html as H, pathlib, re, shutil, sys
from lxml import html as LH, etree

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_home_from_ga as bh   # shared GA -> Utah frame
import build_ba as ba             # Utah before/after sets per page

LEGACY = ROOT / 'tools' / 'legacy'
SHELL = '/house-cleaning-cost-atlanta'     # a GA text page: nav + loc-section + embeds + footer
BOOK = bh.BK + '/booknow'
DROP_CLASSES = ('pp-crumbs', 'trust-chips', 'own-chips', 'review-badge', 'pp-chiprow', 'cta-section', 'pp-footer',
                'pp-location', 'ppq-wrap', 'ppba', 'page-loader', 'pp-facts-sec-img', 'hero-bottom-strip')
DROP_TAGS = ('script', 'style', 'svg', 'img', 'figure', 'iframe', 'noscript', 'form', 'button', 'nav', 'address')
INLINE = ('a', 'strong', 'b', 'em', 'br')

def cls(el):
    return (el.get('class') or '').split()

def has(el, *names):
    c = cls(el)
    return any(n in c for n in names)

def esc(t):
    return H.escape(t or '', quote=False)

def href(h):
    h = (h or '').strip()
    if h.startswith(('http', 'tel:', 'sms:', 'mailto:', '#', '/')):
        return h
    return '/' + h          # legacy pages used relative links like services-residential

def inline(el):
    """Inner HTML of el keeping only text + simple inline tags (links get GA's loc-link class)."""
    out = [esc(el.text)]
    for c in el:
        tag = c.tag if isinstance(c.tag, str) else ''
        if tag in DROP_TAGS or (tag and has(c, 'trust-icon', 'own-icon', 'ppq-ico')):
            out.append(esc(c.tail)); continue
        if tag == 'a':
            out.append(f'<a href="{H.escape(href(c.get("href")))}" class="loc-link"'
                       + (' target="_blank" rel="noopener"' if c.get('target') == '_blank' else '') + f'>{inline(c)}</a>')
        elif tag in ('strong', 'b'):
            out.append(f'<strong>{inline(c)}</strong>')
        elif tag == 'em':
            out.append(f'<em>{inline(c)}</em>')
        elif tag == 'br':
            out.append('<br>')
        else:
            out.append(inline(c))
        out.append(esc(c.tail))
    return re.sub(r'\s+', ' ', ''.join(out)).strip()

def text(el):
    return re.sub(r'\s+', ' ', el.text_content()).strip()

class Conv:
    def __init__(self):
        self.out, self.lead_pending = [], False

    def emit(self, s):
        if s:
            self.out.append(s)

    def p(self, inner):
        if not inner:
            return
        if self.lead_pending:
            self.emit(f'<p class="loc-lead">{inner}</p>'); self.lead_pending = False
        else:
            self.emit(f'<p class="loc-p">{inner}</p>')

    def walk(self, el):
        if not isinstance(el.tag, str):
            return
        tag = el.tag
        # titles that live inside buttons / accordion headers (checked before buttons are dropped)
        if tag == 'button' and has(el, 'sa-trigger'):
            t = el.find('.//*[@class="sa-title"]')
            self.emit(f'<h2 class="loc-h2">{esc(text(t) if t is not None else text(el))}</h2>'); return
        if tag == 'button' and has(el, 'faq-group-toggle'):
            sp = el.find('span')
            self.emit(f'<h2 class="loc-h2">{esc(text(sp) if sp is not None else text(el))}</h2>'); return
        if has(el, 'accordion-header'):
            self.emit(f'<h3 class="loc-h3">{esc(text(el))}</h3>'); return
        if has(el, 'pp-facts'):                                # quick facts -> labeled list
            items = []
            for d in el:
                if not isinstance(d.tag, str):
                    continue
                lab, val = d.find('span'), d.find('strong')
                if lab is not None and val is not None:
                    items.append(f'<li class="loc-li"><strong>{esc(text(lab))}:</strong> {inline(val)}</li>')
            if items:
                self.emit('<ul role="list" class="loc-list">' + ''.join(items) + '</ul>')
            return
        if tag in DROP_TAGS or has(el, *DROP_CLASSES):
            return
        if tag == 'h1':
            self.emit(f'<h1 class="loc-h1">{inline(el)}</h1>'); self.lead_pending = True; return
        if tag == 'h2':
            self.emit(f'<h2 class="loc-h2">{inline(el) or esc(text(el))}</h2>'); self.lead_pending = False; return
        if tag in ('h3', 'h4', 'h5', 'h6'):
            self.emit(f'<h3 class="loc-h3">{inline(el) or esc(text(el))}</h3>'); return
        if tag == 'p':
            links = [a for a in el if isinstance(a.tag, str) and a.tag == 'a']
            loose = (el.text or '').strip() + ''.join((a.tail or '').strip() for a in links)
            if len(links) >= 2 and not loose:                 # a row of buttons/links -> "A · B · C"
                self.emit('<p class="loc-p">' + ' · '.join(
                    f'<a href="{H.escape(href(a.get("href")))}" class="loc-link">{esc(text(a))}</a>' for a in links) + '</p>')
                return
            self.p(inline(el)); return
        if tag in ('ul', 'ol'):
            items = [f'<li class="loc-li">{inline(li) if not li.xpath(".//p|.//h3|.//h4|.//ul") else esc(text(li))}</li>'
                     for li in el if isinstance(li.tag, str) and li.tag == 'li' and text(li)]
            if items:
                self.emit('<ul role="list" class="loc-list">' + ''.join(items) + '</ul>')
            return
        if tag == 'details':                                   # FAQ item
            s = el.find('summary')
            if s is not None:
                self.emit(f'<h3 class="loc-h3">{inline(s)}</h3>'); s.drop_tree()
            for c in el:
                self.walk(c)
            self.loose_text(el); return
        if has(el, 'pp-cards'):                                # link cards -> list of links
            items = []
            for card in el.iter():
                if not isinstance(card.tag, str) or not has(card, 'pp-card'):
                    continue
                link = card if card.tag == 'a' else card.find('.//a')
                title = card.find('.//h3') if card.find('.//h3') is not None else card.find('.//h4')
                desc = card.find('.//p')
                t = text(title) if title is not None else (text(link) if link is not None else '')
                if not t:
                    continue
                lead = f'<a href="{H.escape(href(link.get("href")))}" class="loc-link">{esc(t)}</a>' if link is not None else f'<strong>{esc(t)}</strong>'
                items.append(f'<li class="loc-li">{lead}' + (f': {inline(desc)}' if desc is not None and text(desc) else '') + '</li>')
            if items:
                self.emit('<ul role="list" class="loc-list">' + ''.join(items) + '</ul>')
            return
        if has(el, 'pp-pills'):                                # city / area links
            links = [f'<a href="{H.escape(href(a.get("href")))}" class="loc-link">{esc(text(a))}</a>' for a in el.iter('a')]
            self.emit('<p class="loc-p">' + ' · '.join(links) + '</p>'); return
        if tag == 'a' and (has(el, 'btn-primary', 'pp-hero-btn', 'pp-btn') or 'book' in (el.get('href') or '')):
            if text(el):
                self.emit(f'<a href="{H.escape(href(el.get("href")))}" class="loc-btn">{esc(text(el))}</a>')
            return
        if tag == 'table':                                     # non-price tables -> simple list
            rows = [' – '.join(esc(text(td)) for td in tr if isinstance(td.tag, str)) for tr in el.iter('tr')]
            rows = [r for r in rows if r.strip(' –')]
            if rows:
                self.emit('<ul role="list" class="loc-list">' + ''.join(f'<li class="loc-li">{r}</li>' for r in rows) + '</ul>')
            return
        if tag == 'a':
            if text(el):
                self.p(f'<a href="{H.escape(href(el.get("href")))}" class="loc-link">{esc(text(el))}</a>')
            return
        # container: recurse; collect stray text
        self.loose_text(el, head_only=True)
        for c in el:
            self.walk(c)
            if c.tail and c.tail.strip() and el.tag not in ('ul', 'ol', 'table', 'tr'):
                self.p(esc(c.tail.strip()))

    def loose_text(self, el, head_only=False):
        if el.text and el.text.strip():
            self.p(esc(el.text.strip()))

CTA = (f'<div class="loc-cta"><p class="loc-cta-text">Want your exact price? Book online or call or text '
       f'<a href="tel:{bh.UT_TEL}" class="loc-link">{bh.UT_PHONE}</a>.</p><a href="{BOOK}" class="loc-btn" target="_blank" rel="noopener">Book Online</a></div>'
       '<p class="loc-p loc-small"><a href="/service-areas" class="loc-link">All Utah service areas</a> · '
       '<a href="https://propeachcleaning.com/" class="loc-link">Also serving metro Atlanta, Georgia</a></p>')

def main_content(legacy_html):
    m = re.search(r'<main id="main">(.*)</main>', legacy_html, re.S)
    frag = LH.fromstring('<div>' + (m.group(1) if m else '') + '</div>')
    c = Conv()
    for el in frag:
        c.walk(el)
    blocks = c.out
    # de-duplicate consecutive identical blocks (legacy pages repeat some CTAs)
    dedup = [b for i, b in enumerate(blocks) if i == 0 or b != blocks[i - 1]]
    return '<section class="loc-section"><div class="loc-wrap">' + ''.join(dedup) + CTA + '</div></section>'

def ppq_embed(legacy_html):
    m = re.search(r'<section class="ppq-wrap"[^>]*>(.*?)</section><!-- /ppq -->', legacy_html, re.S)
    if not m:
        m = re.search(r'<section class="ppq-wrap"[^>]*>(<div class="ppq-tables">.*?</div>)\s*</section>', legacy_html, re.S)
    return f'<div class="w-embed">{m.group(1).strip()}</div>' if m else ''

def ppba_embed(name):
    if name not in ba.PAGES:
        return ''
    keys, sub = ba.PAGES[name]
    return '<div class="w-embed">' + bh.ppba_html(tuple(keys), sub) + '</div>'

def build_page(name, shell_src):
    legacy_path = LEGACY / name
    legacy = legacy_path.read_text()
    meta = bh.utah_head_meta(str(legacy_path))
    block = main_content(legacy) + ppq_embed(legacy) + ppba_embed(name)

    def hook(body):   # cut GA's page content (between the top bar spacer and the footer); mark the spot
        i = body.find('<section class="loc-section">')
        j = body.find('<section class="section footer">')
        return body[:i] + '@@UTAHMAIN@@' + body[j:] if i != -1 and j != -1 else body

    out = bh.convert(shell_src, meta, hook)
    out = out.replace('@@UTAHMAIN@@', block)     # inserted after GA link-mapping so Utah links stay Utah
    (ROOT / name).write_text(out)
    body = out[out.find('<body'):]
    nloc = block.count('class="loc-')
    n470 = body.count('470) 412')
    print(f'{name:46} {len(out):6} bytes  loc blocks:{nloc}  ppq:{bool(ppq_embed(legacy))}  ppba:{name in ba.PAGES}  470:{n470}')

def main(names=None):
    LEGACY.mkdir(exist_ok=True)
    pages = sorted(p.name for p in ROOT.glob('*.html') if p.name not in ('index.html',) and not p.name.startswith('_'))
    for n in pages:                                       # snapshot hand-built pages once (content source)
        if not (LEGACY / n).exists():
            shutil.copy(ROOT / n, LEGACY / n)
    shell = bh.get(bh.GA + SHELL).decode('utf-8')
    for n in (names or pages):
        build_page(n, shell)
    bh.prune_vendor()

if __name__ == '__main__':
    main(sys.argv[1:] or None)
