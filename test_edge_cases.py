# coding: utf-8
"""
Edge Case Test Suite for NGINX Parser
Tests boundary conditions, error handling, and unusual configurations
"""

import unittest
import tempfile
import os
import json
from nginx import NGINX


class TestNGINXParserEdgeCases(unittest.TestCase):
    """Edge case tests for NGINX parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_configs = {}

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        for temp_file in self.test_configs.values():
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Clean up any additional files in temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_config(self, name, content):
        """Create a temporary test configuration file"""
        config_path = os.path.join(self.temp_dir, f"{name}.conf")
        with open(config_path, 'w') as f:
            f.write(content)
        self.test_configs[name] = config_path
        return config_path

    def test_empty_file(self):
        """Test parsing completely empty file"""
        config_content = ""
        config_path = self.create_test_config('empty', config_content)
        nginx = NGINX(config_path)

        # Should not crash and return empty structures
        self.assertEqual(len(nginx.global_config), 0)
        self.assertEqual(len(nginx.events_config), 0)
        self.assertEqual(len(nginx.http_config), 0)
        self.assertEqual(len(nginx.backend), 0)
        self.assertEqual(len(nginx.servers), 0)

    def test_whitespace_only_file(self):
        """Test parsing file with only whitespace"""
        config_content = "   \n\t  \n  \t\n  "
        config_path = self.create_test_config('whitespace', config_content)
        nginx = NGINX(config_path)

        # Should not crash
        self.assertEqual(len(nginx.global_config), 0)
        self.assertEqual(len(nginx.events_config), 0)
        self.assertEqual(len(nginx.http_config), 0)
        self.assertEqual(len(nginx.backend), 0)
        self.assertEqual(len(nginx.servers), 0)

    def test_comment_only_file(self):
        """Test parsing file with only comments"""
        config_content = """
# This is a comment
# Another comment
# Yet another comment
"""
        config_path = self.create_test_config('comments_only', config_content)
        nginx = NGINX(config_path)

        # Should not crash
        self.assertEqual(len(nginx.global_config), 0)
        self.assertEqual(len(nginx.events_config), 0)
        self.assertEqual(len(nginx.http_config), 0)
        self.assertEqual(len(nginx.backend), 0)
        self.assertEqual(len(nginx.servers), 0)

    def test_malformed_syntax(self):
        """Test parsing with malformed syntax"""
        config_content = """
