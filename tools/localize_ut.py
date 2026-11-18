"""Make Utah city pages unique (local FAQs) and add suburb pages (West Jordan, South Jordan, Sandy, Draper).

Edits the content source in tools/legacy/, then run tools/build_pages_from_ga.py to rebuild.
Re-running is safe: FAQs are replaced, new pages are regenerated from the Murray template.
"""
import html as H, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEG = ROOT / 'tools' / 'legacy'
SITE = 'https://utah.propeachcleaning.com'
VETTED = ('Are your cleaners background-checked and insured?',
          'Yes. Only 4% of cleaners make it through our hiring process. Every cleaner is interviewed and background-checked, '
          'and Pro Peach Cleaning is licensed, bonded and insured.')

# Questions 2-4 per page (Q1 = the page's existing cost question, Q5 = VETTED)
FAQS = {
    'house-cleaning-salt-lake-city.html': [
        ('Do you clean older homes in the Avenues and Capitol Hill?',
         'Yes. Many homes in the Avenues and Capitol Hill are over 100 years old, with original wood floors, built-ins and '
         'vintage tile. We use gentle, eco-friendly products and take care with original surfaces.'),
        ('Do you clean downtown condos and apartments?',
         'Yes. We clean condos and apartments downtown and near the University of Utah. Tell us about parking, gate codes '
         'or building rules when you book so our team arrives prepared.'),
        ('How often should I book a cleaning in Salt Lake City?',
         'Most Salt Lake City clients book every two weeks. Winter inversions and spring dust bring extra grime indoors, '
         'so many add a deep clean in early spring.')],
    'house-cleaning-sugar-house.html': [
        ('Do you clean the older bungalows near Sugar House Park?',
         'Yes. Sugar House has many 1920s to 1950s bungalows with hardwood floors and original bathrooms. We clean them '
         'carefully with eco-friendly products and pay extra attention to older tile and grout.'),
        ('Can you clean my apartment near the S-Line?',
         'Yes. We clean apartments and condos near the S-Line streetcar and Sugar House business district, including '
         'move-out cleaning for renters and students from nearby Westminster University.'),
        ('How often should I book a cleaning in Sugar House?',
         'Busy professionals in Sugar House usually book every two weeks. Renters often add a move-out clean at the end '
         'of a lease, and pet owners near the park tend to choose weekly.')],
    'house-cleaning-millcreek-ut.html': [
        ('Do you clean mid-century and ranch homes in Millcreek?',
         'Yes. Many Millcreek homes are mid-century ramblers with finished basements. We clean every finished level, '
         'and pricing is based on square footage so your quote already covers the basement.'),
        ('Can you keep up with trail dust and dog hair?',
         'Yes. Millcreek Canyon trails are steps away for many residents, and dogs bring the dirt home. We focus on '
         'entryways, floors and baseboards, and weekly or biweekly visits keep pet hair under control.'),
        ('How often should I book a cleaning in Millcreek?',
         'Most Millcreek households book every two weeks. Homes with dogs or kids often go weekly, plus a deep clean '
         'in spring once the snow melts.')],
    'house-cleaning-holladay-ut.html': [
        ('Can you clean large homes in Holladay?',
         'Yes. Many Holladay homes are larger houses on big, tree-filled lots. Pricing is based on square footage, so '
         'we schedule the right team size and time to clean every level thoroughly.'),
        ('Do you clean before holiday hosting?',
         'Yes. Book a deep clean a day or two before guests arrive and we will detail the kitchen, bathrooms, floors '
         'and entertaining spaces. Holiday dates fill early, so reserve ahead.'),
        ('How often should I book a cleaning in Holladay?',
         'Most Holladay families book every two weeks. With so many mature trees, many add a deep clean in fall after '
         'the leaves come down.')],
    'house-cleaning-murray-ut.html': [
        ('Can you clean around hospital and shift-work schedules?',
         'Yes. Many Murray clients work at the nearby medical centers on rotating shifts. We book 7 days a week, and '
         'you can give us access with a key, lockbox or door code so you can sleep or work while we clean.'),
        ('Do you do move-out cleaning for Murray apartments?',
         'Yes. Our move-in/move-out cleaning covers inside cabinets, appliances, baseboards, bathrooms and floors in an '
         'empty home, which helps renters near Fashion Place hand back the keys with confidence.'),
        ('How often should I book a cleaning in Murray?',
         'Most Murray families book every two weeks. Apartment renters often choose monthly, and households with kids '
         'and pets usually prefer weekly.')],
    'house-cleaning-cottonwood-heights-ut.html': [
        ('Do you clean ski rentals and Airbnbs?',
         'Yes. Cottonwood Heights sits at the mouth of Big and Little Cottonwood Canyons, so ski-season rentals stay '
         'busy. Our Airbnb turnover cleaning resets the home between guests so it is ready for the next check-in.'),
        ('How do you handle winter salt and snowmelt?',
         'Ski boots and snowy driveways track salt and grit onto floors. We pay extra attention to entryways, mudrooms '
         'and hard floors, and remove salt residue so it does not dull your floors.'),
        ('How often should I book a cleaning in Cottonwood Heights?',
         'Most homeowners book every two weeks, and many switch to weekly during ski season. Rental hosts book a '
         'turnover clean after each stay.')],
    'house-cleaning-south-salt-lake-ut.html': [
        ('Do you clean Airbnbs in South Salt Lake?',
         'Yes. South Salt Lake is minutes from downtown, which makes it popular for short-term rentals. Our Airbnb '
         'turnover cleaning gets your unit ready for the next guest.'),
        ('Do you clean new apartments and townhomes along State Street?',
         'Yes. Many newer apartments and townhomes have open kitchens, quartz counters and luxury vinyl floors. We use '
         'surface-safe products and damp-mop LVP instead of soaking it.'),
        ('How often should I book a cleaning in South Salt Lake?',
         'Apartment residents often book every two weeks or monthly. Renters add a move-out clean at the end of a '
         'lease, and rental hosts book after each stay.')],
}

