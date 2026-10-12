"""Builds Salt Lake Valley location/service pages from services-residential.html (header, CTA, footer, scripts)."""
import json,re,os,html
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from areas import CITIES,SERVICES,PRICES,BOOK
BASE="https://utah.propeachcleaning.com"
tpl=open('services-residential.html').read()
head=tpl[:tpl.index('    <nav class="services-subnav"')]
tail=tpl[tpl.index('    <section class="cta-section">'):]
# head: drop page-specific Service/Breadcrumb JSON-LD (keep LocalBusiness)
head=re.sub(r'    <script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "(Service|BreadcrumbList)".*?</script>\n','',head)
AREAS=["Salt Lake City","Millcreek","Holladay","Murray","Cottonwood Heights","South Salt Lake","Sugar House"]
lb=json.loads(re.search(r'<script type="application/ld\+json">(\{"@context": "https://schema.org", "@type": \["LocalBusiness".*?)</script>',head).group(1))
lb["areaServed"]=[{"@type":"City","name":n+", UT"} if n!="Sugar House" else {"@type":"Place","name":"Sugar House, Salt Lake City, UT"} for n in AREAS]
lb["priceRange"]="$$"
lb["slogan"]="Immaculate results, every time"
lb["knowsLanguage"]=["en","es"] if False else lb.get("knowsLanguage")
lb.pop("knowsLanguage",None)
head=re.sub(r'(<script type="application/ld\+json">)\{"@context": "https://schema.org", "@type": \["LocalBusiness".*?(</script>)',lambda m:m.group(1)+json.dumps(lb,ensure_ascii=False)+m.group(2),head,count=1)
E=lambda s:html.escape(s,quote=True)
def set_meta(h,title,desc,path):
    url=BASE+'/'+path if path else BASE+'/'
    h=re.sub(r'<title>.*?</title>',f'<title>{E(title)}</title>',h)
    h=re.sub(r'<meta name="description" content="[^"]*"',f'<meta name="description" content="{E(desc)}"',h)
    h=re.sub(r'<link rel="canonical" href="[^"]*"',f'<link rel="canonical" href="{url}"',h)
    h=re.sub(r'<meta property="og:title" content="[^"]*"',f'<meta property="og:title" content="{E(title)}"',h)
    h=re.sub(r'<meta property="og:description" content="[^"]*"',f'<meta property="og:description" content="{E(desc)}"',h)
    h=re.sub(r'<meta property="og:url" content="[^"]*"',f'<meta property="og:url" content="{url}"',h)
    return h,url
def ld(o): return '    <script type="application/ld+json">'+json.dumps(o,ensure_ascii=False)+'</script>\n'
def inject(h,blocks): return h.replace('    <link\n      href="https://cdn.jsdelivr.net/npm/bootstrap',''.join(blocks)+'    <link\n      href="https://cdn.jsdelivr.net/npm/bootstrap',1)
CHIPS='''      <div class="pp-chiprow">
        <div class="trust-chips"><div class="trust-chip"><span class="trust-icon" aria-hidden="true">&#10003;</span><span class="trust-label">Bonded &amp; Insured</span></div><div class="trust-chip"><span class="trust-icon" aria-hidden="true">&#10003;</span><span class="trust-label">Background-Checked</span></div><div class="trust-chip"><span class="trust-icon" aria-hidden="true">&#10003;</span><span class="trust-label">Eco-Friendly</span></div></div>
        <div class="own-chips"><div class="own-chip"><span class="own-icon" aria-hidden="true">&#9733;</span><span class="own-label">Women-Owned</span></div><div class="own-chip"><span class="own-icon" aria-hidden="true">&#9733;</span><span class="own-label">Veteran-Owned</span></div><div class="own-chip"><span class="own-icon" aria-hidden="true">&#9733;</span><span class="own-label">Latino-Owned</span></div></div>
      </div>
'''
def crumbs(items):
    vis='<nav class="pp-crumbs" aria-label="Breadcrumb">'+' <span aria-hidden="true">›</span> '.join(f'<a href="{u}">{E(n)}</a>' if i<len(items)-1 else f'<span aria-current="page">{E(n)}</span>' for i,(n,u) in enumerate(items))+'</nav>\n'
    js={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u if u.startswith('/') else u} for i,(n,u) in enumerate(items)]}
    return vis,ld(js)
