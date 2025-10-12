# Product Requirements Document: Comprehensive Nginx Configuration Parser

## 1. Overview

### 1.1 Purpose
Develop a comprehensive Python-based nginx configuration parser that can extract and analyze all major nginx configuration blocks including global settings, events, http, server, upstream, and location blocks.

### 1.2 Scope
The parser will support parsing nginx configuration files with the following capabilities:
- Parse global configuration directives
- Parse events block configuration
- Parse http block configuration
- Parse server blocks with all directives
- Parse upstream blocks and backend servers
- Parse location blocks with proxy_pass configurations
- Handle include directives and merge configurations
- Extract and analyze worker processes, CPU affinity, and resource limits

## 2. Features

### 2.1 Global Block Parsing
**Priority:** HIGH
**Tasks:**
- TASK_001: Parse `user` directive to extract process user
- TASK_002: Parse `worker_processes` to get number of worker processes
- TASK_003: Parse `worker_cpu_affinity` to extract CPU binding configuration
- TASK_004: Parse `error_log` directive with log level
- TASK_005: Parse `pid` directive for PID file location
- TASK_006: Parse `worker_rlimit_nofile` for file descriptor limits

### 2.2 Events Block Parsing
**Priority:** HIGH
**Tasks:**
- TASK_007: Parse `events` block structure
- TASK_008: Parse `use` directive to extract I/O model (epoll, select, etc.)
- TASK_009: Parse `worker_connections` to get max connections per worker
- TASK_010: Parse `multi_accept` directive
- TASK_011: Parse `accept_mutex` directive

### 2.3 HTTP Block Parsing
**Priority:** MEDIUM
**Tasks:**
- TASK_012: Parse http-level `include` directives
- TASK_013: Parse `default_type` directive
- TASK_014: Parse `sendfile` directive
- TASK_015: Parse `keepalive_timeout` directive
- TASK_016: Parse `gzip` directives

### 2.4 Upstream Block Parsing (EXISTING - ENHANCE)
**Priority:** MEDIUM
**Tasks:**
- TASK_017: Enhance upstream parsing to support weight parameter
- TASK_018: Add support for max_fails and fail_timeout parameters
- TASK_019: Add support for backup and down server flags
- TASK_020: Add support for load balancing methods (least_conn, ip_hash, hash)

### 2.5 Server Block Parsing (EXISTING - ENHANCE)
**Priority:** HIGH
**Tasks:**
- TASK_021: Maintain existing server block parsing
- TASK_022: Add support for multiple listen directives
- TASK_023: Parse SSL/TLS configuration (ssl_certificate, ssl_certificate_key)
- TASK_024: Parse access_log and error_log at server level
- TASK_025: Parse root and index directives

### 2.6 Location Block Parsing (EXISTING - ENHANCE)
**Priority:** HIGH
**Tasks:**
- TASK_026: Maintain existing location and proxy_pass parsing
- TASK_027: Add support for location modifiers (=, ~, ~*, ^~)
- TASK_028: Parse fastcgi_pass configurations
- TASK_029: Parse rewrite rules
- TASK_030: Parse try_files directives

### 2.7 Configuration Merging (EXISTING - MAINTAIN)
**Priority:** HIGH
**Tasks:**
- TASK_031: Maintain existing include file merging functionality
- TASK_032: Maintain comment removal functionality

## 3. Technical Requirements

### 3.1 Input
- nginx.conf file path
- Support for relative and absolute include paths

### 3.2 Output Structure
```python
{
    'global': {
        'user': 'nginx',
        'worker_processes': 8,
        'worker_cpu_affinity': 'auto',
        'error_log': '/var/log/nginx/error.log error',
        'pid': '/var/run/nginx.pid',
        'worker_rlimit_nofile': 65535
    },
    'events': {
        'use': 'epoll',
        'worker_connections': 20480
    },
    'http': {
        'default_type': 'application/octet-stream',
        'sendfile': 'on',
        'keepalive_timeout': 65,
        'gzip': 'on'
    },
    'upstreams': [
        {
            'name': 'backend_name',
            'servers': [
                {
                    'address': '10.10.10.10:8080',
                    'weight': 5,
                    'max_fails': 3,
                    'fail_timeout': '30s'
                }
            ],
            'load_balancing': 'round_robin'
        }
    ],
    'servers': [
        {
            'port': '80',
            'server_name': 'example.com',
            'root': '/var/www/html',
            'access_log': '/var/log/nginx/access.log',
            'backend': [
                {
                    'backend_path': '/api',
                    'backend_ip': '10.10.10.10:8080'
                }
            ]
        }
    ]
}
```

### 3.3 Python Compatibility
- Python 2.7
- Python 3.x (3.6+)

### 3.4 Dependencies
- Standard library only (re, os)

## 4. Success Criteria

### 4.1 Functional Requirements
- Successfully parse all global directives
- Successfully parse events block completely
- Successfully parse http, server, upstream, and location blocks
- Handle nested configurations correctly
- Merge include files properly
- Extract all backend IPs from proxy_pass and upstream blocks

### 4.2 Performance Requirements
- Parse typical nginx.conf (< 1000 lines) in under 1 second
- Handle large configurations (> 10000 lines) in under 5 seconds

### 4.3 Reliability Requirements
- Handle malformed configurations gracefully
- Provide meaningful error messages
- Don't crash on missing include files

## 5. Implementation Phases

### Phase 1: Core Enhancement (CURRENT)
- Implement global block parsing
- Implement events block parsing
- Create TaskMaster system for automated task execution

### Phase 2: HTTP Block Enhancement
- Parse http-level directives
- Enhance upstream parsing with all parameters

### Phase 3: Server/Location Enhancement
- Add SSL configuration parsing
- Add advanced location parsing
- Add rewrite and try_files support

### Phase 4: Testing and Validation
- Create comprehensive test suite
- Validate against real-world nginx configurations
- Performance testing and optimization

## 6. Task Execution Order

Tasks should be executed in the following priority order:
1. TASK_001 through TASK_006 (Global Block)
2. TASK_007 through TASK_011 (Events Block)
3. TASK_031, TASK_032 (Maintain existing functionality)
4. TASK_021, TASK_026 (Maintain existing server/location parsing)
5. TASK_012 through TASK_016 (HTTP Block)
6. TASK_017 through TASK_020 (Upstream Enhancement)
7. TASK_022 through TASK_030 (Server/Location Enhancement)
