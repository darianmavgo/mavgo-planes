export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/planes')) {
      const targetUrl = new URL(request.url);
      targetUrl.hostname = 'mavgo-planes.pages.dev';
      
      if (url.pathname === '/planes' || url.pathname === '/planes/') {
        targetUrl.pathname = '/';
      } else {
        targetUrl.pathname = url.pathname.replace(/^\/planes/, '');
      }
      return fetch(targetUrl, request);
    }
    return fetch(request);
  }
};
