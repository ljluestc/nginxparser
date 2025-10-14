# coding: utf-8
# Demo script for TASK_001: Parse security headers configuration
# This demonstrates how to extract security-related headers from nginx configuration

import json
from nginx import NGINX

def demo_security_headers_parsing():
    """
    Demonstrates security headers parsing functionality (TASK_001)

    The parser extracts security-related HTTP headers from nginx configuration:
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Content-Security-Policy
    - Strict-Transport-Security
    - Referrer-Policy
    - Permissions-Policy
    - And other security headers

    Output format: {'security_headers': {'X-Frame-Options': 'DENY', ...}}
    """

    print("=" * 80)
    print("TASK_001 Demo: Parse Security Headers Configuration")
    print("=" * 80)

    # Parse the sample configuration with security headers
    config_file = 'nginx_with_security_headers.conf'

    print(f"\nParsing nginx configuration: {config_file}")
    print("-" * 80)

    # Create NGINX parser instance
    nginx = NGINX(config_file)

    print(f"\nFound {len(nginx.servers)} server blocks\n")

    # Iterate through each server and display security headers
    for i, server in enumerate(nginx.servers, 1):
        print(f"\n{'=' * 80}")
        print(f"Server #{i}")
        print(f"{'=' * 80}")
        print(f"Server Name: {server['server_name']}")
        print(f"Listen:      {server['port']}")

        # Access security headers
        security_headers = server.get('security_headers', {})

        if security_headers:
            print(f"\nSecurity Headers ({len(security_headers)} found):")
            print("-" * 80)
            for header_name, header_value in security_headers.items():
                print(f"  {header_name:40s} : {header_value}")
        else:
            print("\n  (No security headers configured)")

        # Show other relevant server info
        if server.get('ssl_certificate'):
            print(f"\nSSL Configuration:")
            print(f"  Certificate: {server['ssl_certificate']}")
            if server.get('ssl_protocols'):
                print(f"  Protocols:   {server['ssl_protocols']}")

    # Example: Accessing security headers programmatically
    print(f"\n\n{'=' * 80}")
    print("Programmatic Access Example")
    print(f"{'=' * 80}\n")

    # Find a specific server
    secure_server = next((s for s in nginx.servers if 'secure.example.com' in s['server_name']), None)

    if secure_server:
        print("Accessing security headers for 'secure.example.com':\n")
        print("Python code:")
        print("  nginx = NGINX('nginx_with_security_headers.conf')")
        print("  server = nginx.servers[0]")
        print("  headers = server['security_headers']")
        print()

        # Show the actual dictionary structure
        headers = secure_server['security_headers']
        print("Output (JSON format):")
        print(json.dumps({'security_headers': headers}, indent=2))

        # Show how to check for specific headers
        print("\n\nChecking for specific security headers:")
        print("-" * 80)

        critical_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Content-Security-Policy',
            'Strict-Transport-Security'
        ]

        for header in critical_headers:
            if header in headers:
                print(f"  ✓ {header:40s} : {headers[header]}")
            else:
                print(f"  ✗ {header:40s} : NOT CONFIGURED")

    # Summary of implementation
    print(f"\n\n{'=' * 80}")
    print("Implementation Details")
    print(f"{'=' * 80}\n")

    print("Location: nginx.py:341-396")
    print("Method:   parse_security_headers()")
    print()
    print("Supported Security Headers:")
    supported_headers = [
        'X-Frame-Options',
        'X-Content-Type-Options',
        'X-XSS-Protection',
        'Content-Security-Policy',
        'Strict-Transport-Security',
        'Referrer-Policy',
        'Permissions-Policy',
        'X-Download-Options',
        'X-Permitted-Cross-Domain-Policies',
        'Feature-Policy',
        'Expect-CT',
        'Cross-Origin-Embedder-Policy',
        'Cross-Origin-Opener-Policy',
        'Cross-Origin-Resource-Policy'
    ]

    for header in supported_headers:
        print(f"  - {header}")

    print("\n\nFeatures:")
    print("  - Parses add_header directives for security-related headers")
    print("  - Case-insensitive header name matching")
    print("  - Handles quoted and unquoted values")
    print("  - Supports 'always' parameter")
    print("  - Handles duplicate headers (last value wins)")
    print("  - Returns empty dict if no security headers found")

    print(f"\n{'=' * 80}")
    print("Demo completed successfully!")
    print(f"{'=' * 80}\n")

if __name__ == '__main__':
    demo_security_headers_parsing()
