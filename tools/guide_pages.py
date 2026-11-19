"""Shared content for Pro Peach guide pages that mirror Sparkle's: recurring cost, tipping, do I need to be home,
Airbnb cleaning fee. Only Pro Peach's published prices/policies are used (from $149 under 1,000 sq ft, ~$30 per
extra 250 sq ft, recurring 10/15/20/25%, 50% off first clean with recurring, $15 per pet).

render(site) returns {slug: (title, meta, h1, lead, blocks, faqs)}; blocks = [(kind, data)] with kind in
h2 / p / ul. Links in text use [text](/path). GA and UT builders turn these into their own markup.
"""

SITES = {
    'GA': dict(area='Atlanta', region='metro Atlanta', phone='(470) 412-9977', book='/booknow',
               cost='/house-cleaning-cost-atlanta', checklist='/checklist', prep='/how-to-prepare-for-house-cleaners',
               wvb='/weekly-vs-biweekly-cleaning', airbnb='/airbnb-cleaning-atlanta', airbnb_check='/airbnb-turnover-cleaning-checklist',
               deep='/deep-cleaning-atlanta', guarantee='/guarantee',
               condo='Midtown, Buckhead and other high-rise buildings', climate='Georgia pollen and red clay',
               cities=[('/house-cleaning-midtown-atlanta', 'Midtown'), ('/house-cleaning-buckhead', 'Buckhead'),
                       ('/house-cleaning-alpharetta', 'Alpharetta'), ('/house-cleaning-marietta', 'Marietta')],
               airbnb_cities=[('/airbnb-cleaning-midtown-atlanta', 'Midtown'), ('/airbnb-cleaning-buckhead', 'Buckhead'),
                              ('/airbnb-cleaning-college-park', 'College Park')]),
    'UT': dict(area='Salt Lake City', region='the Salt Lake Valley', phone='(385) 217-9244',
               book='https://propeachcleaning.bookingkoala.com/booknow', cost='/house-cleaning-cost-salt-lake-city',
               checklist='/services-residential', prep='/faq', wvb='/house-cleaning-cost-salt-lake-city',
               airbnb='/airbnb-cleaning-salt-lake-city', airbnb_check='/airbnb-cleaning-salt-lake-city',
               deep='/deep-cleaning-salt-lake-city', guarantee='/faq',
               condo='downtown Salt Lake City and other condo buildings', climate='Utah snow, salt and hard water',
               cities=[('/house-cleaning-salt-lake-city', 'Salt Lake City'), ('/house-cleaning-sandy-ut', 'Sandy'),
                       ('/house-cleaning-south-jordan-ut', 'South Jordan'), ('/house-cleaning-millcreek-ut', 'Millcreek')],
               airbnb_cities=[('/airbnb-cleaning-sandy-ut', 'Sandy'), ('/house-cleaning-cottonwood-heights-ut', 'Cottonwood Heights'),
                              ('/house-cleaning-sugar-house', 'Sugar House')]),
}

TIERS = [('Under 1,000 sq ft', 149), ('1,000 to 1,249 sq ft', 189), ('1,250 to 1,499 sq ft', 219),
         ('1,500 to 1,749 sq ft', 249), ('1,750 to 1,999 sq ft', 279), ('2,000 to 2,249 sq ft', 309),
         ('2,250 to 2,499 sq ft', 339), ('2,500 to 2,749 sq ft', 369), ('2,750 to 2,999 sq ft', 399)]


def money(x):
    return f'${x:,.2f}'.replace('.00', '')