NEW = {
    'west-jordan': dict(
        city='West Jordan', geo=(40.6097, -111.9391),
        desc='House cleaning in West Jordan, UT. Recurring, deep, move-out and Airbnb cleaning by background-checked, eco-friendly cleaners. Book online.',
        card='House cleaning in West Jordan, UT: recurring, deep and move-in/move-out cleaning for growing west-side families.',
        intro=[('Family homes on the west side',
                'West Jordan has grown fast, with family neighborhoods spreading west along Bangerter Highway and the '
                'Mountain View Corridor. Many homes are two-story houses with finished basements and busy kitchens, and '
                'we clean every level with the same detailed checklist.'),
               ('Kids, pets and long commutes',
                'Between school, sports and the drive to work, weekends go fast. Recurring biweekly cleaning keeps floors, '
                'kitchens and bathrooms under control so West Jordan families get their Saturdays back.'),
               ('Moving into a new build?',
                'New construction leaves fine dust in vents, window tracks and cabinets for months. Our move-in cleaning '
                'clears it out so you can unpack into a truly clean home.')],
        hoods=['Jordan Landing area', 'Gardner Village area', 'Highlands', 'Oquirrh Shadows', 'Copper Hills area', 'Sugar Factory Road area'],
        faqs=[('Do you clean homes with finished basements in West Jordan?',
               'Yes. Many West Jordan homes have a finished basement used as a family room or guest suite. We include every '
               'finished level, and pricing is based on square footage so your quote already covers it.'),
              ('How do you handle hard water spots?',
               'Salt Lake Valley water is very hard, which leaves white spots on faucets, shower glass and fixtures. Our '
               'deep clean targets hard-water buildup, and regular visits keep it from coming back.'),
              ('How often should I book a cleaning in West Jordan?',
               'Most West Jordan families book every two weeks. Homes with several kids or pets often go weekly, and many '
               'add a deep clean in spring.')],
        near=['south-jordan', 'murray-ut', 'sandy', 'salt-lake-city']),
    'south-jordan': dict(
        city='South Jordan', geo=(40.5622, -111.9297),
        desc='House cleaning in South Jordan, UT, including Daybreak. Recurring, deep, move-out and Airbnb cleaning by background-checked cleaners.',
        card='House cleaning in South Jordan and Daybreak, UT: recurring, deep and move-in cleaning for newer homes.',
        intro=[('Daybreak and beyond',
                'From the townhomes and cottages around Oquirrh Lake in Daybreak to the larger homes east of Bangerter, '
                'South Jordan is full of newer houses with open layouts. We clean them all with the same detailed checklist.'),
               ('Newer homes, modern surfaces',
                'Quartz counters, luxury vinyl plank floors and big glass showers look great but need the right products. '
                'Our cleaners use surface-safe, eco-friendly supplies that will not dull finishes or leave streaks.'),
               ('Busy families, recurring help',
                'Biweekly cleaning is our most popular option in South Jordan: kitchens, bathrooms and floors stay '
                'consistently clean without giving up your weekends.')],
        hoods=['Daybreak', 'Oquirrh Lake area', 'The District area', 'Glenmoor', 'River Park area', 'Bingham Junction area'],
        faqs=[('Do you clean homes and townhomes in Daybreak?',
               'Yes. We clean single-family homes, cottages and townhomes throughout Daybreak. Let us know about any '
               'parking details or gate codes when you book.'),
              ('Can you clean a new-construction home before we move in?',
               'Yes. Our move-in cleaning removes builder dust from cabinets, drawers, window tracks, vents and baseboards '
               'so you can unpack into a clean house.'),
              ('How often should I book a cleaning in South Jordan?',
               'Most South Jordan families book every two weeks. Larger households often choose weekly, and new homeowners '
               'usually start with a move-in clean.')],
        near=['west-jordan', 'sandy', 'draper', 'murray-ut']),
    'sandy': dict(
        city='Sandy', geo=(40.5649, -111.8389),
        desc='House cleaning in Sandy, UT. Recurring, deep, move-out and ski-rental cleaning by background-checked, eco-friendly cleaners. Book online.',
        card='House cleaning in Sandy, UT: recurring, deep, move-out and ski-season rental cleaning near Little Cottonwood Canyon.',
        intro=[('Close to the canyons',
                'Sandy sits at the doorstep of Little Cottonwood Canyon, so ski gear, hiking boots and snowmelt are part '
                'of everyday life. We focus on the entryways, mudrooms and floors that take the most wear.'),
               ('Established neighborhoods and newer builds',
                'From the established homes near Dimple Dell Park to newer houses on the east bench, Sandy homes range '
                'from cozy ramblers to large multi-level houses. Pricing is based on square footage, so every size fits.'),
               ('Rentals and move-outs',
                'Hosting skiers or moving out of a rental? Our Airbnb turnover and move-out cleaning get the space ready '
                'for the next guest or resident.')],
        hoods=['Dimple Dell area', 'East Sandy bench', 'South Towne area', 'Historic Sandy', 'Willow Creek area', 'Alta Canyon area'],
        faqs=[('Do you clean ski-season rentals in Sandy?',
               'Yes. Sandy is a popular base for skiing Little Cottonwood Canyon. Our Airbnb turnover cleaning resets the '
               'kitchen, bathrooms and floors between guests so your rental is ready for the next check-in.'),
              ('How do you handle snow, salt and mud on floors?',
               'Winter brings salt and grit into entryways. We pay extra attention to mudrooms, entry tile and hard floors '
               'and remove salt residue so it does not dull your floors.'),
              ('How often should I book a cleaning in Sandy?',
               'Most Sandy families book every two weeks, and many switch to weekly during ski season. Rental hosts book '
               'a turnover clean after each stay.')],
        near=['draper', 'cottonwood-heights-ut', 'south-jordan', 'murray-ut']),
    'draper': dict(
        city='Draper', geo=(40.5247, -111.8638),
        desc='House cleaning in Draper, UT. Recurring, deep, move-out and Airbnb cleaning by background-checked, eco-friendly cleaners. Book online.',
        card='House cleaning in Draper, UT: recurring, deep and move-in/move-out cleaning for larger family homes.',
        intro=[('Larger homes, detailed cleaning',
                'Many Draper homes are larger multi-level houses with bonus rooms, finished basements and several bathrooms. '
                'We plan the right team size and time to clean every level thoroughly.'),
               ('Trail dust and active families',
                'With Corner Canyon trails close by, bikes, shoes and dogs bring the outdoors in. We focus on entryways, '
                'floors and baseboards so the dirt does not spread through the house.'),
               ('Hosting and holidays',
                'Planning a party or family visit? A deep clean before guests arrive gets the kitchen, bathrooms and '
                'living spaces ready to impress.')],
        hoods=['Corner Canyon area', 'South Mountain', 'Suncrest', 'Draper Park area', 'SoJo Station area', 'East Draper bench'],
        faqs=[('Do you clean large homes with several bathrooms in Draper?',
               'Yes. Many Draper homes have four or more bathrooms, bonus rooms and finished basements. Pricing is based on '
               'square footage, so we schedule the right team and time for your home.'),
              ('Do you clean homes up in Suncrest?',
               'We serve Draper, including many homes on the bench and up toward Suncrest. Enter your address when you book '
               'and we will confirm it is in our area.'),
              ('How often should I book a cleaning in Draper?',
               'Most Draper families book every two weeks, and larger households often choose weekly. Many add a deep '
               'clean before the holidays.')],
        near=['sandy', 'south-jordan', 'cottonwood-heights-ut', 'holladay-ut']),
}
NAMES = {'salt-lake-city': 'Salt Lake City', 'murray-ut': 'Murray', 'holladay-ut': 'Holladay', 'millcreek-ut': 'Millcreek',
         'cottonwood-heights-ut': 'Cottonwood Heights', 'south-salt-lake-ut': 'South Salt Lake', 'sugar-house': 'Sugar House',
         **{k: v['city'] for k, v in NEW.items()}}
