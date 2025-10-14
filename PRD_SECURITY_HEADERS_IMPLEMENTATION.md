# Product Requirements Document: NGINXPARSER: Security Headers Implementation

---

## Document Information
**Project:** nginxparser
**Document:** SECURITY_HEADERS_IMPLEMENTATION
**Version:** 1.0.0
**Date:** 2025-10-13
**Status:** READY FOR TASK-MASTER PARSING

---

## 1. EXECUTIVE SUMMARY

### 1.1 Overview
This PRD captures the requirements and implementation details for NGINXPARSER: Security Headers Implementation.

### 1.2 Purpose
This document provides a structured specification that can be parsed by task-master to generate actionable tasks.

### 1.3 Scope
The scope includes all requirements, features, and implementation details from the original documentation.

---

## 2. REQUIREMENTS

### 2.1 Functional Requirements
**Priority:** HIGH

**REQ-001:** extracts headers configured via the `add_header` directive and includes them in the parsed server data structure.

**REQ-002:** permissions (deprecated, use Permissions-Policy)

**REQ-003:** is production-ready and can be used to audit nginx configurations for security header presence and values.


## 3. TASKS

The following tasks have been identified for implementation:

**TASK_001** [MEDIUM]: `X-Frame-Options` - Prevents clickjacking attacks

**TASK_002** [MEDIUM]: `X-Content-Type-Options` - Prevents MIME type sniffing

**TASK_003** [MEDIUM]: `X-XSS-Protection` - Enables XSS filtering

**TASK_004** [MEDIUM]: `Content-Security-Policy` - Controls resource loading

**TASK_005** [MEDIUM]: `Strict-Transport-Security` - Enforces HTTPS

**TASK_006** [MEDIUM]: `Referrer-Policy` - Controls referrer information

**TASK_007** [MEDIUM]: `Permissions-Policy` - Controls browser features

**TASK_008** [MEDIUM]: `X-Download-Options` - Prevents file execution

**TASK_009** [MEDIUM]: `X-Permitted-Cross-Domain-Policies` - Controls cross-domain policies

**TASK_010** [MEDIUM]: `Feature-Policy` - Browser feature permissions (deprecated, use Permissions-Policy)

**TASK_011** [MEDIUM]: `Expect-CT` - Certificate Transparency

**TASK_012** [MEDIUM]: `Cross-Origin-Embedder-Policy` - Controls embedding

**TASK_013** [MEDIUM]: `Cross-Origin-Opener-Policy` - Controls window/tab opening

**TASK_014** [MEDIUM]: `Cross-Origin-Resource-Policy` - Controls resource loading

**TASK_015** [MEDIUM]: Case-insensitive header name matching

**TASK_016** [MEDIUM]: Supports both quoted and unquoted header values

**TASK_017** [MEDIUM]: Handles the `always` flag in `add_header` directives

**TASK_018** [MEDIUM]: When duplicate headers exist, the last one takes precedence (nginx behavior)

**TASK_019** [MEDIUM]: Preserves the original case of header names as they appear in the config

**TASK_020** [MEDIUM]: Called from `parse_server_block()` method (Line 318)

**TASK_021** [MEDIUM]: Results merged into the server dictionary (Line 337)

**TASK_022** [MEDIUM]: Servers with multiple security headers

**TASK_023** [MEDIUM]: Servers with different header combinations

**TASK_024** [MEDIUM]: Servers without security headers

**TASK_025** [MEDIUM]: Case-insensitive header parsing

**TASK_026** [MEDIUM]: Duplicate header handling (last value wins)

**TASK_027** [MEDIUM]: Output format verification

**TASK_028** [MEDIUM]: Production server with comprehensive security headers

**TASK_029** [MEDIUM]: Basic server with minimal security headers

**TASK_030** [MEDIUM]: API server with CORS and security headers

**TASK_031** [HIGH]: **Extract all add_header directives** from the server block using regex

