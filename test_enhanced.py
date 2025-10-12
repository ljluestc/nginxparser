# coding: utf-8
# Enhanced test for nginx parser with global, events, and http block parsing

from nginx import NGINX
import json

# Parse nginx configuration
print("="*70)
print("Testing Enhanced NGINX Parser")
print("="*70)

nginx = NGINX('nginx.conf')

print("\n[1] Global Configuration:")
print(json.dumps(nginx.global_config, indent=2))

print("\n[2] Events Configuration:")
print(json.dumps(nginx.events_config, indent=2))

print("\n[3] HTTP Configuration:")
print(json.dumps(nginx.http_config, indent=2))

print("\n[4] Backend/Upstream Pools:")
print(json.dumps(nginx.backend, indent=2))

print("\n[5] Server Blocks:")
print(json.dumps(nginx.servers, indent=2))

print("\n" + "="*70)
print("Full Configuration Summary:")
print("="*70)

full_config = {
    'global': nginx.global_config,
    'events': nginx.events_config,
    'http': nginx.http_config,
    'upstreams': nginx.backend,
    'servers': nginx.servers
}

print(json.dumps(full_config, indent=2))
