"""Utah service-by-city pages (deep / move-out / Airbnb x suburb), generated from the Salt Lake City service pages.

Writes tools/legacy/<svc>-<city>-ut.html, points each city page's service card at its local version, and adds the
pages to the sitemap and llms.txt. Then run: python3 tools/build_pages_from_ga.py <names...>
"""
import html as H, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEG = ROOT / 'tools' / 'legacy'
SITE = 'https://utah.propeachcleaning.com'
GEO = {'sandy': (40.5649, -111.8389), 'south-jordan': (40.5622, -111.9297), 'murray': (40.6669, -111.888),
       'draper': (40.5247, -111.8638), 'west-jordan': (40.6097, -111.9391)}
NAME = {'sandy': 'Sandy', 'south-jordan': 'South Jordan', 'murray': 'Murray', 'draper': 'Draper', 'west-jordan': 'West Jordan'}
SVC = {'deep': ('deep-cleaning-salt-lake-city.html', 'Deep Cleaning', 'Deep cleaning'),
       'move-out': ('move-out-cleaning-salt-lake-city.html', 'Move-In &amp; Move-Out Cleaning', 'Move-in / move-out cleaning'),
       'airbnb': ('airbnb-cleaning-salt-lake-city.html', 'Airbnb &amp; Vacation Rental Cleaning', 'Airbnb &amp; vacation rental cleaning')}
SLUG = {'deep': 'deep-cleaning', 'move-out': 'move-out-cleaning', 'airbnb': 'airbnb-cleaning'}

