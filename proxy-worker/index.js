export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // Only intercept paths starting with /planes
    if (url.pathname.startsWith('/planes')) {
      const targetUrl = new URL(request.url);
      
      // Point it to the Cloudflare Pages project domain
      targetUrl.hostname = 'mavgo-planes.pages.dev';
      
      // If it's precisely /planes or /planes/, map to root of Pages
      if (url.pathname === '/planes' || url.pathname === '/planes/') {
        targetUrl.pathname = '/';
      } else {
        // e.g. /planes/style.css -> /style.css
        targetUrl.pathname = url.pathname.replace(/^\/planes/, '');
      }
      
      return fetch(targetUrl, request);
    }
    
    // Fallback: pass-through to original Google Sites mapping
    return fetch(request);
  }
};
