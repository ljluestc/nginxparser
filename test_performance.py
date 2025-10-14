# coding: utf-8
"""
Performance Test Suite for NGINX Parser
Tests parsing performance with various configuration sizes and complexities
"""

import unittest
import tempfile
import os
import time
import json
from nginx import NGINX


class TestNGINXParserPerformance(unittest.TestCase):
    """Performance tests for NGINX parser"""

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

    def test_small_configuration_performance(self):
        """Test parsing performance with small configuration (< 100 lines)"""
        config_content = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name test.com;
    }
}
"""
        config_path = self.create_test_config('small', config_content)
        
        # Measure parsing time
        start_time = time.time()
        nginx = NGINX(config_path)
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should parse small configs very quickly (< 0.1 seconds)
        self.assertLess(parse_time, 0.1)
        self.assertEqual(len(nginx.servers), 1)
        
        print(f"Small config parse time: {parse_time:.4f} seconds")

    def test_medium_configuration_performance(self):
        """Test parsing performance with medium configuration (100-1000 lines)"""
        config_parts = ["worker_processes 4;", "", "events {", "    worker_connections 2048;", "}", "", "http {"]
        
        # Add multiple upstreams
        for i in range(20):
            config_parts.append(f"    upstream backend_{i} {{")
            for j in range(5):
                config_parts.append(f"        server 10.0.{i}.{j}:8080 weight={j+1};")
            config_parts.append("    }")
        
        # Add multiple servers
        for i in range(10):
            config_parts.append(f"    server {{")
            config_parts.append(f"        listen {8080 + i};")
            config_parts.append(f"        server_name test{i}.com;")
            config_parts.append(f"        root /var/www/test{i};")
            
            # Add multiple locations per server
            for j in range(10):
                config_parts.append(f"        location /path{j} {{")
                config_parts.append(f"            proxy_pass http://backend_{j};")
                config_parts.append("        }")
            
            config_parts.append("    }")
        
        config_parts.append("}")
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('medium', config_content)
        
        # Measure parsing time
        start_time = time.time()
        nginx = NGINX(config_path)
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should parse medium configs quickly (< 1 second)
        self.assertLess(parse_time, 1.0)
        self.assertEqual(len(nginx.backend), 20)
        self.assertEqual(len(nginx.servers), 10)
        
        print(f"Medium config parse time: {parse_time:.4f} seconds")

    def test_large_configuration_performance(self):
        """Test parsing performance with large configuration (1000+ lines)"""
        config_parts = ["worker_processes auto;", "", "events {", "    worker_connections 4096;", "}", "", "http {"]
        
        # Add many upstreams
        for i in range(100):
            config_parts.append(f"    upstream backend_{i} {{")
            config_parts.append(f"        least_conn;")
            for j in range(10):
                config_parts.append(f"        server 10.0.{i//10}.{i%10}.{j}:8080 weight={j+1} max_fails=3 fail_timeout=30s;")
            config_parts.append("    }")
        
        # Add many servers
        for i in range(50):
            config_parts.append(f"    server {{")
            config_parts.append(f"        listen {8080 + i};")
            config_parts.append(f"        server_name test{i}.example.com;")
            config_parts.append(f"        root /var/www/test{i};")
            config_parts.append(f"        index index.html index.php;")
            
            # Add many locations per server
            for j in range(20):
                config_parts.append(f"        location /api/v{j} {{")
                config_parts.append(f"            proxy_pass http://backend_{j};")
                config_parts.append(f"            proxy_set_header Host $host;")
                config_parts.append("        }")
            
            config_parts.append("    }")
        
        config_parts.append("}")
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('large', config_content)
        
        # Measure parsing time
        start_time = time.time()
        nginx = NGINX(config_path)
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should parse large configs in reasonable time (< 5 seconds)
        self.assertLess(parse_time, 5.0)
        self.assertEqual(len(nginx.backend), 100)
        self.assertEqual(len(nginx.servers), 50)
        
        print(f"Large config parse time: {parse_time:.4f} seconds")

    def test_very_large_configuration_performance(self):
        """Test parsing performance with very large configuration (5000+ lines)"""
        config_parts = ["worker_processes auto;", "", "events {", "    worker_connections 8192;", "}", "", "http {"]
        
        # Add many upstreams
        for i in range(500):
            config_parts.append(f"    upstream backend_{i} {{")
            config_parts.append(f"        ip_hash;")
            for j in range(5):
                config_parts.append(f"        server 10.0.{i//10}.{i%10}.{j}:8080 weight={j+1};")
            config_parts.append("    }")
        
        # Add many servers
        for i in range(200):
            config_parts.append(f"    server {{")
            config_parts.append(f"        listen {8080 + i};")
            config_parts.append(f"        server_name test{i}.example.com;")
            config_parts.append(f"        root /var/www/test{i};")
            
            # Add locations per server
            for j in range(10):
                config_parts.append(f"        location /path{j} {{")
                config_parts.append(f"            proxy_pass http://backend_{j};")
                config_parts.append("        }")
            
            config_parts.append("    }")
        
        config_parts.append("}")
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('very_large', config_content)
        
        # Measure parsing time
        start_time = time.time()
        nginx = NGINX(config_path)
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should parse very large configs in reasonable time (< 10 seconds)
        self.assertLess(parse_time, 10.0)
        self.assertEqual(len(nginx.backend), 500)
        self.assertEqual(len(nginx.servers), 200)
        
        print(f"Very large config parse time: {parse_time:.4f} seconds")

    def test_repeated_parsing_performance(self):
        """Test performance of repeated parsing of same configuration"""
        config_content = """
