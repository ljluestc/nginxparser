# TASK_001: Parse Security Headers Configuration

## Status: ✅ COMPLETED

## Description
Extract security-related headers from nginx configuration files.

## Implementation Location
- **File**: `nginx.py`
- **Method**: `parse_security_headers()` (lines 341-396)
- **Called from**: `parse_server_block()` (line 318)

## Output Format
```python
{
    'security_headers': {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': 'default-src \'self\'; script-src \'self\' \'unsafe-inline\'',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'X-Download-Options': 'noopen'
    }
}
```

## Supported Security Headers

The parser recognizes and extracts the following security headers:

### Primary Security Headers
1. **X-Frame-Options** - Prevents clickjacking attacks
2. **X-Content-Type-Options** - Prevents MIME type sniffing
3. **X-XSS-Protection** - XSS filter protection
4. **Content-Security-Policy** - Controls resource loading
5. **Strict-Transport-Security** - Forces HTTPS connections

### Additional Security Headers
6. **Referrer-Policy** - Controls referrer information
7. **Permissions-Policy** - Controls browser features
8. **X-Download-Options** - Prevents downloads from opening
9. **X-Permitted-Cross-Domain-Policies** - Cross-domain policy
10. **Feature-Policy** - Feature access control
11. **Expect-CT** - Certificate Transparency
12. **Cross-Origin-Embedder-Policy** - Cross-origin isolation
13. **Cross-Origin-Opener-Policy** - Window access control
14. **Cross-Origin-Resource-Policy** - Resource loading policy

## Usage Example

```python
from nginx import NGINX

# Parse nginx configuration
nginx = NGINX('nginx.conf')

# Access security headers for each server
for server in nginx.servers:
    server_name = server['server_name']
    security_headers = server.get('security_headers', {})

    if security_headers:
        print(f"Server: {server_name}")
        for header, value in security_headers.items():
            print(f"  {header}: {value}")
    else:
        print(f"Server: {server_name} - No security headers")

# Check for specific header
if 'X-Frame-Options' in nginx.servers[0]['security_headers']:
    frame_options = nginx.servers[0]['security_headers']['X-Frame-Options']
    print(f"X-Frame-Options: {frame_options}")
```

## Features

### 1. Case-Insensitive Matching
Recognizes headers regardless of case:
```nginx
add_header X-Frame-Options "DENY";
add_header x-frame-options "DENY";    # Also recognized
add_header X-FRAME-OPTIONS "DENY";    # Also recognized
```

### 2. Quoted and Unquoted Values
Handles both formats:
```nginx
add_header X-Frame-Options DENY;        # Unquoted
add_header X-Frame-Options "DENY";      # Quoted with "
add_header X-Frame-Options 'DENY';      # Quoted with '
```

### 3. Always Parameter Support
Correctly parses the `always` parameter:
```nginx
add_header Strict-Transport-Security "max-age=31536000" always;
```

### 4. Duplicate Header Handling
When multiple headers with the same name exist, the last value is used:
```nginx
add_header X-Frame-Options "DENY";
add_header X-Frame-Options "SAMEORIGIN";  # This value is used
```

### 5. Empty Result Handling
Returns empty dictionary if no security headers are found:
```python
server['security_headers']  # Returns {} if no headers
```

## Regular Expression
```python
add_header_pattern = r'add_header\s+([A-Za-z-]+)\s+(["\']?)(.+?)\2\s*(?:always)?\s*;'
```

This regex captures:
- Header name: `([A-Za-z-]+)`
- Optional quotes: `(["\']?)`
- Header value: `(.+?)`
- Optional `always` parameter: `(?:always)?`

## Testing

### Test File
`test_security_headers.py` - Comprehensive test suite

### Test Cases
1. ✅ Comprehensive security headers parsing
2. ✅ Multiple different security headers
3. ✅ Servers without security headers
4. ✅ Case-insensitive header matching
5. ✅ Duplicate header handling (last value wins)

### Run Tests
```bash
python3 test_security_headers.py
```

## Demo Script
`demo_task_001.py` - Interactive demonstration

Run the demo:
```bash
python3 demo_task_001.py
```

## Example Configuration
See `nginx_with_security_headers.conf` for sample nginx configuration with various security headers.

## Integration
The security headers are automatically included in the server dictionary returned by the NGINX parser:

```python
server = {
    'port': '443 ssl http2',
    'listen': ['443 ssl http2'],
    'server_name': 'secure.example.com',
    'root': '/var/www/secure',
    'index': None,
    'access_log': None,
    'error_log': None,
    'ssl_certificate': '/etc/nginx/ssl/cert.pem',
    'ssl_certificate_key': '/etc/nginx/ssl/cert.key',
    'ssl_protocols': 'TLSv1.2 TLSv1.3',
    'ssl_ciphers': None,
    'include': '',
    'backend': [...],
    'security_headers': {           # ← Security headers added here
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        ...
    }
}
```

## Benefits
1. **Security Auditing** - Quickly identify which servers have security headers configured
2. **Compliance Checking** - Verify security headers meet organizational standards
3. **Migration Planning** - Understand current security posture before changes
4. **Documentation** - Generate reports of security configurations
5. **Automated Testing** - Verify security headers in CI/CD pipelines

## Implementation Notes
- The method is called automatically during `parse_server_block()`
- Headers are extracted at the server block level only
- Location-level headers are not currently parsed (could be future enhancement)
- The parser preserves the original header names as they appear in the config
- All values are stored as strings

## Compatibility
- Python 2.7 / 3.x
- Works with all nginx configuration formats
- No external dependencies beyond standard library

---

**Status**: Fully implemented and tested ✅
**Last Updated**: 2025-10-12
