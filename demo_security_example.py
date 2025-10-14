# coding: utf-8
# Demo script to parse the comprehensive security headers example

from nginx import NGINX
import json

print("=" * 80)
print("Security Headers Parsing Demo - Comprehensive Example")
print("=" * 80)

# Parse the configuration file with security headers
nginx = NGINX('nginx_with_security_headers.conf')

print(f"\nTotal servers found: {len(nginx.servers)}\n")

for i, server in enumerate(nginx.servers):
    print("=" * 80)
    print(f"Server #{i+1}: {server['server_name']}")
    print("=" * 80)
    print(f"  Listen: {', '.join(server['listen'])}")
    print(f"  Port: {server['port']}")
    if server['ssl_certificate']:
        print(f"  SSL: Enabled")
        print(f"    Certificate: {server['ssl_certificate']}")
        print(f"    Protocols: {server['ssl_protocols']}")

    # Display security headers
    security_headers = server.get('security_headers', {})
    if security_headers:
        print(f"\n  Security Headers Configuration ({len(security_headers)} headers):")
        print("  " + "-" * 76)
        for header_name, header_value in security_headers.items():
            print(f"    {header_name}:")
            print(f"      {header_value}")
    else:
        print("\n  Security Headers: None configured")

    # Display backend configuration
    if server['backend']:
        print(f"\n  Location Blocks ({len(server['backend'])} locations):")
        for loc in server['backend']:
            path = loc.get('path', '/')
            print(f"    - {path}")
            if 'proxy_pass' in loc:
                print(f"      Proxy: {loc['proxy_pass']}")

    print()

# Show the complete data structure in JSON format
print("\n" + "=" * 80)
print("Complete Output Format (JSON)")
print("=" * 80)
print(json.dumps(nginx.servers, indent=2, ensure_ascii=False))