def render(site):
    s = SITES[site]
    A, R, PH, BK = s['area'], s['region'], s['phone'], s['book']
    citylinks = ', '.join(f'[house cleaning in {n}]({u})' for u, n in s['cities'])
    P = {}

    # 1. Recurring cleaning cost
    b = 249
    plans = [('Monthly', .10, 12), ('Every other week', .15, 26), ('Weekly', .20, 52), ('Twice a week', .25, 104)]
    P['recurring-house-cleaning-cost' + ('' if site == 'GA' else '-salt-lake-city')] = (
        'Recurring House Cleaning Cost | Pro Peach',
        f'How much recurring house cleaning costs in {A}: monthly saves 10%, every other week 15%, weekly 20% and twice a week 25% on every visit.',
        f'How Much Does Recurring House Cleaning Cost in {A}?',
        f'Recurring cleaning costs less per visit than a one-time clean. With Pro Peach Cleaning, a monthly plan saves 10% on every visit, every other week saves 15%, weekly saves 20% and twice a week saves 25%. Here is what that looks like for a real home in {R}.',
        [('h2', 'Recurring Discounts at a Glance'),
         ('ul', ['One-time cleaning: full price', 'Monthly: 10% off every visit', 'Every other week: 15% off every visit',
                 'Weekly: 20% off every visit', 'Twice a week: 25% off every visit']),
         ('h2', 'Worked Example: A 1,600 Sq Ft Home'),
         ('p', f'A 1,600 sq ft home falls in our 1,500 to 1,749 sq ft range, where a standard clean starts at {money(b)}.'),
         ('ul', [f'{n}: {int(d*100)}% off makes each visit {money(round(b*(1-d),2))}' +
                 ('' if n == 'Monthly' else f', about {money(round(b*(1-d)*v/12))} a month') + '.' for n, d, v in plans]),
         ('p', 'Weekly costs more per month than every other week because you get twice the visits, but every single visit costs less.'),
         ('h2', 'New Customers: 50% Off Your First Cleaning'),
         ('p', f'Sign up for recurring service and your first cleaning is 50% off. On a home under 1,000 sq ft, that first clean is {money(74.5)} instead of {money(149)}, then every other week visits are {money(round(149*.85,2))}.'),
         ('h2', 'Standard Prices by Home Size'),
         ('ul', [f'{t}: from {money(p)}' for t, p in TIERS] + ['3,000 sq ft and up: quoted for your home']),
         ('p', f'Deep cleaning adds $50 to these prices. See every detail on our [house cleaning cost guide]({s["cost"]}).'),
         ('h2', 'What Can Change Your Price'),
         ('ul', ['Pets: $15 per pet', 'Condition: a home that has not been cleaned in a while takes longer, so we ask a few quick questions before we quote',
                 'Paid parking at your building may be added to your total']),
         ('h2', 'Which Schedule Is Right for You?'),
         ('p', f'Kids or two or more pets usually call for weekly. Two working adults with maybe one pet do well every other week. Living alone and tidy? Monthly or every other week works. With {s["climate"]}, many {A} clients also add a seasonal [deep clean]({s["deep"]}).'),
         ('h2', 'Recurring Cleaning Near You'),
         ('p', f'We clean homes across {R}, including {citylinks}.')],
        [(f'How much does biweekly house cleaning cost in {A}?', f'Every other week cleaning saves 15% on every visit. For a home under 1,000 sq ft, that is {money(round(149*.85,2))} a visit, or about {money(round(149*.85*26/12))} a month.'),
         ('Is weekly cleaning cheaper than biweekly?', 'Per visit, yes: weekly saves 20% and every other week saves 15%. Per month, weekly costs more because you get twice as many visits.'),
         ('How does the 50% off first cleaning offer work?', 'New customers who sign up for recurring service get 50% off their first cleaning. For a home under 1,000 sq ft, that first clean is $74.50.'),
         ('Can I change my schedule later?', 'Yes. You can move between weekly, every other week and monthly as your needs change. Just let us know before your next cleaning.')])

    # 2. How much to tip
    P['how-much-to-tip-house-cleaners' + ('' if site == 'GA' else '-utah')] = (
        'How Much to Tip House Cleaners | Pro Peach',
        f'How much to tip house cleaners in {A}: common ranges for standard, deep and move-out cleans, and when a bigger tip makes sense. Tips are always optional.',
        'How Much to Tip House Cleaners',
        f'Tipping your cleaning team is never required, but it is a thank-you they always appreciate. Here is what many customers in {R} tip for each type of cleaning.',
        [('h2', 'The Short Answer'),
         ('p', 'There is no rule. Many customers tip 15% to 20% of the cleaning price for a one-time clean, or $10 to $20 per cleaner. Bigger jobs like deep cleans and move-outs often get a little more. Recurring customers usually tip a smaller amount each visit, or give a holiday tip.'),
         ('h2', 'Tipping Guide by Type of Cleaning'),
         ('ul', ['Standard cleaning: 15% to 20%, or $10 to $20 per cleaner', 'Deep cleaning: 15% to 20%, or $20 to $40 per cleaner',
                 'Move-in or move-out cleaning: 15% to 20%, or $20 to $40 per cleaner', 'Recurring cleaning: a smaller tip each visit, or a holiday tip of about one cleaning',
                 'Airbnb turnovers: many hosts skip per-visit tips and tip at the holidays']),
         ('p', 'These are common customer habits, not a Pro Peach requirement. Tips are always optional.'),
         ('h2', 'When a Bigger Tip Makes Sense'),
         ('ul', ['The home needed more work than usual, like after a party, a renovation or a long stretch without a cleaning',
                 'You booked on short notice', 'The team worked through pet hair or a long list of extras',
                 'Your recurring team keeps going above and beyond', 'It is the holidays']),
         ('p', f'Not happy with something? Skip the tip guilt and tell us. Call or text {PH} within 24 hours of your cleaning and we will come back and touch it up for free.'),
         ('h2', 'Do You Have to Tip House Cleaners?'),
         ('p', 'No. Tipping is a personal choice. Every Pro Peach cleaner is interviewed and background-checked and follows the same detailed checklist on every visit, whether or not you tip.'),
         ('p', 'Want to say thanks another way? A Google review that mentions your cleaner by name means a lot to the team.'),
         ('h2', 'Related Guides'),
         ('p', f'See our [house cleaning cost guide]({s["cost"]}) and {citylinks}.')],
        [('How much should I tip a house cleaner?', 'Many customers tip 15% to 20% of the cleaning price, or $10 to $20 per cleaner for a standard clean. It is always optional.'),
         ('Should I tip more for a deep clean or move-out clean?', 'Many customers do, since those cleanings take longer. 15% to 20% of the price, or $20 to $40 per cleaner, is common.'),
         ('Do I need to tip every time for recurring cleaning?', 'No. Many recurring customers tip a smaller amount per visit, or skip it and give a holiday tip of about one cleaning.'),
         ('Is tipping required with Pro Peach Cleaning?', 'No. Your price does not include a tip and a tip is never required.')])

    # 3. Do I need to be home
    P['do-i-need-to-be-home-for-house-cleaners' + ('' if site == 'GA' else '-utah')] = (
        'Do I Need to Be Home for House Cleaners? | Pro Peach',
        f'Do you need to be home for house cleaners in {A}? No. How to give the team access, what to set up before you leave, and what to expect on cleaning day.',
        'Do I Need to Be Home for House Cleaners?',
        f'No. Many of our clients in {R} are at work, out of town or running errands while we clean. Here is how to give the team access and what to set up ahead of time.',
        [('h2', 'Ways to Let the Team In'),
         ('ul', ['A key left in a lockbox or a safe spot', 'A door code or smart lock code', 'A garage code',
                 'Gate or community access codes', 'A key left with the front desk or concierge']),
         ('p', 'Share the details in your booking notes and we will follow them every visit.'),
         ('h2', 'Condo and Apartment Buildings'),
         ('p', f'In {s["condo"]}, the front desk often decides who goes up. Sort it out the day before:'),
         ('ul', ['Tell the front desk or concierge a cleaning team is coming and add them to your guest list',
                 'Leave a key or written authorization if the desk needs one',
                 'Ask whether vendors need to check in or book the service elevator',
                 'If your building needs a certificate of insurance, tell us when you book']),
         ('h2', 'Before You Leave'),
         ('ul', ['Secure your pets in a closed room or crate, and tell us which room to skip',
                 'Put away valuables like jewelry, cash, medications and important documents',
                 'Leave a short note about what matters most this visit and any surfaces that need special care',
                 'Leave fresh sheets out if you would like the beds made with clean linens',
                 'Point out where the team can park']),
         ('p', f'More tips in our guide to [preparing for house cleaners]({s["prep"]}).'),
         ('h2', 'Rather Be Home? That Works Too'),
         ('p', 'It is fine to be home. Staying out of the room being cleaned helps things move faster. Working from home? Tell the team which room to clean first, or which one to leave alone during your calls.'),
         ('h2', 'Cleaning Near You'),
         ('p', f'We clean homes across {R}, including {citylinks}.')],
        [('Do I need to be home during the cleaning?', 'No. Many clients give us a key, lockbox, door code, smart lock or gate access. Just share the instructions when you book.'),
         ('How do I let cleaners into my condo building?', 'Tell your front desk or concierge a cleaning team is coming, leave a key or authorization, and ask about vendor check-in or service elevator rules.'),
         ('What should I do with my pets?', 'Pets are welcome, but please keep them secured in a closed room or crate during the clean and tell us which room to skip.'),
         ('Are your cleaners background-checked?', 'Yes. Every Pro Peach cleaner is interviewed and background-checked, and Pro Peach Cleaning is licensed, bonded and insured.')])

    # 4. Airbnb cleaning fee (Utah only; GA already has /airbnb-cleaning-cost-atlanta)
    if site == 'UT':
        acity = ', '.join(f'[{n}]({u})' for u, n in s['airbnb_cities'])
        P['airbnb-cleaning-fee-salt-lake-city'] = (
            'Airbnb Cleaning Cost in Salt Lake City | Pro Peach',
            'Airbnb cleaning cost in Salt Lake City: turnovers start at $149 for rentals under 1,000 sq ft. Prices by size and how to set your cleaning fee.',
            'Airbnb Cleaning Cost in Salt Lake City: What Hosts Pay Per Turnover',
            'Airbnb and vacation rental turnovers with Pro Peach Cleaning start at $149 for rentals under 1,000 square feet, the same as our standard cleaning price. Here is what a turnover costs by rental size, and how to set a cleaning fee that covers it.',
            [('h2', 'Turnover Prices by Rental Size'),
             ('ul', [f'{t}: from {money(p)}' for t, p in TIERS] + ['3,000 sq ft and up: quoted for your home']),
             ('p', 'Most condos and townhome rentals near downtown and the canyons fall in the first few tiers.'),
             ('h2', 'What Every Turnover Includes'),
             ('ul', ['Kitchen cleaned and counters, sink and appliance fronts wiped', 'Bathrooms sanitized',
                     'Beds made and linens changed', 'Floors vacuumed and mopped', 'Trash removed and surfaces dusted']),
             ('h2', 'Setting Your Cleaning Fee'),
             ('p', 'Your cleaning fee should cover the turnover itself plus anything you restock between guests, like toiletries, paper goods and linens. Guests see the fee before they book, so price it for your real costs and keep your nightly rate competitive.'),
             ('h2', 'Ski Season in Salt Lake'),
             ('p', 'From December through spring, rentals near Little and Big Cottonwood Canyons book back to back. Ski boots, wet gear and road salt mean extra floor and entryway work, so plan a seasonal deep clean between busy stretches.'),
             ('h2', 'What Can Change Your Price'),
             ('ul', ['Condition: a rental left in rough shape takes longer', 'Pets: $15 per pet',
                     'Clutter: more items to move means more time', 'Paid parking at the property may be added']),
             ('h2', 'Airbnb Cleaning Near You'),
             ('p', f'We turn over rentals across the valley, including {acity}. See our [Airbnb cleaning service]({s["airbnb"]}).')],
            [('How much does Airbnb cleaning cost in Salt Lake City?', 'Turnovers start at $149 for rentals under 1,000 square feet and go up about $30 for every additional 250 square feet.'),
             ('Can you clean between same-day check-out and check-in?', 'Yes. Share your check-out and check-in times when you book and we schedule the turnover in between.'),
             ('Do you change the linens?', 'Yes. We make the beds and change linens as part of every turnover.'),
             ('How do I get an exact price?', 'Book online to see your exact price instantly, or call or text (385) 217-9244.')])
    return P