# (service, city): description, [(when h3, p) x3], [(q, a) x3]  — Q1 cost question is kept from the template
PAGES = {
    ('deep', 'sandy'): (
        'Deep cleaning in Sandy, UT: baseboards, vents, grout and hard-water buildup by background-checked, eco-friendly cleaners. Instant online quote.',
        [('After ski season', 'Months of boots, gear and snowmelt leave grit in entryways, mudrooms and floors. A spring deep clean resets the whole house.'),
         ('Before holiday guests', 'Hosting family near the canyons? A deep clean gets kitchens, bathrooms and guest rooms ready.'),
         ('Starting recurring service', 'Begin with a deep clean so every recurring visit after that keeps a fully reset home.')],
        [('Do you deep clean larger multi-level homes in Sandy?', 'Yes. Many Sandy homes have several levels and finished basements. Pricing is based on square footage, so we plan the right team and time to reach every level.'),
         ('Can you remove hard-water spots on fixtures and shower glass?', 'Yes. Salt Lake Valley water is very hard. Our deep clean treats white buildup on faucets, shower glass and tile so fixtures shine again.'),
         ('How often should I deep clean my Sandy home?', 'Most families book a deep clean two to four times a year, often in spring after ski season and before the holidays, with standard cleaning in between.')]),
    ('deep', 'south-jordan'): (
        'Deep cleaning in South Jordan and Daybreak, UT: detail work on newer homes, quartz, LVP and glass showers. Background-checked cleaners. Instant quote.',
        [('A few months after moving in', 'New builds keep releasing fine construction dust into vents, window tracks and cabinets. A deep clean clears it out.'),
         ('Spring reset', 'Winter keeps homes closed up; a spring deep clean removes dust, salt residue and buildup from every room.'),
         ('Before hosting', 'Family visits and holidays are easier when the whole house has had a top-to-bottom clean.')],
        [('Do you deep clean homes in Daybreak?', 'Yes. We deep clean single-family homes, cottages and townhomes throughout Daybreak and the rest of South Jordan.'),
         ('Are your products safe for quartz, LVP and glass showers?', 'Yes. We use surface-safe, eco-friendly products, damp-mop luxury vinyl instead of soaking it, and leave glass showers streak-free.'),
         ('How often should I deep clean my South Jordan home?', 'Most households book a deep clean two to four times a year, with biweekly standard cleaning in between.')]),
    ('deep', 'murray'): (
        'Deep cleaning in Murray, UT: baseboards, vents, cabinets, grout and hard-water spots by background-checked, eco-friendly cleaners. Instant quote.',
        [('Older brick homes', 'Classic Murray ramblers collect dust in vents, trim and basements over the years. A deep clean reaches the details.'),
         ('Between busy shifts', 'Working long shifts at nearby medical centers? Let us do the heavy cleaning while you rest.'),
         ('Seasonal reset', 'A spring or fall deep clean clears winter grime, dust and buildup from every room.')],
        [('Do you deep clean basements in Murray homes?', 'Yes. Many Murray homes have finished basements. We include every finished level, and pricing is based on square footage.'),
         ('Can I book a deep clean while I am at work?', 'Yes. Many clients give us access with a key, lockbox or door code and come home to a deep-cleaned house.'),
         ('How often should I deep clean in Murray?', 'Most homes do well with a deep clean two to four times a year plus regular standard cleaning.')]),
    ('deep', 'draper'): (
        'Deep cleaning in Draper, UT for larger homes with bonus rooms and basements. Background-checked, eco-friendly cleaners. Instant online quote.',
        [('Larger family homes', 'Bonus rooms, finished basements and several bathrooms take time. We plan the right team to deep clean every level.'),
         ('After trail season', 'Corner Canyon dust and dog hair build up on floors and baseboards; a deep clean resets them.'),
         ('Before hosting', 'Get the kitchen, bathrooms and living spaces guest-ready before a party or holiday visit.')],
        [('Can you deep clean a large home in one visit?', 'Yes. Pricing is based on square footage, so we schedule enough team and time to finish your whole home.'),
         ('Do you serve homes up toward Suncrest?', 'We serve Draper, including many homes on the bench. Enter your address when you book and we will confirm it is in our area.'),
         ('How often should I deep clean my Draper home?', 'Most larger households book a deep clean two to four times a year with weekly or biweekly cleaning in between.')]),
    ('move-out', 'west-jordan'): (
        'Move-in and move-out cleaning in West Jordan, UT: inside cabinets, appliances, closets and floors. Background-checked cleaners. Instant quote.',
        [('Renters moving out', 'Hand back the keys to a spotless home and give yourself the best chance at your deposit.'),
         ('Buying a new build', 'Move into a newly built home without the builder dust inside cabinets, drawers and window tracks.'),
         ('Landlords between tenants', 'Turn rentals quickly near Jordan Landing and across West Jordan.')],
        [('Does the home need to be empty?', 'Yes. Move-in/move-out cleaning is designed for empty homes so we can reach inside every cabinet, closet and appliance.'),
         ('Do you clean finished basements on move-out?', 'Yes. We clean every finished level, and pricing is based on square footage.'),
         ('Can you clean on closing or lease-end day?', 'Book online to see open times. Many clients schedule the day before closing or key hand-off so the home is ready.')]),
    ('move-out', 'south-jordan'): (
        'Move-in and move-out cleaning in South Jordan and Daybreak, UT: empty-home cleaning inside cabinets and appliances. Instant online quote.',
        [('New construction move-ins', 'Clear builder dust from cabinets, drawers, vents and window tracks before you unpack.'),
         ('Selling your home', 'An empty, spotless home photographs better and is ready for the final walk-through.'),
         ('Renters and landlords', 'Townhomes and apartments near the District and Daybreak turn over faster with a professional clean.')],
        [('Do you clean townhomes in Daybreak?', 'Yes. We clean homes, cottages and townhomes throughout Daybreak and South Jordan.'),
         ('Does the home need to be empty?', 'Yes. Move-in/move-out cleaning is designed for empty homes so we can reach inside every cabinet and appliance.'),
         ('What is included that a standard clean skips?', 'Inside cabinets and drawers, inside the oven, fridge and microwave, closets, shelves and window tracks.')]),
    ('move-out', 'murray'): (
        'Move-in and move-out cleaning in Murray, UT for apartments, condos and homes. Inside cabinets and appliances. Instant online quote.',
        [('Apartment renters', 'Moving out near Fashion Place or downtown Murray? Hand back the keys to a spotless unit.'),
         ('Home buyers', 'Move into a Murray home that is clean inside every cabinet, closet and appliance.'),
         ('Landlords', 'Turn units quickly between tenants across Murray and nearby cities.')],
        [('Do you clean apartments and condos?', 'Yes. We clean apartments, condos, townhomes and houses. Share parking or building access rules when you book.'),
         ('Does the home need to be empty?', 'Yes. The service is designed for empty homes so we can reach inside cabinets, closets and appliances.'),
         ('Can I book while I am moving?', 'Yes. Many clients book the day after the movers leave and give us access with a key or lockbox.')]),
    ('move-out', 'sandy'): (
        'Move-in and move-out cleaning in Sandy, UT: empty-home cleaning inside cabinets, appliances and closets. Background-checked cleaners. Instant quote.',
        [('Renters moving out', 'Hand back the keys to a spotless home and give yourself the best chance at your deposit.'),
         ('Buyers and sellers', 'Get an empty Sandy home ready for listing photos, final walk-through or move-in day.'),
         ('Rental owners', 'Turn long-term rentals and ski-season properties between tenants.')],
        [('Does the home need to be empty?', 'Yes. Move-in/move-out cleaning is designed for empty homes so we can reach inside every cabinet, closet and appliance.'),
         ('Do you clean multi-level homes and basements?', 'Yes. We clean every finished level, and pricing is based on square footage.'),
         ('What is included that a standard clean skips?', 'Inside cabinets and drawers, inside the oven, fridge and microwave, closets, shelves and window tracks.')]),
    ('airbnb', 'sandy'): (
        'Airbnb and ski rental turnover cleaning in Sandy, UT near Little Cottonwood Canyon. Guest-ready resets between stays. Instant online quote.',
        [('Ski season turnovers', 'Back-to-back winter bookings near Little Cottonwood Canyon need fast, reliable resets between guests.'),
         ('Summer hiking stays', 'Trail dust and gear come home with guests; we reset floors, bathrooms and kitchens for the next check-in.'),
         ('Deep resets between seasons', 'Pair regular turnovers with a seasonal deep clean to keep reviews strong.')],
        [('Do you clean ski rentals in Sandy?', 'Yes. Sandy is a popular base for Little Cottonwood Canyon, and our turnover cleaning resets the kitchen, bathrooms and floors between guests.'),
         ('How do you handle snow, salt and wet gear?', 'We pay extra attention to entryways, mudrooms and hard floors and remove salt residue so it does not dull floors.'),
         ('Can you work around check-in and check-out times?', 'Yes. Book online and share your checkout and next check-in times so we can schedule the turnover in between.')]),
}

