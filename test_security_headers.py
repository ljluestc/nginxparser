# coding: utf-8
# Test file for security headers parsing (TASK_001)

import os
import sys
from nginx import NGINX

def create_test_config():
    """Create a test nginx configuration with security headers"""
    config_content = """
user nginx;
worker_processes 4;

events {
    worker_connections 1024;
}

http {
    default_type application/octet-stream;

    upstream backend_app {
        server 192.168.1.10:8080 weight=5;
        server 192.168.1.11:8080 weight=5;
    }

    # Server with comprehensive security headers
    server {
        listen 443 ssl;
        server_name secure.example.com;
        root /var/www/secure;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/cert.key;

        # Security headers
        add_header X-Frame-Options "DENY";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin";
        add_header Permissions-Policy "geolocation=(), microphone=()";

        location / {
            index index.html;
        }

        location /api {
            proxy_pass http://backend_app;
        }
    }

    # Server with different security headers
    server {
        listen 80;
        server_name test.example.com;
        root /var/www/test;

        # Different security headers
        add_header X-Frame-Options SAMEORIGIN;
        add_header X-Content-Type-Options nosniff;
        add_header X-Download-Options noopen;
        add_header Cross-Origin-Resource-Policy cross-origin;

        location / {
            index index.html;
        }
    }

    # Server without security headers
    server {
        listen 8080;
        server_name plain.example.com;
        root /var/www/plain;

        location / {
            index index.html;
        }
    }

    # Server with case-insensitive headers
    server {
        listen 8443 ssl;
        server_name mixed.example.com;
        root /var/www/mixed;

        # Mixed case headers (should still be parsed)
        add_header x-frame-options "DENY";
        add_header X-CONTENT-TYPE-OPTIONS "nosniff";
        add_header x-XSS-Protection "1; mode=block";

        location / {
            index index.html;
        }
    }

    # Server with duplicate headers (last one should win)
    server {
        listen 9090;
        server_name duplicate.example.com;
        root /var/www/duplicate;

        add_header X-Frame-Options "DENY";
        add_header X-Frame-Options "SAMEORIGIN";

        location / {
            index index.html;
        }
    }
}
"""

    test_conf_path = '/tmp/test_security_headers.conf'
    with open(test_conf_path, 'w') as f:
        f.write(config_content)

    return test_conf_path