def faq_html(faqs,place):
    out=f'    <section class="pp-sec pp-faq"><div class="pp-in"><h2>{E(place)} House Cleaning FAQs</h2>\n'
    for q,a in faqs: out+=f'      <details class="pp-faq-item"><summary>{E(q)}</summary><p>{E(a)}</p></details>\n'
    return out+'    </div></section>\n'
def faq_ld(faqs): return ld({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]})
def facts(place):
    return f'''    <section class="pp-sec pp-facts-sec"><div class="pp-in">
      <div class="pp-facts" aria-label="Quick facts">
        <div><span>Pricing</span><strong>Instant online quote</strong></div>
        <div><span>Hours</span><strong>7 days &middot; 8 AM–8 PM</strong></div>
        <div><span>Call or text</span><strong><a href="tel:+14704129977">(470) 412-9977</a></strong></div>
        <div><span>Booking</span><strong><a href="{BOOK}" target="_blank" rel="noopener">Online in 60 seconds</a></strong></div>
      </div>
    </div></section>
'''
def price_table(place,highlight=None):
    return f'''    <section class="pp-sec" id="pricing"><div class="pp-in">
      <h2>How Pricing Works in {E(place)}</h2>
      <p>Every home is different, so your price is based on your home's size and the type of clean you choose: standard, deep, move-in/move-out or Airbnb turnover. Book online and you'll see your exact price instantly, before you confirm, with no phone call and no surprise fees.</p>
      <ul class="pp-check"><li>Instant, upfront quote online</li><li>Price set by home size and cleaning type</li><li>No hidden fees</li><li>24-hour free touch-up included</li></ul>
      <p style="margin-top:18px"><a class="btn-primary" href="{BOOK}" target="_blank" rel="noopener">Get My Price</a></p>
      <p class="pp-small">Commercial and post-construction cleaning are quoted per project. <a href="/services-commercial">Commercial cleaning</a> · <a href="/services-construction">Post-construction cleaning</a></p>
    </div></section>
'''
WHY='''    <section class="pp-sec pp-why"><div class="pp-in">
      <h2>Why {place} Chooses Pro Peach Cleaning</h2>
      <div class="pp-cards">
        <div class="pp-card"><h3>Background-checked &amp; insured</h3><p>Every cleaner passes a background check, and Pro Peach Cleaning is bonded and insured.</p></div>
        <div class="pp-card"><h3>Eco-friendly supplies included</h3><p>We bring our own eco-friendly products and equipment to every clean. You don't need to provide a thing.</p></div>
        <div class="pp-card"><h3>24-hour free touch-up</h3><p>If anything on the checklist was missed, tell us within 24 hours and we'll come back at no charge.</p></div>
        <div class="pp-card"><h3>Women-, veteran- &amp; Latino-owned</h3><p>A locally run, family-minded business that treats your home like our own.</p></div>
      </div>
    </div></section>
'''
SVCS='''    <section class="pp-sec"><div class="pp-in">
      <h2>Cleaning Services in {place}</h2>
      <div class="pp-cards pp-cards--svc">
        <a class="pp-card pp-card--link" href="/{std}"><h3>Standard &amp; recurring cleaning</h3><p>Weekly, biweekly or monthly upkeep: kitchens, bathrooms, bedrooms, living areas and floors.</p></a>
        <a class="pp-card pp-card--link" href="/deep-cleaning-salt-lake-city"><h3>Deep cleaning</h3><p>Baseboards, vents, cabinet fronts, grout and hard-water buildup.</p></a>
        <a class="pp-card pp-card--link" href="/move-out-cleaning-salt-lake-city"><h3>Move-in / move-out cleaning</h3><p>Empty-home cleaning inside cabinets, appliances and closets.</p></a>
        <a class="pp-card pp-card--link" href="/airbnb-cleaning-salt-lake-city"><h3>Airbnb &amp; vacation rental cleaning</h3><p>Guest-ready turnovers between stays.</p></a>
        <a class="pp-card pp-card--link" href="/services-commercial"><h3>Commercial &amp; office cleaning</h3><p>Offices, retail, gyms and medical spaces on a schedule that fits your business.</p></a>
        <a class="pp-card pp-card--link" href="/services-construction"><h3>Post-construction cleaning</h3><p>Dust and debris removal after builds and remodels so the space is move-in ready.</p></a>
      </div>
    </div></section>
'''
def near_html(keys,title="Nearby Areas We Serve"):
    links=''.join(f'<a class="pp-pill" href="/{CITIES[k]["slug"]}">House cleaning in {E(CITIES[k]["name"])}</a>' for k in keys)
    return f'    <section class="pp-sec"><div class="pp-in"><h2>{title}</h2><div class="pp-pills">{links}<a class="pp-pill pp-pill--alt" href="/service-areas">All service areas</a></div></div></section>\n'