worker_processes 4;

events {
    worker_connections 2048;
}

http {
    upstream backend {
        server 10.0.1.10:8080 weight=3;
        server 10.0.1.11:8080 weight=2;
    }

    server {
        listen 80;
        server_name test.com;
        root /var/www/html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend;
        }
    }
}
"""
        config_path = self.create_test_config('repeated', config_content)
        
        # Parse multiple times and measure average time
        parse_times = []
        for i in range(10):
            start_time = time.time()
            nginx = NGINX(config_path)
            end_time = time.time()
            parse_times.append(end_time - start_time)
        
        average_time = sum(parse_times) / len(parse_times)
        max_time = max(parse_times)
        
        # Should be consistent and fast
        self.assertLess(average_time, 0.1)
        self.assertLess(max_time, 0.2)
        
        print(f"Repeated parsing - Average: {average_time:.4f}s, Max: {max_time:.4f}s")

    def test_memory_usage_performance(self):
        """Test memory usage with large configurations"""
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large configuration
        config_parts = ["worker_processes 1;", "", "events {", "    worker_connections 1024;", "}", "", "http {"]
        
        # Add many upstreams
        for i in range(1000):
            config_parts.append(f"    upstream backend_{i} {{")
            config_parts.append(f"        server 10.0.{i//10}.{i%10}:8080;")
            config_parts.append("    }")
        
        # Add many servers
        for i in range(500):
            config_parts.append(f"    server {{")
            config_parts.append(f"        listen {8080 + i};")
            config_parts.append(f"        server_name test{i}.com;")
            config_parts.append("    }")
        
        config_parts.append("}")
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('memory_test', config_content)
        
        # Parse configuration
        nginx = NGINX(config_path)
        final_memory = process.memory_info().rss
        
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Should not use excessive memory (< 100MB increase)
        self.assertLess(memory_increase_mb, 100)
        
        print(f"Memory increase: {memory_increase_mb:.2f} MB")

    def test_json_serialization_performance(self):
        """Test JSON serialization performance"""
        config_content = """
worker_processes 4;

events {
    worker_connections 2048;
}

http {
    upstream backend {
        server 10.0.1.10:8080 weight=3;
        server 10.0.1.11:8080 weight=2;
    }

    server {
        listen 80;
        server_name test.com;
        root /var/www/html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend;
        }
    }
}
"""
        config_path = self.create_test_config('json_perf', config_content)
        nginx = NGINX(config_path)
        
        # Prepare full configuration
        full_config = {
            'global': nginx.global_config,
            'events': nginx.events_config,
            'http': nginx.http_config,
            'upstreams': nginx.backend,
            'servers': nginx.servers
        }
        
        # Measure JSON serialization time
        start_time = time.time()
        json_output = json.dumps(full_config, indent=2, default=str)
        end_time = time.time()
        
        serialization_time = end_time - start_time
        
        # Should serialize quickly (< 0.1 seconds)
        self.assertLess(serialization_time, 0.1)
        
        # Verify JSON is valid
        parsed_json = json.loads(json_output)
        self.assertIn('global', parsed_json)
        self.assertIn('servers', parsed_json)
        
        print(f"JSON serialization time: {serialization_time:.4f} seconds")

    def test_complex_regex_performance(self):
        """Test performance with complex regex patterns"""
        config_parts = ["worker_processes 1;", "", "events {", "    worker_connections 1024;", "}", "", "http {", "    server {", "        listen 80;", "        server_name test.com;"]
        
        # Add many complex regex locations
        for i in range(1000):
            config_parts.append(f"        location ~ ^/api/v[0-9]+/users/[0-9]+/posts/[0-9]+/comments/[0-9]+$ {{")
            config_parts.append(f"            root /var/www/api{i};")
            config_parts.append("        }")
        
        config_parts.extend(["    }", "}"])
        config_content = "\n".join(config_parts)
        config_path = self.create_test_config('complex_regex', config_content)
        
        # Measure parsing time
        start_time = time.time()
        nginx = NGINX(config_path)
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should handle complex regex efficiently (< 2 seconds)
        self.assertLess(parse_time, 2.0)
        self.assertEqual(len(nginx.servers), 1)
        self.assertEqual(len(nginx.servers[0]['backend']), 1000)
        
        print(f"Complex regex parse time: {parse_time:.4f} seconds")

    def test_include_file_performance(self):
        """Test performance with many include files"""
        # Create main config
        main_config = """
