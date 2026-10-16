"""Build the Utah homepage (index.html) from the LIVE Georgia homepage (propeachcleaning.com, Webflow).

Same layout, styles, fonts, Webflow animations (rolling cart) and popups as GA; Utah phone, wording, links,
photos (never GA's), before/after set, schema and lead handling. Re-run any time to re-sync with GA:

    python3 tools/build_home_from_ga.py

Webflow CSS/JS are vendored into /vendor so Utah keeps working even if GA republishes.
Popup + newsletter forms post to a Make webhook (GA's Webflow forms only work on GA's domain).
"""
import html as H, json, pathlib, re, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
GA = 'https://propeachcleaning.com'
BK = 'https://propeachcleaning.bookingkoala.com'
HOOK = 'https://hook.us2.make.com/spb46zymblfw212vedyp5pevqlmgmayw'
UT_PHONE, UT_TEL = '(385) 217-9244', '+13852179244'
GA_CID, UT_CID = 'cid=16449210000793791146', 'cid=8996771839070111800'

# Utah photos (never shared with GA). Reviews + H1-banner photos are owner-locked.
IMG = {
    'hero': '/images/pro-peach-utah-living-room-real.jpg',          # real job photo
    'h1banner': '/images/pro-peach-utah-clean-living-room-windows.jpg',  # owner-locked
    'section3': '/images/utah-3.jpg',                               # real Utah hallway
    'reviews': '/images/pro-peach-utah-bright-living-room.jpg',     # owner-locked
}

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Pro Peach Utah sync)'})
    return urllib.request.urlopen(req, timeout=60).read()

def vendor(url):
    """Download a GA Webflow asset into /vendor and return its local path."""
    name = re.sub(r'[^A-Za-z0-9._-]', '_', url.split('/')[-1].split('?')[0])
    (ROOT / 'vendor').mkdir(exist_ok=True)
    (ROOT / 'vendor' / name).write_bytes(get(url))
    return '/vendor/' + name

def utah_head_meta():
    """Title, description, canonical, OG/Twitter, favicons and JSON-LD from the previous Utah homepage."""
    old = (ROOT / 'tools' / 'legacy-index.html').read_text()
    head = old[old.find('<head>'):old.find('</head>')]
    keep = re.findall(r'<title>.*?</title>|<meta (?:name="(?:description|twitter:[^"]+)"|property="og:[^"]+")[^>]*>|'
                      r'<link rel="(?:canonical|icon|apple-touch-icon)"[^>]*>|<script type="application/ld\+json">.*?</script>',
                      head, flags=re.S)
    meta = '\n'.join(keep)
    meta = meta.replace('images/pro-peach-utah-living-room-hero.jpg', IMG['hero'].lstrip('/'))
    meta = meta.replace('href="favicon', 'href="/favicon').replace('href="apple-touch', 'href="/apple-touch')
    return meta

