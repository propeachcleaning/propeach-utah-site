/* Pro Peach GA4 event tracking: calls, texts, Book Now, review profiles */
document.addEventListener('click',function(e){
  var a=e.target.closest&&e.target.closest('a[href]');if(!a||!window.gtag)return;
  var h=a.getAttribute('href')||'',u=a.href||'',P={page_path:location.pathname};
  if(h.indexOf('tel:')===0){P.link_url=h;gtag('event','phone_call_click',P);}
  else if(h.indexOf('sms:')===0){P.link_url=h;gtag('event','text_message_click',P);}
  else if(/booknow/.test(u)){P.link_text=(a.textContent||'').trim().slice(0,60);gtag('event','book_now_click',P);}
  else{var p=/maps\.google|google\.com\/maps|g\.page/.test(u)?'google':/facebook\.com/.test(u)?'facebook':/thumbtack\.com/.test(u)?'thumbtack':/yelp\.com/.test(u)?'yelp':null;if(p){P.platform=p;gtag('event','review_profile_click',P);}}
},true);
