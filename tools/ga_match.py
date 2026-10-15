"""Make utah.propeachcleaning.com match propeachcleaning.com (GA Webflow): brand fonts (Adobe kit shi6pzx),
GA coral #FF978C / cream #FFF6EF, GA-style nav + outline buttons + footer. Idempotent."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = '<link rel="preconnect" href="https://use.typekit.net" crossorigin /><link rel="stylesheet" href="https://use.typekit.net/shi6pzx.css" />'
H = '"neuzeit-grotesk-extra-conden", Oswald, sans-serif'
B = '"neuzeit-grotesk", "Helvetica Neue", Arial, sans-serif'

def css():
    f = ROOT / 'style.css'; s = f.read_text()
    s = re.sub(r'\n/\* ga-match \*/.*?/\* /ga-match \*/\n', '\n', s, flags=re.S)
    out = []
    for line in s.split('\n'):
        if 'ppq' in line or 'ppba' in line:   # shared ppq/ppba cards already use GA's palette
            out.append(line); continue
        line = re.sub(r'#(F27D72|e8826f|ff9a8d)\b', '#FF978C', line, flags=re.I)
        line = re.sub(r'#fffee2\b', '#FFF6EF', line, flags=re.I)
        line = re.sub(r'#fffee5\b', '#FFF6EF', line, flags=re.I)
        line = re.sub(r'rgba?\(255, ?254, ?226', lambda m: m.group(0)[:m.group(0).index('(')+1]+'255, 246, 239', line)
        line = re.sub(r'#c9c77a\b', '#FF978C', line, flags=re.I)
        line = re.sub(r'#a8a660\b', '#F28A7F', line, flags=re.I)
        line = line.replace('font-family: "Oswald", "Segoe UI", Arial, sans-serif', 'font-family: ' + B)
        line = re.sub(r'font-family: ?"?Oswald"?, ?("Arial Narrow", ?)?sans-serif', 'font-family: ' + H, line)
        line = re.sub(r'font-family: ?(Arial, ?"Helvetica Neue", ?Helvetica, ?sans-serif|"Helvetica Neue", ?Arial, ?sans-serif)', 'font-family: ' + B, line)
        out.append(line)
    s = '\n'.join(out).rstrip('\n') + '\n'
    s += '''
/* ga-match */
body{font-weight:400}
h1,h2,h3,h4{font-family:%(H)s;font-weight:700}
/* top bar = GA navbar: coral, white Oswald 16px, normal case, plain-text Book Now */
header{background:#FF978C}
.site-nav .nav-list>li>a,.site-nav .nav-link{font-family:Oswald,sans-serif!important;font-size:16px!important;font-weight:400!important;text-transform:none!important;letter-spacing:normal!important;color:#fff!important}
.site-nav .nav-book-btn{background:transparent!important;border:0!important;padding:0!important;border-radius:0!important;box-shadow:none!important}
/* buttons = GA primarybutton: outline, Oswald, small radius */
.btn-primary{background:transparent!important;color:#fff!important;border:1.5px solid #fff!important;border-radius:6px!important;font-family:Oswald,sans-serif!important;font-weight:400!important;font-size:15px!important;letter-spacing:normal!important;text-transform:none!important;padding:10px 22px!important}
.btn-primary:hover{background:rgba(255,255,255,.14)!important;transform:none}
.pp-h1wrap .btn-primary,.pp-sec .btn-primary,.pp-light .btn-primary{color:#FF978C!important;border-color:#FF978C!important}
.pp-h1wrap .btn-primary:hover,.pp-sec .btn-primary:hover{background:#FFF2EA!important}
/* footer = GA footer */
footer.pp-main-footer,.pp-footer{background:#FFF6EF}
.pp-main-footer .pp-field-label{font-family:%(H)s;color:#FF978C}
.pp-main-footer .pp-text-field{border-radius:0!important;background:#FFF6EF!important;border:1px solid #FF978C!important;color:#333;font-family:%(B)s}
.pp-main-footer .pp-submit{border-radius:0!important;background:#FF978C!important;color:#fff!important;border:0!important;font-family:%(H)s;letter-spacing:.5px}
.pp-main-footer .pp-signuphelper,.pp-main-footer .pp-footer-links a{font-family:%(H)s;color:#FF978C}
.pp-main-footer .pp-hours>div{font-family:%(H)s;color:#FF978C}
.pp-main-footer .pp-hours p,.pp-main-footer .pp-copy{font-family:%(B)s}
/* before/after band on cream like GA */
section.ppba{max-width:none;margin:0;background:#FFF6EF;padding:48px max(20px,calc((100%% - 1080px)/2)) 8px}
@media (max-width:767px){section.ppba{padding:28px 14px 4px}}
/* phone menu: Georgia link full strength like the other items */
.mobile-menu .mobile-menu-atl{color:#FFF6EF!important;font-size:0.82rem!important;letter-spacing:0.15em!important;font-weight:600!important}
/* phone menu Book Now: GA outline button (was yellow; coral-on-coral after the color swap) */
.mobile-menu .mobile-menu-book{background:transparent!important;border:1.5px solid #FFF6EF!important;color:#FFF6EF!important;border-radius:6px!important;text-align:center;margin-top:10px}
/* /ga-match */
''' % {'H': H, 'B': B}
    f.write_text(s)

def html():
    for f in sorted(ROOT.glob('*.html')):
        h = f.read_text(); o = h
        if 'typekit.net/shi6pzx.css' not in h:
            h = h.replace('</head>', '    ' + KIT + '\n  </head>', 1)
        # GA-style nav: Call -> Contact (anchor to the footer call box)
        h = h.replace('<li><a href="tel:+13852179244">Call</a></li>', '<li><a href="#contact">Contact</a></li>')
        h = h.replace('<div class="pp-hours">', '<div class="pp-hours" id="contact">')
        h = re.sub(r'#fffee2\b', '#FFF6EF', h, flags=re.I)   # inline creams (ppq wrap bands, 404) -> GA cream
        # Prices: GA/SS have no Prices in the top bar or phone menu -> footer link row instead
        h = h.replace("            <li><a href='/house-cleaning-cost-salt-lake-city'>Prices</a></li>\n", '')
        h = h.replace("          <a href='/house-cleaning-cost-salt-lake-city'>Prices</a>\n", '')
        if "'>PRICES</a>" not in h:
            h = h.replace("            <a href='/faq'>FAQ</a>\n", "            <a href='/faq'>FAQ</a>\n            <a href='/house-cleaning-cost-salt-lake-city'>PRICES</a>\n", 1)
        # inline page styles: same coral
        h = re.sub(r'(<style>[^<]*?)</style>', lambda m: re.sub(r'#(F27D72|e8826f)\b', '#FF978C', m.group(0), flags=re.I) if 'ppq' not in m.group(0) and 'ppba' not in m.group(0) else m.group(0), h)
        if h != o: f.write_text(h); print('updated', f.name)

css(); html()