**TASK_032** [HIGH]: **Group headers by name** (case-insensitive) to handle duplicates

**TASK_033** [HIGH]: **Filter for security headers** from the predefined list

**TASK_034** [HIGH]: **Return structured data** in the specified format

**TASK_035** [MEDIUM]: `add_header` directive

**TASK_036** [MEDIUM]: Header name (letters and hyphens)

**TASK_037** [MEDIUM]: Optional quotes (single or double)

**TASK_038** [MEDIUM]: Header value (everything until matching quote or semicolon)

**TASK_039** [MEDIUM]: Optional `always` flag

**TASK_040** [MEDIUM]: Semicolon terminator

**TASK_041** [HIGH]: **Quoted values with special characters**: `"max-age=31536000; includeSubDomains"`

**TASK_042** [HIGH]: **Unquoted simple values**: `nosniff`

**TASK_043** [HIGH]: **Case variations**: `X-Frame-Options`, `x-frame-options`, `X-FRAME-OPTIONS`

**TASK_044** [HIGH]: **Duplicate headers**: Last occurrence takes precedence

**TASK_045** [HIGH]: **Always flag**: Correctly handled and stripped from value

**TASK_046** [HIGH]: **No security headers**: Returns empty dictionary `{}`

**TASK_047** [MEDIUM]: **Python 2.7/3.x**: Compatible with both versions

**TASK_048** [MEDIUM]: **Existing code**: Fully backward compatible

**TASK_049** [MEDIUM]: **Server structure**: Adds `security_headers` key to each server dictionary

**TASK_050** [MEDIUM]: **Implementation**: `nginx.py:341-396`

**TASK_051** [MEDIUM]: **Integration**: `nginx.py:318` (call), `nginx.py:337` (merge)

**TASK_052** [MEDIUM]: **Tests**: `test_security_headers.py`

**TASK_053** [MEDIUM]: **Examples**: `nginx_with_security_headers.conf`, demo scripts

**TASK_054** [MEDIUM]: ✓ Extracts all supported security headers from nginx configurations

**TASK_055** [MEDIUM]: ✓ Handles various header value formats (quoted, unquoted)

**TASK_056** [MEDIUM]: ✓ Supports case-insensitive matching

**TASK_057** [MEDIUM]: ✓ Correctly handles duplicate headers (last wins)

**TASK_058** [MEDIUM]: ✓ Returns data in the specified format: `{'security_headers': {...}}`

**TASK_059** [MEDIUM]: ✓ Maintains backward compatibility

**TASK_060** [MEDIUM]: ✓ Passes all test cases


## 4. DETAILED SPECIFICATIONS

### 4.1 Original Content

The following sections contain the original documentation:


#### Security Headers Parsing Implementation Task 1 

# Security Headers Parsing Implementation (TASK #1)


#### Overview

## Overview
This implementation adds support for parsing security-related HTTP headers from nginx configuration files. The feature extracts headers configured via the `add_header` directive and includes them in the parsed server data structure.


#### Implementation Details

## Implementation Details


#### Modified Files

### Modified Files


#### 1 Nginx Py Line 341 396 

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


#### Output Format

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


#### Test Files

## Test Files


#### 1 Test Security Headers Py 

### 1. `test_security_headers.py`
Comprehensive test suite covering:
- Servers with multiple security headers
- Servers with different header combinations
- Servers without security headers
- Case-insensitive header parsing
- Duplicate header handling (last value wins)
- Output format verification

**Test Results:** ✓ All tests pass


#### 2 Demo Security Headers Py 

### 2. `demo_security_headers.py`
Simple demo script that parses `nginx.conf` and displays security headers.


#### 3 Demo Security Example Py 

### 3. `demo_security_example.py`
Advanced demo that parses `nginx_with_security_headers.conf` showing comprehensive examples.


#### 4 Nginx With Security Headers Conf 

