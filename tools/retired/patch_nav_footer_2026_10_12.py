"""One-off: SS-style top bar, 'Serving you since Oct 2024', Georgia areas wording, rounded reviews photo."""
import glob,re
BK="https://propeachcleaning.bookingkoala.com"
NAV='''<header>
      <nav class="site-nav">
        <div class="nav-left">
          <ul class="nav-list">
            <li class="dropdown">
              <span
                class="nav-link dropdown-toggle"
                id="servicesDropdown"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                >Services</span
              >
              <ul class="dropdown-menu" aria-labelledby="servicesDropdown">
                <li><a class='dropdown-item' href='/services-residential'>Residential</a></li>
                <li><a class='dropdown-item' href='/services-commercial'>Commercial</a></li>
                <li><a class='dropdown-item' href='/services-construction'>Construction</a></li>
                <li><a class='dropdown-item' href='/airbnb-cleaning-salt-lake-city'>Airbnb</a></li>
                <li><a class='dropdown-item' href='/house-cleaning-cost-salt-lake-city'>Prices</a></li>
              </ul>
            </li>
            <li><a href='/faq'>FAQ</a></li>
            <li><a href='/service-areas'>Service Areas</a></li>
          </ul>
        </div>
        <div class="nav-center">
          <a href='/'><img
              src="images/pro-peach-cart-cream.png"
              alt="Pro Peach Cleaning"
              class="logo"
          /></a>
        </div>
        <div class="nav-right">
          <ul class="nav-list">
            <li><a href="'''+BK+'''/login" target="_blank" rel="noopener">Log In</a></li>
            <li><a href="tel:+13852179244">Call</a></li>
            <li>
              <a
                href="'''+BK+'''/booknow"
                target="_blank"
                class="nav-book-btn"
                >Book Now</a
              >
            </li>
          </ul>
        </div>
        <div class="nav-mobile-btns">
          <a href="tel:+13852179244" class="nav-mobile-btn">Call</a>
          <a href="'''+BK+'''/booknow" target="_blank" class="nav-mobile-btn">Book Now</a>
        </div>
        <button
          class="nav-hamburger"
          data-bs-toggle="collapse"
          data-bs-target="#mobileMenu"
          aria-expanded="false"
          aria-controls="mobileMenu"
          aria-label="Toggle navigation"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </nav>
      <div class="collapse" id="mobileMenu">
        <div class="mobile-menu">
          <a href='/services-residential'>Residential</a>
          <a href='/services-commercial'>Commercial</a>
          <a href='/services-construction'>Construction</a>
          <a href='/airbnb-cleaning-salt-lake-city'>Airbnb</a>
          <a href='/house-cleaning-cost-salt-lake-city'>Prices</a>
          <a href='/service-areas'>Service Areas</a>
          <a href='/faq'>FAQ</a>
          <a href="'''+BK+'''/login" target="_blank" rel="noopener">Log In</a>
          <a href="tel:+13852179244" class="mobile-menu-call">Call or Text (385) 217-9244</a>
          <a
            href="'''+BK+'''/booknow"
            target="_blank"
            class="mobile-menu-book"
            >Book Now</a
          >
          <a
            href="https://propeachcleaning.com"
            target="_blank"
            rel="noopener"
            class="mobile-menu-atl"
            >Also in Georgia &rarr;</a
          >
        </div>
      </div>
    </header>'''
GA_OLD='plus metro Atlanta, Georgia.'
GA_NEW='plus metro Atlanta and the Athens (UGA), Savannah and Augusta areas of Georgia.'
SEC_OLD='<h2>Also in Metro Atlanta, Georgia</h2><p>Pro Peach Cleaning also serves metro Atlanta. <a href="https://propeachcleaning.com/">Visit Pro Peach Cleaning Atlanta</a>.</p>'
SEC_NEW='<h2>Also in Georgia</h2><p>Pro Peach Cleaning also serves metro Atlanta and the Athens (UGA), Savannah and Augusta areas of Georgia. <a href="https://propeachcleaning.com/">Visit Pro Peach Cleaning Georgia</a>.</p>'
n=0
for f in sorted(glob.glob('*.html')):
    h=open(f).read(); o=h
    i=h.find('<header'); j=h.find('</header>')+len('</header>')
    if i>=0 and j>i: h=h[:i]+NAV+h[j:]
    h=h.replace('<div><h3>Our locations</h3></div>','<div><h3>Our locations</h3><p class="pp-founded">Serving you since Oct 2024</p></div>')
    h=h.replace('<p>Serving Salt Lake City &amp; Metro Atlanta</p>','<p>Serving Salt Lake City &amp; Georgia</p>')
    h=h.replace(GA_OLD,GA_NEW).replace(SEC_OLD,SEC_NEW)
    h=re.sub(r'("@id": "https://utah\.propeachcleaning\.com/#business", "name": "Pro Peach Cleaning", "legalName": "Pro Peach Cleaning, LLC",)(?! "foundingDate")',r'\1 "foundingDate": "2024-10",',h)
    if h!=o: open(f,'w').write(h); n+=1
b=open('tools/build_areas.py').read()
b2=b.replace(SEC_OLD,SEC_NEW)
if b2!=b: open('tools/build_areas.py','w').write(b2)
css=open('style.css').read()
ADD='''
/* 2026-10-12: SS-style top bar, founded line, rounded reviews photo */
.nav-left .nav-list{gap:2.5rem}
.nav-mobile-btns{display:none}
.nav-mobile-call{display:none!important}
@media (max-width:768px){
  .nav-mobile-btns{display:flex;gap:8px;margin-left:auto;margin-right:10px}
  .nav-mobile-btn{color:#fffee2;font-family:Oswald,"Arial Narrow",sans-serif;font-size:.8rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;border:1.5px solid rgba(255,254,226,.75);border-radius:10px;padding:.4rem .8rem;line-height:1.2;text-decoration:none}
  .nav-mobile-btn:hover{background:rgba(255,254,226,.12);color:#fffee2}
  .nav-center{flex:0 0 auto}
}
.pp-footer .pp-founded{margin:5px 0 0;font-family:Oswald,"Arial Narrow",sans-serif;font-size:20px;font-weight:700;line-height:1.2;color:var(--pp-peach);text-transform:uppercase}
.reviews-right{margin:2.5rem 5vw 2.5rem 0;border-radius:24px;overflow:hidden}
'''
if '2026-10-12: SS-style top bar' not in css: open('style.css','w').write(css+ADD)
print('files changed',n)
