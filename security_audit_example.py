# coding: utf-8
# Security Audit Example using TASK_001 implementation
# This script demonstrates how to audit nginx configurations for security headers

from nginx import NGINX
import json

def audit_security_headers(config_file):
    """
    Perform a security audit on nginx configuration

    Checks for critical security headers and provides recommendations
    """

    print("=" * 80)
    print("NGINX Security Headers Audit Report")
    print("=" * 80)
    print(f"\nConfiguration File: {config_file}\n")

    # Parse configuration
    nginx = NGINX(config_file)

    # Define critical security headers that should be present
    critical_headers = {
        'X-Frame-Options': {
            'description': 'Prevents clickjacking attacks',
            'recommended_values': ['DENY', 'SAMEORIGIN'],
            'severity': 'HIGH'
        },
        'X-Content-Type-Options': {
            'description': 'Prevents MIME type sniffing',
            'recommended_values': ['nosniff'],
            'severity': 'HIGH'
        },
        'Content-Security-Policy': {
            'description': 'Controls which resources can be loaded',
            'recommended_values': None,  # Complex policy
            'severity': 'HIGH'
        },
        'Strict-Transport-Security': {
            'description': 'Forces HTTPS connections',
            'recommended_values': None,  # Contains max-age
            'severity': 'HIGH'
        },
        'X-XSS-Protection': {
            'description': 'Enables XSS filter',
            'recommended_values': ['1; mode=block'],
            'severity': 'MEDIUM'
        },
        'Referrer-Policy': {
            'description': 'Controls referrer information',
            'recommended_values': ['no-referrer', 'strict-origin-when-cross-origin'],
            'severity': 'MEDIUM'
        }
    }

    # Audit results
    total_servers = len(nginx.servers)
    servers_with_all_critical = 0
    servers_with_some_critical = 0
    servers_with_no_headers = 0

    print("-" * 80)
    print(f"Total Servers: {total_servers}")
    print("-" * 80)

    detailed_results = []

    for i, server in enumerate(nginx.servers, 1):
        server_name = server['server_name']
        port = server['port']
        security_headers = server.get('security_headers', {})
        is_ssl = 'ssl' in port.lower()

        print(f"\n{'=' * 80}")
        print(f"Server #{i}: {server_name}")
        print(f"{'=' * 80}")
        print(f"Listen:    {port}")
        print(f"SSL:       {'Yes' if is_ssl else 'No'}")

        if security_headers:
            print(f"Headers:   {len(security_headers)} security headers configured")
        else:
            print(f"Headers:   No security headers configured")
            servers_with_no_headers += 1

        # Check for critical headers
        print(f"\nCritical Security Headers Check:")
        print("-" * 80)

        found_count = 0
        missing_headers = []

        for header_name, header_info in critical_headers.items():
            severity = header_info['severity']
            description = header_info['description']

            if header_name in security_headers:
                value = security_headers[header_name]
                status = "✓ PRESENT"
                found_count += 1

                # Check if value matches recommendations
                recommended = header_info['recommended_values']
                if recommended and value not in recommended:
                    status = "⚠ PRESENT (non-standard value)"

                print(f"  [{severity:6}] {status:30} {header_name}")
                print(f"           Value: {value}")
            else:
                status = "✗ MISSING"
                print(f"  [{severity:6}] {status:30} {header_name}")
                print(f"           {description}")
                missing_headers.append(header_name)

        # Additional headers found
        extra_headers = set(security_headers.keys()) - set(critical_headers.keys())
        if extra_headers:
            print(f"\nAdditional Security Headers:")
            print("-" * 80)
            for header in sorted(extra_headers):
                print(f"  ✓ {header}: {security_headers[header]}")

        # SSL-specific recommendations
        if is_ssl and 'Strict-Transport-Security' not in security_headers:
            print(f"\n⚠ WARNING: SSL/TLS enabled but HSTS not configured!")

        # Calculate score
        score = (found_count / len(critical_headers)) * 100

        print(f"\nSecurity Score: {score:.1f}% ({found_count}/{len(critical_headers)} critical headers)")

        if found_count == len(critical_headers):
            print("Status: ✓ EXCELLENT - All critical headers present")
            servers_with_all_critical += 1
        elif found_count >= len(critical_headers) / 2:
            print("Status: ⚠ FAIR - Some critical headers missing")
            servers_with_some_critical += 1
        else:
            print("Status: ✗ POOR - Many critical headers missing")

        # Store results
        detailed_results.append({
            'server_name': server_name,
            'port': port,
            'ssl': is_ssl,
            'score': score,
            'found': found_count,
            'total': len(critical_headers),
            'missing': missing_headers,
            'headers': security_headers
        })

    # Summary
    print(f"\n\n{'=' * 80}")
    print("AUDIT SUMMARY")
    print(f"{'=' * 80}\n")

    print(f"Total Servers Analyzed:              {total_servers}")
    print(f"Servers with all critical headers:   {servers_with_all_critical}")
    print(f"Servers with some critical headers:  {servers_with_some_critical}")
    print(f"Servers with no security headers:    {servers_with_no_headers}")

    # Calculate overall score
    if total_servers > 0:
        overall_score = sum(r['score'] for r in detailed_results) / total_servers
        print(f"\nOverall Security Score:              {overall_score:.1f}%")

        if overall_score >= 80:
            print("Overall Status:                      ✓ GOOD")
        elif overall_score >= 50:
            print("Overall Status:                      ⚠ FAIR")
        else:
            print("Overall Status:                      ✗ NEEDS IMPROVEMENT")

    # Recommendations
    print(f"\n{'=' * 80}")
    print("RECOMMENDATIONS")
    print(f"{'=' * 80}\n")

    all_missing = set()
    for result in detailed_results:
        all_missing.update(result['missing'])

    if all_missing:
        print("The following critical headers are missing from one or more servers:\n")
        for i, header in enumerate(sorted(all_missing), 1):
            info = critical_headers[header]
            print(f"{i}. {header}")
            print(f"   Severity:    {info['severity']}")
            print(f"   Description: {info['description']}")
            if info['recommended_values']:
                print(f"   Recommended: {', '.join(info['recommended_values'])}")
            print()
    else:
        print("✓ All critical security headers are present on all servers!")

    # Export results
    print(f"{'=' * 80}")
    print("Exporting results to JSON...")
    print(f"{'=' * 80}\n")

    output = {
        'audit_date': '2025-10-12',
        'config_file': config_file,
        'summary': {
            'total_servers': total_servers,
            'overall_score': overall_score if total_servers > 0 else 0,
            'servers_with_all_critical': servers_with_all_critical,
            'servers_with_some_critical': servers_with_some_critical,
            'servers_with_no_headers': servers_with_no_headers
        },
        'servers': detailed_results
    }

    output_file = 'security_audit_report.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Report saved to: {output_file}\n")

    return output

if __name__ == '__main__':
    # Run audit on the sample configuration
    audit_security_headers('nginx_with_security_headers.conf')