### 4. `nginx_with_security_headers.conf`
Example nginx configuration demonstrating various security header configurations:
- Production server with comprehensive security headers
- Basic server with minimal security headers
- API server with CORS and security headers


#### Usage Examples

## Usage Examples


#### Basic Usage

### Basic Usage

```python
from nginx import NGINX


#### Parse Nginx Configuration

# Parse nginx configuration
nginx = NGINX('nginx.conf')


#### Access Security Headers For Each Server

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


#### Expected Output

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


#### Configuration Examples

## Configuration Examples


#### Example 1 Comprehensive Security Headers

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


#### Example 2 Basic Security Headers

### Example 2: Basic Security Headers
```nginx
server {
    listen 80;
    server_name basic.example.com;

    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
}
```


#### Example 3 Mixed Case Headers Still Parsed Correctly 

### Example 3: Mixed Case Headers (Still Parsed Correctly)
```nginx
server {
    listen 443 ssl;
    server_name mixed.example.com;

    add_header x-frame-options "DENY";
    add_header X-CONTENT-TYPE-OPTIONS "nosniff";
}
```


#### Technical Implementation Notes

## Technical Implementation Notes


#### Parsing Strategy

### Parsing Strategy

1. **Extract all add_header directives** from the server block using regex
2. **Group headers by name** (case-insensitive) to handle duplicates
3. **Filter for security headers** from the predefined list
4. **Return structured data** in the specified format


#### Regex Pattern

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


#### Edge Cases Handled

### Edge Cases Handled

1. **Quoted values with special characters**: `"max-age=31536000; includeSubDomains"`
2. **Unquoted simple values**: `nosniff`
3. **Case variations**: `X-Frame-Options`, `x-frame-options`, `X-FRAME-OPTIONS`
4. **Duplicate headers**: Last occurrence takes precedence
5. **Always flag**: Correctly handled and stripped from value
6. **No security headers**: Returns empty dictionary `{}`


#### Testing

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


#### Compatibility

## Compatibility

- **Python 2.7/3.x**: Compatible with both versions
- **Existing code**: Fully backward compatible
- **Server structure**: Adds `security_headers` key to each server dictionary


#### Location In Code

## Location in Code

- **Implementation**: `nginx.py:341-396`
- **Integration**: `nginx.py:318` (call), `nginx.py:337` (merge)
- **Tests**: `test_security_headers.py`
- **Examples**: `nginx_with_security_headers.conf`, demo scripts


#### Summary

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


---

## 5. TECHNICAL REQUIREMENTS

### 5.1 Dependencies
- All dependencies from original documentation apply
- Standard development environment
- Required tools and libraries as specified

### 5.2 Compatibility
- Compatible with existing infrastructure
- Follows project standards and conventions

---

## 6. SUCCESS CRITERIA

### 6.1 Functional Success Criteria
- All identified tasks completed successfully
- All requirements implemented as specified
- All tests passing

### 6.2 Quality Success Criteria
- Code meets quality standards
- Documentation is complete and accurate
- No critical issues remaining

---

## 7. IMPLEMENTATION PLAN

### Phase 1: Preparation
- Review all requirements and tasks
- Set up development environment
- Gather necessary resources

### Phase 2: Implementation
- Execute tasks in priority order
- Follow best practices
- Test incrementally

### Phase 3: Validation
- Run comprehensive tests
- Validate against requirements
- Document completion

---

## 8. TASK-MASTER INTEGRATION

### How to Parse This PRD

```bash
# Parse this PRD with task-master
task-master parse-prd --input="{doc_name}_PRD.md"

# List generated tasks
task-master list

# Start execution
task-master next
```

### Expected Task Generation
Task-master should generate approximately {len(tasks)} tasks from this PRD.

---

## 9. APPENDIX

### 9.1 References
- Original document: {doc_name}.md
- Project: {project_name}

### 9.2 Change History
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | Initial PRD conversion |

---

*End of PRD*
*Generated by MD-to-PRD Converter*