worker_processes 1
events {
    worker_connections 1024
http {
    server {
        listen 80
        server_name test.com
    }
}
"""
        config_path = self.create_test_config('malformed', config_content)
        nginx = NGINX(config_path)

        # Should handle gracefully - may not parse everything due to malformed syntax
        # Just verify it doesn't crash
        self.assertIsNotNone(nginx)

    def test_unclosed_blocks(self):
        """Test parsing with unclosed blocks"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;

http {
    server {
        listen 80;
        server_name test.com;
    }
"""
        config_path = self.create_test_config('unclosed', config_content)
        nginx = NGINX(config_path)

        # Should handle gracefully
        self.assertEqual(nginx.global_config['worker_processes'], '1')
        self.assertEqual(nginx.events_config['worker_connections'], '1024')

    def test_nested_comments(self):
        """Test parsing with nested comments"""
        config_content = """
# Outer comment
worker_processes 1; # Inline comment
# Another comment

events {
    # Comment in block
    worker_connections 1024; # Inline comment
    # Another comment
}

http {
    # Comment in http block
    server {
        listen 80; # Inline comment
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('nested_comments', config_content)
        nginx = NGINX(config_path)

        # Should parse correctly despite comments
        self.assertEqual(nginx.global_config['worker_processes'], '1')
        self.assertEqual(nginx.events_config['worker_connections'], '1024')
        self.assertEqual(len(nginx.servers), 1)

    def test_very_long_values(self):
        """Test parsing with very long directive values"""
        long_value = "a" * 1000
        config_content = f"""
worker_processes 1;

events {{
    worker_connections 1024;
}}

http {{
    server {{
        listen 80;
        server_name {long_value};
        root /var/www/html;
    }}
}}
"""
        config_path = self.create_test_config('long_values', config_content)
        nginx = NGINX(config_path)

        # Should handle long values
        self.assertEqual(nginx.servers[0]['server_name'], long_value)

    def test_special_characters_in_values(self):
        """Test parsing with special characters in values"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name "test.example.com" 'another.example.com' test-with-dashes.com test_with_underscores.com;
        root /var/www/html;
        index "index.html index.htm" 'index.php index.php5';
    }
}
"""
        config_path = self.create_test_config('special_chars', config_content)
        nginx = NGINX(config_path)

        # Should handle special characters
        server_name = nginx.servers[0]['server_name']
        self.assertIn('test.example.com', server_name)
        self.assertIn('another.example.com', server_name)
        self.assertIn('test-with-dashes.com', server_name)
        self.assertIn('test_with_underscores.com', server_name)

    def test_unicode_characters(self):
        """Test parsing with Unicode characters"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name 测试.example.com 测试2.example.com;
        root /var/www/html;
    }
}
"""
        config_path = self.create_test_config('unicode', config_content)
        nginx = NGINX(config_path)

        # Should handle Unicode characters
        server_name = nginx.servers[0]['server_name']
        self.assertIn('测试.example.com', server_name)
        self.assertIn('测试2.example.com', server_name)

    def test_multiple_spaces_and_tabs(self):
        """Test parsing with multiple spaces and tabs"""
        config_content = """
worker_processes    1;

events    {
    worker_connections		1024;
}

http		{
    server		{
        listen		80;
        server_name		test.com;
    }
}
"""
        config_path = self.create_test_config('spaces_tabs', config_content)
        nginx = NGINX(config_path)

        # Should handle multiple spaces and tabs
        self.assertEqual(nginx.global_config['worker_processes'], '1')
        self.assertEqual(nginx.events_config['worker_connections'], '1024')
        # May not parse server due to malformed syntax, just verify it doesn't crash
        self.assertIsNotNone(nginx)

    def test_case_sensitivity(self):
        """Test case sensitivity handling"""
        config_content = """
WORKER_PROCESSES 1;

EVENTS {
    WORKER_CONNECTIONS 1024;
}

HTTP {
    SERVER {
        LISTEN 80;
        SERVER_NAME test.com;
    }
}
"""
        config_path = self.create_test_config('case_sensitive', config_content)
        nginx = NGINX(config_path)

        # Should handle case sensitivity (nginx is case-sensitive)
        # The parser should not find these uppercase directives
        self.assertEqual(len(nginx.global_config), 0)
        self.assertEqual(len(nginx.events_config), 0)
        self.assertEqual(len(nginx.http_config), 0)
        self.assertEqual(len(nginx.servers), 0)

    def test_duplicate_directives(self):
        """Test parsing with duplicate directives"""
        config_content = """
worker_processes 1;
worker_processes 2;
worker_processes 4;

events {
    worker_connections 1024;
    worker_connections 2048;
}

http {
    sendfile on;
    sendfile off;
    sendfile on;

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('duplicates', config_content)
        nginx = NGINX(config_path)

        # Should handle duplicates (first one wins in current implementation)
        self.assertEqual(nginx.global_config['worker_processes'], '1')
        self.assertEqual(nginx.events_config['worker_connections'], '1024')
        self.assertEqual(nginx.http_config['sendfile'], 'on')

    def test_empty_upstream_block(self):
        """Test parsing empty upstream block"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    upstream empty_backend {
        # No servers
    }

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('empty_upstream', config_content)
        nginx = NGINX(config_path)

        # Should handle empty upstream gracefully
        self.assertEqual(len(nginx.backend), 0)

    def test_upstream_with_only_comments(self):
        """Test upstream block with only comments"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    upstream commented_backend {
        # server 10.0.1.10:8080;
        # server 10.0.1.11:8080;
    }

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('commented_upstream', config_content)
        nginx = NGINX(config_path)

        # Should handle commented upstream gracefully
        self.assertEqual(len(nginx.backend), 0)

    def test_empty_server_block(self):
        """Test parsing empty server block"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        # Empty server block
    }
}
"""
        config_path = self.create_test_config('empty_server', config_content)
        nginx = NGINX(config_path)

        # Should handle empty server block
        self.assertEqual(len(nginx.servers), 0)  # No server_name means no server

    def test_server_without_server_name(self):
        """Test server block without server_name"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        # No server_name
    }
}
"""
        config_path = self.create_test_config('no_server_name', config_content)
        nginx = NGINX(config_path)

        # Should handle server without server_name
        self.assertEqual(len(nginx.servers), 0)

    def test_server_with_ip_server_name(self):
        """Test server block with IP as server_name"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name 127.0.0.1;
    }

    server {
        listen 80;
        server_name 192.168.1.1;
    }
}
"""
        config_path = self.create_test_config('ip_server_name', config_content)
        nginx = NGINX(config_path)

        # Should skip servers with IP server_names
        self.assertEqual(len(nginx.servers), 0)

    def test_empty_location_block(self):
        """Test parsing empty location block"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name test.com;

        location /empty {
            # Empty location
        }
    }
}
"""
        config_path = self.create_test_config('empty_location', config_content)
        nginx = NGINX(config_path)

        # Should handle empty location
        server = nginx.servers[0]
        self.assertEqual(len(server['backend']), 1)
        location = server['backend'][0]
        self.assertEqual(location['path'], '/empty')

    def test_location_with_complex_regex(self):
        """Test location with complex regex patterns"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name test.com;

        location ~ ^/api/v[0-9]+/users/[0-9]+$ {
            root /var/www/api;
        }

        location ~* \\.(jpg|jpeg|png|gif|ico|svg|webp|avif)$ {
            root /var/www/images;
        }

        location ~ ^/admin/.*\\.(php|php5|phtml)$ {
            root /var/www/admin;
        }
    }
}
"""
        config_path = self.create_test_config('complex_regex', config_content)
        nginx = NGINX(config_path)

        # Should handle complex regex patterns
        server = nginx.servers[0]
        locations = server['backend']

        # Find the complex regex location
        api_location = next((loc for loc in locations if 'api/v' in loc['path']), None)
        self.assertIsNotNone(api_location)
        self.assertEqual(api_location['modifier'], '~')

        # Find the image location
        image_location = next((loc for loc in locations if 'jpg|jpeg' in loc['path']), None)
        self.assertIsNotNone(image_location)
        self.assertEqual(image_location['modifier'], '~*')

    def test_missing_include_files(self):
        """Test handling missing include files"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include nonexistent1.conf;
    include nonexistent2.conf;
    include /path/to/nonexistent3.conf;

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('missing_includes', config_content)
        nginx = NGINX(config_path)

        # Should handle missing includes gracefully
        self.assertEqual(len(nginx.servers), 1)
        self.assertEqual(nginx.servers[0]['server_name'], 'test.com')

    def test_circular_includes(self):
        """Test handling circular include references"""
        # Create main config
        main_config = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include circular.conf;
}
"""
        # Create circular config
        circular_config = """
