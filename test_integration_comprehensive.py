# coding: utf-8
"""
Integration Test Suite for NGINX Parser
Tests real-world configurations and complex scenarios
"""

import unittest
import tempfile
import os
import json
from nginx import NGINX


class TestNGINXParserIntegration(unittest.TestCase):
    """Integration tests for NGINX parser with real-world scenarios"""

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
        os.rmdir(self.temp_dir)

    def create_test_config(self, name, content):
        """Create a temporary test configuration file"""
        config_path = os.path.join(self.temp_dir, f"{name}.conf")
        with open(config_path, 'w') as f:
            f.write(content)
        self.test_configs[name] = config_path
        return config_path

    def test_production_like_configuration(self):
        """Test a production-like nginx configuration"""
        config_content = """
# Production nginx configuration
user nginx;
worker_processes auto;
worker_cpu_affinity auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;
worker_rlimit_nofile 65535;

events {
    use epoll;
    worker_connections 2048;
    multi_accept on;
    accept_mutex off;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    sendfile        on;
    tcp_nopush     on;
    tcp_nodelay    on;
    keepalive_timeout  65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream configurations
    upstream api_backend {
        least_conn;
        server 10.0.1.10:8080 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.1.11:8080 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.1.12:8080 weight=2 max_fails=3 fail_timeout=30s;
        server 10.0.1.13:8080 weight=1 backup;
    }

    upstream web_backend {
        ip_hash;
        server 10.0.2.10:80 weight=5;
        server 10.0.2.11:80 weight=5;
        server 10.0.2.12:80 weight=3 backup;
    }

    upstream static_backend {
        hash $request_uri consistent;
        server 10.0.3.10:80;
        server 10.0.3.11:80;
        server 10.0.3.12:80;
    }

    # Main HTTP server
    server {
        listen 80;
        listen [::]:80;
        server_name example.com www.example.com;
        root /var/www/html;
        index index.html index.htm;

        access_log /var/log/nginx/access.log main;
        error_log /var/log/nginx/error.log warn;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Main location
        location = / {
            try_files $uri $uri/ /index.html;
        }

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Web application
        location /app/ {
            proxy_pass http://web_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Static files
        location /static/ {
            proxy_pass http://static_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # PHP files
        location ~ \\.php$ {
            root /var/www/html;
            fastcgi_pass 127.0.0.1:9000;
            fastcgi_index index.php;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            include fastcgi_params;
        }

        # Image optimization
        location ~* \\.(jpg|jpeg|png|gif|ico|svg)$ {
            root /var/www/images;
            expires 1y;
            add_header Cache-Control "public";
            try_files $uri =404;
        }

        # CSS and JS files
        location ~* \\.(css|js)$ {
            root /var/www/assets;
            expires 1y;
            add_header Cache-Control "public";
            try_files $uri =404;
        }

        # Admin panel with strict access
        location ^~ /admin {
            limit_req zone=login burst=5 nodelay;
            root /var/www/admin;
            index admin.html;
            auth_basic "Admin Area";
            auth_basic_user_file /etc/nginx/.htpasswd;
        }

        # Health check endpoint
        location = /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # Error pages
        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name secure.example.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/cert.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        root /var/www/secure;
        index index.html;

        access_log /var/log/nginx/secure.access.log main;
        error_log /var/log/nginx/secure.error.log warn;

        # Security headers for HTTPS
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name secure.example.com;
        return 301 https://$server_name$request_uri;
    }
}
"""
        config_path = self.create_test_config('production', config_content)
        nginx = NGINX(config_path)

        # Test global configuration
        self.assertEqual(nginx.global_config['user'], 'nginx')
        self.assertEqual(nginx.global_config['worker_processes'], 'auto')
        self.assertEqual(nginx.global_config['worker_cpu_affinity'], 'auto')
        self.assertEqual(nginx.global_config['error_log'], '/var/log/nginx/error.log warn')
        self.assertEqual(nginx.global_config['pid'], '/var/run/nginx.pid')
        self.assertEqual(nginx.global_config['worker_rlimit_nofile'], '65535')

        # Test events configuration
        self.assertEqual(nginx.events_config['use'], 'epoll')
        self.assertEqual(nginx.events_config['worker_connections'], '2048')
        self.assertEqual(nginx.events_config['multi_accept'], 'on')
        self.assertEqual(nginx.events_config['accept_mutex'], 'off')

        # Test HTTP configuration
        self.assertEqual(nginx.http_config['default_type'], 'application/octet-stream')
        self.assertEqual(nginx.http_config['sendfile'], 'on')
        self.assertEqual(nginx.http_config['keepalive_timeout'], '65')
        self.assertEqual(nginx.http_config['gzip'], 'on')

        # Test upstream configurations
        self.assertEqual(len(nginx.backend), 3)

        # API backend
        api_backend = nginx.backend[0]
        self.assertEqual(api_backend['poolname'], 'api_backend')
        self.assertEqual(api_backend['load_balancing'], 'least_conn')
        self.assertEqual(len(api_backend['servers']), 4)
        self.assertTrue(api_backend['servers'][3]['backup'])

        # Web backend
        web_backend = nginx.backend[1]
        self.assertEqual(web_backend['poolname'], 'web_backend')
        self.assertEqual(web_backend['load_balancing'], 'ip_hash')
        self.assertEqual(len(web_backend['servers']), 3)
        self.assertTrue(web_backend['servers'][2]['backup'])

        # Static backend
        static_backend = nginx.backend[2]
        self.assertEqual(static_backend['poolname'], 'static_backend')
        self.assertEqual(static_backend['load_balancing'], 'hash $request_uri consistent')
        self.assertEqual(len(static_backend['servers']), 3)

        # Test server configurations
        self.assertEqual(len(nginx.servers), 3)

        # HTTP server
        http_server = nginx.servers[0]
        self.assertEqual(http_server['port'], '80')
        self.assertEqual(http_server['listen'], ['80', '[::]:80'])
        self.assertEqual(http_server['server_name'], 'example.com www.example.com')
        self.assertEqual(http_server['root'], '/var/www/html')
        self.assertEqual(http_server['index'], 'index.html index.htm')
        self.assertEqual(http_server['access_log'], '/var/log/nginx/access.log main')
        self.assertEqual(http_server['error_log'], '/var/log/nginx/error.log warn')

        # Test locations in HTTP server
        locations = http_server['backend']
        self.assertGreater(len(locations), 5)

        # Find specific locations
        api_location = next((loc for loc in locations if loc['path'] == '/api/'), None)
        self.assertIsNotNone(api_location)
        self.assertEqual(api_location['proxy_pass'], 'http://10.0.1.10:8080 10.0.1.11:8080 10.0.1.12:8080 10.0.1.13:8080')

        php_location = next((loc for loc in locations if loc['path'] == '\\.php$'), None)
        self.assertIsNotNone(php_location)
        self.assertEqual(php_location['modifier'], '~')
        self.assertEqual(php_location['fastcgi_pass'], '127.0.0.1:9000')

        admin_location = next((loc for loc in locations if loc['path'] == '/admin'), None)
        self.assertIsNotNone(admin_location)
        self.assertEqual(admin_location['modifier'], '^~')
        self.assertEqual(admin_location['root'], '/var/www/admin')

        # HTTPS server
        https_server = nginx.servers[1]
        self.assertEqual(https_server['port'], '443 ssl http2')
        self.assertEqual(https_server['listen'], ['443 ssl http2', '[::]:443 ssl http2'])
        self.assertEqual(https_server['server_name'], 'secure.example.com')
        self.assertEqual(https_server['ssl_certificate'], '/etc/nginx/ssl/cert.pem')
        self.assertEqual(https_server['ssl_certificate_key'], '/etc/nginx/ssl/cert.key')
        self.assertEqual(https_server['ssl_protocols'], 'TLSv1.2 TLSv1.3')

        # Redirect server
        redirect_server = nginx.servers[2]
        self.assertEqual(redirect_server['server_name'], 'secure.example.com')

    def test_microservices_configuration(self):
        """Test microservices architecture configuration"""
        config_content = """
user nginx;
worker_processes 4;

events {
    worker_connections 1024;
}

http {
    # Microservices upstreams
    upstream user_service {
        least_conn;
        server 10.0.1.10:8001 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.1.11:8001 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.1.12:8001 weight=2 backup;
    }

    upstream order_service {
        ip_hash;
        server 10.0.2.10:8002 weight=5;
        server 10.0.2.11:8002 weight=5;
    }

    upstream payment_service {
        server 10.0.3.10:8003 weight=3 max_fails=2 fail_timeout=20s;
        server 10.0.3.11:8003 weight=3 max_fails=2 fail_timeout=20s;
        server 10.0.3.12:8003 weight=1 backup;
    }

    upstream notification_service {
        hash $request_uri consistent;
        server 10.0.4.10:8004;
        server 10.0.4.11:8004;
    }

    upstream inventory_service {
        least_conn;
        server 10.0.5.10:8005 weight=2;
        server 10.0.5.11:8005 weight=2;
        server 10.0.5.12:8005 weight=1 backup;
    }

    # API Gateway
    server {
        listen 80;
        server_name api.example.com;

        # User service
        location /api/users/ {
            proxy_pass http://user_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Order service
        location /api/orders/ {
            proxy_pass http://order_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Payment service
        location /api/payments/ {
            proxy_pass http://payment_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Notification service
        location /api/notifications/ {
            proxy_pass http://notification_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Inventory service
        location /api/inventory/ {
            proxy_pass http://inventory_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "API Gateway OK\\n";
            add_header Content-Type text/plain;
        }
    }

    # Web frontend
    server {
        listen 80;
        server_name www.example.com;
        root /var/www/frontend;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://api.example.com/api/;
            proxy_set_header Host api.example.com;
        }
    }
}
"""
        config_path = self.create_test_config('microservices', config_content)
        nginx = NGINX(config_path)

        # Test all upstreams are parsed
        self.assertEqual(len(nginx.backend), 5)

        upstream_names = [up['poolname'] for up in nginx.backend]
        expected_services = ['user_service', 'order_service', 'payment_service', 
                           'notification_service', 'inventory_service']
        for service in expected_services:
            self.assertIn(service, upstream_names)

        # Test load balancing methods
        user_service = next(up for up in nginx.backend if up['poolname'] == 'user_service')
        self.assertEqual(user_service['load_balancing'], 'least_conn')

        order_service = next(up for up in nginx.backend if up['poolname'] == 'order_service')
        self.assertEqual(order_service['load_balancing'], 'ip_hash')

        notification_service = next(up for up in nginx.backend if up['poolname'] == 'notification_service')
        self.assertEqual(notification_service['load_balancing'], 'hash $request_uri consistent')

        # Test servers
        self.assertEqual(len(nginx.servers), 2)

        # API Gateway server
        api_server = nginx.servers[0]
        self.assertEqual(api_server['server_name'], 'api.example.com')
        self.assertEqual(len(api_server['backend']), 6)  # 5 services + health check

        # Web frontend server
        web_server = nginx.servers[1]
        self.assertEqual(web_server['server_name'], 'www.example.com')

    def test_load_balancer_configuration(self):
        """Test load balancer with multiple algorithms"""
        config_content = """
user nginx;
worker_processes 2;

events {
    worker_connections 1024;
}

http {
    # Round robin (default)
    upstream round_robin_backend {
        server 10.0.1.10:80 weight=3;
        server 10.0.1.11:80 weight=2;
        server 10.0.1.12:80 weight=1;
    }

    # Least connections
    upstream least_conn_backend {
        least_conn;
        server 10.0.2.10:80 weight=5;
        server 10.0.2.11:80 weight=3;
        server 10.0.2.12:80 weight=2;
    }

    # IP hash
    upstream ip_hash_backend {
        ip_hash;
        server 10.0.3.10:80;
        server 10.0.3.11:80;
        server 10.0.3.12:80;
    }

    # Hash with consistent
    upstream hash_backend {
        hash $request_uri consistent;
        server 10.0.4.10:80;
        server 10.0.4.11:80;
        server 10.0.4.12:80;
    }

    # Hash with key
    upstream hash_key_backend {
        hash $arg_user consistent;
        server 10.0.5.10:80;
        server 10.0.5.11:80;
    }

    server {
        listen 80;
        server_name lb.example.com;

        location /round-robin {
            proxy_pass http://round_robin_backend;
        }

        location /least-conn {
            proxy_pass http://least_conn_backend;
        }

        location /ip-hash {
            proxy_pass http://ip_hash_backend;
        }

        location /hash {
            proxy_pass http://hash_backend;
        }

        location /hash-key {
            proxy_pass http://hash_key_backend;
        }
    }
}
"""
        config_path = self.create_test_config('load_balancer', config_content)
        nginx = NGINX(config_path)

        # Test all upstreams
        self.assertEqual(len(nginx.backend), 5)

        # Test round robin
        round_robin = next(up for up in nginx.backend if up['poolname'] == 'round_robin_backend')
        self.assertEqual(round_robin['load_balancing'], 'round_robin')
        self.assertEqual(len(round_robin['servers']), 3)
        self.assertEqual(round_robin['servers'][0]['weight'], 3)
        self.assertEqual(round_robin['servers'][1]['weight'], 2)
        self.assertEqual(round_robin['servers'][2]['weight'], 1)

        # Test least connections
        least_conn = next(up for up in nginx.backend if up['poolname'] == 'least_conn_backend')
        self.assertEqual(least_conn['load_balancing'], 'least_conn')

        # Test IP hash
        ip_hash = next(up for up in nginx.backend if up['poolname'] == 'ip_hash_backend')
        self.assertEqual(ip_hash['load_balancing'], 'ip_hash')

        # Test hash
        hash_backend = next(up for up in nginx.backend if up['poolname'] == 'hash_backend')
        self.assertEqual(hash_backend['load_balancing'], 'hash $request_uri consistent')

        # Test hash with key
        hash_key = next(up for up in nginx.backend if up['poolname'] == 'hash_key_backend')
        self.assertEqual(hash_key['load_balancing'], 'hash $arg_user consistent')

    def test_ssl_termination_configuration(self):
        """Test SSL termination and certificate management"""
        config_content = """
user nginx;
worker_processes 2;

events {
    worker_connections 1024;
}

http {
    upstream backend {
        server 10.0.1.10:8080;
        server 10.0.1.11:8080;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name example.com www.example.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name example.com www.example.com;

        ssl_certificate /etc/nginx/ssl/example.com.crt;
        ssl_certificate_key /etc/nginx/ssl/example.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_stapling on;
        ssl_stapling_verify on;

        root /var/www/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }
    }

    # Wildcard certificate
    server {
        listen 443 ssl;
        server_name *.example.com;

        ssl_certificate /etc/nginx/ssl/wildcard.example.com.crt;
        ssl_certificate_key /etc/nginx/ssl/wildcard.example.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;

        root /var/www/wildcard;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
"""
        config_path = self.create_test_config('ssl_termination', config_content)
        nginx = NGINX(config_path)

        # Test servers
        self.assertEqual(len(nginx.servers), 3)

        # HTTP redirect server
        redirect_server = nginx.servers[0]
        self.assertEqual(redirect_server['server_name'], 'example.com www.example.com')

        # HTTPS server
        https_server = nginx.servers[1]
        self.assertEqual(https_server['port'], '443 ssl http2')
        self.assertEqual(https_server['listen'], ['443 ssl http2', '[::]:443 ssl http2'])
        self.assertEqual(https_server['server_name'], 'example.com www.example.com')
        self.assertEqual(https_server['ssl_certificate'], '/etc/nginx/ssl/example.com.crt')
        self.assertEqual(https_server['ssl_certificate_key'], '/etc/nginx/ssl/example.com.key')
        self.assertEqual(https_server['ssl_protocols'], 'TLSv1.2 TLSv1.3')

        # Wildcard server
        wildcard_server = nginx.servers[2]
        self.assertEqual(wildcard_server['server_name'], '*.example.com')
        self.assertEqual(wildcard_server['ssl_certificate'], '/etc/nginx/ssl/wildcard.example.com.crt')
        self.assertEqual(wildcard_server['ssl_certificate_key'], '/etc/nginx/ssl/wildcard.example.com.key')

    def test_complex_location_rules(self):
        """Test complex location matching rules"""
        config_content = """
user nginx;
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    upstream api {
        server 10.0.1.10:8080;
    }

    upstream static {
        server 10.0.2.10:80;
    }

    server {
        listen 80;
        server_name complex.example.com;

        # Exact match (highest priority)
        location = /exact {
            return 200 "Exact match";
        }

        # Prefix match with ^~ (higher priority than regex)
        location ^~ /prefix {
            root /var/www/prefix;
            try_files $uri $uri/ /index.html;
        }

        # Case-sensitive regex
        location ~ \\.(php|php5)$ {
            root /var/www/php;
            fastcgi_pass 127.0.0.1:9000;
            fastcgi_index index.php;
            include fastcgi_params;
        }

        # Case-insensitive regex
        location ~* \\.(jpg|jpeg|png|gif|ico|svg)$ {
            root /var/www/images;
            expires 1y;
            add_header Cache-Control "public";
        }

        # Regular prefix match
        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
        }

        # Static files with try_files
        location /static/ {
            root /var/www;
            try_files $uri $uri/ @fallback;
        }

        # Named location
        location @fallback {
            proxy_pass http://static;
        }

        # Default location
        location / {
            root /var/www/html;
            try_files $uri $uri/ /index.html;
        }
    }
}
"""
        config_path = self.create_test_config('complex_locations', config_content)
        nginx = NGINX(config_path)

        server = nginx.servers[0]
        locations = server['backend']

        # Test exact match
        exact_location = next((loc for loc in locations if loc['path'] == '/exact'), None)
        self.assertIsNotNone(exact_location)
        self.assertEqual(exact_location['modifier'], '=')

        # Test prefix match with ^~
        prefix_location = next((loc for loc in locations if loc['path'] == '/prefix'), None)
        self.assertIsNotNone(prefix_location)
        self.assertEqual(prefix_location['modifier'], '^~')

        # Test regex match
        php_location = next((loc for loc in locations if loc['path'] == '\\.(php|php5)$'), None)
        self.assertIsNotNone(php_location)
        self.assertEqual(php_location['modifier'], '~')
        self.assertEqual(php_location['fastcgi_pass'], '127.0.0.1:9000')

        # Test case-insensitive regex
        image_location = next((loc for loc in locations if loc['path'] == '\\.(jpg|jpeg|png|gif|ico|svg)$'), None)
        self.assertIsNotNone(image_location)
        self.assertEqual(image_location['modifier'], '~*')

        # Test regular prefix match
        api_location = next((loc for loc in locations if loc['path'] == '/api/'), None)
        self.assertIsNotNone(api_location)
        self.assertIsNone(api_location['modifier'])
        self.assertEqual(api_location['proxy_pass'], 'http://10.0.1.10:8080/')

        # Test default location
        default_location = next((loc for loc in locations if loc['path'] == '/'), None)
        self.assertIsNotNone(default_location)
        self.assertIsNone(default_location['modifier'])

    def test_performance_optimization_configuration(self):
        """Test performance optimization features"""
        config_content = """
user nginx;
worker_processes auto;
worker_cpu_affinity auto;
worker_rlimit_nofile 65535;

events {
    use epoll;
    worker_connections 2048;
    multi_accept on;
    accept_mutex off;
}

http {
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Caching
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Connection limiting
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;

    upstream backend {
        least_conn;
        server 10.0.1.10:8080 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.1.11:8080 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.1.12:8080 weight=2 backup;
    }

    server {
        listen 80;
        server_name perf.example.com;

        # Connection limiting
        limit_conn conn_limit_per_ip 10;

        # API with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Static files with caching
        location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
            root /var/www/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary Accept-Encoding;
        }

        # HTML files with shorter cache
        location ~* \\.html$ {
            root /var/www/html;
            expires 1h;
            add_header Cache-Control "public";
        }
    }
}
"""
        config_path = self.create_test_config('performance', config_content)
        nginx = NGINX(config_path)

        # Test global performance settings
        self.assertEqual(nginx.global_config['worker_processes'], 'auto')
        self.assertEqual(nginx.global_config['worker_cpu_affinity'], 'auto')
        self.assertEqual(nginx.global_config['worker_rlimit_nofile'], '65535')

        # Test events performance settings
        self.assertEqual(nginx.events_config['use'], 'epoll')
        self.assertEqual(nginx.events_config['worker_connections'], '2048')
        self.assertEqual(nginx.events_config['multi_accept'], 'on')
        self.assertEqual(nginx.events_config['accept_mutex'], 'off')

        # Test HTTP performance settings
        self.assertEqual(nginx.http_config['sendfile'], 'on')
        self.assertEqual(nginx.http_config['keepalive_timeout'], '65')
        self.assertEqual(nginx.http_config['gzip'], 'on')

        # Test upstream with performance settings
        backend = nginx.backend[0]
        self.assertEqual(backend['load_balancing'], 'least_conn')
        self.assertEqual(len(backend['servers']), 3)
        self.assertTrue(backend['servers'][2]['backup'])

    def test_json_output_consistency(self):
        """Test JSON output consistency across different configurations"""
        config_content = """
user nginx;
worker_processes 2;

events {
    worker_connections 1024;
}

http {
    upstream backend {
        server 10.0.1.10:8080 weight=3;
        server 10.0.1.11:8080 weight=2;
    }

    server {
        listen 80;
        server_name test.example.com;
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
        config_path = self.create_test_config('json_consistency', config_content)
        nginx = NGINX(config_path)

        # Test that all expected keys are present
        full_config = {
            'global': nginx.global_config,
            'events': nginx.events_config,
            'http': nginx.http_config,
            'upstreams': nginx.backend,
            'servers': nginx.servers
        }

        # Verify JSON serialization works
        json_output = json.dumps(full_config, indent=2, default=str)
        self.assertIsInstance(json_output, str)
        self.assertGreater(len(json_output), 100)

        # Verify deserialization works
        parsed_config = json.loads(json_output)
        self.assertIn('global', parsed_config)
        self.assertIn('events', parsed_config)
        self.assertIn('http', parsed_config)
        self.assertIn('upstreams', parsed_config)
        self.assertIn('servers', parsed_config)

        # Verify data integrity
        self.assertEqual(parsed_config['global']['worker_processes'], '2')
        self.assertEqual(parsed_config['events']['worker_connections'], '1024')
        self.assertEqual(len(parsed_config['upstreams']), 1)
        self.assertEqual(len(parsed_config['servers']), 1)


if __name__ == '__main__':
    # Run all integration tests
    unittest.main(verbosity=2)