def e(t):
    return H.escape(t, quote=False).replace("'", '&#x27;')

def build(svc, city, desc, when, faqs):
    src, label, card = SVC[svc]
    cname = NAME[city]
    slug = f'{SLUG[svc]}-{city}-ut'
    s = (LEG / src).read_text()
    cost_q = re.search(r'<details class="pp-faq-item"><summary>(.*?)</summary><p>(.*?)</p></details>', s, re.S)
    cost = (H.unescape(cost_q.group(1)), H.unescape(cost_q.group(2)))
    s = s.replace(f'{SLUG[svc]}-salt-lake-city', slug)
    s = re.sub(r'"areaServed": \[.*?\]', '"areaServed": ' + json.dumps({'@type': 'City', 'name': f'{cname}, UT', 'geo': {
        '@type': 'GeoCoordinates', 'latitude': GEO[city][0], 'longitude': GEO[city][1]}}), s, count=1, flags=re.S)
    s = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*', lambda m: m.group(1) + desc, s)
    # "When to book" cards
    cards = ''.join(f'<div class="pp-card"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in when)
    s = re.sub(r'(<h2>When to Book [^<]*</h2><div class="pp-cards">).*?(</div></div></section>)',
               lambda m: m.group(1) + cards + m.group(2), s, count=1, flags=re.S)
    keep = {'Salt Lake City cleaning price guide': 'SLCPRICE', 'Salt Lake City reviews on Google': 'SLCREV',
            'house-cleaning-cost-salt-lake-city': 'SLCCOST', 'House cleaning in Salt Lake City': 'SLCPILL',
            '/house-cleaning-salt-lake-city': 'SLCURL', 'Salt Lake Valley': 'SLVALLEY'}
    for k, v in keep.items():
        s = s.replace(k, v)
    s = s.replace('Salt Lake City', cname)
    for k, v in keep.items():
        s = s.replace(v, k)
    # FAQs + FAQPage schema
    qas = [(cost[0].replace('Salt Lake City', cname), cost[1])] + faqs
    first = s.find('<details'); last = s.rfind('</details>') + len('</details>')
    s = s[:first] + '\n      '.join(f'<details class="pp-faq-item"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in qas) + s[last:]
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qas]}
    s = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
               lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', s, count=1, flags=re.S)
    (LEG / f'{slug}.html').write_text(s)
    # point the city page's service card at the local page
    cp = LEG / f'house-cleaning-{city}-ut.html'
    if cp.exists():
        c = cp.read_text()
        c = c.replace(f'<a class="pp-card pp-card--link" href="/{SLUG[svc]}-salt-lake-city"><h3>{card}',
                      f'<a class="pp-card pp-card--link" href="/{slug}"><h3>{card} in {cname}', 1)
        cp.write_text(c)
    return slug, f'{H.unescape(label)} in {cname}', desc

def main():
    made = [build(svc, city, *v) for (svc, city), v in PAGES.items()]
    sm = ROOT / 'sitemap.xml'; t = sm.read_text()
    for slug, _, _ in made:
        if f'/{slug}<' not in t:
            t = t.replace('</urlset>', f'  <url><loc>{SITE}/{slug}</loc><lastmod>2026-11-18</lastmod></url>\n</urlset>')
    sm.write_text(t)
    ll = ROOT / 'llms.txt'; t = ll.read_text()
    add = ''.join(f'- [{title}]({SITE}/{slug}): {desc}\n' for slug, title, desc in made if slug not in t)
    anchor = re.search(r'- \[House Cleaning in Draper\].*\n', t).group(0)
    ll.write_text(t.replace(anchor, anchor + add))
    print('\n'.join(f'{s}.html' for s, _, _ in made))

if __name__ == '__main__':
    main()
