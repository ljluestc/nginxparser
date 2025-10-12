# nginxparser

## 功能

用python解析nginx配置，获取完整的nginx配置信息，包括：
- **全局配置** (user, worker_processes, worker_cpu_affinity, error_log, pid, worker_rlimit_nofile)
- **Events配置** (use, worker_connections, multi_accept, accept_mutex)
- **HTTP配置** (default_type, sendfile, keepalive_timeout, gzip)
- **Upstream配置** (支持weight, max_fails, fail_timeout, backup, down标志，以及所有负载均衡方法)
- **Server配置** (支持多个listen指令, SSL/TLS配置, 日志配置, root和index指令)
- **Location配置** (支持修饰符, proxy_pass, fastcgi_pass, rewrite规则, try_files)

## 版本

**Version 2.0.0** - 完整实现，支持所有主要nginx指令

## 安装

```bash
wget https://raw.githubusercontent.com/JoyChou93/nginxparser/master/nginx.py
```

或直接从本仓库使用

## 使用

### 基本使用

```python
from nginx import NGINX

nginx = NGINX('nginx.conf')
print(nginx.servers)
```

### 完整使用示例

```python
from nginx import NGINX
import json

# 解析nginx配置
nginx = NGINX('nginx.conf')

# 访问不同的配置块
print("Global Config:", nginx.global_config)
print("Events Config:", nginx.events_config)
print("HTTP Config:", nginx.http_config)
print("Upstreams:", nginx.backend)
print("Servers:", nginx.servers)

# 输出完整JSON
config = {
    'global': nginx.global_config,
    'events': nginx.events_config,
    'http': nginx.http_config,
    'upstreams': nginx.backend,
    'servers': nginx.servers
}
print(json.dumps(config, indent=2))
```

## 输出格式

### 全局配置示例
```python
{
    'user': 'nginx',
    'worker_processes': '8',
    'worker_cpu_affinity': 'auto',
    'error_log': '/var/log/nginx/error.log error',
    'pid': '/var/run/nginx.pid',
    'worker_rlimit_nofile': '65535'
}
```

### Upstream配置示例（增强版）
```python
{
    'poolname': 'backend_api',
    'ip': '192.168.1.10:8080 192.168.1.11:8080',
    'load_balancing': 'least_conn',
    'servers': [
        {
            'address': '192.168.1.10:8080',
            'weight': 5,
            'max_fails': 3,
            'fail_timeout': '30s'
        },
        {
            'address': '192.168.1.11:8080',
            'weight': 3,
            'backup': True
        }
    ]
}
```

### Server配置示例（增强版）
```python
{
    'port': '443 ssl',
    'listen': ['443 ssl', '[::]:443 ssl'],
    'server_name': 'secure.example.com',
    'root': '/var/www/secure',
    'index': 'index.html index.htm',
    'access_log': '/var/log/nginx/secure.access.log main',
    'ssl_certificate': '/etc/nginx/ssl/cert.pem',
    'ssl_certificate_key': '/etc/nginx/ssl/cert.key',
    'ssl_protocols': 'TLSv1.2 TLSv1.3',
    'backend': [ /* locations */ ]
}
```

### Location配置示例（增强版）
```python
[
    {
        'path': '/api',
        'modifier': None,
        'proxy_pass': 'http://backend_api',
        'backend_ip': '192.168.1.10:8080 192.168.1.11:8080'
    },
    {
        'path': '\\.php$',
        'modifier': '~',
        'fastcgi_pass': '127.0.0.1:9000',
        'root': '/var/www/html'
    },
    {
        'path': '/old-path',
        'rewrites': [
            '^/old-path/(.*)$ /new-path/$1 permanent'
        ]
    },
    {
        'path': '/static',
        'try_files': '$uri $uri/ /index.html'
    }
]
```

## 特性

### ✅ 全局配置解析
- user, worker_processes, worker_cpu_affinity
- error_log, pid, worker_rlimit_nofile

### ✅ Events配置解析
- use (epoll/select), worker_connections
- multi_accept, accept_mutex

### ✅ HTTP配置解析
- default_type, sendfile, keepalive_timeout, gzip

### ✅ 增强的Upstream解析
- 支持weight, max_fails, fail_timeout参数
- 支持backup和down标志
- 支持所有负载均衡方法 (round_robin, least_conn, ip_hash, hash)

### ✅ 增强的Server块解析
- 支持多个listen指令
- SSL/TLS配置 (ssl_certificate, ssl_certificate_key, ssl_protocols, ssl_ciphers)
- Server级别的access_log和error_log
- root和index指令

### ✅ 增强的Location块解析
- 支持所有修饰符 (=, ~, ~*, ^~)
- proxy_pass配置
- fastcgi_pass配置
- rewrite规则解析
- try_files指令解析

### ✅ 现有特性（保持）
- Include文件合并
- 注释移除
- Python 2.7/3.x兼容

## 测试

运行完整功能测试：

```bash
python test_full_features.py
```

运行基本测试：

```bash
python test.py
```

## 文档

- **PRD.md** - 完整的产品需求文档
- **FINAL_REPORT.md** - 最终实现报告
- **IMPLEMENTATION_SUMMARY.md** - 实现摘要
- **taskmaster.py** - 自动化任务执行系统

## 兼容性

- Python 2.7
- Python 3.x (3.6+)
- 无外部依赖，仅使用标准库

## 更新日志

### Version 2.0.0 (2025-10-11)
- ✅ 完整实现所有32个PRD任务
- ✅ 添加全局、events、HTTP配置解析
- ✅ 增强upstream解析（weight, max_fails, fail_timeout, backup, down, 负载均衡方法）
- ✅ 增强server解析（多listen, SSL/TLS, 日志, root, index）
- ✅ 增强location解析（修饰符, proxy_pass, fastcgi_pass, rewrite, try_files）
- ✅ 修复所有语法警告
- ✅ 100%测试通过率

### Version 1.0.0
- 基本的server块和location块解析
- 后端IP提取
- Include文件合并