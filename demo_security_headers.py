# coding: utf-8
# Demo script to show security headers parsing on nginx.conf

from nginx import NGINX
import json

print("=" * 70)
print("Security Headers Parsing Demo")
print("=" * 70)

# Parse the nginx.conf file
nginx = NGINX('nginx.conf')

print(f"\nTotal servers found: {len(nginx.servers)}\n")

for i, server in enumerate(nginx.servers):
    print(f"Server #{i+1}: {server['server_name']}")
    print(f"  Port: {server['port']}")

    # Display security headers
    security_headers = server.get('security_headers', {})
    if security_headers:
        print(f"  Security Headers ({len(security_headers)} found):")
        for header_name, header_value in security_headers.items():
            print(f"    - {header_name}: {header_value}")
    else:
        print("  Security Headers: None configured")

    print()

print("=" * 70)
print("Complete server data with security headers:")
print("=" * 70)
print(json.dumps(nginx.servers, indent=2, ensure_ascii=False))