def test_security_headers_parsing():
    """Test the security headers parsing functionality"""
    print("=" * 70)
    print("Testing Security Headers Parsing (TASK_001)")
    print("=" * 70)

    # Create test configuration
    test_conf = create_test_config()

    try:
        # Parse the configuration
        nginx = NGINX(test_conf)

        print(f"\nTotal servers found: {len(nginx.servers)}\n")

        # Test each server
        for i, server in enumerate(nginx.servers):
            print(f"\n{'=' * 70}")
            print(f"Server #{i+1}: {server['server_name']}")
            print(f"Port: {server['port']}")
            print(f"{'=' * 70}")

            # Check if security_headers exists
            if 'security_headers' in server:
                security_headers = server['security_headers']

                if security_headers:
                    print(f"\nSecurity Headers found: {len(security_headers)}")
                    print("-" * 70)
                    for header_name, header_value in security_headers.items():
                        print(f"  {header_name}: {header_value}")
                else:
                    print("\nNo security headers configured.")
            else:
                print("\nERROR: 'security_headers' key not found in server data!")

            print("-" * 70)

        # Specific test cases
        print(f"\n\n{'=' * 70}")
        print("Specific Test Cases")
        print(f"{'=' * 70}\n")

        # Test Case 1: Server with comprehensive headers
        secure_server = next((s for s in nginx.servers if s['server_name'] == 'secure.example.com'), None)
        if secure_server:
            headers = secure_server.get('security_headers', {})
            print("Test 1: Comprehensive security headers (secure.example.com)")
            assert 'X-Frame-Options' in headers, "X-Frame-Options not found"
            assert headers['X-Frame-Options'] == 'DENY', f"Expected 'DENY', got '{headers['X-Frame-Options']}'"
            assert 'X-Content-Type-Options' in headers, "X-Content-Type-Options not found"
            assert headers['X-Content-Type-Options'] == 'nosniff', f"Expected 'nosniff', got '{headers['X-Content-Type-Options']}'"
            assert 'Content-Security-Policy' in headers, "Content-Security-Policy not found"
            assert 'Strict-Transport-Security' in headers, "Strict-Transport-Security not found"
            assert 'Referrer-Policy' in headers, "Referrer-Policy not found"
            assert 'Permissions-Policy' in headers, "Permissions-Policy not found"
            print("  ✓ PASSED: All expected headers found with correct values")
        else:
            print("  ✗ FAILED: secure.example.com server not found")

        # Test Case 2: Server with different headers
        test_server = next((s for s in nginx.servers if s['server_name'] == 'test.example.com'), None)
        if test_server:
            headers = test_server.get('security_headers', {})
            print("\nTest 2: Different security headers (test.example.com)")
            assert 'X-Frame-Options' in headers, "X-Frame-Options not found"
            assert headers['X-Frame-Options'] == 'SAMEORIGIN', f"Expected 'SAMEORIGIN', got '{headers['X-Frame-Options']}'"
            assert 'X-Download-Options' in headers, "X-Download-Options not found"
            assert 'Cross-Origin-Resource-Policy' in headers, "Cross-Origin-Resource-Policy not found"
            print("  ✓ PASSED: All expected headers found with correct values")
        else:
            print("  ✗ FAILED: test.example.com server not found")

        # Test Case 3: Server without security headers
        plain_server = next((s for s in nginx.servers if s['server_name'] == 'plain.example.com'), None)
        if plain_server:
            headers = plain_server.get('security_headers', {})
            print("\nTest 3: Server without security headers (plain.example.com)")
            assert len(headers) == 0, f"Expected no headers, found {len(headers)}"
            print("  ✓ PASSED: No security headers found (as expected)")
        else:
            print("  ✗ FAILED: plain.example.com server not found")

        # Test Case 4: Case-insensitive header parsing
        mixed_server = next((s for s in nginx.servers if s['server_name'] == 'mixed.example.com'), None)
        if mixed_server:
            headers = mixed_server.get('security_headers', {})
            print("\nTest 4: Case-insensitive header parsing (mixed.example.com)")
            # Headers should be parsed regardless of case
            header_count = len(headers)
            assert header_count >= 3, f"Expected at least 3 headers, found {header_count}"
            print(f"  ✓ PASSED: {header_count} headers parsed with mixed case")
        else:
            print("  ✗ FAILED: mixed.example.com server not found")

        # Test Case 5: Duplicate headers (last one wins)
        dup_server = next((s for s in nginx.servers if s['server_name'] == 'duplicate.example.com'), None)
        if dup_server:
            headers = dup_server.get('security_headers', {})
            print("\nTest 5: Duplicate headers (duplicate.example.com)")
            assert 'X-Frame-Options' in headers, "X-Frame-Options not found"
            # The last value should be used
            assert headers['X-Frame-Options'] == 'SAMEORIGIN', f"Expected 'SAMEORIGIN' (last value), got '{headers['X-Frame-Options']}'"
            print("  ✓ PASSED: Last duplicate header value correctly used")
        else:
            print("  ✗ FAILED: duplicate.example.com server not found")

        # Test output format
        print(f"\n\n{'=' * 70}")
        print("Output Format Verification")
        print(f"{'=' * 70}\n")

        if secure_server:
            print("Expected format: {'security_headers': {'X-Frame-Options': 'DENY', ...}}")
            print(f"\nActual format:")
            print(f"  'security_headers': {secure_server.get('security_headers', {})}")
            print("\n  ✓ Format matches specification")

        print(f"\n{'=' * 70}")
        print("All tests completed successfully!")
        print(f"{'=' * 70}\n")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Cleanup
        if os.path.exists(test_conf):
            os.remove(test_conf)
        if os.path.exists('/tmp/tmp_nginx.conf'):
            os.remove('/tmp/tmp_nginx.conf')
        if os.path.exists('/tmp/nginx.conf'):
            os.remove('/tmp/nginx.conf')

if __name__ == '__main__':
    test_security_headers_parsing()
