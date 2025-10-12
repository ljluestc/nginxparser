# coding: utf-8
# Complete feature test for ALL PRD tasks

from nginx import NGINX
import json

print("="*80)
print("COMPLETE NGINX PARSER TEST - ALL PRD FEATURES")
print("="*80)

nginx = NGINX('nginx_full_test.conf')

print("\n" + "="*80)
print("TASK_001-006: GLOBAL CONFIGURATION")
print("="*80)
for key, value in nginx.global_config.items():
    print(f"  {key:30s}: {value}")

print("\n" + "="*80)
print("TASK_007-011: EVENTS CONFIGURATION")
print("="*80)
for key, value in nginx.events_config.items():
    print(f"  {key:30s}: {value}")

print("\n" + "="*80)
print("TASK_012-016: HTTP CONFIGURATION")
print("="*80)
for key, value in nginx.http_config.items():
    print(f"  {key:30s}: {value}")

print("\n" + "="*80)
print("TASK_017-020: UPSTREAM CONFIGURATION (Enhanced)")
print("="*80)
for upstream in nginx.backend:
    print(f"\n  Upstream: {upstream['poolname']}")
    print(f"    Load Balancing: {upstream['load_balancing']}")
    print(f"    Backend IPs: {upstream['ip']}")
    print(f"    Servers:")
    for server in upstream['servers']:
        print(f"      - {server['address']}", end='')
        if 'weight' in server:
            print(f" weight={server['weight']}", end='')
        if 'max_fails' in server:
            print(f" max_fails={server['max_fails']}", end='')
        if 'fail_timeout' in server:
            print(f" fail_timeout={server['fail_timeout']}", end='')
        if server.get('backup'):
            print(f" [BACKUP]", end='')
        if server.get('down'):
            print(f" [DOWN]", end='')
        print()

print("\n" + "="*80)
print("TASK_021-030: SERVER & LOCATION CONFIGURATION")
print("="*80)
for i, server in enumerate(nginx.servers, 1):
    print(f"\n  Server #{i}: {server['server_name']}")
    print(f"    Listen: {', '.join(server['listen'])}")
    if server['root']:
        print(f"    Root: {server['root']}")
    if server['index']:
        print(f"    Index: {server['index']}")
    if server['access_log']:
        print(f"    Access Log: {server['access_log']}")
    if server['error_log']:
        print(f"    Error Log: {server['error_log']}")
    if server['ssl_certificate']:
        print(f"    SSL Certificate: {server['ssl_certificate']}")
        print(f"    SSL Certificate Key: {server['ssl_certificate_key']}")
        print(f"    SSL Protocols: {server['ssl_protocols']}")
        print(f"    SSL Ciphers: {server['ssl_ciphers']}")

    if server['backend']:
        print(f"    Locations ({len(server['backend'])}):")
        for loc in server['backend']:
            modifier_str = f" [{loc['modifier']}]" if loc.get('modifier') else ""
            print(f"      - {loc['path']}{modifier_str}")
            if 'proxy_pass' in loc:
                print(f"        Proxy Pass: {loc['proxy_pass']}")
                if 'backend_ip' in loc:
                    print(f"        Backend IPs: {loc['backend_ip']}")
            if 'fastcgi_pass' in loc:
                print(f"        FastCGI Pass: {loc['fastcgi_pass']}")
            if 'rewrites' in loc:
                print(f"        Rewrites:")
                for rewrite in loc['rewrites']:
                    print(f"          - {rewrite}")
            if 'try_files' in loc:
                print(f"        Try Files: {loc['try_files']}")
            if 'root' in loc:
                print(f"        Root: {loc['root']}")
            if 'index' in loc:
                print(f"        Index: {loc['index']}")

print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

# Validate all PRD tasks
validations = {
    'TASK_001-006 (Global)': len(nginx.global_config) >= 4,
    'TASK_007-011 (Events)': len(nginx.events_config) >= 2,
    'TASK_012-016 (HTTP)': len(nginx.http_config) >= 3,
    'TASK_017-020 (Upstream)': len(nginx.backend) >= 3 and any('weight' in s for u in nginx.backend for s in u['servers']),
    'TASK_021-025 (Server)': any(s.get('ssl_certificate') for s in nginx.servers),
    'TASK_026 (Proxy Pass)': any(any('proxy_pass' in l for l in s['backend']) for s in nginx.servers if s['backend']),
    'TASK_027 (Modifiers)': any(any(l.get('modifier') for l in s['backend']) for s in nginx.servers if s['backend']),
    'TASK_028 (FastCGI)': any(any('fastcgi_pass' in l for l in s['backend']) for s in nginx.servers if s['backend']),
    'TASK_029 (Rewrite)': any(any('rewrites' in l for l in s['backend']) for s in nginx.servers if s['backend']),
    'TASK_030 (Try Files)': any(any('try_files' in l for l in s['backend']) for s in nginx.servers if s['backend']),
}

all_passed = True
for task, passed in validations.items():
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} {task}")
    if not passed:
        all_passed = False

print("\n" + "="*80)
if all_passed:
    print("SUCCESS! All PRD tasks implemented and validated!")
else:
    print("WARNING: Some tasks may need additional validation")
print("="*80)

# Output full JSON for inspection
print("\n" + "="*80)
print("COMPLETE JSON OUTPUT")
print("="*80)

full_config = {
    'global': nginx.global_config,
    'events': nginx.events_config,
    'http': nginx.http_config,
    'upstreams': nginx.backend,
    'servers': nginx.servers
}

print(json.dumps(full_config, indent=2, default=str))
