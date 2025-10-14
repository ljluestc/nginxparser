# Security Headers Parsing Implementation (TASK #1)

## Overview
This implementation adds support for parsing security-related HTTP headers from nginx configuration files. The feature extracts headers configured via the `add_header` directive and includes them in the parsed server data structure.

## Implementation Details

### Modified Files

#### 1. `nginx.py` (Line 341-396)

**Added Method: `parse_security_headers(self, server_block)`**

This method extracts security headers from a server block configuration and returns them in a structured format.

**Supported Security Headers:**
- `X-Frame-Options` - Prevents clickjacking attacks
- `X-Content-Type-Options` - Prevents MIME type sniffing
- `X-XSS-Protection` - Enables XSS filtering
- `Content-Security-Policy` - Controls resource loading
- `Strict-Transport-Security` - Enforces HTTPS
- `Referrer-Policy` - Controls referrer information
- `Permissions-Policy` - Controls browser features
- `X-Download-Options` - Prevents file execution
- `X-Permitted-Cross-Domain-Policies` - Controls cross-domain policies
- `Feature-Policy` - Browser feature permissions (deprecated, use Permissions-Policy)
- `Expect-CT` - Certificate Transparency
- `Cross-Origin-Embedder-Policy` - Controls embedding
- `Cross-Origin-Opener-Policy` - Controls window/tab opening
- `Cross-Origin-Resource-Policy` - Controls resource loading

**Key Features:**
- Case-insensitive header name matching
- Supports both quoted and unquoted header values
- Handles the `always` flag in `add_header` directives
- When duplicate headers exist, the last one takes precedence (nginx behavior)
- Preserves the original case of header names as they appear in the config

**Integration:**
- Called from `parse_server_block()` method (Line 318)
- Results merged into the server dictionary (Line 337)

### Output Format

```json
{
  "security_headers": {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'self'",
    ...
  }
}
```

## Test Files

### 1. `test_security_headers.py`
Comprehensive test suite covering:
- Servers with multiple security headers
- Servers with different header combinations
- Servers without security headers
- Case-insensitive header parsing
- Duplicate header handling (last value wins)
- Output format verification

**Test Results:** ✓ All tests pass

### 2. `demo_security_headers.py`
Simple demo script that parses `nginx.conf` and displays security headers.

### 3. `demo_security_example.py`
Advanced demo that parses `nginx_with_security_headers.conf` showing comprehensive examples.

### 4. `nginx_with_security_headers.conf`
Example nginx configuration demonstrating various security header configurations:
- Production server with comprehensive security headers
- Basic server with minimal security headers
- API server with CORS and security headers

## Usage Examples

### Basic Usage

```python
from nginx import NGINX

# Parse nginx configuration
nginx = NGINX('nginx.conf')

# Access security headers for each server
for server in nginx.servers:
    server_name = server['server_name']
    security_headers = server.get('security_headers', {})

    print(f"Server: {server_name}")
    if security_headers:
        for header, value in security_headers.items():
            print(f"  {header}: {value}")
    else:
        print("  No security headers configured")
```

### Expected Output

```
Server: secure.example.com
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  X-Download-Options: noopen
```

## Configuration Examples

### Example 1: Comprehensive Security Headers
```nginx
server {
    listen 443 ssl;
    server_name secure.example.com;

    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'";
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

### Example 2: Basic Security Headers
```nginx
server {
    listen 80;
    server_name basic.example.com;

    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
}
```

### Example 3: Mixed Case Headers (Still Parsed Correctly)
```nginx
server {
    listen 443 ssl;
    server_name mixed.example.com;

    add_header x-frame-options "DENY";
    add_header X-CONTENT-TYPE-OPTIONS "nosniff";
}
```

## Technical Implementation Notes

### Parsing Strategy

1. **Extract all add_header directives** from the server block using regex
2. **Group headers by name** (case-insensitive) to handle duplicates
3. **Filter for security headers** from the predefined list
4. **Return structured data** in the specified format

### Regex Pattern

```python
add_header_pattern = r'add_header\s+([A-Za-z-]+)\s+(["\']?)(.+?)\2\s*(?:always)?\s*;'
```

This pattern matches:
- `add_header` directive
- Header name (letters and hyphens)
- Optional quotes (single or double)
- Header value (everything until matching quote or semicolon)
- Optional `always` flag
- Semicolon terminator

### Edge Cases Handled

1. **Quoted values with special characters**: `"max-age=31536000; includeSubDomains"`
2. **Unquoted simple values**: `nosniff`
3. **Case variations**: `X-Frame-Options`, `x-frame-options`, `X-FRAME-OPTIONS`
4. **Duplicate headers**: Last occurrence takes precedence
5. **Always flag**: Correctly handled and stripped from value
6. **No security headers**: Returns empty dictionary `{}`

## Testing

Run the comprehensive test suite:
```bash
python3 test_security_headers.py
```

Run demo scripts:
```bash
python3 demo_security_headers.py
python3 demo_security_example.py
```

## Compatibility

- **Python 2.7/3.x**: Compatible with both versions
- **Existing code**: Fully backward compatible
- **Server structure**: Adds `security_headers` key to each server dictionary

## Location in Code

- **Implementation**: `nginx.py:341-396`
- **Integration**: `nginx.py:318` (call), `nginx.py:337` (merge)
- **Tests**: `test_security_headers.py`
- **Examples**: `nginx_with_security_headers.conf`, demo scripts

## Summary

The security headers parsing implementation successfully:
- ✓ Extracts all supported security headers from nginx configurations
- ✓ Handles various header value formats (quoted, unquoted)
- ✓ Supports case-insensitive matching
- ✓ Correctly handles duplicate headers (last wins)
- ✓ Returns data in the specified format: `{'security_headers': {...}}`
- ✓ Maintains backward compatibility
- ✓ Passes all test cases

The feature is production-ready and can be used to audit nginx configurations for security header presence and values.
