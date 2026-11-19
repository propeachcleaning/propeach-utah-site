"""Expand the Utah site to the full service area (Salt Lake, Davis and Utah counties, owner-confirmed 2026-11-18).

Adds city pages (via localize_ut.new_page, Murray template) and deep / move-out pages for the bigger cities
(via service_city_ut.build), then updates the service-areas hub, sitemap and llms.txt.
Run: python3 tools/expand_ut.py   then build with tools/build_pages_from_ga.py <printed names>
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import localize_ut as LU
import service_city_ut as SC

ROOT = LU.ROOT; LEG = LU.LEG; SITE = LU.SITE

# key: (name, county, lat, lon, local headline, local paragraph, homes, life, hoods, near keys, (local Q, A), service?)
C = {
 'west-valley-city': ('West Valley City', 'Salt Lake', 40.6916, -112.0011, 'Utah\'s second-largest city',
   'West Valley City is home to the Maverik Center and the Utah Cultural Celebration Center, and to families from all over the world. Neighborhoods range from classic ramblers and split-levels to newer townhomes off Bangerter and the Mountain View Corridor.',
   'ramblers, split-levels and newer townhomes', 'big families and long commutes',
   ['Hunter', 'Granger', 'Chesterfield', 'Redwood', 'Lake Park area', 'Maverik Center area'], ['taylorsville', 'kearns', 'magna', 'west-jordan'],
   ('Do you clean homes with large families in West Valley City?', 'Yes. Busy kitchens, extra bathrooms and lots of foot traffic are what we do every day. Pricing is based on square footage, and you can tell us which rooms to focus on first.'), True),
 'taylorsville': ('Taylorsville', 'Salt Lake', 40.6677, -111.9388, 'Central valley living',
   'Taylorsville sits in the middle of the valley near Valley Regional Park and the Salt Lake Community College Redwood campus, with established neighborhoods of brick ramblers, condos and apartments.',
   'brick ramblers, condos and apartments', 'students, commuters and families',
   ['Valley Regional Park area', 'Redwood Road corridor', 'Bennion', 'Plymouth', 'SLCC Redwood campus area', 'Atherton'], ['murray-ut', 'west-valley-city', 'kearns', 'west-jordan'],
   ('Do you clean apartments near the SLCC Redwood campus?', 'Yes. We clean apartments and condos for students and staff, including move-out cleaning at the end of a lease so you can hand back the keys with confidence.'), True),
 'midvale': ('Midvale', 'Salt Lake', 40.6111, -111.8999, 'Old Town charm, new apartments',
   'Midvale mixes Old Town Midvale and older bungalows with new apartments and townhomes at Bingham Junction and along the TRAX lines near Fort Union.',
   'bungalows, apartments and townhomes', 'renters and professionals near TRAX',
   ['Old Town Midvale', 'Bingham Junction', 'Fort Union area', 'East Midvale', 'Union Park area', 'Jordan River area'], ['sandy-ut', 'murray-ut', 'cottonwood-heights-ut', 'south-jordan'],
   ('Do you clean new apartments at Bingham Junction?', 'Yes. Newer apartments and townhomes have quartz counters, glass showers and luxury vinyl floors, and we use surface-safe products that keep them looking new.'), True),
 'riverton': ('Riverton', 'Salt Lake', 40.5219, -111.9391, 'Family neighborhoods in the southwest valley',
   'Riverton is known for Riverton City Park, the Mountain View Village shopping area and street after street of two-story family homes, many with finished basements.',
   'two-story family homes with finished basements', 'kids, sports and busy weeknights',
   ['Riverton City Park area', 'Mountain View Village area', 'Western Springs', 'Riverton Ranches', 'Rose Creek', 'Old Riverton'], ['herriman', 'south-jordan', 'bluffdale', 'west-jordan'],
   ('Do you clean finished basements in Riverton?', 'Yes. We clean every finished level, and since pricing is based on square footage, your quote already covers the basement.'), True),
 'herriman': ('Herriman', 'Salt Lake', 40.5141, -112.0330, 'One of the fastest-growing cities in Utah',
   'Herriman has grown fast, with new neighborhoods around Herriman Towne Center, Rose Creek and the Real Salt Lake academy, and lots of newly built homes with open layouts.',
   'newly built homes with open floor plans', 'young families settling into new builds',
   ['Herriman Towne Center', 'Rose Creek', 'Juniper Canyon', 'Anthem', 'Rosecrest', 'Hidden Oaks'], ['riverton', 'bluffdale', 'south-jordan', 'west-jordan'],
   ('Can you clean a new-construction home before we move in?', 'Yes. Our move-in cleaning clears builder dust from cabinets, drawers, vents, window tracks and baseboards so you can unpack into a clean house.'), True),
 'bluffdale': ('Bluffdale', 'Salt Lake', 40.4897, -111.9388, 'Room to spread out',
   'Bluffdale near the Point of the Mountain has larger lots, horse properties and newer neighborhoods like Independence, with homes that see plenty of dirt, pets and outdoor gear.',
   'larger homes on bigger lots', 'pets, horses and outdoor living',
   ['Independence', 'Point of the Mountain area', 'Camp Williams area', 'Bluffdale Heights', 'Jordan Narrows area', 'Wood Hollow'], ['riverton', 'herriman', 'draper', 'south-jordan'],
   ('Do you clean larger homes on acreage?', 'Yes. Pricing is based on the home\'s square footage, and we pay extra attention to entryways and mudrooms where dirt and pet hair come in.'), False),
 'kearns': ('Kearns', 'Salt Lake', 40.6599, -111.9963, 'Home of the Utah Olympic Oval',
   'Kearns, home of the Utah Olympic Oval, is full of affordable ramblers and family homes on the west side of the valley.',
   'ramblers and family homes', 'working families',
   ['Olympic Oval area', 'Kearns Park area', 'West Kearns', 'Copper Hills area', '5400 South corridor', 'Oquirrh Park'], ['west-valley-city', 'taylorsville', 'magna', 'west-jordan'],
   ('Do you offer move-out cleaning for rentals in Kearns?', 'Yes. Move-out cleaning covers inside cabinets, appliances, closets, baseboards and bathrooms so the home is ready for inspection or the next tenant.'), False),
 'magna': ('Magna', 'Salt Lake', 40.7091, -112.1016, 'Historic Main Street on the west side',
   'Magna has a historic Main Street, older miner\'s homes and newer subdivisions near the Oquirrh foothills and the Great Salt Lake shoreline.',
   'historic homes and newer subdivisions', 'families on the west side',
   ['Main Street Magna', 'Oquirrh foothills', 'Pleasant Green', 'Copper Park area', 'Magna Town Center', 'Saltair area'], ['west-valley-city', 'kearns', 'taylorsville'],
   ('Do you clean older homes in Magna?', 'Yes. Older homes often have original wood floors and trim, so our cleaners use gentle, eco-friendly products and take extra care with older surfaces.'), False),
 'bountiful': ('Bountiful', 'Davis', 40.8894, -111.8808, 'East bench homes with valley views',
   'Bountiful climbs up the east bench toward the mountains, with established ramblers, larger view homes near the Bountiful Temple and plenty of mature trees.',
   'established ramblers and larger bench homes', 'families who have been here for years',
   ['East Bench', 'Bountiful Temple area', 'Val Verda', 'Main Street Bountiful', 'Mueller Park area', 'Orchard Drive area'], ['woods-cross', 'centerville', 'north-salt-lake', 'salt-lake-city'],
   ('Do you clean multi-level bench homes in Bountiful?', 'Yes. Many Bountiful homes have several levels and walkout basements. We clean every finished level, and pricing is based on square footage.'), True),
 'centerville': ('Centerville', 'Davis', 40.9180, -111.8722, 'Quiet family neighborhoods in south Davis County',
   'Centerville is a quiet Davis County city of family homes between Bountiful and Farmington, close to Legacy Parkway and the foothill trails.',
   'family homes and foothill houses', 'families who love the trails',
   ['East Centerville', 'Parrish Lane area', 'Centerville Main Street', 'Deuel Creek area', 'Legacy Parkway area', 'Community Park area'], ['bountiful', 'farmington', 'woods-cross'],
   ('Do you clean homes near the foothill trails?', 'Yes. Trail dust and pet hair come home with you, so we focus on entryways, floors and baseboards to keep them from spreading through the house.'), False),
 'farmington': ('Farmington', 'Davis', 40.9805, -111.8874, 'Station Park and Lagoon',
   'Farmington is home to Station Park and Lagoon, with newer neighborhoods west of I-15 and established homes up toward the foothills.',
   'newer homes and established foothill houses', 'families near Station Park',
   ['Station Park area', 'Lagoon area', 'Farmington Ranches', 'Historic Farmington', 'Oakridge area', 'Shepard Creek'], ['kaysville', 'centerville', 'bountiful'],
   ('Do you clean townhomes near Station Park?', 'Yes. We clean townhomes, condos and single-family homes around Station Park and across Farmington.'), True),
 'kaysville': ('Kaysville', 'Davis', 41.0352, -111.9385, 'Small-town Main Street, big family homes',
   'Kaysville has a small-town Main Street, Barnes Park and plenty of larger family homes, many with bonus rooms and finished basements.',
   'larger family homes with bonus rooms', 'busy families with kids',
   ['Main Street Kaysville', 'Barnes Park area', 'East Kaysville', 'Hill Farms', 'Fairfield area', 'Flint Street area'], ['layton', 'farmington', 'centerville'],
   ('Do you clean large homes with bonus rooms in Kaysville?', 'Yes. Pricing is based on square footage, so we plan the right team and time to clean every room thoroughly.'), True),
 'layton': ('Layton', 'Davis', 41.0602, -111.9711, 'Next door to Hill Air Force Base',
   'Layton is the largest city in Davis County, home to Layton Hills Mall and many military families stationed at nearby Hill Air Force Base.',
   'family homes, townhomes and rentals', 'military families and frequent moves',
   ['Layton Hills Mall area', 'East Layton', 'Hill AFB area', 'Ellison Park area', 'Layton Commons', 'Kays Creek'], ['kaysville', 'clearfield', 'syracuse', 'farmington'],
   ('Do you clean homes for military families moving near Hill AFB?', 'Yes. Move-in and move-out cleaning is popular with families on PCS moves. We clean inside cabinets, appliances and closets so the home is ready for inspection or move-in day.'), True),
 'north-salt-lake': ('North Salt Lake', 'Davis', 40.8486, -111.9069, 'Foxboro and Eaglewood',
   'North Salt Lake stretches from Foxboro\'s newer neighborhoods to hillside homes near Eaglewood Golf Course, just minutes from downtown Salt Lake City.',
   'newer townhomes and hillside homes', 'commuters into Salt Lake City',
   ['Foxboro', 'Eaglewood', 'Orchard Drive area', 'Highland Drive area', 'Legacy Crossing', 'Hatch Park area'], ['woods-cross', 'bountiful', 'salt-lake-city'],
   ('Do you clean townhomes in Foxboro?', 'Yes. We clean townhomes and single-family homes throughout Foxboro and the rest of North Salt Lake.'), False),
 'woods-cross': ('Woods Cross', 'Davis', 40.8716, -111.8924, 'Small city, quick commute',
   'Woods Cross is a small Davis County city with newer townhomes near Legacy Parkway and the FrontRunner station, plus established neighborhoods to the east.',
   'townhomes and established homes', 'commuters on FrontRunner',
   ['FrontRunner station area', 'Legacy Parkway area', 'East Woods Cross', '2600 South area', 'Mills Park area', 'Hogan Park area'], ['bountiful', 'north-salt-lake', 'centerville'],
   ('Can you clean while I am at work?', 'Yes. Many clients give us access with a key, lockbox or door code and come home to a clean house.'), False),
 'clearfield': ('Clearfield', 'Davis', 41.1108, -112.0261, 'Close to Hill AFB and Freeport Center',
   'Clearfield sits next to Hill Air Force Base and the Freeport Center, with many rentals, townhomes and starter homes.',
   'rentals, townhomes and starter homes', 'renters and military families',
   ['Freeport Center area', 'Hill AFB area', 'Clearfield Station area', 'Steed Park area', 'North Clearfield', 'Fisher Park area'], ['layton', 'syracuse', 'kaysville'],
   ('Do you offer move-out cleaning for Clearfield rentals?', 'Yes. Move-out cleaning covers inside cabinets, appliances, closets, baseboards and bathrooms so renters can hand back the keys with confidence.'), False),
 'syracuse': ('Syracuse', 'Davis', 41.0894, -112.0647, 'Gateway to Antelope Island',
   'Syracuse, the gateway to the Antelope Island causeway, has grown quickly with newer subdivisions and larger family homes.',
   'newer subdivisions and larger family homes', 'growing families',
   ['Antelope Drive area', 'Jensen Park area', 'West Syracuse', 'Bluff Ridge', 'Founders Park area', 'Doral Lane area'], ['layton', 'clearfield', 'kaysville'],
   ('Can you deep clean a newer home in Syracuse?', 'Yes. A deep clean reaches baseboards, vents, window tracks and the construction dust that keeps surfacing in newer homes.'), False),
 'lehi': ('Lehi', 'Utah', 40.3916, -111.8508, 'Silicon Slopes and Thanksgiving Point',
   'Lehi is home to Silicon Slopes tech offices and Thanksgiving Point, with newer neighborhoods on Traverse Mountain and around Holbrook Farms.',
   'newer two-story homes and townhomes', 'tech professionals with busy schedules',
   ['Traverse Mountain', 'Thanksgiving Point area', 'Holbrook Farms', 'Old Lehi', 'Silicon Slopes area', 'Ivory Ridge'], ['american-fork', 'saratoga-springs', 'highland', 'draper'],
   ('Can you clean while I am at work in Silicon Slopes?', 'Yes. Many Lehi clients give us a key, lockbox or door code and come home to a clean house at the end of the day.'), True),
 'american-fork': ('American Fork', 'Utah', 40.3769, -111.7958, 'Main Street and the canyon',
   'American Fork has a historic Main Street and quick access to American Fork Canyon and Timpanogos Cave, with a mix of established homes and newer subdivisions.',
   'established homes and newer subdivisions', 'families who love the canyon',
   ['Historic Main Street', 'American Fork Canyon area', 'The Meadows', 'Art Dye Park area', 'North American Fork', 'Barratt area'], ['lehi', 'pleasant-grove', 'highland', 'alpine'],
   ('Do you clean homes with lots of outdoor gear and pets?', 'Yes. We focus on mudrooms, entryways and floors where canyon dirt and pet hair collect, and weekly or biweekly visits keep it under control.'), True),
 'pleasant-grove': ('Pleasant Grove', 'Utah', 40.3641, -111.7385, 'At the foot of Mount Timpanogos',
   'Pleasant Grove sits below Mount Timpanogos, known for Strawberry Days and the Battle Creek Falls trail, with family homes on quiet streets.',
   'family homes on quiet streets', 'outdoorsy families',
   ['Battle Creek area', 'Downtown Pleasant Grove', 'Grove Creek', 'Manila area', 'Discovery Park area', 'North Pleasant Grove'], ['american-fork', 'lindon', 'orem'],
   ('Do you clean homes near the Battle Creek trailhead?', 'Yes. Trail dust and muddy boots come home with you, so we pay extra attention to entryways and floors.'), True),
 'orem': ('Orem', 'Utah', 40.2969, -111.6946, 'Utah Valley University and University Place',
   'Orem is home to Utah Valley University and University Place, with student apartments, established ramblers and family homes across the city.',
   'student apartments, ramblers and family homes', 'students and families',
   ['UVU area', 'University Place area', 'Orem Center Street', 'Windsor', 'Cherry Hill', 'Sharon Park'], ['provo', 'lindon', 'pleasant-grove'],
   ('Do you clean student apartments near UVU?', 'Yes. We clean apartments and rental homes near Utah Valley University, including move-out cleaning at the end of a contract.'), True),
 'provo': ('Provo', 'Utah', 40.2338, -111.6585, 'BYU, downtown and the Provo River',
   'Provo blends BYU student housing, downtown condos and older homes near Center Street with family neighborhoods along the Provo River.',
   'student housing, condos and older family homes', 'students, landlords and families',
   ['BYU area', 'Downtown Provo', 'Joaquin', 'Riverside', 'Edgemont', 'Grandview'], ['orem', 'springville', 'spanish-fork'],
   ('Do you clean student housing near BYU?', 'Yes. Move-out cleaning is especially busy at the end of semesters. It covers inside cabinets, the fridge and the oven so tenants can hand back the keys with confidence.'), True),
 'saratoga-springs': ('Saratoga Springs', 'Utah', 40.3491, -111.9047, 'Newer homes along Utah Lake',
   'Saratoga Springs has grown along the Utah Lake shoreline with newer subdivisions and larger family homes.',
   'newer subdivisions and larger family homes', 'young families in new homes',
   ['Utah Lake shoreline', 'Harbor Park area', 'Saratoga Hills', 'Talus Ridge', 'Wildflower', 'Jacobs Ranch'], ['lehi', 'eagle-mountain', 'american-fork'],
   ('Can you clean a new build in Saratoga Springs?', 'Yes. Our move-in cleaning removes builder dust from cabinets, drawers, vents and window tracks before you unpack.'), True),
 'eagle-mountain': ('Eagle Mountain', 'Utah', 40.3141, -112.0069, 'Room to grow',
   'Eagle Mountain is one of Utah\'s fastest-growing cities, with new neighborhoods, larger homes and plenty of wind-blown dust from open land nearby.',
   'newer, larger family homes', 'growing families',
   ['Eagle Mountain City Center', 'Silver Lake', 'Pony Express area', 'Porter\'s Crossing', 'Cedar Valley', 'Ranches area'], ['saratoga-springs', 'lehi'],
   ('How do you handle dust in a newer Eagle Mountain home?', 'Open land and construction nearby mean extra dust on window sills, tracks and floors. A deep clean resets it, and regular visits keep it from building up.'), True),
 'highland': ('Highland', 'Utah', 40.4252, -111.7952, 'Large homes on big lots',
   'Highland is known for large homes on half-acre lots near the mouth of American Fork Canyon.',
   'large homes on big lots', 'larger households',
   ['Highland Town Center', 'Murdock Canal Trail area', 'Highland Glen', 'Beacon Hills', 'Dry Creek area', 'Skye Ridge'], ['alpine', 'american-fork', 'lehi'],
   ('Can you clean a large Highland home in one visit?', 'Yes. Pricing is based on square footage, so we schedule enough team and time to finish your whole home.'), False),
 'alpine': ('Alpine', 'Utah', 40.4533, -111.7779, 'Mountain homes near Lambert Park',
   'Alpine sits right against the mountains near Lambert Park, with larger custom homes and plenty of trail dust and wildlife nearby.',
   'larger custom homes', 'outdoorsy families',
   ['Lambert Park area', 'Alpine Main Street', 'Box Elder area', 'Healey Boulevard area', 'Fort Canyon area', 'Three Falls'], ['highland', 'american-fork', 'lehi'],
   ('Do you clean large custom homes in Alpine?', 'Yes. We clean larger homes with several levels and bathrooms and take extra care with stone, wood and custom finishes.'), False),
 'lindon': ('Lindon', 'Utah', 40.3433, -111.7208, 'Small city, larger lots',
   'Lindon is a small Utah County city between Orem and Pleasant Grove with larger lots and family homes.',
   'family homes on larger lots', 'families with room to spread out',
   ['North Lindon', 'Lindon Hollow', 'Pioneer Park area', 'Lindon Center', 'East Lindon', 'Geneva Road area'], ['orem', 'pleasant-grove', 'american-fork'],
   ('Do you clean homes on larger lots in Lindon?', 'Yes. We clean the whole home, with extra attention on entryways and mudrooms where yard dirt comes in.'), False),
 'spanish-fork': ('Spanish Fork', 'Utah', 40.1149, -111.6549, 'South Utah County\'s growing city',
   'Spanish Fork, home of the Festival of Colors, is growing fast with newer neighborhoods and established homes near Main Street and Spanish Fork Canyon.',
   'newer neighborhoods and established homes', 'growing families',
   ['Main Street Spanish Fork', 'Spanish Fork Canyon area', 'Canyon Creek', 'River Bottoms', 'Sports Park area', 'Maple Mountain'], ['springville', 'provo'],
   ('Do you clean newer homes in Spanish Fork?', 'Yes. We clean new and established homes, including move-in cleaning to clear builder dust before you unpack.'), False),
 'springville': ('Springville', 'Utah', 40.1652, -111.6107, 'Art City',
   'Springville, Utah\'s "Art City" and home of the Springville Museum of Art, has a mix of historic homes and family neighborhoods.',
   'historic homes and family neighborhoods', 'families and longtime residents',
   ['Historic downtown', 'Museum of Art area', 'Hobble Creek Canyon area', 'Spring Acres', 'West Springville', 'Bartholomew Park area'], ['spanish-fork', 'provo'],
   ('Do you clean older historic homes in Springville?', 'Yes. Our cleaners use gentle products and take extra care with original wood floors, trim and older tile.'), False),
}


def city_data(key):
    name, county, lat, lon, h, p, homes, life, hoods, near, qa, _ = C[key]
    county_note = {'Salt Lake': 'Salt Lake Valley', 'Davis': 'Davis County', 'Utah': 'Utah County'}[county]
    return dict(
        city=name, geo=(lat, lon),
        desc=f'House cleaning in {name}, UT. Recurring, deep, move-in/move-out and Airbnb cleaning by background-checked, eco-friendly cleaners. Book online.',
        card=f'House cleaning in {name}, UT: recurring, deep and move-in/move-out cleaning for {homes}.',
        intro=[(h, p),
               (f'Homes we clean in {name}', f'{name} homes range from {homes}. We clean them all with the same detailed checklist, bring our own eco-friendly supplies, and back every clean with a 24-hour free touch-up.'),
               (f'Made for {life}', f'Recurring cleaning every week or two keeps kitchens, bathrooms and floors under control so you get your weekends back. Many {county_note} clients add a deep clean each spring after a long winter indoors.')],
        hoods=hoods,
        faqs=[qa,
              (f'Do you also clean near {name}?', f'Yes. Along with {name}, we clean homes across {county_note} and the Salt Lake Valley. Enter your address when you book and we will confirm it is in our area.'),
              (f'How often should I book a cleaning in {name}?', f'Most {name} households book every two weeks. Homes with kids or pets often go weekly, and many add a deep clean before the holidays or in spring.')],
        near=[n for n in near if n in LU.NAMES or n in C][:4] or ['salt-lake-city'])


def svc_data(svc, key):
    name, county, lat, lon, h, p, homes, life, hoods, near, qa, _ = C[key]
    if svc == 'deep':
        return (f'Deep cleaning in {name}, UT: baseboards, vents, cabinets, grout and hard-water buildup by background-checked, eco-friendly cleaners. Instant quote.',
                [('Spring reset after winter', f'Months of closed windows, snow and road salt leave dust and grime in {name} homes. A spring deep clean resets every room.'),
                 (f'Detail work for {homes}', f'Baseboards, vents, cabinet fronts and light fixtures get the attention a standard clean skips.'),
                 ('Before guests or after a project', 'Hosting, holidays or post-remodel dust? A deep clean gets the whole home ready.')],
                [(f'Do you deep clean {homes} in {name}?', f'Yes. We deep clean {homes} across {name}. Pricing is based on square footage, so every size home fits.'),
                 ('Can you remove hard-water spots?', 'Yes. Utah water is very hard. Our deep clean treats white buildup on faucets, shower glass and tile so fixtures shine again.'),
                 (f'How often should I deep clean in {name}?', 'Most homes do well with a deep clean two to four times a year, with standard cleaning every week or two in between.')])
    return (f'Move-in and move-out cleaning in {name}, UT: inside cabinets, appliances, closets and floors in empty homes. Background-checked cleaners. Instant quote.',
            [('Renters moving out', f'Hand back the keys to a spotless {name} home or apartment and give yourself the best chance at your deposit.'),
             ('Buyers and new owners', 'Move into a home that is truly clean, inside every cabinet, drawer and appliance.'),
             ('Landlords and property managers', f'Turn rentals quickly between tenants across {name} and nearby cities.')],
            [('Does the home need to be empty?', 'Yes. Move-in/move-out cleaning is designed for empty homes so we can reach inside every cabinet, closet and appliance.'),
             (f'Do you clean {homes} on move-out?', f'Yes. We clean {homes} throughout {name}, including every finished level. Pricing is based on square footage.'),
             ('What is included that a standard clean skips?', 'Inside cabinets and drawers, inside the oven, fridge and microwave, closets, shelves and window tracks.')])


def main():
    for k, v in C.items():
        LU.NAMES[k] = v[0]
        LU.SLUG[k] = k + '-ut'
        SC.GEO[k] = (v[2], v[3]); SC.NAME[k] = v[0]
    city_slugs, svc_slugs = [], []
    for k in C:
        city_slugs.append(LU.new_page(k, city_data(k)))
    for k, v in C.items():
        if v[11]:
            for svc in ('deep', 'move-out'):
                slug, title, desc = SC.build(svc, k, *svc_data(svc, k))
                svc_slugs.append((slug, title, desc))
    # service-areas hub: ItemList + cards
    p = LEG / 'service-areas.html'; s = p.read_text()
    for k, v in C.items():
        url = f'{SITE}/house-cleaning-{k}-ut'
        if url in s:
            continue
        n = s.count('"@type": "ListItem", "position"')
        s = s.replace(']}</script>', f', {{"@type": "ListItem", "position": {n + 1}, "url": "{url}", "name": "House Cleaning {v[0]}"}}]}}</script>', 1)
        card = f'<a class="pp-card pp-card--link" href="/house-cleaning-{k}-ut"><h3>{v[0]}</h3><p>{city_data(k)["card"]}</p></a>'
        i = s.find('<h2>Choose Your City</h2>'); j = s.find('</div></div></section>', i)
        s = s[:j] + card + s[j:]
    p.write_text(s)
    sm = ROOT / 'sitemap.xml'; t = sm.read_text()
    for slug in [f'house-cleaning-{x}' for x in city_slugs] + [x[0] for x in svc_slugs]:
        if f'/{slug}<' not in t:
            t = t.replace('</urlset>', f'  <url><loc>{SITE}/{slug}</loc><lastmod>2026-11-18</lastmod></url>\n</urlset>')
    sm.write_text(t)
    ll = ROOT / 'llms.txt'; t = ll.read_text().rstrip('\n') + '\n'
    for k in C:
        if f'house-cleaning-{k}-ut' not in t:
            t += f'- [House Cleaning in {C[k][0]}]({SITE}/house-cleaning-{k}-ut): {city_data(k)["desc"]}\n'
    for slug, title, desc in svc_slugs:
        if slug not in t:
            t += f'- [{title}]({SITE}/{slug}): {desc}\n'
    ll.write_text(t)
    names = [f'house-cleaning-{x}.html' for x in city_slugs] + [x[0] + '.html' for x in svc_slugs] + ['service-areas.html']
    print(' '.join(names))
    print(len(city_slugs), 'city pages,', len(svc_slugs), 'service pages')


if __name__ == '__main__':
    main()