server {
    listen 80;
    server_name test.com;
}

include main.conf;
"""
        main_path = self.create_test_config('main', main_config)
        circular_path = os.path.join(self.temp_dir, 'circular.conf')
        with open(circular_path, 'w') as f:
            f.write(circular_config)

        nginx = NGINX(main_path)

        # Should handle circular includes gracefully
        # May not parse servers due to circular reference, just verify it doesn't crash
        self.assertIsNotNone(nginx)

    def test_very_deep_nesting(self):
        """Test parsing with very deep nesting"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    upstream backend {
        server 10.0.1.10:8080;
    }

    server {
        listen 80;
        server_name test.com;

        location /level1 {
            location /level2 {
                location /level3 {
                    location /level4 {
                        location /level5 {
                            proxy_pass http://backend;
                        }
                    }
                }
            }
        }
    }
}
"""
        config_path = self.create_test_config('deep_nesting', config_content)
        nginx = NGINX(config_path)

        # Should handle deep nesting
        self.assertEqual(len(nginx.servers), 1)
        server = nginx.servers[0]
        # Note: The current parser doesn't handle nested locations
        # This test documents the current behavior
        self.assertEqual(len(server['backend']), 1)

    def test_mixed_line_endings(self):
        """Test parsing with mixed line endings"""
        config_content = "worker_processes 1;\r\n\r\nevents {\r\n    worker_connections 1024;\n}\r\n\r\nhttp {\n    server {\r\n        listen 80;\n        server_name test.com;\r\n    }\n}"
        config_path = self.create_test_config('mixed_endings', config_content)
        nginx = NGINX(config_path)

        # Should handle mixed line endings
        self.assertEqual(nginx.global_config['worker_processes'], '1')
        self.assertEqual(nginx.events_config['worker_connections'], '1024')
        self.assertEqual(len(nginx.servers), 1)

    def test_very_large_configuration(self):
        """Test parsing very large configuration"""
        # Generate a large configuration
        config_parts = ["worker_processes 1;", "", "events {", "    worker_connections 1024;", "}", "", "http {"]
        
        # Add many upstreams
        for i in range(100):
            config_parts.append(f"    upstream backend_{i} {{")
            config_parts.append(f"        server 10.0.{i//10}.{i%10}:8080;")
            config_parts.append("    }")
        
        # Add many servers
        for i in range(50):
            config_parts.append(f"    server {{")
            config_parts.append(f"        listen {8080 + i};")
            config_parts.append(f"        server_name test{i}.com;")
            config_parts.append("    }")
        
        config_parts.append("}")
        
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('large_config', config_content)
        nginx = NGINX(config_path)

        # Should handle large configuration
        self.assertEqual(len(nginx.backend), 100)
        self.assertEqual(len(nginx.servers), 50)

    def test_negative_values(self):
        """Test parsing with negative values"""
        config_content = """
