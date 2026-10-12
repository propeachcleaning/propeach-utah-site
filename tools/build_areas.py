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
        <a class="review-badge" href="https://maps.google.com/?cid=16449210000793791146" target="_blank" rel="noopener"><span class="review-stars" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span><span class="review-text">4.8 from 100+ Google reviews</span><span class="review-cta">Read reviews &rarr;</span></a>
        <div class="trust-chips"><div class="trust-chip"><span class="trust-icon" aria-hidden="true">&#10003;</span><span class="trust-label">Licensed, Bonded &amp; Insured</span></div><div class="trust-chip"><span class="trust-icon" aria-hidden="true">&#10003;</span><span class="trust-label">Background-Checked</span></div><div class="trust-chip"><span class="trust-icon" aria-hidden="true">&#10003;</span><span class="trust-label">Eco-Friendly</span></div></div>
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
        <div><span>Call or text</span><strong><a href="tel:+13852179244">(385) 217-9244</a></strong></div>
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
      <p class="pp-small">See our <a href="/house-cleaning-cost-salt-lake-city">Salt Lake City cleaning price guide</a>. Commercial and post-construction cleaning are quoted per project. <a href="/services-commercial">Commercial cleaning</a> · <a href="/services-construction">Post-construction cleaning</a></p>
    </div></section>
'''
WHY='''    <section class="pp-sec pp-why"><div class="pp-in">
      <h2>Why {place} Chooses Pro Peach Cleaning</h2>
      <div class="pp-cards">
        <div class="pp-card"><h3>Licensed, insured &amp; hand-picked</h3><p>Only 4% of cleaners make it through our hiring process. Every cleaner is interviewed and background-checked, and Pro Peach Cleaning is licensed, bonded and insured.</p></div>
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
body=vis+hero("House Cleaning in Salt Lake City & Surrounding Areas","Pro Peach Cleaning serves Salt Lake City and the surrounding Salt Lake Valley: Millcreek, Holladay, Murray, Cottonwood Heights, Sugar House and South Salt Lake. We offer standard, deep, move-in/move-out, Airbnb, commercial and post-construction cleaning. Get an instant price online or call or text (385) 217-9244.")+facts("Salt Lake City")
body+=f'    <section class="pp-sec"><div class="pp-in"><h2>Choose Your City</h2><div class="pp-cards pp-cards--svc">{cards}</div></div></section>\n'
body+=f'    <section class="pp-sec"><div class="pp-in"><h2>Popular Services in Salt Lake City</h2><div class="pp-pills">{svc}</div></div></section>\n'
body+=price_table("the Salt Lake Valley")+WHY.format(place="the Salt Lake Valley")
body+='    <section class="pp-sec"><div class="pp-in"><h2>Also in Metro Atlanta, Georgia</h2><p>Pro Peach Cleaning also serves metro Atlanta. <a href="https://propeachcleaning.com/">Visit Pro Peach Cleaning Atlanta</a>.</p></div></section>\n'
open('service-areas.html','w').write(h+body+'\n'+tail); pages.append(('service-areas','Service Areas'))
print('\n'.join(f'{p}  ({len(t)})  {t}' for p,t in pages))

# ===== Cost pages (prices live ONLY here, like Sparkle) =====
from areas import COSTS,TIERS,STANDARD,OFFICE
def cost_shell(slug,title,desc,crumb,faqs,body_inner):
    h,url=set_meta(head,title,desc,slug)
    vis,bld=crumbs([("Home","/"),("Service Areas","/service-areas"),(crumb,"/"+slug)])
    h=inject(h,[bld,faq_ld(faqs)])
    open(slug+'.html','w').write(h+vis+body_inner+'\n'+tail); pages.append((slug,title))
