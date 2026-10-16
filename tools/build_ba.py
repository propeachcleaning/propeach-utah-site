"""Insert the Pro Peach before/after photo card on Utah pages (idempotent). Photos: real cleaning jobs; alt text makes no city claims."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
P = {
 "oven": ("Oven and range", "oven-cleaning", "debris inside the oven", "a spotless black range"),
 "glass": ("Oven door glass", "oven-door-glass-cleaning", "baked-on grease on the oven door glass", "clear oven door glass"),
 "fridge": ("Refrigerator", "fridge-cleaning", "crumbs and spills on the fridge shelves", "clean, wiped fridge shelves"),
 "shower": ("Shower floor", "shower-deep-cleaning", "soap scum and grime on the shower floor", "a bright white shower floor"),
 "stove": ("Stovetop", "stovetop-cleaning", "crumbs and grease on a white stovetop", "a gleaming white stovetop"),
 "office": ("Office floor", "office-cleaning", "debris scattered on the office carpet", "a clear, vacuumed office floor"),
}
SUB = {"home": "Real photos from real cleanings. No filters, no stock photos, just the mess before and the clean after.",
       "res": "Real photos from real cleanings. The grime that builds up where nobody looks is exactly where our checklist goes.",
       "com": "Real photos from real cleanings. No filters, no stock photos."}
PAGES = {
 "services-residential.html": (["glass", "fridge", "shower", "stove"], "res"),
 "airbnb-cleaning-salt-lake-city.html": (["shower", "fridge"], "res"),
 "services-commercial.html": (["office", "shower"], "com"),
 "office-cleaning-cost-salt-lake-city.html": (["office", "shower"], "com"),
 "house-cleaning-cost-salt-lake-city.html": (["oven", "fridge"], "res"),
 "deep-cleaning-cost-salt-lake-city.html": (["glass", "shower"], "res"),
 "move-out-cleaning-cost-salt-lake-city.html": (["fridge", "oven"], "res"),
 "deep-cleaning-salt-lake-city.html": (["stove", "shower"], "res"),
 "move-out-cleaning-salt-lake-city.html": (["fridge", "glass"], "res"),
}
def shot(f, alt, tag, a=""):
    return (f'<div class="ppba-shot"><span class="ppba-tag{a}">{tag}</span><img src="/images/ba/{f}.webp" '
            f'width="520" height="693" alt="{alt}" loading="lazy" decoding="async"></div>')
def card(keys, sub):
    figs = "".join(
        f'<figure class="ppba-pair"><div class="ppba-ba">{shot(P[k][1]+"-before", "Before a Pro Peach cleaning: "+P[k][2], "Before")}'
        f'{shot(P[k][1]+"-after", "After a Pro Peach cleaning: "+P[k][3], "After", " a")}</div><figcaption><b>{P[k][0]}</b></figcaption></figure>'
        for k in keys)
    return (f'<section class="ppba" aria-label="Before and After"><div class="ppba-card"><p class="ppba-kicker">Real results</p>'
            f'<h2 class="ppba-title">Before and After</h2><p class="ppba-sub">{SUB[sub]}</p><div class="ppba-grid">{figs}</div></div></section><!-- /ppba -->')
def main():
  for name, (keys, sub) in PAGES.items():
      f = ROOT / name; h = f.read_text()
      h = re.sub(r'\n?<section class="ppba".*?<!-- /ppba -->', '', h, flags=re.S)
      block = "\n" + card(keys, sub)
      if "<!-- /ppq -->" in h: h = h.replace("<!-- /ppq -->", "<!-- /ppq -->" + block, 1)
      elif '<section class="pp-footer"' in h:   # above "Our locations", same order as GA
          i = h.find('<section class="pp-footer"'); h = h[:i] + block.lstrip("\n") + "\n    " + h[i:]
      else:
          i = h.rfind("</main>"); h = h[:i] + block + "\n" + h[i:]
      f.write_text(h); print("ok", name)

if __name__ == '__main__':
    # Pages are now generated from GA (tools/build_pages_from_ga.py embeds these sets). Kept as data only.
    print('build_ba.py is data-only now; run tools/build_pages_from_ga.py')
