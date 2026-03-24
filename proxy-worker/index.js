export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/planes') {
      return Response.redirect(`${url.origin}/planes/`, 301);
    }
    
    if (url.pathname.startsWith('/planes/')) {
      const targetUrl = new URL(request.url);
      targetUrl.hostname = 'mavgo-planes.pages.dev';
      targetUrl.pathname = url.pathname.replace(/^\/planes/, '');
      
      return fetch(targetUrl, request);
    }
    return fetch(request);
  }
};
