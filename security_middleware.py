"""
Security middleware for Cloudflare integration
"""
import os
from flask import request, abort
from ipaddress import ip_address, ip_network

class CloudflareSecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        # Cloudflare IP ranges (update these periodically)
        self.cloudflare_ips = [
            '173.245.48.0/20',
            '103.21.244.0/22',
            '103.22.200.0/22',
            '103.31.4.0/22',
            '141.101.64.0/18',
            '108.162.192.0/18',
            '190.93.240.0/20',
            '188.114.96.0/20',
            '197.234.240.0/22',
            '198.41.128.0/17',
            '162.158.0.0/15',
            '104.16.0.0/13',
            '104.24.0.0/14',
            '172.64.0.0/13',
            '131.0.72.0/22'
        ]
        
        self.cloudflare_only = os.environ.get('CLOUDFLARE_ONLY', 'false').lower() == 'true'
        
        if self.cloudflare_only:
            app.before_request(self.check_cloudflare_ip)
        
        app.before_request(self.process_cf_headers)
    
    def check_cloudflare_ip(self):
        """Check if request comes from Cloudflare IP range"""
        if not self.cloudflare_only:
            return
            
        client_ip = ip_address(request.remote_addr)
        
        for cf_range in self.cloudflare_ips:
            if client_ip in ip_network(cf_range):
                return  # Valid Cloudflare IP
        
        # Not from Cloudflare, reject
        abort(403, "Access denied: requests must come through Cloudflare")
    
    def process_cf_headers(self):
        """Process Cloudflare headers to get real client IP and other info"""
        # Get real client IP from Cloudflare headers
        cf_connecting_ip = request.headers.get('CF-Connecting-IP')
        if cf_connecting_ip:
            # Store original for logging
            request.environ['ORIGINAL_REMOTE_ADDR'] = request.environ.get('REMOTE_ADDR')
            # Update with real client IP
            request.environ['REMOTE_ADDR'] = cf_connecting_ip
        
        # Store Cloudflare info for potential use
        request.cf_ray = request.headers.get('CF-Ray')
        request.cf_country = request.headers.get('CF-IPCountry')
        request.cf_visitor = request.headers.get('CF-Visitor')
        
        # Log security info (optional)
        if cf_connecting_ip:
            print(f"[CF] Real IP: {cf_connecting_ip}, Country: {request.cf_country}, Ray: {request.cf_ray}")

# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        @app.after_request
        def add_security_headers(response):
            # HTTPS redirect (Cloudflare usually handles this)
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdn.jsdelivr.net https://unpkg.com https://www.googletagmanager.com "
                "https://telegram.org https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' "
                "https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https: wss:; "
                "frame-src 'self' https://telegram.org; "
                "object-src 'none'; "
                "base-uri 'self';"
            )
            
            # Other security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            return response
