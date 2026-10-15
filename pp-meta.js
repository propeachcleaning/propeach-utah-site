/* Pro Peach Meta Pixel (3646053565556649) + bridge: mirrors GA4 lead events to Facebook */
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','3646053565556649');fbq('track','PageView');
(function(){
  var M={phone_call_click:['track','Contact'],text_message_click:['track','Contact'],book_now_click:['track','InitiateCheckout'],generate_lead:['track','Lead'],sign_up:['track','CompleteRegistration'],review_profile_click:['trackCustom','ReviewProfileClick']};
  function wrap(){var g=window.gtag;if(!g||g.__pp)return;var w=function(){var a=arguments;try{if(a[0]==='event'&&M[a[1]])fbq(M[a[1]][0],M[a[1]][1],a[2]||{});}catch(e){}return g.apply(this,a);};w.__pp=1;window.gtag=w;}
  wrap();document.addEventListener('DOMContentLoaded',wrap);
})();
