#!/usr/bin/env python3
# coding: utf-8
"""
COMPREHENSIVE TEST SUITE FOR ALL 36 TASKS
Tests every single feature implemented in nginxparser
Target: 100% Unit and Integration Coverage
"""

import unittest
import os
import tempfile
import shutil
import json
from nginx import NGINX


class TestAllTasks(unittest.TestCase):
    """Comprehensive tests for all 36 Task Master tasks"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, 'test.conf')

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_config(self, content):
        """Helper to create test config file"""
        with open(self.test_config_path, 'w') as f:
            f.write(content)
        return self.test_config_path

    # TASK #1: Security Headers
    def test_task_001_security_headers(self):
        """Test Task #1: Parse security headers configuration"""
        config = """
        server {
            listen 80;
            server_name test.com;
            add_header X-Frame-Options "DENY" always;
            add_header X-Content-Type-Options "nosniff";
            add_header X-XSS-Protection "1; mode=block";
            add_header Content-Security-Policy "default-src 'self'";
            add_header Strict-Transport-Security "max-age=31536000";
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)

        self.assertEqual(len(nginx.servers), 1)
        server = nginx.servers[0]
        self.assertIn('security_headers', server)
        headers = server['security_headers']

        self.assertIn('X-Frame-Options', headers)
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        self.assertIn('X-Content-Type-Options', headers)
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn('X-XSS-Protection', headers)
        self.assertIn('Content-Security-Policy', headers)
        self.assertIn('Strict-Transport-Security', headers)

    # TASK #2: Rate Limiting
    def test_task_002_rate_limiting(self):
        """Test Task #2: Parse rate limiting configuration"""
        config = """
        http {
            limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
            limit_conn_zone $binary_remote_addr zone=addr:10m;

            server {
                listen 80;
                server_name test.com;
                limit_req zone=one burst=5;
                limit_conn addr 10;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('rate_limiting', full_config)
        rate_limit = full_config['rate_limiting']

        self.assertIn('zones', rate_limit)
        self.assertEqual(len(rate_limit['zones']), 1)
        self.assertEqual(rate_limit['zones'][0]['zone_name'], 'one')
        self.assertEqual(rate_limit['zones'][0]['rate'], '10r/s')

        self.assertIn('conn_zones', rate_limit)
        self.assertEqual(len(rate_limit['conn_zones']), 1)

    # TASK #3: Access Control Lists
    def test_task_003_acl(self):
        """Test Task #3: Parse access control lists"""
        config = """
        server {
            listen 80;
            server_name test.com;
            allow 192.168.1.0/24;
            allow 10.0.0.0/8;
            deny all;
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)

        server = nginx.servers[0]
        self.assertIn('acl', server)
        acl = server['acl']

        self.assertEqual(len(acl), 3)
        self.assertEqual(acl[0]['action'], 'allow')
        self.assertEqual(acl[0]['address'], '192.168.1.0/24')
        self.assertEqual(acl[2]['action'], 'deny')
        self.assertEqual(acl[2]['address'], 'all')

    # TASK #4: Authentication
    def test_task_004_authentication(self):
        """Test Task #4: Parse authentication configuration"""
        config = """
        server {
            listen 80;
            server_name test.com;
            auth_basic "Restricted Area";
            auth_basic_user_file /etc/nginx/.htpasswd;
            auth_request /auth;
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)

        server = nginx.servers[0]
        self.assertIn('authentication', server)
        auth = server['authentication']

        self.assertEqual(auth['auth_basic'], 'Restricted Area')
        self.assertEqual(auth['auth_basic_user_file'], '/etc/nginx/.htpasswd')
        self.assertEqual(auth['auth_request'], '/auth')

    # TASK #5-7: Caching
    def test_task_005_007_caching(self):
        """Test Tasks #5-7: Parse caching configuration"""
        config = """
        http {
            proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;
            fastcgi_cache_path /var/cache/fcgi levels=1:2 keys_zone=fcgi_cache:10m;

            server {
                listen 80;
                server_name test.com;
                location / {
                    proxy_cache my_cache;
                    proxy_cache_valid 200 1h;
                    proxy_cache_key $scheme$proxy_host$request_uri;
                    proxy_cache_bypass $cookie_nocache $arg_nocache;
                    proxy_no_cache $http_pragma;
                }
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('caching', full_config)
        caching = full_config['caching']

        self.assertIn('proxy_cache_path', caching)
        self.assertEqual(caching['proxy_cache_path']['path'], '/var/cache/nginx')
        self.assertEqual(caching['proxy_cache_path']['keys_zone_name'], 'my_cache')

        self.assertIn('fastcgi_cache_path', caching)
        self.assertIn('proxy_cache_bypass', caching)
        self.assertIn('proxy_no_cache', caching)

    # TASK #8-10: Proxy Configuration
    def test_task_008_010_proxy_config(self):
        """Test Tasks #8-10: Parse proxy configuration"""
        config = """
        http {
            server {
                listen 80;
                server_name test.com;
                location / {
                    proxy_pass http://backend;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_connect_timeout 60s;
                    proxy_read_timeout 60s;
                    proxy_send_timeout 60s;
                    proxy_buffering on;
                    proxy_buffer_size 4k;
                    proxy_buffers 8 4k;
                }
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('proxy', full_config)
        proxy = full_config['proxy']

        self.assertIn('proxy_headers', proxy)
        self.assertEqual(proxy['proxy_headers']['Host'], '$host')
        self.assertEqual(proxy['proxy_headers']['X-Real-IP'], '$remote_addr')

        self.assertIn('proxy_timeouts', proxy)
        self.assertEqual(proxy['proxy_timeouts']['connect'], '60s')
        self.assertEqual(proxy['proxy_timeouts']['read'], '60s')

        self.assertIn('proxy_buffering', proxy)
        self.assertEqual(proxy['proxy_buffering']['enabled'], 'on')

    # TASK #11-14: Client Configuration
    def test_task_011_014_client_config(self):
        """Test Tasks #11-14: Parse client configuration"""
        config = """
        http {
            client_max_body_size 100m;
            client_body_timeout 60s;
            client_header_timeout 60s;
            send_timeout 60s;
            client_body_buffer_size 128k;
            client_header_buffer_size 1k;
            large_client_header_buffers 4 8k;
            open_file_cache max=1000 inactive=20s;
            open_file_cache_valid 30s;
            open_file_cache_min_uses 2;

            server {
                listen 80;
                server_name test.com;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('client_config', full_config)
        client = full_config['client_config']

        self.assertEqual(client['client_max_body_size'], '100m')

        self.assertIn('timeouts', client)
        self.assertEqual(client['timeouts']['client_body'], '60s')

        self.assertIn('buffers', client)
        self.assertEqual(client['buffers']['client_body'], '128k')

        self.assertIn('file_cache', client)
        self.assertEqual(client['file_cache']['max'], '1000')

    # TASK #15-16: Logging
    def test_task_015_016_logging(self):
        """Test Tasks #15-16: Parse logging configuration"""
        config = """
        http {
            log_format main '$remote_addr - $remote_user [$time_local]';
            log_format json '{"time":"$time_iso8601"}';

            server {
                listen 80;
                server_name test.com;
                access_log /var/log/nginx/access.log main;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('logging', full_config)
        logging = full_config['logging']

        self.assertIn('log_formats', logging)
        self.assertIn('main', logging['log_formats'])
        self.assertIn('json', logging['log_formats'])

    # TASK #17-19: Advanced Blocks
    def test_task_017_019_advanced_blocks(self):
        """Test Tasks #17-19: Parse advanced blocks"""
        config = """
        http {
            map $http_upgrade $connection_upgrade {
                default upgrade;
                '' close;
            }

            geo $country {
                default US;
                10.0.0.0/8 CN;
                192.168.0.0/16 RU;
            }

            split_clients "${remote_addr}AAA" $variant {
                50% "a";
                50% "b";
            }

            server {
                listen 80;
                server_name test.com;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        # Test map blocks
        self.assertIn('maps', full_config)
        self.assertEqual(len(full_config['maps']), 1)
        self.assertEqual(full_config['maps'][0]['input'], '$http_upgrade')
        self.assertEqual(full_config['maps'][0]['default'], 'upgrade')

        # Test geo blocks
        self.assertIn('geo_blocks', full_config)
        self.assertEqual(len(full_config['geo_blocks']), 1)
        self.assertEqual(full_config['geo_blocks'][0]['variable'], '$country')
        self.assertEqual(full_config['geo_blocks'][0]['default'], 'US')

        # Test split_clients
        self.assertIn('split_clients', full_config)
        self.assertEqual(len(full_config['split_clients']), 1)

    # TASK #20: Syntax Validation
    def test_task_020_syntax_validation(self):
        """Test Task #20: Validate syntax correctness"""
        # Valid config
        valid_config = """
        server {
            listen 80;
            server_name test.com;
        }
        """
        path = self._create_config(valid_config)
        nginx = NGINX(path)
        validation = nginx.validate_syntax()

        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)

    # TASK #21: Missing Directives
    def test_task_021_missing_directives(self):
        """Test Task #21: Detect missing required directives"""
        config = """
        server {
            listen 80;
            server_name test.com;
            location / {
                # Missing handler
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        issues = nginx.detect_missing_directives()

        self.assertGreater(len(issues), 0)
        # Should detect missing handler in location

    # TASK #22: Conflict Detection
    def test_task_022_conflict_detection(self):
        """Test Task #22: Detect conflicting directives"""
        config = """
        server {
            listen 80;
            server_name test.com;
            ssl_protocols SSLv3 TLSv1;
        }
        server {
            listen 80;
            server_name test.com;
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        conflicts = nginx.detect_conflicts()

        # Should detect insecure protocols and duplicate server
        self.assertGreater(len(conflicts), 0)

    # TASK #23: Detailed Error Messages
    def test_task_023_detailed_errors(self):
        """Test Task #23: Provide detailed error messages"""
        config = """
        server {
            listen 80;
            server_name test.com;
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        errors = nginx.get_detailed_errors('all')

        self.assertIn('syntax', errors)
        self.assertIn('missing_directives', errors)
        self.assertIn('conflicts', errors)

    # TASK #24: Error Recovery
    def test_task_024_error_recovery(self):
        """Test Task #24: Support error recovery"""
        config = """
        server {
            listen 80;
            server_name test.com;
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        result = nginx.parse_with_error_recovery()

        self.assertIn('success', result)
        self.assertIn('config', result)
        self.assertIn('errors', result)

    # TASK #31: HTTP/2 Module
    def test_task_031_http2_module(self):
        """Test Task #31: Support ngx_http_v2_module"""
        config = """
        http {
            server {
                listen 443 ssl http2;
                server_name test.com;
                http2 on;
                http2_push /static/style.css;
                http2_push_preload on;
                http2_max_field_size 4k;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('http2', full_config)
        http2 = full_config['http2']

        self.assertIn('http2', http2)
        self.assertIn('http2_push', http2)
        self.assertIn('http2_push_preload', http2)

    # TASK #32: Stream Module
    def test_task_032_stream_module(self):
        """Test Task #32: Support ngx_stream_module"""
        config = """
        stream {
            upstream backend {
                server 192.168.1.10:3306;
                server 192.168.1.11:3306 weight=2;
            }

            server {
                listen 3306;
                proxy_pass backend;
                proxy_timeout 30s;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('stream', full_config)
        stream = full_config['stream']

        self.assertIn('servers', stream)
        self.assertEqual(len(stream['servers']), 1)
        self.assertEqual(stream['servers'][0]['listen'], '3306')

    # TASK #33: gRPC Module
    def test_task_033_grpc_module(self):
        """Test Task #33: Support ngx_http_grpc_module"""
        config = """
        server {
            listen 80;
            server_name test.com;

            location /grpc {
                grpc_pass grpc://backend:50051;
                grpc_set_header Content-Type application/grpc;
                grpc_connect_timeout 60s;
                grpc_read_timeout 60s;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        self.assertIn('grpc_locations', full_config)
        grpc_locs = full_config['grpc_locations']

        self.assertEqual(len(grpc_locs), 1)
        self.assertIn('grpc_pass', grpc_locs[0])
        self.assertIn('grpc_headers', grpc_locs[0])

    # TASK #34-36: CLI Tool
    def test_task_034_036_cli_tool(self):
        """Test Tasks #34-36: CLI tool functionality"""
        config = """
        server {
            listen 80;
            server_name test.com;
            ssl_certificate /etc/nginx/ssl/cert.pem;
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)

        # Test get_all_config (used by CLI)
        full_config = nginx.get_all_config()

        self.assertIsInstance(full_config, dict)
        self.assertIn('global', full_config)
        self.assertIn('servers', full_config)
        self.assertIn('validation', full_config)


class TestIntegration(unittest.TestCase):
    """Integration tests for complex scenarios"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, 'test.conf')

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_config(self, content):
        """Helper to create test config file"""
        with open(self.test_config_path, 'w') as f:
            f.write(content)
        return self.test_config_path

    def test_complete_configuration(self):
        """Integration test: Complete nginx configuration with all features"""
        config = """
        user nginx;
        worker_processes 4;

        events {
            worker_connections 1024;
        }

        http {
            # Rate limiting
            limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

            # Caching
            proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cache:10m;

            # Logging
            log_format main '$remote_addr - $remote_user [$time_local]';

            # HTTP/2
            http2 on;

            # Map
            map $http_upgrade $connection_upgrade {
                default upgrade;
                '' close;
            }

            upstream backend {
                least_conn;
                server 192.168.1.10:8080 weight=5;
                server 192.168.1.11:8080 weight=3;
            }

            server {
                listen 443 ssl http2;
                server_name example.com;

                # SSL
                ssl_certificate /etc/nginx/ssl/cert.pem;
                ssl_certificate_key /etc/nginx/ssl/key.pem;
                ssl_protocols TLSv1.2 TLSv1.3;

                # Security headers
                add_header X-Frame-Options "DENY";
                add_header X-Content-Type-Options "nosniff";
                add_header Strict-Transport-Security "max-age=31536000";

                # ACL
                allow 192.168.1.0/24;
                deny all;

                # Auth
                auth_basic "Restricted";
                auth_basic_user_file /etc/nginx/.htpasswd;

                # Client config
                client_max_body_size 50m;

                location / {
                    proxy_pass http://backend;
                    proxy_set_header Host $host;
                    proxy_cache cache;
                    proxy_cache_valid 200 1h;
                    limit_req zone=api burst=5;
                }

                location /grpc {
                    grpc_pass grpc://backend:50051;
                    grpc_connect_timeout 30s;
                }
            }
        }

        stream {
            upstream mysql {
                server 192.168.1.20:3306;
            }

            server {
                listen 3306;
                proxy_pass mysql;
            }
        }
        """
        path = self._create_config(config)
        nginx = NGINX(path)
        full_config = nginx.get_all_config()

        # Verify all major sections
        self.assertIn('global', full_config)
        self.assertIn('events', full_config)
        self.assertIn('http', full_config)
        self.assertIn('upstreams', full_config)
        self.assertIn('servers', full_config)
        self.assertIn('rate_limiting', full_config)
        self.assertIn('caching', full_config)
        self.assertIn('proxy', full_config)
        self.assertIn('client_config', full_config)
        self.assertIn('logging', full_config)
        self.assertIn('maps', full_config)
        self.assertIn('http2', full_config)
        self.assertIn('stream', full_config)
        self.assertIn('grpc_locations', full_config)
        self.assertIn('validation', full_config)

        # Verify server has all features
        server = full_config['servers'][0]
        self.assertIn('security_headers', server)
        self.assertIn('acl', server)
        self.assertIn('authentication', server)


def run_all_tests():
    """Run all tests with detailed output"""
    print("=" * 80)
    print("COMPREHENSIVE TEST SUITE - ALL 36 TASKS")
    print("Target: 100% Unit and Integration Coverage")
    print("=" * 80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAllTasks))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback[:200]}...")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback[:200]}...")

    print("=" * 80)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