def hero(h1,answer):
    return f'    <div class="pp-h1wrap"><h1>{E(h1)}</h1><p class="pp-answer">{E(answer)}</p><a class="btn-primary pp-hero-btn" href="{BOOK}" target="_blank" rel="noopener">Book a Cleaning</a>\n{CHIPS}    </div>\n'
def service_ld(name,place,url,price):
    return ld({"@context":"https://schema.org","@type":"Service","name":f"{name} in {place}, UT","serviceType":name,"provider":{"@id":BASE+"/#business"},"areaServed":{"@type":"City","name":place+", UT"},"url":url})
pages=[]
for key,c in CITIES.items():
    h,url=set_meta(head,c["title"],c["desc"],c["slug"])
    place=c["name"]; cityname = place if key!="sugar-house" else "Salt Lake City"
    vis,bld=crumbs([("Home","/"),("Service Areas","/service-areas"),(f"House Cleaning {place}","/"+c["slug"])])
    lbloc=ld({"@context":"https://schema.org","@type":"Service","name":f"House Cleaning in {place}, UT","serviceType":"House Cleaning","provider":{"@id":BASE+"/#business"},"areaServed":{"@type":"Place" if key=="sugar-house" else "City","name":f"{place}, UT" if key!="sugar-house" else "Sugar House, Salt Lake City, UT","geo":{"@type":"GeoCoordinates","latitude":c["geo"][0],"longitude":c["geo"][1]}},"url":url})
    h=inject(h,[lbloc,bld,faq_ld(c["faqs"])])
    body=vis+hero(c["h1"],c["answer"])+facts(place)
    body+='    <section class="pp-sec"><div class="pp-in pp-prose">\n'
    for t,p in c["local"]: body+=f'      <h2>{E(t)}</h2>\n      <p>{E(p)}</p>\n'
    body+='    </div></section>\n'
    body+=SVCS.format(place=E(place),std=c["slug"])
    body+=price_table(place)
    body+=f'    <section class="pp-sec"><div class="pp-in"><h2>{E(place)} Neighborhoods We Clean</h2><ul class="pp-hoods">'+''.join(f'<li>{E(n)}</li>' for n in c["hoods"])+f'</ul><p class="pp-small">Don\'t see your street? If you\'re in {E(place)} or nearby, we most likely cover it. Enter your address when you book to confirm.</p></div></section>\n'
    body+=WHY.format(place=E(place))
    body+=faq_html(c["faqs"],place)
    body+=near_html(c["near"])
    open(c["slug"]+'.html','w').write(h+body+'\n'+tail); pages.append((c["slug"],c["title"]))