for slug,c in COSTS.items():
    rows=''.join(f'<li><strong>{E(t)}:</strong> from ${p+c["add"]}{", quoted for your home" if t.startswith("3,000") else ""}</li>' for t,p in zip(TIERS,STANDARD))
    b=f'    <div class="pp-h1wrap"><h1>{E(c["h1"])}</h1><p class="pp-answer">{E(c["lead"])}</p><a class="btn-primary pp-hero-btn" href="{BOOK}" target="_blank" rel="noopener">Get My Exact Price</a>\n{CHIPS}    </div>\n'
    b+=f'    <section class="pp-sec"><div class="pp-in"><h2>{E(c["h2"])}</h2><ul class="pp-tiers">{rows}</ul><p>{E(c["note"])} See <a href="/house-cleaning-cost-salt-lake-city">house cleaning cost</a>, <a href="/deep-cleaning-cost-salt-lake-city">deep cleaning cost</a> and <a href="/move-out-cleaning-cost-salt-lake-city">move-out cleaning cost</a>.</p></div></section>\n'
    if c["add"]==0: b+='    <section class="pp-sec"><div class="pp-in"><h2>Recurring Cleaning Discounts</h2><p>Book a recurring schedule and save on every visit. Discounts come off the one-time price and are applied automatically when you choose a frequency online.</p><ul class="pp-tiers"><li><strong>Monthly:</strong> 10% off</li><li><strong>Twice a month (every other week):</strong> 15% off</li><li><strong>Weekly:</strong> 20% off</li><li><strong>Twice a week:</strong> 25% off</li></ul></div></section>\n'
    b+='    <section class="pp-sec"><div class="pp-in"><h2>What\'s Included</h2><p>Every clean follows our detailed checklist: kitchen and bathrooms cleaned and sanitized, surfaces dusted, floors vacuumed and mopped, and trash taken out. Our background-checked cleaners bring their own eco-friendly supplies, and every visit is backed by our 24-hour free touch-up.</p><p>Need more detail? See <a href="/deep-cleaning-salt-lake-city">deep cleaning</a>, <a href="/move-out-cleaning-salt-lake-city">move-out cleaning</a> or <a href="/airbnb-cleaning-salt-lake-city">Airbnb cleaning</a> in Salt Lake City.</p></div></section>\n'
    b+='    <section class="pp-sec"><div class="pp-in"><h2>What Can Change Your Price</h2><ul class="pp-check"><li><strong>Home size.</strong> Pricing is set by square footage.</li><li><strong>Type of clean.</strong> Deep cleaning adds $50 and move-in/move-out adds $100.</li><li><strong>Pets.</strong> $15 per pet for the extra hair on floors, furniture and baseboards.</li><li><strong>Extras.</strong> Optional add-ons like inside the fridge or oven, inside cabinets, windows, laundry or organizing.</li><li><strong>Parking.</strong> Paid parking or garage fees at your building are added to the total.</li></ul></div></section>\n'
    if c["add"]==100: b=b.replace("Optional add-ons like inside the fridge or oven, inside cabinets, windows, laundry or organizing.","Optional add-ons like windows, laundry, organizing or a garage. Inside the oven, fridge and cabinets is already included in every move-out clean.")
    b+='    <section class="pp-sec"><div class="pp-in"><h2>Standard or Deep Clean?</h2><p>If your home hasn\'t had a professional cleaning in the last month or two, start with a deep clean. After that, a standard clean on a weekly, biweekly or monthly schedule keeps it fresh.</p></div></section>\n'
    b+=faq_html(c["faqs"],"Salt Lake City").replace("House Cleaning FAQs","Cleaning Cost FAQs")
    b+=near_html(["salt-lake-city","millcreek","holladay","murray","cottonwood-heights","sugar-house","south-salt-lake"],"Related Services and Areas")
    cost_shell(slug,c["title"],c["desc"],c["h1"].replace("How Much Does ","").replace("?",""),c["faqs"],b)
of=[("Why don't you list a flat price for office cleaning?","Office cleaning depends on square footage, foot traffic, restrooms and how often you clean. We quote each space so you pay for what your office actually needs."),
    ("Is recurring office cleaning cheaper per visit?","Usually, yes. Regular cleaning keeps dirt from building up, so each visit takes less time."),
    ("Can you clean before or after business hours?","Tell us your hours and we'll set a schedule that keeps the cleaning out of your team's way."),
    ("Are your cleaners background-checked?","Yes. Every cleaner passes a background check, and Pro Peach Cleaning is licensed, bonded and insured.")]
b=f'    <div class="pp-h1wrap"><h1>{E(OFFICE["h1"])}</h1><p class="pp-answer">Office cleaning is priced differently from house cleaning. Two Salt Lake City offices the same size can have very different prices depending on how many people use the space, how many restrooms and kitchens it has, and how often you want it cleaned. Tell us about your space and we\'ll send an accurate quote.</p><a class="btn-primary pp-hero-btn" href="/services-commercial">Request an Office Quote</a>\n{CHIPS}    </div>\n'
b+='    <section class="pp-sec"><div class="pp-in"><h2>What Affects the Cost of Office Cleaning</h2><ul class="pp-check"><li><strong>Square footage.</strong> More space takes more time, but layout matters too.</li><li><strong>Foot traffic.</strong> Busy offices need more restroom, break room and floor care.</li><li><strong>Restrooms and kitchens.</strong> These take the most time.</li><li><strong>How often we clean.</strong> Recurring service keeps each visit shorter.</li><li><strong>Hours.</strong> We schedule around your team.</li><li><strong>Flooring.</strong> Hard floors, carpet and specialty surfaces are cleaned differently.</li><li><strong>Parking and access.</strong> Paid parking or garage fees are added to the total.</li></ul></div></section>\n'
b+='    <section class="pp-sec"><div class="pp-in"><h2>How Often Should an Office Be Cleaned?</h2><ul class="pp-check"><li>Several times a week: busy offices, medical and wellness spaces</li><li>Weekly: small offices and studios</li><li>Every other week: low-traffic spaces</li><li>One-time deep clean: before an inspection, move-in, event or after a renovation</li></ul></div></section>\n'
b+='    <section class="pp-sec"><div class="pp-in"><h2>What\'s Included in Office Cleaning</h2><ul class="pp-check"><li>High-touch surfaces sanitized</li><li>Restrooms cleaned and disinfected</li><li>Break rooms and kitchens wiped down</li><li>Desks and reachable surfaces dusted</li><li>Floors vacuumed and mopped</li><li>Trash emptied and liners replaced</li></ul><p>See <a href="/services-commercial">commercial cleaning in Salt Lake City</a> and <a href="/house-cleaning-cost-salt-lake-city">house cleaning prices</a>.</p></div></section>\n'
b+=faq_html(of,"Salt Lake City").replace("House Cleaning FAQs","Office Cleaning Cost FAQs")
cost_shell(OFFICE["slug"],OFFICE["title"],OFFICE["desc"],"Office Cleaning Cost Salt Lake City",of,b)
print('cost pages built')