SLUG = {k: (k if k in ('salt-lake-city', 'sugar-house') or k.endswith('-ut') else k + '-ut') for k in NAMES}

def e(t):
    return H.escape(t, quote=False).replace("'", '&#x27;')

def set_faqs(s, qas):
    """Replace the <details> FAQ list and the FAQPage JSON-LD with qas."""
    first = s.find('<details'); last = s.rfind('</details>') + len('</details>')
    items = '\n      '.join(f'<details class="pp-faq-item"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in qas)
    s = s[:first] + items + s[last:]
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qas]}
    return re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', s, count=1, flags=re.S)

def first_faq(s):
    m = re.search(r'<details class="pp-faq-item"><summary>(.*?)</summary><p>(.*?)</p></details>', s, re.S)
    return H.unescape(m.group(1)), H.unescape(m.group(2))

def pills(keys):
    return ''.join(f'<a class="pp-pill" href="/house-cleaning-{SLUG[k]}">House cleaning in {NAMES[k]}</a>' for k in keys)

def new_page(key, d):
    s = (LEG / 'house-cleaning-murray-ut.html').read_text()
    slug = SLUG[key]
    cost = first_faq(s)
    s = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{d["desc"]}"', s)
    s = re.sub(r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{d["desc"]}"', s)
    s = re.sub(r'<meta name="twitter:description" content="[^"]*"', f'<meta name="twitter:description" content="{d["desc"]}"', s)
    s = s.replace('"latitude": 40.6669, "longitude": -111.888', f'"latitude": {d["geo"][0]}, "longitude": {d["geo"][1]}')
    # intro prose (the three h2/p pairs before the services section)
    prose = ''.join(f'\n      <h2>{e(h)}</h2>\n      <p>{e(p)}</p>' for h, p in d['intro'])
    s = re.sub(r'(<div class="pp-in pp-prose">)\s*<h2>Central-valley.*?(\n    </div></section>)', lambda m: m.group(1) + prose + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'<ul class="pp-hoods">.*?</ul>', '<ul class="pp-hoods">' + ''.join(f'<li>{e(h)}</li>' for h in d['hoods']) + '</ul>', s, count=1, flags=re.S)
    s = re.sub(r'(<h2>Nearby Areas We Serve</h2><div class="pp-pills">).*?(<a class="pp-pill pp-pill--alt")',
               lambda m: m.group(1) + pills(d['near']) + m.group(2), s, count=1, flags=re.S)
    s = s.replace('house-cleaning-murray-ut', 'house-cleaning-' + slug).replace('Murray', d['city'])
    s = set_faqs(s, [(cost[0].replace('Murray', d['city']), cost[1])] + d['faqs'] + [VETTED])
    assert 'Murray' not in s and 'Central-valley' not in s and 'Fashion Place' not in s, key
    (LEG / f'house-cleaning-{slug}.html').write_text(s)
    return slug

def add_pills(name, keys):
    p = LEG / name; s = p.read_text()
    keys = [k for k in keys if f'house-cleaning-{SLUG[k]}"' not in s]
    if keys:
        s = s.replace('<a class="pp-pill pp-pill--alt" href="/service-areas">', pills(keys) + '<a class="pp-pill pp-pill--alt" href="/service-areas">', 1)
        p.write_text(s)

def main():
    for name, qas in FAQS.items():
        p = LEG / name; s = p.read_text()
        p.write_text(set_faqs(s, [first_faq(s)] + qas + [VETTED]))
    slugs = [new_page(k, d) for k, d in NEW.items()]
    add_pills('house-cleaning-murray-ut.html', ['west-jordan', 'south-jordan'])
    add_pills('house-cleaning-cottonwood-heights-ut.html', ['sandy', 'draper'])
    add_pills('house-cleaning-holladay-ut.html', ['sandy'])
    add_pills('house-cleaning-salt-lake-city.html', ['west-jordan', 'south-jordan', 'sandy', 'draper'])
    # service areas: ItemList + city cards
    p = LEG / 'service-areas.html'; s = p.read_text()
    for k, d in NEW.items():
        url = f'{SITE}/house-cleaning-{SLUG[k]}'
        if url in s:
            continue
        n = s.count('"@type": "ListItem", "position"')
        s = s.replace(']}</script>', f', {{"@type": "ListItem", "position": {n + 1}, "url": "{url}", "name": "House Cleaning {d["city"]}"}}]}}</script>', 1)
        card = f'<a class="pp-card pp-card--link" href="/house-cleaning-{SLUG[k]}"><h3>{d["city"]}</h3><p>{e(d["card"])}</p></a>'
        i = s.find('<h2>Choose Your City</h2>'); j = s.find('</div></div></section>', i)
        s = s[:j] + card + s[j:]
    p.write_text(s)
    # sitemap + llms.txt
    sm = ROOT / 'sitemap.xml'; t = sm.read_text()
    for slug in slugs:
        if slug not in t:
            t = t.replace('</urlset>', f'  <url><loc>{SITE}/house-cleaning-{slug}</loc><lastmod>2026-11-18</lastmod></url>\n</urlset>')
    sm.write_text(t)
    ll = ROOT / 'llms.txt'; t = ll.read_text()
    anchor = re.search(r'- \[House Cleaning in Murray\].*\n', t).group(0)
    add = ''.join(f'- [House Cleaning in {d["city"]}]({SITE}/house-cleaning-{SLUG[k]}): {d["desc"]}\n' for k, d in NEW.items() if SLUG[k] not in t)
    ll.write_text(t.replace(anchor, anchor + add))
    print('updated FAQs:', len(FAQS), 'new pages:', slugs)

if __name__ == '__main__':
    main()