for slug,s in SERVICES.items():
    h,url=set_meta(head,s["title"],s["desc"],slug)
    vis,bld=crumbs([("Home","/"),("Service Areas","/service-areas"),(f'{s["name"]} {s["city"]}',"/"+slug)])
    h=inject(h,[service_ld(s["name"],s["city"],url,s["price"]),bld,faq_ld(s["faqs"])])
    body=vis+hero(s["h1"],s["answer"])+facts(s["city"])
    body+=f'    <section class="pp-sec"><div class="pp-in"><h2>What\'s Included in {E(s["name"])}</h2><ul class="pp-check">'+''.join(f'<li>{E(i)}</li>' for i in s["included"])+'</ul></div></section>\n'
    body+=f'    <section class="pp-sec"><div class="pp-in"><h2>When to Book {E(s["name"])} in {E(s["city"])}</h2><div class="pp-cards">'+''.join(f'<div class="pp-card"><h3>{E(t)}</h3><p>{E(p)}</p></div>' for t,p in s["when"])+'</div></div></section>\n'
    body+=price_table(s["city"],highlight=s["name"].split()[0].replace("Airbnb","Airbnb"))
    body+=WHY.format(place="Salt Lake City")
    body+=faq_html(s["faqs"],s["city"]).replace("House Cleaning FAQs",E(s["name"])+" FAQs")
    body+=near_html(["salt-lake-city","millcreek","holladay","murray","cottonwood-heights","sugar-house","south-salt-lake"],"We Also Clean In")
    open(slug+'.html','w').write(h+body+'\n'+tail); pages.append((slug,s["title"]))
# service-areas hub
h,url=set_meta(head,"Service Areas: Salt Lake City & Nearby | Pro Peach","House cleaning in Salt Lake City, Millcreek, Holladay, Murray, Cottonwood Heights, Sugar House & South Salt Lake, UT. Instant online quotes.","service-areas")
vis,bld=crumbs([("Home","/"),("Service Areas","/service-areas")])
h=inject(h,[bld,ld({"@context":"https://schema.org","@type":"ItemList","name":"Pro Peach Cleaning Utah service areas","itemListElement":[{"@type":"ListItem","position":i+1,"url":BASE+"/"+c["slug"],"name":"House Cleaning "+c["name"]} for i,c in enumerate(CITIES.values())]})])
cards=''.join(f'<a class="pp-card pp-card--link" href="/{c["slug"]}"><h3>{E(c["name"])}</h3><p>{E(c["desc"])}</p></a>' for c in CITIES.values())
svc=''.join(f'<a class="pp-pill" href="/{k}">{E(v["name"])} in {E(v["city"])}</a>' for k,v in SERVICES.items())
body=vis+hero("House Cleaning in Salt Lake City & Surrounding Areas","Pro Peach Cleaning serves Salt Lake City and the surrounding Salt Lake Valley: Millcreek, Holladay, Murray, Cottonwood Heights, Sugar House and South Salt Lake. We offer standard, deep, move-in/move-out, Airbnb, commercial and post-construction cleaning. Get an instant price online or call or text (470) 412-9977.")+facts("Salt Lake City")
body+=f'    <section class="pp-sec"><div class="pp-in"><h2>Choose Your City</h2><div class="pp-cards pp-cards--svc">{cards}</div></div></section>\n'
body+=f'    <section class="pp-sec"><div class="pp-in"><h2>Popular Services in Salt Lake City</h2><div class="pp-pills">{svc}</div></div></section>\n'
body+=price_table("the Salt Lake Valley")+WHY.format(place="the Salt Lake Valley")
body+='    <section class="pp-sec"><div class="pp-in"><h2>Also in Metro Atlanta, Georgia</h2><p>Pro Peach Cleaning also serves metro Atlanta. <a href="https://propeachcleaning.com/">Visit Pro Peach Cleaning Atlanta</a>.</p></div></section>\n'
open('service-areas.html','w').write(h+body+'\n'+tail); pages.append(('service-areas','Service Areas'))
print('\n'.join(f'{p}  ({len(t)})  {t}' for p,t in pages))