def ppba_html():
    """Utah before/after card in GA's embed markup (inline CSS, like the GA embed)."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import build_ba as ba
    ga_ppba = ROOT.parent / 'pro-peach-ga-webflow' / 'ppba.py'
    css = re.search(r"CSS = \((.*?)\)\nSUB", ga_ppba.read_text(), re.S)
    css = eval('(' + css.group(1) + ')') if css else ''
    keys = ['oven', 'fridge', 'shower', 'stove']
    figs = ''.join(
        f'<figure class="ppba-pair"><div class="ppba-ba">'
        f'<div class="ppba-shot"><span class="ppba-tag">Before</span><img src="/images/ba/{ba.P[k][1]}-before.webp" width="520" height="693" alt="Before a Pro Peach cleaning: {ba.P[k][2]}" loading="lazy" decoding="async"></div>'
        f'<div class="ppba-shot"><span class="ppba-tag a">After</span><img src="/images/ba/{ba.P[k][1]}-after.webp" width="520" height="693" alt="After a Pro Peach cleaning: {ba.P[k][3]}" loading="lazy" decoding="async"></div>'
        f'</div><figcaption><b>{ba.P[k][0]}</b></figcaption></figure>' for k in keys)
    return (f'<div class="ppba" style="padding-top:48px">{css}<section class="ppba-card" aria-label="Before and After">'
            f'<p class="ppba-kicker">Real results</p><h2 class="ppba-title">Before and After</h2>'
            f'<p class="ppba-sub">{ba.SUB["home"]}</p><div class="ppba-grid">{figs}</div></section></div>')

LOC = '''<section class="loc-section"><div class="loc-wrap"><h2 class="loc-h2">House Cleaning Services in Salt Lake City &amp; the Salt Lake Valley</h2><p class="loc-p">Pro Peach Cleaning is a women-, veteran- and Latino-owned house cleaning company serving Salt Lake City and the surrounding valley. Pick the clean that fits your home: <a href="/services-residential" class="loc-link">standard cleaning</a> for recurring upkeep, <a href="/deep-cleaning-salt-lake-city" class="loc-link">deep cleaning</a> for a top-to-bottom reset, <a href="/move-out-cleaning-salt-lake-city" class="loc-link">move-in / move-out cleaning</a> for empty homes, and <a href="/airbnb-cleaning-salt-lake-city" class="loc-link">Airbnb and vacation rental cleaning</a> between guests. See <a href="/house-cleaning-cost-salt-lake-city" class="loc-link">what house cleaning costs in Salt Lake City</a>.</p><h2 class="loc-h2">Popular Areas We Clean</h2><p class="loc-p"><a href="/house-cleaning-salt-lake-city" class="loc-link">Salt Lake City</a> · <a href="/house-cleaning-sugar-house" class="loc-link">Sugar House</a> · <a href="/house-cleaning-millcreek-ut" class="loc-link">Millcreek</a> · <a href="/house-cleaning-holladay-ut" class="loc-link">Holladay</a> · <a href="/house-cleaning-murray-ut" class="loc-link">Murray</a> · <a href="/house-cleaning-cottonwood-heights-ut" class="loc-link">Cottonwood Heights</a> · <a href="/house-cleaning-south-salt-lake-ut" class="loc-link">South Salt Lake</a> · <a href="/service-areas" class="loc-link">All service areas</a></p><h2 class="loc-h2">Moving, Hosting or Running a Business?</h2><p class="loc-p">See <a href="/move-out-cleaning-cost-salt-lake-city" class="loc-link">move-out cleaning cost</a>, <a href="/deep-cleaning-cost-salt-lake-city" class="loc-link">deep cleaning cost</a> and <a href="/office-cleaning-cost-salt-lake-city" class="loc-link">office cleaning cost</a>. Also serving <a href="https://propeachcleaning.com/" class="loc-link">metro Atlanta, Georgia</a>.</p></div></section>'''

FAQ_AREAS = ('We serve Salt Lake City and the Salt Lake Valley, including Sugar House, Millcreek, Holladay, Murray, '
             'Cottonwood Heights and South Salt Lake. We also serve metro Atlanta, Georgia. Contact us to confirm availability for your address.')
FOOT_HOURS = ('Open 7 days a week, 8 AM to 8 PM. Pro Peach Cleaning serves homes and businesses across Salt Lake City, Utah, '
              'plus Georgia from metro Atlanta to the Athens &amp; UGA area, out to metro Savannah and metro Augusta. '
              'We come to you, so there’s no storefront to visit. Questions? Email clean@propeachcleaning.com.')

LINKS = {'/': '/', '/services/residential': '/services-residential', '/services/commercial': '/services-commercial',
         '/services/construction': '/services-construction', '/services/airbnb-cleaning': '/airbnb-cleaning-salt-lake-city',
         '/faq/frequently-asked-questions': '/faq', '/service-areas': '/service-areas', '/privacy-policy': '/privacy-policy',
         '/house-cleaning-cost-atlanta': '/house-cleaning-cost-salt-lake-city', '/house-cleaning-atlanta': '/house-cleaning-salt-lake-city',
         '/deep-cleaning-atlanta': '/deep-cleaning-salt-lake-city', '/move-out-cleaning-atlanta': '/move-out-cleaning-salt-lake-city',
         '/move-out-cleaning-cost-atlanta': '/move-out-cleaning-cost-salt-lake-city', '/airbnb-cleaning-atlanta': '/airbnb-cleaning-salt-lake-city',
         '/airbnb-cleaning-cost-atlanta': '/airbnb-cleaning-salt-lake-city', '/booknow': BK + '/booknow', '/login': BK + '/login',
         '/contact': '#contact'}

FORM_JS = '''<script>
/* Utah: popup + newsletter forms post to Make (GA's Webflow forms only work on propeachcleaning.com). */
(function(){var HOOK='%s';
document.addEventListener('submit',function(e){var f=e.target;if(!f||f.tagName!=='FORM')return;
 e.preventDefault();e.stopImmediatePropagation();
 if(!f.checkValidity()){f.reportValidity();return;}
 var p=new URLSearchParams();p.append('form',f.getAttribute('data-name')||f.id||'form');p.append('page',location.href);
 p.append('site','utah.propeachcleaning.com');p.append('submitted_at',new Date().toISOString());
 new FormData(f).forEach(function(v,k){if(!/turnstile|recaptcha/i.test(k))p.append(k,v);});
 var wrap=f.closest('.w-form'),done=wrap&&wrap.querySelector('.w-form-done'),fail=wrap&&wrap.querySelector('.w-form-fail');
 var btn=f.querySelector('[type=submit]');if(btn)btn.disabled=true;
 fetch(HOOK,{method:'POST',mode:'no-cors',body:p}).then(function(){
   f.style.display='none';if(done)done.style.display='block';
   var pop=f.closest('#main-popup,#discount-popup');
   if(pop){try{localStorage.setItem('ppPopupCompleted','true');localStorage.removeItem('ppPopupSuppressedUntil');}catch(x){}
     setTimeout(function(){pop.style.display='none';document.body.style.overflow='';},5000);}
 }).catch(function(){if(fail)fail.style.display='block';if(btn)btn.disabled=false;});
},true);})();
</script>''' % HOOK

CSS_UT = '''<style id="utah-photos">
/* Utah photos (GA and Utah never share a photo) */
.herobg{background-image:linear-gradient(#0006,#0006),url(%(hero)s)!important;background-position:0 0,50%% 55%%!important}
.herowrapper,.container.herowrapper{background-image:url(%(hero)s)!important}
.container.photobg{background-image:url(%(h1banner)s)!important}
.container.photobg.section1{background-image:none!important}
.container.photobg.section3,.container.image{background-image:url(%(section3)s)!important}
</style>''' % IMG

def protect(body):
    """Keep the Atlanta footer card pointing at Atlanta (phone, Google profile, links)."""
    parts = body.split('<div class="pp-loc-card">')
    for i in range(1, len(parts)):
        if 'pp-loc-city">Atlanta<' in parts[i]:
            card = parts[i]
            end = card.find('<div class="pp-loc-card">')
            card = re.sub(r'href="(/[^"]*)"', lambda x: f'href="{GA}{x.group(1)}"', card)
            parts[i] = '@@ATLCARD@@'
            return '<div class="pp-loc-card">'.join(parts), card
    return body, None

def build():
    src = get(GA + '/').decode('utf-8')
    head = src[src.find('<head>') + 6:src.find('</head>')]
    body = src[src.find('</head>') + 7:]
    html_tag = re.search(r'<html[^>]*>', src).group(0).replace('data-wf-domain="propeachcleaning.com"', 'data-wf-domain="utah.propeachcleaning.com"')
    if 'lang=' not in html_tag:
        html_tag = html_tag.replace('<html', '<html lang="en"', 1)

    # ---- head: GA design + scripts, Utah identity
    head = re.sub(r'<title>.*?</title>', '', head, flags=re.S)
    head = re.sub(r'<meta (?:content="[^"]*" )?(?:name|property)="(?:description|og:[^"]+|twitter:[^"]+)"[^>]*>|<meta (?:name|property)="(?:description|og:[^"]+|twitter:[^"]+)"[^>]*>', '', head)
    head = re.sub(r'<link [^>]*rel="(?:canonical|alternate|shortcut icon|apple-touch-icon)"[^>]*>|<link [^>]*hreflang[^>]*/?>', '', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    head = re.sub(r'<script[^>]*src="/[^"]*"[^>]*></script>', '', head)                      # GA-relative scripts
    head = re.sub(r'<script>\(function\(w,i,g\).*?</script>|<script[^>]*GT-WBZ56PJP[^>]*></script>|<script>[^<]*GT-WBZ56PJP[^<]*</script>', '', head, flags=re.S)
    for url in set(re.findall(r'href="(https://cdn\.prod\.website-files\.com/[^"]+\.css)"', head)):
        head = head.replace(url, vendor(url))
    head = '<meta charset="utf-8"/>\n' + utah_head_meta() + '\n' + head + '\n' + CSS_UT

    # ---- body
    for url in set(re.findall(r'src="(https://(?:cdn\.prod\.website-files\.com/[^"]+/js/webflow[^"]+|d3e54v103j8qbb\.cloudfront\.net/js/jquery[^"]+))"', body)):
        body = body.replace(url, vendor(url))
    body = re.sub(r'<script[^>]*src="/(?!vendor/)[^"]*"[^>]*></script>', '', body)   # GA-relative scripts (keep our /vendor copies)
    body = re.sub(r'<script>\s*/\* Language switch.*?</script>', '', body, flags=re.S)
    body = re.sub(r'\s*data-turnstile-sitekey="[^"]*"', '', body)
    body, atl_card = protect(body)

    # phone (script + text + links)
    body = body.replace(r'\(470\)\s?412-9977', r'\(385\)\s?217-9244')
    body = re.sub(r'(tel:|sms:)\+?1?4704129977', lambda m: m.group(1) + UT_TEL, body)
    body = body.replace("'+14704129977'", "'" + UT_TEL + "'").replace('(470) 412-9977', UT_PHONE)

    # Utah wording
    rep = [
        (r"Georgia(?:&#x27;|'|’)s Trusted Cleaning Service", 'Utah’s Trusted Cleaning Service'),
        ('8PM EST', '8PM MT'),
        ('SERVING ATLANTA, ATHENS, SAVANNAH &amp; AUGUSTA', 'SERVING SALT LAKE CITY &amp; THE SALT LAKE VALLEY'),
        ('HOUSE CLEANING IN ATLANTA, GA. LICENSED', 'HOUSE CLEANING IN SALT LAKE CITY, UT. LICENSED'),
        ('METRO ATLANTA TO ATHENS, SAVANNAH &amp; AUGUSTA.', 'SALT LAKE CITY TO MILLCREEK, MURRAY &amp; HOLLADAY.'),
        ('ACROSS GEORGIA', 'ACROSS THE SALT LAKE VALLEY'),
        ('YOUR ATLANTA HOME', 'YOUR SALT LAKE CITY HOME'), ('Your Atlanta home', 'Your Salt Lake City home'),
        (r'We serve metro Atlanta across[^<]*', FAQ_AREAS),
        ('Serving Georgia &amp; Salt Lake City', 'Serving Salt Lake City &amp; Georgia'),
        (r'Open 7 days a week, 8 AM to 8 PM\. Pro Peach Cleaning serves homes and businesses from metro Atlanta[^<]*', FOOT_HOURS),
    ]
    for a, b in rep:
        body = re.sub(a, b, body)
    body = re.sub(r'<section class="loc-section">.*?</section>', LOC, body, flags=re.S)

    # Google reviews -> Utah profile (honest badge text); Atlanta card stays Atlanta (protected)
    body = body.replace(GA_CID, UT_CID).replace('4.9 from 100+ Google reviews', 'Salt Lake City reviews on Google')

    # nav: cross-link points back to Georgia
    body = re.sub(r'<a([^>]*?)href="https://utah\.propeachcleaning\.com/"([^>]*)>Utah</a>', r'<a\1href="' + GA + r'/"\2>Georgia</a>', body)
    body = body.replace('title="Pro Peach Cleaning in Salt Lake City, Utah"', 'title="Pro Peach Cleaning in Georgia"')
    body = re.sub(r'<a([^>]*?)href="https://utah\.propeachcleaning\.com/"([^>]*)>Also in Utah →</a>', r'<a\1href="' + GA + r'/"\2>Also in Georgia →</a>', body)

    # links
    body = re.sub(r'href="(/[^"#?]*)"', lambda m: f'href="{LINKS.get(m.group(1).rstrip("/") or "/", GA + m.group(1))}"', body)

    # photos
    body = re.sub(r'src="[^"]*atlanta-move-out-cleaning-hardwood[^"]*"', f'src="{IMG["reviews"]}"', body)
    body = re.sub(r'(<img[^>]*src="' + re.escape(IMG['reviews']) + r'"[^>]*?)\s+srcset="[^"]*"', r'\1', body)
    body = re.sub(r'(<img[^>]*src="' + re.escape(IMG['reviews']) + r'"[^>]*?)\s+sizes="[^"]*"', r'\1', body)
    body = re.sub(r'(<img[^>]*src="' + re.escape(IMG['reviews']) + r'"[^>]*?)alt="[^"]*"', r'\1alt="Bright, freshly cleaned living room"', body)
    body = re.sub(r'<div class="ppba".*?</section></div>', lambda m: ppba_html(), body, count=1, flags=re.S)

    if atl_card:
        body = body.replace('@@ATLCARD@@', atl_card)
    body = body.replace('</body>', FORM_JS + '\n</body>')
    out = '<!DOCTYPE html>\n<!-- Built by tools/build_home_from_ga.py from propeachcleaning.com. Edit GA, then re-run. -->\n' \
          + html_tag + '<head>' + head + '</head>' + body
    (ROOT / 'index.html').write_text(out)
    for f in (ROOT / 'vendor').iterdir():          # drop vendored files GA no longer uses
        if '/vendor/' + f.name not in out:
            f.unlink()

    # sanity report
    left = {k: len(re.findall(k, body)) for k in ['Atlanta', '470', 'atlanta', 'Savannah']}
    print('index.html', len(out), 'bytes; remaining mentions:', left)

if __name__ == '__main__':
    build()
