#!/usr/bin/env python3
"""
Production readiness test script
"""
import os
import sys
import requests
import time
from urllib.parse import urljoin

def test_app_health(base_url):
    """Test basic app health"""
    print(f"🔍 Testing app health at {base_url}")
    
    tests = [
        ("/", "Landing page"),
        ("/app", "SPA main page"),
        ("/api/publisher/status", "API health"),
        ("/manifest.json", "PWA manifest"),
        ("/assets/css/main.css", "Static assets"),
    ]
    
    results = []
    
    for endpoint, description in tests:
        try:
            url = urljoin(base_url, endpoint)
            response = requests.get(url, timeout=10)
            status = "✅ PASS" if response.status_code < 400 else f"❌ FAIL ({response.status_code})"
            results.append((description, status, response.status_code))
            print(f"  {status} - {description}")
        except Exception as e:
            results.append((description, f"❌ ERROR", str(e)))
            print(f"  ❌ ERROR - {description}: {e}")
    
    return results

def test_security_headers(base_url):
    """Test security headers"""
    print(f"\n🔒 Testing security headers at {base_url}")
    
    try:
        response = requests.get(base_url, timeout=10)
        headers = response.headers
        
        security_checks = [
            ("Content-Security-Policy", "CSP header"),
            ("X-Content-Type-Options", "MIME sniffing protection"),
            ("X-Frame-Options", "Clickjacking protection"),
            ("Strict-Transport-Security", "HTTPS enforcement"),
        ]
        
        for header, description in security_checks:
            if header in headers:
                print(f"  ✅ PASS - {description}")
            else:
                print(f"  ❌ MISSING - {description}")
                
    except Exception as e:
        print(f"  ❌ ERROR testing security headers: {e}")

def test_environment():
    """Test environment configuration"""
    print("\n⚙️ Testing environment configuration")
    
    required_vars = ["SECRET_KEY", "DATABASE_URL"]
    optional_vars = ["FLASK_ENV", "CORS_ORIGINS", "CLOUDFLARE_ONLY"]
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"  ✅ REQUIRED - {var} is set")
        else:
            print(f"  ❌ MISSING - {var} is required for production")
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"  ✅ OPTIONAL - {var} is set: {os.environ.get(var)}")
        else:
            print(f"  ⚠️ OPTIONAL - {var} not set (using default)")

def main():
    """Main test function"""
    print("🚀 CUR8.FUN Production Readiness Test")
    print("=" * 50)
    
    # Test environment
    test_environment()
    
    # Determine base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Test app health
    health_results = test_app_health(base_url)
    
    # Test security headers
    test_security_headers(base_url)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    
    passed = sum(1 for _, status, _ in health_results if "PASS" in status)
    total = len(health_results)
    
    print(f"Health tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! App is production ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Review issues before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
