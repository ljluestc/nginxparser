# coding: utf-8
# Test comprehensive nginx configuration

from nginx import NGINX
import json

print("="*70)
print("Testing Comprehensive NGINX Configuration")
print("="*70)

nginx = NGINX('nginx_comprehensive.conf')

print("\n[Global Configuration]")
print("-" * 70)
for key, value in nginx.global_config.items():
    print(f"  {key:25s}: {value}")

print("\n[Events Configuration]")
print("-" * 70)
for key, value in nginx.events_config.items():
    print(f"  {key:25s}: {value}")

print("\n[HTTP Configuration]")
print("-" * 70)
for key, value in nginx.http_config.items():
    print(f"  {key:25s}: {value}")

print("\n[Upstream Pools]")
print("-" * 70)
for upstream in nginx.backend:
    print(f"  Pool: {upstream['poolname']}")
    print(f"    IPs: {upstream['ip']}")

print("\n[Server Blocks]")
print("-" * 70)
for i, server in enumerate(nginx.servers, 1):
    print(f"  Server #{i}:")
    print(f"    Port:        {server['port']}")
    print(f"    Server Name: {server['server_name']}")
    print(f"    Include:     {server['include']}")
    if server['backend']:
        print(f"    Backends:")
        for backend in server['backend']:
            print(f"      Path: {backend['path']}")
            if 'backend_ip' in backend:
                print(f"      IP:   {backend['backend_ip']}")
            elif 'proxy_pass' in backend:
                print(f"      Proxy: {backend['proxy_pass']}")
            elif 'fastcgi_pass' in backend:
                print(f"      FastCGI: {backend['fastcgi_pass']}")
    print()

print("="*70)
print("JSON Output:")
print("="*70)

full_config = {
    'global': nginx.global_config,
    'events': nginx.events_config,
    'http': nginx.http_config,
    'upstreams': nginx.backend,
    'servers': nginx.servers
}

print(json.dumps(full_config, indent=2))