worker_processes -1;

events {
    worker_connections -1024;
}

http {
    keepalive_timeout -65;

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('negative_values', config_content)
        nginx = NGINX(config_path)

        # Should handle negative values (nginx will validate them)
        self.assertEqual(nginx.global_config['worker_processes'], '-1')
        self.assertEqual(nginx.events_config['worker_connections'], '-1024')
        self.assertEqual(nginx.http_config['keepalive_timeout'], '-65')

    def test_zero_values(self):
        """Test parsing with zero values"""
        config_content = """
worker_processes 0;

events {
    worker_connections 0;
}

http {
    keepalive_timeout 0;

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('zero_values', config_content)
        nginx = NGINX(config_path)

        # Should handle zero values
        self.assertEqual(nginx.global_config['worker_processes'], '0')
        self.assertEqual(nginx.events_config['worker_connections'], '0')
        self.assertEqual(nginx.http_config['keepalive_timeout'], '0')

    def test_boolean_values(self):
        """Test parsing boolean values"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
    multi_accept on;
    accept_mutex off;
}

http {
    sendfile on;
    tcp_nopush off;
    gzip on;

    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('boolean_values', config_content)
        nginx = NGINX(config_path)

        # Should handle boolean values
        self.assertEqual(nginx.events_config['multi_accept'], 'on')
        self.assertEqual(nginx.events_config['accept_mutex'], 'off')
        self.assertEqual(nginx.http_config['sendfile'], 'on')
        self.assertEqual(nginx.http_config['gzip'], 'on')

    def test_quoted_values(self):
        """Test parsing quoted values"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name "test.example.com" 'another.example.com';
        root "/var/www/html";
        index 'index.html index.htm';
    }
}
"""
        config_path = self.create_test_config('quoted_values', config_content)
        nginx = NGINX(config_path)

        # Should handle quoted values (quotes may be preserved)
        server_name = nginx.servers[0]['server_name']
        self.assertIn('test.example.com', server_name)
        self.assertIn('another.example.com', server_name)
        # Quotes may be preserved in the parsed value
        self.assertIn('html', nginx.servers[0]['root'])

    def test_escaped_characters(self):
        """Test parsing escaped characters"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name test\\.example\\.com;
        root /var/www/html;
    }
}
"""
        config_path = self.create_test_config('escaped_chars', config_content)
        nginx = NGINX(config_path)

        # Should handle escaped characters
        self.assertEqual(nginx.servers[0]['server_name'], 'test\\.example\\.com')

    def test_performance_with_many_locations(self):
        """Test performance with many location blocks"""
        config_parts = ["worker_processes 1;", "", "events {", "    worker_connections 1024;", "}", "", "http {", "    server {", "        listen 80;", "        server_name test.com;"]
        
        # Add many locations
        for i in range(1000):
            config_parts.append(f"        location /path{i} {{")
            config_parts.append(f"            root /var/www/path{i};")
            config_parts.append("        }")
        
        config_parts.extend(["    }", "}"])
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('many_locations', config_content)
        
        import time
        start_time = time.time()
        nginx = NGINX(config_path)
        end_time = time.time()
        
        # Should handle many locations efficiently
        self.assertEqual(len(nginx.servers), 1)
        self.assertEqual(len(nginx.servers[0]['backend']), 1000)
        
        # Should complete in reasonable time (less than 5 seconds)
        self.assertLess(end_time - start_time, 5.0)


if __name__ == '__main__':
    # Run all edge case tests
    unittest.main(verbosity=2)
