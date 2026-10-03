from django.conf import settings


class NoBrowserCacheMiddleware:
    """During development the browser has, more than once, kept showing an
    old version of a page after a template edit (the client saw stale text/
    layout and assumed the fix hadn't been applied, when the server was
    already serving the corrected HTML). Django sends no Cache-Control
    header of its own, so some browsers were free to reuse an old response.
    This forces every response to be re-fetched, only while DEBUG is on, so
    it never affects the real deployed site.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
        return response
