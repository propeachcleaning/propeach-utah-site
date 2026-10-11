# PRO PEACH CLEANING – Utah website (utah.propeachcleaning.com)

**Company: Pro Peach Cleaning, LLC. NOT Sparkle Squad.**

Static site (HTML + CSS + images). Hosted on Netlify; the custom domain utah.propeachcleaning.com points to it.
The main Atlanta site (propeachcleaning.com) is WordPress and is not in this repo.

## Change log
- 2026-10-11: Fixed every "Book" button. They pointed to the BookingKoala staff-only admin page (`/admin/booking/add`); they now go to the customer booking form (`/booknow`).
- 2026-10-11: Removed favicon.ico/favicon.png (they were saved 404 pages, not icons).
- 2026-10-11: Phone changed from (786) 600-4088 (Sparkle's Miami number, wrong company) to Pro Peach's (470) 412-9977.
- 2026-10-11: Added canonical tag pointing to https://utah.propeachcleaning.com/ so old copies (e.g. propeach.netlify.app, github.io) never compete in Google.
- 2026-10-11: Removed unprovable claims: 'Utah's #1 Cleaning Service' and 'Utah's Premier Cleaning Service' -> 'Trusted Utah House Cleaning'; title 'Top-Rated...' -> 'House Cleaning Services in Utah'. Reviews section labeled as Atlanta Google reviews (they are real Pro Peach reviews, not Utah).
- 2026-10-11: Restored 5 pages missed in the Netlify move (services-residential, services-commercial, services-construction, faq, privacy-policy) and applied the same fixes (customer booking link, Pro Peach phone, no #1/Premier/Top-Rated claims, Netlify comments removed).
- 2026-10-11: SEO/AEO/GEO pass: unique title + meta description + canonical + Open Graph per page; one keyword H1 per page; LocalBusiness (Utah, parent = Atlanta), Service, BreadcrumbList and FAQPage (25 Q&As) structured data; sitemap.xml, robots.txt, llms.txt.
- 2026-10-11: FAQ policy fixes: "100% satisfaction guarantee / re-clean" -> 24-hour free touch-up; reschedule policy -> 24h notice, 50% late fee (matches Atlanta).
- 2026-10-11: Cross-linking: footer "Also serving metro Atlanta, GA -> propeachcleaning.com" on every page (nav "Also in ATL" already existed). The Atlanta site links back to Utah (header Service Areas + footer + schema).
- 2026-10-11: Curved edges everywhere (pill buttons/tabs, 22px cards, rounded images/video) per owner preference.
