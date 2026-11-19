"""Utah county hub pages (Salt Lake, Davis, Utah counties) — mirrors the Nov 19 GA county hubs.
Uses localize_ut.new_page (Murray template); 'Nearby Areas' pills list every city page in the county.
Run: python3 tools/county_ut.py  then build with tools/build_pages_from_ga.py <printed names>"""
import io, contextlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
with contextlib.redirect_stdout(io.StringIO()):
    import localize_ut as LU, expand_ut as X
for k, v in X.C.items():
    LU.NAMES[k] = v[0]; LU.SLUG[k] = k + '-ut'
ORIG = {'Salt Lake': ['salt-lake-city', 'sugar-house', 'murray-ut', 'holladay-ut', 'millcreek-ut', 'cottonwood-heights-ut',
                      'south-salt-lake-ut', 'west-jordan', 'south-jordan', 'sandy', 'draper']}
def cities(county):
    return ORIG.get(county, []) + [k for k, v in X.C.items() if v[1] == county]
D = {
 'salt-lake-county': ('Salt Lake County', 'Salt Lake', (40.6670, -111.9240),
   ('The whole Salt Lake Valley', 'From Sugar House bungalows and downtown condos to family homes in Sandy, South Jordan, Riverton and Herriman, Salt Lake County is where Pro Peach Cleaning does most of its Utah work. We clean every corner of the valley on a recurring, deep or move-in/move-out basis.'),
   ('Homes we clean across the valley', 'Older brick ramblers on the east bench, split-levels in Taylorsville and West Valley, new builds out west and high-rise apartments downtown all get the same detailed checklist, eco-friendly supplies and 24-hour free touch-up.'),
   ('Winter grime and hard water', 'Road salt, snowmelt and inversion-season dust come indoors all winter, and valley water leaves white buildup on fixtures and glass. Recurring cleaning keeps it under control, and a spring deep clean resets the whole house.'),
   ('Which Salt Lake County cities do you serve?', 'Salt Lake City, Sugar House, MURRAY_NAME_PH, Holladay, Millcreek, Cottonwood Heights, South Salt Lake, West Valley City, Taylorsville, Midvale, West Jordan, South Jordan, Sandy, Draper, Riverton, Herriman, Bluffdale, Kearns, Magna and nearby communities.')),
 'davis-county': ('Davis County', 'Davis', (40.9900, -111.8870),
   ('North of Salt Lake, from Bountiful to Syracuse', 'Davis County families in Bountiful, Centerville, Farmington, Kaysville, Layton and Syracuse count on Pro Peach Cleaning for recurring, deep and move-in/move-out cleaning.'),
   ('Homes we clean in Davis County', 'Established bench homes in Bountiful, newer two-story subdivisions in Kaysville and Syracuse, and homes for Hill Air Force Base families in Layton and Clearfield all get our detailed checklist and 24-hour free touch-up.'),
   ('Busy families and military moves', 'Kids, sports and long commutes on I-15 leave little time for housework, and military families moving to or from Hill AFB rely on move-out and move-in cleaning to hand off or settle into a home quickly.'),
   ('Which Davis County cities do you serve?', 'Bountiful, Centerville, Farmington, Kaysville, Layton, North Salt Lake, Woods Cross, Clearfield, Syracuse and nearby Davis County communities.')),
 'utah-county': ('Utah County', 'Utah', (40.3200, -111.7500),
   ('From Lehi to Spanish Fork', 'Utah County is growing fast, and Pro Peach Cleaning cleans homes from Silicon Slopes in Lehi to Orem, Provo, Springville and Spanish Fork with recurring, deep and move-in/move-out cleaning.'),
   ('Homes we clean in Utah County', 'New builds in Saratoga Springs and Eagle Mountain, family homes in American Fork and Pleasant Grove, and student rentals near BYU and UVU all get the same detailed checklist and eco-friendly supplies.'),
   ('Lease turnover and new construction', 'Provo and Orem see heavy lease turnover around BYU and UVU semesters, and new-construction neighborhoods are full of builder dust. Our move-in and move-out cleaning handles both.'),
   ('Which Utah County cities do you serve?', 'Lehi, American Fork, Pleasant Grove, Orem, Provo, Saratoga Springs, Eagle Mountain, Highland, Alpine, Lindon, Spanish Fork, Springville and nearby Utah County communities.')),
}
def main():
    names = []
    for key, (name, county, geo, i1, i2, i3, qa) in D.items():
        LU.NAMES[key] = name; LU.SLUG[key] = key + '-ut'
        cs = cities(county)
        d = dict(city=name, geo=geo,
                 desc=f'House cleaning in {name}, UT: recurring, deep, move-in/move-out and Airbnb cleaning by background-checked, eco-friendly cleaners. Book online.',
                 card=f'House cleaning across {name}, UT.',
                 intro=[i1, i2, i3],
                 hoods=[LU.NAMES[c] for c in cs],
                 faqs=[qa,
                       (f'Do I need to be home during the cleaning in {name}?', 'No. Many clients leave a key, lockbox or door code. Just tell us how to get in when you book.'),
                       (f'How often should I book a cleaning in {name}?', 'Most households book every two weeks. Homes with kids or pets often go weekly, and many add a deep clean in spring and before the holidays.')],
                 near=cs)
        # Murray is the template city: new_page() swaps every 'Murray' for the page name, so
        # protect the real Murray link/name with placeholders and restore them afterwards.
        LU.NAMES['murray-ut'], LU.SLUG['murray-ut'] = 'MURRAY_NAME_PH', 'MURRAY_SLUG_PH'
        d['hoods'] = [LU.NAMES[c] for c in cs]
        slug = LU.new_page(key, d)
        LU.NAMES['murray-ut'], LU.SLUG['murray-ut'] = 'Murray', 'murray-ut'
        f = LU.LEG / f'house-cleaning-{slug}.html'
        f.write_text(f.read_text().replace('MURRAY_NAME_PH', 'Murray').replace('MURRAY_SLUG_PH', 'murray-ut'))
        names.append(f'house-cleaning-{slug}.html')
    # hub + sitemap + llms.txt
    p = LU.LEG / 'service-areas.html'; s = p.read_text()
    for key, v in D.items():
        url = f'{LU.SITE}/house-cleaning-{key}-ut'
        if url in s: continue
        n = s.count('"@type": "ListItem", "position"')
        s = s.replace(']}</script>', f', {{"@type": "ListItem", "position": {n + 1}, "url": "{url}", "name": "House Cleaning {v[0]}"}}]}}</script>', 1)
        card = f'<a class="pp-card pp-card--link" href="/house-cleaning-{key}-ut"><h3>{v[0]}</h3><p>All of our {v[0]} cities in one place.</p></a>'
        i = s.find('<h2>Choose Your City</h2>'); j = s.find('</div></div></section>', i)
        s = s[:j] + card + s[j:]
    p.write_text(s)
    sm = LU.ROOT / 'sitemap.xml'; t = sm.read_text()
    for key in D:
        if f'/house-cleaning-{key}-ut<' not in t:
            t = t.replace('</urlset>', f'  <url><loc>{LU.SITE}/house-cleaning-{key}-ut</loc><lastmod>2026-11-19</lastmod></url>\n</urlset>')
    sm.write_text(t)
    ll = LU.ROOT / 'llms.txt'; t = ll.read_text().rstrip('\n') + '\n'
    for key, v in D.items():
        if f'house-cleaning-{key}-ut' not in t:
            t += f'- [House Cleaning in {v[0]}]({LU.SITE}/house-cleaning-{key}-ut): House cleaning across {v[0]}, UT.\n'
    ll.write_text(t)
    print(' '.join(names + ['service-areas.html']))
if __name__ == '__main__':
    main()
