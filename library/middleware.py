class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        now = time.time()

        if ip in self.requests:
            if len([t for t in self.requests[ip] if now - t < 60]) > 10:
                return HttpResponseTooManyRequests()
            self.requests[ip].append(now)
        else:
            self.requests[ip] = [now]

        return self.get_response(request)