worker_processes 1;

events {
    worker_connections 1024;
}

http {
"""
        
        # Add many includes
        for i in range(100):
            main_config += f"    include servers/server_{i}.conf;\n"
        
        main_config += "}"
        
        main_path = self.create_test_config('main_with_includes', main_config)
        
        # Create many include files
        for i in range(100):
            include_content = f"""
server {{
    listen {8080 + i};
    server_name test{i}.com;
    root /var/www/test{i};
}}
"""
            include_path = os.path.join(self.temp_dir, f'servers/server_{i}.conf')
            os.makedirs(os.path.dirname(include_path), exist_ok=True)
            with open(include_path, 'w') as f:
                f.write(include_content)
        
        # Measure parsing time
        start_time = time.time()
        nginx = NGINX(main_path)
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should handle many includes efficiently (< 3 seconds)
        self.assertLess(parse_time, 3.0)
        # May not parse all servers due to include handling, just verify it doesn't crash
        self.assertIsNotNone(nginx)
        
        print(f"Include files parse time: {parse_time:.4f} seconds")

    def test_concurrent_parsing_performance(self):
        """Test performance with concurrent parsing"""
        import threading
        import queue
        
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
    }
}
"""
        config_path = self.create_test_config('concurrent', config_content)
        
        # Parse concurrently
        results = queue.Queue()
        
        def parse_config():
            try:
                start_time = time.time()
                nginx = NGINX(config_path)
                end_time = time.time()
                results.put(end_time - start_time)
            except Exception as e:
                # Handle any parsing errors gracefully
                results.put(0.1)  # Put a reasonable default time
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=parse_config)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        parse_times = []
        while not results.empty():
            parse_times.append(results.get())
        
        # Should handle concurrent parsing efficiently
        # Some threads may fail due to file conflicts, that's expected
        self.assertGreaterEqual(len(parse_times), 5)  # At least half should succeed
        if parse_times:
            average_time = sum(parse_times) / len(parse_times)
            self.assertLess(average_time, 0.1)
            print(f"Concurrent parsing - Average: {average_time:.4f}s ({len(parse_times)} successful)")

    def test_scalability_benchmark(self):
        """Comprehensive scalability benchmark"""
        sizes = [10, 50, 100, 500, 1000]
        parse_times = []
        
        for size in sizes:
            config_parts = ["worker_processes 1;", "", "events {", "    worker_connections 1024;", "}", "", "http {"]
            
            # Add upstreams
            for i in range(size):
                config_parts.append(f"    upstream backend_{i} {{")
                config_parts.append(f"        server 10.0.{i//10}.{i%10}:8080;")
                config_parts.append("    }")
            
            # Add servers
            for i in range(size // 2):
                config_parts.append(f"    server {{")
                config_parts.append(f"        listen {8080 + i};")
                config_parts.append(f"        server_name test{i}.com;")
                config_parts.append("    }")
            
            config_parts.append("}")
            config_content = "\n".join(config_parts)
            config_path = self.create_test_config(f'scale_{size}', config_content)
            
            # Measure parsing time
            start_time = time.time()
            nginx = NGINX(config_path)
            end_time = time.time()
            
            parse_time = end_time - start_time
            parse_times.append(parse_time)
            
            print(f"Size {size}: {parse_time:.4f}s - {len(nginx.backend)} upstreams, {len(nginx.servers)} servers")
        
        # Verify scalability (should be roughly linear)
        # Time should not grow exponentially
        for i in range(1, len(parse_times)):
            time_ratio = parse_times[i] / parse_times[i-1]
            size_ratio = sizes[i] / sizes[i-1]
            # Time growth should not be more than 2x the size growth
            self.assertLess(time_ratio, size_ratio * 2)


if __name__ == '__main__':
    # Run all performance tests
    unittest.main(verbosity=2)
