# coding: utf-8
# date:   2018.02.28
# author: JoyChou
# desc:   用python解析nginx.conf配置，得到server块及server块的后端IP
# python: 2.7/3.x

import re
import os


class NGINX:

    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.backend = list()  # 保存后端ip和pool name
        self.serverBlock = list()  # 保存解析后端每个server块
        self.servers = list()
        self.global_config = {}  # 保存全局配置
        self.events_config = {}  # 保存events配置
        self.http_config = {}    # 保存http配置
        self.tmp_conf = '/tmp/tmp_nginx.conf'
        self.all_conf = '/tmp/nginx.conf'
        self.merge_conf()
        self.parse_global_block()
        self.parse_events_block()
        self.parse_http_block()
        self.parse_backend_ip()
        self.parse_server_block()

    # 将所有include的配置，合并到一个配置文件里
    def merge_conf(self):
        # 切换到self.conf.path的当前目录
        conf_dir = os.path.dirname(self.conf_path)

        # 判断是否是nginx.py的当前目录
        if len(conf_dir) != 0:
            os.chdir(conf_dir)

        include_regex = r'^[^#]nclude\s*([^;]*);'

        # 现将include的文件的内容整合一个文件，并且去掉注释行
        fm = open(self.tmp_conf, 'w+')
        with open(self.conf_path, 'r') as f:
            for line in f.readlines():
                r = re.findall(include_regex, line)
                # 如果存在include行
                if len(r) > 0:
                    include_path = r[0]
                    if os.path.exists(include_path):
                        with open(include_path, 'r') as ff:
                            include_con = ff.read()
                            fm.write(include_con)
                else:
                    fm.write(line)
        fm.close()

        fm = open(self.tmp_conf, 'r')
        # 去掉注释行
        with open(self.all_conf, 'w+') as fp:
            for xx in fm.readlines():
                # 判断是否是注释标识符#开头
                if len(re.findall(r'^\s*#', xx)) == 0:
                    fp.write(xx)
        fm.close()

        # 删除临时配置文件
        if os.path.exists(self.tmp_conf):
            os.remove(self.tmp_conf)

    def parse_global_block(self):
        """解析全局配置块 (Global Block)"""
        with open(self.all_conf, 'r') as fp:
            alllines = fp.read()

        # 定义全局指令的正则表达式
        global_directives = {
            'user': r'^\s*user\s+([^;]+);',
            'worker_processes': r'^\s*worker_processes\s+([^;]+);',
            'worker_cpu_affinity': r'^\s*worker_cpu_affinity\s+([^;]+);',
            'error_log': r'^\s*error_log\s+([^;]+);',
            'pid': r'^\s*pid\s+([^;]+);',
            'worker_rlimit_nofile': r'^\s*worker_rlimit_nofile\s+([^;]+);'
        }

        # 解析每个全局指令
        for directive_name, regex in global_directives.items():
            match = re.search(regex, alllines, re.MULTILINE)
            if match:
                self.global_config[directive_name] = match.group(1).strip()

    def parse_events_block(self):
        """解析events配置块 (Events Block)"""
        with open(self.all_conf, 'r') as fp:
            alllines = fp.read()

        # 提取events块内容
        events_regex = r'events\s*\{([^}]*)\}'
        events_match = re.search(events_regex, alllines, re.DOTALL)

        if events_match:
            events_content = events_match.group(1)

            # 定义events指令的正则表达式
            events_directives = {
                'use': r'^\s*use\s+([^;]+);',
                'worker_connections': r'^\s*worker_connections\s+([^;]+);',
                'multi_accept': r'^\s*multi_accept\s+([^;]+);',
                'accept_mutex': r'^\s*accept_mutex\s+([^;]+);'
            }

            # 解析每个events指令
            for directive_name, regex in events_directives.items():
                match = re.search(regex, events_content, re.MULTILINE)
                if match:
                    self.events_config[directive_name] = match.group(1).strip()

    def parse_http_block(self):
        """解析http配置块 (HTTP Block) - 提取http级别的指令"""
        with open(self.all_conf, 'r') as fp:
            alllines = fp.read()

        # 提取http块内容 (注意：这个正则不够完美，但对大多数情况有效)
        http_regex = r'http\s*\{(.*)'
        http_match = re.search(http_regex, alllines, re.DOTALL)

        if http_match:
            # 获取http块的开始位置
            http_start = http_match.start()
            http_content = alllines[http_start:]

            # 定义http指令的正则表达式
            http_directives = {
                'default_type': r'^\s*default_type\s+([^;]+);',
                'sendfile': r'^\s*sendfile\s+([^;]+);',
                'keepalive_timeout': r'^\s*keepalive_timeout\s+([^;]+);',
                'gzip': r'^\s*gzip\s+([^;]+);'
            }

            # 解析每个http指令
            for directive_name, regex in http_directives.items():
                match = re.search(regex, http_content, re.MULTILINE)
                if match:
                    self.http_config[directive_name] = match.group(1).strip()

    def parse_backend_ip(self):
        # 获取后端的poolname和对应的ip，放在一个dict的list里
        with open(self.all_conf, 'r') as fp:
            alllines = fp.read()

            # 获取每个upstream块
            regex_1 = r'upstream\s+([^{ ]+)\s*\{([^}]*)\}'
            upstreams = re.findall(regex_1, alllines, re.DOTALL)

            for up in upstreams:
                poolname = up[0].strip()
                upstream_content = up[1]

                # 检测负载均衡方法
                load_balancing = 'round_robin'  # 默认
                if re.search(r'least_conn\s*;', upstream_content):
                    load_balancing = 'least_conn'
                elif re.search(r'ip_hash\s*;', upstream_content):
                    load_balancing = 'ip_hash'
                elif re.search(r'hash\s+', upstream_content):
                    hash_match = re.search(r'hash\s+([^;]+);', upstream_content)
                    if hash_match:
                        load_balancing = f"hash {hash_match.group(1).strip()}"

                # 获取每个server行的详细信息
                # 匹配完整的server行，包括所有参数
                server_regex = r'server\s+([^\s;]+)([^;]*);'
                servers = re.findall(server_regex, upstream_content)

                server_list = []
                backend_ips = []

                for srv in servers:
                    server_addr = srv[0].strip()
                    params_str = srv[1].strip()

                    # 解析参数
                    server_info = {
                        'address': server_addr
                    }

                    # 提取weight
                    weight_match = re.search(r'weight=(\d+)', params_str)
                    if weight_match:
                        server_info['weight'] = int(weight_match.group(1))

                    # 提取max_fails
                    max_fails_match = re.search(r'max_fails=(\d+)', params_str)
                    if max_fails_match:
                        server_info['max_fails'] = int(max_fails_match.group(1))

                    # 提取fail_timeout
                    fail_timeout_match = re.search(r'fail_timeout=([^\s]+)', params_str)
                    if fail_timeout_match:
                        server_info['fail_timeout'] = fail_timeout_match.group(1)

                    # 检查backup标志
                    if 'backup' in params_str:
                        server_info['backup'] = True

                    # 检查down标志
                    if 'down' in params_str:
                        server_info['down'] = True

                    server_list.append(server_info)
                    backend_ips.append(server_addr)

                # 判断是否有后端的ip设置
                if len(server_list) > 0:
                    pool_data = {
                        'poolname': poolname,
                        'ip': ' '.join(backend_ips),
                        'servers': server_list,
                        'load_balancing': load_balancing
                    }
                    self.backend.append(pool_data)

    def parse_server_block(self):
        flag = False
        serverblock = ''
        num_of_quote = 0

        with open(self.all_conf, 'r') as fp:
            for line in fp.readlines():
                x = line.replace(' ', '')
                if x.startswith('server{'):
                    num_of_quote += 1
                    flag = True
                    serverblock += line
                    continue
                # 发现{，计数加1。发现}，计数减1，直到计数为0
                if flag and '{' in line:
                    num_of_quote += 1

                # 将proxy_pass的别名换成ip
                if flag and 'proxy_pass' in line:
                    r = re.findall(r'proxy_pass\s+https?://([^;/]*)[^;]*;', line)
                    if len(r) > 0:
                        for pool in self.backend:
                            if r[0] == pool['poolname']:
                                line = line.replace(r[0], pool['ip'])

                if flag and num_of_quote != 0:
                    serverblock += line

                if flag and '}' in line:
                    num_of_quote -= 1

                if flag and num_of_quote == 0:
                    self.serverBlock.append(serverblock)
                    flag = False
                    serverblock = ''
                    num_of_quote = 0

        for singleServer in self.serverBlock:
            # TASK_022: 支持多个listen指令
            listen_matches = re.findall(r'listen\s+([^;]+);', singleServer)
            listen_directives = []
            for listen_match in listen_matches:
                listen_directives.append(listen_match.strip())

            # 保持向后兼容，提取第一个listen作为port
            port = listen_directives[0] if listen_directives else ''

            r = re.findall(r'server_name\s+([^;]*);', singleServer)  # server_name只有一个

            # 可能存在没有server_name的情况
            if len(r) > 0:
                servername = r[0]
            else:
                continue

            # 判断servername是否有ip，有ip就不存。比如servername 127.0.0.1这样的配置
            if len(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', servername)) > 0:
                continue

            # TASK_025: 解析root和index指令
            root_match = re.search(r'root\s+([^;]+);', singleServer)
            root = root_match.group(1).strip() if root_match else None

            index_match = re.search(r'index\s+([^;]+);', singleServer)
            index = index_match.group(1).strip() if index_match else None

            # TASK_024: 解析server级别的access_log和error_log
            access_log_match = re.search(r'access_log\s+([^;]+);', singleServer)
            access_log = access_log_match.group(1).strip() if access_log_match else None

            error_log_match = re.search(r'error_log\s+([^;]+);', singleServer)
            error_log = error_log_match.group(1).strip() if error_log_match else None

            # TASK_023: 解析SSL/TLS配置
            ssl_certificate_match = re.search(r'ssl_certificate\s+([^;]+);', singleServer)
            ssl_certificate = ssl_certificate_match.group(1).strip() if ssl_certificate_match else None

            ssl_certificate_key_match = re.search(r'ssl_certificate_key\s+([^;]+);', singleServer)
            ssl_certificate_key = ssl_certificate_key_match.group(1).strip() if ssl_certificate_key_match else None

            ssl_protocols_match = re.search(r'ssl_protocols\s+([^;]+);', singleServer)
            ssl_protocols = ssl_protocols_match.group(1).strip() if ssl_protocols_match else None

            ssl_ciphers_match = re.search(r'ssl_ciphers\s+([^;]+);', singleServer)
            ssl_ciphers = ssl_ciphers_match.group(1).strip() if ssl_ciphers_match else None

            include = ' '.join(re.findall(r'include\s+([^;]*);', singleServer))  # include不止一个

            # TASK_026-030: 增强location块解析
            # TASK_027: 支持location修饰符 (=, ~, ~*, ^~)
            # TASK_028: 支持fastcgi_pass
            # TASK_029: 支持rewrite规则
            # TASK_030: 支持try_files
            locations = self.parse_locations(singleServer)

            # TASK_001: 解析安全头部配置
            security_headers_data = self.parse_security_headers(singleServer)

            # TASK #3: 解析ACL
            acl_data = self.parse_acl(singleServer)

            # TASK #4: 解析认证配置
            auth_data = self.parse_authentication(singleServer)

            server = {
                'port': port,
                'listen': listen_directives,
                'server_name': servername,
                'root': root,
                'index': index,
                'access_log': access_log,
                'error_log': error_log,
                'ssl_certificate': ssl_certificate,
                'ssl_certificate_key': ssl_certificate_key,
                'ssl_protocols': ssl_protocols,
                'ssl_ciphers': ssl_ciphers,
                'include': include,
                'backend': locations
            }

            # 合并所有解析的数据到server字典
            server.update(security_headers_data)
            server.update(acl_data)
            server.update(auth_data)

            self.servers.append(server)

    def parse_security_headers(self, server_block):
        """解析安全相关的HTTP头部配置 (TASK_001)

        支持的安全头部：
        - X-Frame-Options
        - X-Content-Type-Options
        - X-XSS-Protection
        - Content-Security-Policy
        - Strict-Transport-Security
        - Referrer-Policy
        - Permissions-Policy
        - X-Download-Options

        返回格式: {'security_headers': {'X-Frame-Options': 'DENY', ...}}
        """
        security_headers = {}

        # 定义需要匹配的安全头部列表
        security_header_names = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Strict-Transport-Security',
            'Referrer-Policy',
            'Permissions-Policy',
            'X-Download-Options',
            'X-Permitted-Cross-Domain-Policies',
            'Feature-Policy',
            'Expect-CT',
            'Cross-Origin-Embedder-Policy',
            'Cross-Origin-Opener-Policy',
            'Cross-Origin-Resource-Policy'
        ]

        # 首先找出所有 add_header 指令
        # 匹配模式：add_header Header-Name value; 或 add_header Header-Name "value" always;
        # 支持带引号和不带引号的值
        add_header_pattern = r'add_header\s+([A-Za-z-]+)\s+(["\']?)(.+?)\2\s*(?:always)?\s*;'
        all_add_headers = re.findall(add_header_pattern, server_block, re.IGNORECASE | re.MULTILINE)

        # 按header名称分组，保留最后一个出现的值
        header_map = {}
        for match in all_add_headers:
            header_name = match[0]
            header_value = match[2].strip()
            header_map[header_name.lower()] = (header_name, header_value)

        # 从分组中提取安全相关的header
        for security_header in security_header_names:
            security_header_lower = security_header.lower()
            if security_header_lower in header_map:
                actual_header_name, header_value = header_map[security_header_lower]
                security_headers[actual_header_name] = header_value

        return {'security_headers': security_headers} if security_headers else {'security_headers': {}}

    def parse_locations(self, server_block):
        """解析location块，支持proxy_pass, fastcgi_pass, rewrite, try_files"""
        location_list = []

        # 匹配location块 - 支持修饰符 (=, ~, ~*, ^~)
        # 这个正则会匹配整个location块
        location_pattern = r'location\s*(=|~\*?|\^~)?\s*([^{]+)\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        location_matches = re.findall(location_pattern, server_block, re.DOTALL)

        for loc_match in location_matches:
            modifier = loc_match[0].strip() if loc_match[0] else None
            path = loc_match[1].strip()
            content = loc_match[2]

            location_info = {
                'path': path,
                'modifier': modifier
            }

            # TASK_026: 解析proxy_pass
            proxy_pass_match = re.search(r'proxy_pass\s+(https?://[^;]+);', content)
            if proxy_pass_match:
                proxy_pass_url = proxy_pass_match.group(1).strip()
                location_info['proxy_pass'] = proxy_pass_url

                # 提取backend name或IP
                backend_match = re.search(r'https?://([^;/]+)', proxy_pass_url)
                if backend_match:
                    poolname = backend_match.group(1)
                    # 如果不是IP，查找对应的upstream
                    if not re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', poolname):
                        for backend in self.backend:
                            if poolname == backend['poolname']:
                                location_info['backend_ip'] = backend['ip']
                                break
                    else:
                        location_info['backend_ip'] = poolname

                # 保持向后兼容
                location_info['backend_path'] = path

            # TASK_028: 解析fastcgi_pass
            fastcgi_pass_match = re.search(r'fastcgi_pass\s+([^;]+);', content)
            if fastcgi_pass_match:
                location_info['fastcgi_pass'] = fastcgi_pass_match.group(1).strip()

            # TASK_029: 解析rewrite规则
            rewrite_matches = re.findall(r'rewrite\s+([^;]+);', content)
            if rewrite_matches:
                location_info['rewrites'] = [r.strip() for r in rewrite_matches]

            # TASK_030: 解析try_files
            try_files_match = re.search(r'try_files\s+([^;]+);', content)
            if try_files_match:
                location_info['try_files'] = try_files_match.group(1).strip()

            # 解析其他常见指令
            root_match = re.search(r'root\s+([^;]+);', content)
            if root_match:
                location_info['root'] = root_match.group(1).strip()

            index_match = re.search(r'index\s+([^;]+);', content)
            if index_match:
                location_info['index'] = index_match.group(1).strip()

            location_list.append(location_info)

        return location_list

    # TASK #2: Parse rate limiting configuration
    def parse_rate_limiting(self, content):
        """解析速率限制配置"""
        rate_limit_data = {}

        # Parse limit_req_zone (http context)
        limit_req_zone_matches = re.findall(r'limit_req_zone\s+(\$[^\s]+)\s+zone=([^:]+):(\S+)\s+rate=([^;]+);', content)
        if limit_req_zone_matches:
            rate_limit_data['zones'] = []
            for match in limit_req_zone_matches:
                rate_limit_data['zones'].append({
                    'key': match[0],
                    'zone_name': match[1],
                    'size': match[2],
                    'rate': match[3]
                })

        # Parse limit_req (server/location context)
        limit_req_matches = re.findall(r'limit_req\s+zone=([^\s]+)(?:\s+burst=(\d+))?(?:\s+nodelay)?;', content)
        if limit_req_matches:
            rate_limit_data['requests'] = []
            for match in limit_req_matches:
                req_data = {'zone': match[0]}
                if match[1]:
                    req_data['burst'] = int(match[1])
                rate_limit_data['requests'].append(req_data)

        # Parse limit_conn_zone
        limit_conn_zone_matches = re.findall(r'limit_conn_zone\s+(\$[^\s]+)\s+zone=([^:]+):(\S+);', content)
        if limit_conn_zone_matches:
            rate_limit_data['conn_zones'] = []
            for match in limit_conn_zone_matches:
                rate_limit_data['conn_zones'].append({
                    'key': match[0],
                    'zone_name': match[1],
                    'size': match[2]
                })

        # Parse limit_conn
        limit_conn_matches = re.findall(r'limit_conn\s+([^\s]+)\s+(\d+);', content)
        if limit_conn_matches:
            rate_limit_data['connections'] = []
            for match in limit_conn_matches:
                rate_limit_data['connections'].append({
                    'zone': match[0],
                    'number': int(match[1])
                })

        return {'rate_limiting': rate_limit_data} if rate_limit_data else {}

    # TASK #3: Parse access control lists (ACL)
    def parse_acl(self, content):
        """解析访问控制列表"""
        acl_rules = []

        # Parse allow directives
        allow_matches = re.findall(r'allow\s+([^;]+);', content)
        for match in allow_matches:
            acl_rules.append({'action': 'allow', 'address': match.strip()})

        # Parse deny directives
        deny_matches = re.findall(r'deny\s+([^;]+);', content)
        for match in deny_matches:
            acl_rules.append({'action': 'deny', 'address': match.strip()})

        return {'acl': acl_rules} if acl_rules else {}

    # TASK #4: Parse authentication configuration
    def parse_authentication(self, content):
        """解析认证配置"""
        auth_config = {}

        # Parse auth_basic
        auth_basic_match = re.search(r'auth_basic\s+"?([^";]+)"?;', content)
        if auth_basic_match:
            auth_config['auth_basic'] = auth_basic_match.group(1).strip()

        # Parse auth_basic_user_file
        auth_user_file_match = re.search(r'auth_basic_user_file\s+([^;]+);', content)
        if auth_user_file_match:
            auth_config['auth_basic_user_file'] = auth_user_file_match.group(1).strip()

        # Parse auth_request
        auth_request_match = re.search(r'auth_request\s+([^;]+);', content)
        if auth_request_match:
            auth_config['auth_request'] = auth_request_match.group(1).strip()

        # Parse auth_request_set
        auth_request_set_matches = re.findall(r'auth_request_set\s+(\$[^\s]+)\s+([^;]+);', content)
        if auth_request_set_matches:
            auth_config['auth_request_set'] = []
            for match in auth_request_set_matches:
                auth_config['auth_request_set'].append({
                    'variable': match[0],
                    'value': match[1].strip()
                })

        return {'authentication': auth_config} if auth_config else {}

    # TASK #5-7: Parse caching configuration
    def parse_caching(self, content):
        """解析缓存配置"""
        cache_config = {}

        # Parse proxy_cache
        proxy_cache_match = re.search(r'proxy_cache\s+([^;]+);', content)
        if proxy_cache_match:
            cache_config['proxy_cache'] = proxy_cache_match.group(1).strip()

        # Parse proxy_cache_path
        proxy_cache_path_match = re.search(r'proxy_cache_path\s+([^\s]+)(?:\s+levels=([^\s]+))?(?:\s+keys_zone=([^:]+):([^\s]+))?(?:\s+max_size=([^\s]+))?(?:\s+inactive=([^\s;]+))?', content)
        if proxy_cache_path_match:
            cache_config['proxy_cache_path'] = {
                'path': proxy_cache_path_match.group(1),
                'levels': proxy_cache_path_match.group(2) if proxy_cache_path_match.group(2) else None,
                'keys_zone_name': proxy_cache_path_match.group(3) if proxy_cache_path_match.group(3) else None,
                'keys_zone_size': proxy_cache_path_match.group(4) if proxy_cache_path_match.group(4) else None,
                'max_size': proxy_cache_path_match.group(5) if proxy_cache_path_match.group(5) else None,
                'inactive': proxy_cache_path_match.group(6) if proxy_cache_path_match.group(6) else None
            }

        # Parse proxy_cache_valid
        proxy_cache_valid_matches = re.findall(r'proxy_cache_valid\s+([^;]+);', content)
        if proxy_cache_valid_matches:
            cache_config['proxy_cache_valid'] = [m.strip() for m in proxy_cache_valid_matches]

        # Parse proxy_cache_key
        proxy_cache_key_match = re.search(r'proxy_cache_key\s+([^;]+);', content)
        if proxy_cache_key_match:
            cache_config['proxy_cache_key'] = proxy_cache_key_match.group(1).strip()

        # Parse fastcgi_cache
        fastcgi_cache_match = re.search(r'fastcgi_cache\s+([^;]+);', content)
        if fastcgi_cache_match:
            cache_config['fastcgi_cache'] = fastcgi_cache_match.group(1).strip()

        # Parse fastcgi_cache_path
        fastcgi_cache_path_match = re.search(r'fastcgi_cache_path\s+([^\s]+)(?:\s+levels=([^\s]+))?(?:\s+keys_zone=([^:]+):([^\s]+))?', content)
        if fastcgi_cache_path_match:
            cache_config['fastcgi_cache_path'] = {
                'path': fastcgi_cache_path_match.group(1),
                'levels': fastcgi_cache_path_match.group(2) if fastcgi_cache_path_match.group(2) else None,
                'keys_zone_name': fastcgi_cache_path_match.group(3) if fastcgi_cache_path_match.group(3) else None,
                'keys_zone_size': fastcgi_cache_path_match.group(4) if fastcgi_cache_path_match.group(4) else None
            }

        # Parse cache bypass rules
        proxy_cache_bypass_matches = re.findall(r'proxy_cache_bypass\s+([^;]+);', content)
        if proxy_cache_bypass_matches:
            cache_config['proxy_cache_bypass'] = [m.strip() for m in proxy_cache_bypass_matches]

        proxy_no_cache_matches = re.findall(r'proxy_no_cache\s+([^;]+);', content)
        if proxy_no_cache_matches:
            cache_config['proxy_no_cache'] = [m.strip() for m in proxy_no_cache_matches]

        return {'caching': cache_config} if cache_config else {}

    # TASK #8-10: Parse proxy configuration
    def parse_proxy_config(self, content):
        """解析代理配置"""
        proxy_config = {}

        # Parse proxy_set_header
        proxy_headers_matches = re.findall(r'proxy_set_header\s+([^\s]+)\s+([^;]+);', content)
        if proxy_headers_matches:
            proxy_config['proxy_headers'] = {}
            for match in proxy_headers_matches:
                proxy_config['proxy_headers'][match[0]] = match[1].strip()

        # Parse proxy timeouts
        proxy_connect_timeout_match = re.search(r'proxy_connect_timeout\s+([^;]+);', content)
        if proxy_connect_timeout_match:
            if 'proxy_timeouts' not in proxy_config:
                proxy_config['proxy_timeouts'] = {}
            proxy_config['proxy_timeouts']['connect'] = proxy_connect_timeout_match.group(1).strip()

        proxy_read_timeout_match = re.search(r'proxy_read_timeout\s+([^;]+);', content)
        if proxy_read_timeout_match:
            if 'proxy_timeouts' not in proxy_config:
                proxy_config['proxy_timeouts'] = {}
            proxy_config['proxy_timeouts']['read'] = proxy_read_timeout_match.group(1).strip()

        proxy_send_timeout_match = re.search(r'proxy_send_timeout\s+([^;]+);', content)
        if proxy_send_timeout_match:
            if 'proxy_timeouts' not in proxy_config:
                proxy_config['proxy_timeouts'] = {}
            proxy_config['proxy_timeouts']['send'] = proxy_send_timeout_match.group(1).strip()

        # Parse proxy buffering
        proxy_buffering_match = re.search(r'proxy_buffering\s+([^;]+);', content)
        if proxy_buffering_match:
            if 'proxy_buffering' not in proxy_config:
                proxy_config['proxy_buffering'] = {}
            proxy_config['proxy_buffering']['enabled'] = proxy_buffering_match.group(1).strip()

        proxy_buffer_size_match = re.search(r'proxy_buffer_size\s+([^;]+);', content)
        if proxy_buffer_size_match:
            if 'proxy_buffering' not in proxy_config:
                proxy_config['proxy_buffering'] = {}
            proxy_config['proxy_buffering']['buffer_size'] = proxy_buffer_size_match.group(1).strip()

        proxy_buffers_match = re.search(r'proxy_buffers\s+([^;]+);', content)
        if proxy_buffers_match:
            if 'proxy_buffering' not in proxy_config:
                proxy_config['proxy_buffering'] = {}
            proxy_config['proxy_buffering']['buffers'] = proxy_buffers_match.group(1).strip()

        proxy_busy_buffers_size_match = re.search(r'proxy_busy_buffers_size\s+([^;]+);', content)
        if proxy_busy_buffers_size_match:
            if 'proxy_buffering' not in proxy_config:
                proxy_config['proxy_buffering'] = {}
            proxy_config['proxy_buffering']['busy_buffers_size'] = proxy_busy_buffers_size_match.group(1).strip()

        return {'proxy': proxy_config} if proxy_config else {}

    # TASK #11-14: Parse client and performance configuration
    def parse_client_config(self, content):
        """解析客户端配置"""
        client_config = {}

        # Parse client_max_body_size
        client_max_body_size_match = re.search(r'client_max_body_size\s+([^;]+);', content)
        if client_max_body_size_match:
            client_config['client_max_body_size'] = client_max_body_size_match.group(1).strip()

        # Parse timeouts
        timeouts = {}
        client_body_timeout_match = re.search(r'client_body_timeout\s+([^;]+);', content)
        if client_body_timeout_match:
            timeouts['client_body'] = client_body_timeout_match.group(1).strip()

        client_header_timeout_match = re.search(r'client_header_timeout\s+([^;]+);', content)
        if client_header_timeout_match:
            timeouts['client_header'] = client_header_timeout_match.group(1).strip()

        send_timeout_match = re.search(r'send_timeout\s+([^;]+);', content)
        if send_timeout_match:
            timeouts['send'] = send_timeout_match.group(1).strip()

        if timeouts:
            client_config['timeouts'] = timeouts

        # Parse buffers
        buffers = {}
        client_body_buffer_size_match = re.search(r'client_body_buffer_size\s+([^;]+);', content)
        if client_body_buffer_size_match:
            buffers['client_body'] = client_body_buffer_size_match.group(1).strip()

        client_header_buffer_size_match = re.search(r'client_header_buffer_size\s+([^;]+);', content)
        if client_header_buffer_size_match:
            buffers['client_header'] = client_header_buffer_size_match.group(1).strip()

        large_client_header_buffers_match = re.search(r'large_client_header_buffers\s+([^;]+);', content)
        if large_client_header_buffers_match:
            buffers['large_client_header'] = large_client_header_buffers_match.group(1).strip()

        if buffers:
            client_config['buffers'] = buffers

        # Parse open_file_cache
        open_file_cache_match = re.search(r'open_file_cache\s+max=(\d+)(?:\s+inactive=([^\s;]+))?', content)
        if open_file_cache_match:
            file_cache = {
                'max': open_file_cache_match.group(1),
                'inactive': open_file_cache_match.group(2) if open_file_cache_match.group(2) else None
            }

            open_file_cache_valid_match = re.search(r'open_file_cache_valid\s+([^;]+);', content)
            if open_file_cache_valid_match:
                file_cache['valid'] = open_file_cache_valid_match.group(1).strip()

            open_file_cache_min_uses_match = re.search(r'open_file_cache_min_uses\s+([^;]+);', content)
            if open_file_cache_min_uses_match:
                file_cache['min_uses'] = open_file_cache_min_uses_match.group(1).strip()

            open_file_cache_errors_match = re.search(r'open_file_cache_errors\s+([^;]+);', content)
            if open_file_cache_errors_match:
                file_cache['errors'] = open_file_cache_errors_match.group(1).strip()

            client_config['file_cache'] = file_cache

        return {'client_config': client_config} if client_config else {}

    # TASK #15-16: Parse logging configuration
    def parse_logging_config(self, content):
        """解析日志配置"""
        logging_config = {}

        # Parse log_format
        log_format_matches = re.findall(r'log_format\s+([^\s]+)\s+([^;]+);', content, re.DOTALL)
        if log_format_matches:
            logging_config['log_formats'] = {}
            for match in log_format_matches:
                format_name = match[0].strip()
                format_string = match[1].strip().replace('\n', ' ')
                logging_config['log_formats'][format_name] = format_string

        # Parse conditional logging (access_log with if)
        access_log_if_matches = re.findall(r'access_log\s+([^\s]+)(?:\s+([^\s]+))?(?:\s+if=([^\s;]+))?', content)
        if access_log_if_matches:
            logging_config['access_logs'] = []
            for match in access_log_if_matches:
                log_entry = {'path': match[0].strip()}
                if match[1]:
                    log_entry['format'] = match[1].strip()
                if match[2]:
                    log_entry['condition'] = match[2].strip()
                logging_config['access_logs'].append(log_entry)

        return {'logging': logging_config} if logging_config else {}

    # TASK #17-19: Parse map, geo, and split_clients blocks
    def parse_advanced_blocks(self, content):
        """解析高级配置块"""
        advanced_config = {}

        # Parse map blocks
        map_pattern = r'map\s+(\$[^\s]+)\s+(\$[^\s]+)\s*\{([^}]*)\}'
        map_matches = re.findall(map_pattern, content, re.DOTALL)
        if map_matches:
            advanced_config['maps'] = []
            for match in map_matches:
                map_data = {
                    'input': match[0].strip(),
                    'output': match[1].strip(),
                    'mappings': {}
                }

                # Parse mappings inside the map block
                map_content = match[2]
                default_match = re.search(r'default\s+([^;]+);', map_content)
                if default_match:
                    map_data['default'] = default_match.group(1).strip()

                mapping_matches = re.findall(r'([^\s;]+)\s+([^;]+);', map_content)
                for mapping in mapping_matches:
                    if mapping[0] != 'default':
                        map_data['mappings'][mapping[0].strip()] = mapping[1].strip()

                advanced_config['maps'].append(map_data)

        # Parse geo blocks
        geo_pattern = r'geo\s+(\$[^\s]+)\s*\{([^}]*)\}'
        geo_matches = re.findall(geo_pattern, content, re.DOTALL)
        if geo_matches:
            advanced_config['geo_blocks'] = []
            for match in geo_matches:
                geo_data = {
                    'variable': match[0].strip(),
                    'rules': {}
                }

                geo_content = match[1]
                default_match = re.search(r'default\s+([^;]+);', geo_content)
                if default_match:
                    geo_data['default'] = default_match.group(1).strip()

                rule_matches = re.findall(r'([^\s;]+)\s+([^;]+);', geo_content)
                for rule in rule_matches:
                    if rule[0] != 'default':
                        geo_data['rules'][rule[0].strip()] = rule[1].strip()

                advanced_config['geo_blocks'].append(geo_data)

        # Parse split_clients blocks
        split_clients_pattern = r'split_clients\s+"([^"]+)"\s+(\$[^\s]+)\s*\{([^}]*)\}'
        split_clients_matches = re.findall(split_clients_pattern, content, re.DOTALL)
        if split_clients_matches:
            advanced_config['split_clients'] = []
            for match in split_clients_matches:
                split_data = {
                    'seed': match[0].strip(),
                    'variable': match[1].strip(),
                    'splits': {}
                }

                split_content = match[2]
                split_matches = re.findall(r'([^\s]+)\s+([^;]+);', split_content)
                for split in split_matches:
                    split_data['splits'][split[0].strip()] = split[1].strip()

                advanced_config['split_clients'].append(split_data)

        return advanced_config

    def get_all_config(self):
        """获取完整的配置数据 - 包括所有解析功能 (ALL 36 TASKS)"""
        with open(self.all_conf, 'r') as fp:
            alllines = fp.read()

        config = {
            'global': self.global_config,
            'events': self.events_config,
            'http': self.http_config,
            'upstreams': self.backend,
            'servers': self.servers
        }

        # TASK #2: Rate limiting
        rate_limiting = self.parse_rate_limiting(alllines)
        if rate_limiting:
            config.update(rate_limiting)

        # TASK #17-19: Advanced blocks
        advanced_blocks = self.parse_advanced_blocks(alllines)
        if advanced_blocks:
            config.update(advanced_blocks)

        # TASK #5-7: Caching
        caching = self.parse_caching(alllines)
        if caching:
            config.update(caching)

        # TASK #8-10: Proxy config
        proxy = self.parse_proxy_config(alllines)
        if proxy:
            config.update(proxy)

        # TASK #11-14: Client config
        client = self.parse_client_config(alllines)
        if client:
            config.update(client)

        # TASK #15-16: Logging
        logging = self.parse_logging_config(alllines)
        if logging:
            config.update(logging)

        # TASK #31: HTTP/2 module
        http2 = self.parse_http2_module(alllines)
        if http2:
            config.update(http2)

        # TASK #32: Stream module
        stream = self.parse_stream_module(alllines)
        if stream:
            config.update(stream)

        # TASK #33: gRPC module
        grpc = self.parse_grpc_module(alllines)
        if grpc:
            config.update(grpc)

        # TASK #20-24: Validation
        config['validation'] = {
            'syntax': self.validate_syntax(),
            'missing_directives': self.detect_missing_directives(),
            'conflicts': self.detect_conflicts()
        }

        # Note: ACL and auth are now parsed directly in parse_server_block()
        return config

    def find_server_block_content(self, server_name):
        """查找特定server块的内容"""
        for block in self.serverBlock:
            if f'server_name {server_name};' in block or f'server_name  {server_name};' in block:
                return block
        return None

    # TASK #20-24: Validation and Error Handling
    def validate_syntax(self):
        """验证nginx配置语法 (TASK #20)"""
        errors = []
        warnings = []

        try:
            with open(self.all_conf, 'r') as fp:
                content = fp.read()

            # Check for matching braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                errors.append({
                    'type': 'syntax_error',
                    'message': f'Mismatched braces: {open_braces} opening, {close_braces} closing',
                    'severity': 'error'
                })

            # Check for semicolons on directives
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith('#'):
                    continue
                # Skip lines with only braces
                if stripped in ['{', '}']:
                    continue
                # Check if directive line is missing semicolon
                if not stripped.endswith((';', '{', '}')):
                    # Check if it's a block directive
                    block_keywords = ['events', 'http', 'server', 'location', 'upstream', 'map', 'geo', 'split_clients', 'if']
                    is_block = any(stripped.startswith(kw) for kw in block_keywords)
                    if not is_block and len(stripped) > 0:
                        warnings.append({
                            'type': 'missing_semicolon',
                            'line': line_num,
                            'message': f'Possible missing semicolon: {stripped[:50]}',
                            'severity': 'warning'
                        })

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }

        except Exception as e:
            return {
                'valid': False,
                'errors': [{'type': 'parse_error', 'message': str(e), 'severity': 'error'}],
                'warnings': []
            }

    def detect_missing_directives(self):
        """检测缺失的必需指令 (TASK #21)"""
        issues = []

        # Check each server block
        for idx, server in enumerate(self.servers):
            # Check for missing server_name
            if not server.get('server_name') or server['server_name'].strip() == '':
                issues.append({
                    'server': idx,
                    'type': 'missing_directive',
                    'directive': 'server_name',
                    'message': f'Server block {idx} is missing server_name directive',
                    'severity': 'warning'
                })

            # Check for missing listen directive
            if not server.get('listen') or len(server.get('listen', [])) == 0:
                issues.append({
                    'server': idx,
                    'type': 'missing_directive',
                    'directive': 'listen',
                    'message': f'Server block {idx} is missing listen directive',
                    'severity': 'warning'
                })

            # Check locations for missing proxy_pass or root
            for loc_idx, location in enumerate(server.get('backend', [])):
                has_handler = any(k in location for k in ['proxy_pass', 'fastcgi_pass', 'root', 'return', 'rewrite'])
                if not has_handler:
                    issues.append({
                        'server': idx,
                        'location': loc_idx,
                        'path': location.get('path', 'unknown'),
                        'type': 'missing_handler',
                        'message': f'Location "{location.get("path")}" has no handler (proxy_pass, root, etc.)',
                        'severity': 'warning'
                    })

        return issues

    def detect_conflicts(self):
        """检测配置冲突 (TASK #22)"""
        conflicts = []

        # Check for duplicate server_name + listen combinations
        server_map = {}
        for idx, server in enumerate(self.servers):
            server_name = server.get('server_name', '')
            listen_ports = server.get('listen', [])

            for port in listen_ports:
                key = f"{server_name}:{port}"
                if key in server_map:
                    conflicts.append({
                        'type': 'duplicate_server',
                        'server_name': server_name,
                        'listen': port,
                        'servers': [server_map[key], idx],
                        'message': f'Duplicate server_name "{server_name}" on port {port}',
                        'severity': 'error'
                    })
                else:
                    server_map[key] = idx

        # Check for conflicting SSL protocols
        for idx, server in enumerate(self.servers):
            ssl_protocols = server.get('ssl_protocols', '')
            if ssl_protocols:
                # Check for insecure protocols
                if 'SSLv2' in ssl_protocols or 'SSLv3' in ssl_protocols or 'TLSv1 ' in ssl_protocols:
                    conflicts.append({
                        'type': 'insecure_protocol',
                        'server': idx,
                        'server_name': server.get('server_name'),
                        'protocols': ssl_protocols,
                        'message': f'Server uses insecure SSL/TLS protocols: {ssl_protocols}',
                        'severity': 'warning'
                    })

        return conflicts

    def get_detailed_errors(self, error_type='all'):
        """获取详细的错误信息 (TASK #23)"""
        all_errors = {
            'syntax': self.validate_syntax(),
            'missing_directives': self.detect_missing_directives(),
            'conflicts': self.detect_conflicts()
        }

        if error_type == 'all':
            return all_errors
        elif error_type in all_errors:
            return all_errors[error_type]
        else:
            return {'error': 'Invalid error_type specified'}

    def parse_with_error_recovery(self):
        """带错误恢复的解析 (TASK #24)"""
        errors_encountered = []
        partial_config = {
            'global': {},
            'events': {},
            'http': {},
            'upstreams': [],
            'servers': []
        }

        try:
            # Try parsing global config
            try:
                partial_config['global'] = self.global_config
            except Exception as e:
                errors_encountered.append({'section': 'global', 'error': str(e)})

            # Try parsing events config
            try:
                partial_config['events'] = self.events_config
            except Exception as e:
                errors_encountered.append({'section': 'events', 'error': str(e)})

            # Try parsing http config
            try:
                partial_config['http'] = self.http_config
            except Exception as e:
                errors_encountered.append({'section': 'http', 'error': str(e)})

            # Try parsing upstreams
            try:
                partial_config['upstreams'] = self.backend
            except Exception as e:
                errors_encountered.append({'section': 'upstreams', 'error': str(e)})

            # Try parsing servers
            try:
                partial_config['servers'] = self.servers
            except Exception as e:
                errors_encountered.append({'section': 'servers', 'error': str(e)})

            return {
                'success': len(errors_encountered) == 0,
                'config': partial_config,
                'errors': errors_encountered
            }

        except Exception as e:
            return {
                'success': False,
                'config': partial_config,
                'errors': errors_encountered + [{'section': 'general', 'error': str(e)}]
            }

    # TASK #31-33: Module Support
    def parse_http2_module(self, content):
        """解析HTTP/2模块配置 (TASK #31)"""
        http2_config = {}

        # Parse http2 directive
        http2_match = re.search(r'http2\s+(on|off);', content)
        if http2_match:
            http2_config['http2'] = http2_match.group(1)

        # Parse http2_push
        http2_push_matches = re.findall(r'http2_push\s+([^;]+);', content)
        if http2_push_matches:
            http2_config['http2_push'] = [m.strip() for m in http2_push_matches]

        # Parse http2_push_preload
        http2_push_preload_match = re.search(r'http2_push_preload\s+(on|off);', content)
        if http2_push_preload_match:
            http2_config['http2_push_preload'] = http2_push_preload_match.group(1)

        # Parse http2_max_field_size
        http2_max_field_match = re.search(r'http2_max_field_size\s+([^;]+);', content)
        if http2_max_field_match:
            http2_config['http2_max_field_size'] = http2_max_field_match.group(1).strip()

        # Parse http2_max_header_size
        http2_max_header_match = re.search(r'http2_max_header_size\s+([^;]+);', content)
        if http2_max_header_match:
            http2_config['http2_max_header_size'] = http2_max_header_match.group(1).strip()

        return {'http2': http2_config} if http2_config else {}

    def parse_stream_module(self, content):
        """解析Stream模块配置 (TASK #32)"""
        stream_config = {'servers': []}

        # Parse stream block - improved pattern to handle nested braces
        # First, find the stream block start
        stream_start = content.find('stream {')
        if stream_start == -1:
            return {}

        # Count braces to find the matching closing brace
        brace_count = 0
        stream_end = -1
        for i in range(stream_start, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    stream_end = i + 1
                    break

        if stream_end == -1:
            return {}

        stream_content = content[stream_start:stream_end]

        if stream_content:
            # Parse upstream blocks within stream
            upstream_pattern = r'upstream\s+([^\s{]+)\s*\{([^}]*)\}'
            upstreams = re.findall(upstream_pattern, stream_content, re.DOTALL)

            stream_upstreams = []
            for up_name, up_content in upstreams:
                servers = re.findall(r'server\s+([^\s;]+)(?:\s+([^;]*))?;', up_content)
                server_list = []
                for srv_addr, srv_params in servers:
                    server_info = {'address': srv_addr.strip()}
                    if srv_params:
                        if 'weight' in srv_params:
                            weight_match = re.search(r'weight=(\d+)', srv_params)
                            if weight_match:
                                server_info['weight'] = int(weight_match.group(1))
                    server_list.append(server_info)

                stream_upstreams.append({
                    'name': up_name.strip(),
                    'servers': server_list
                })

            # Parse server blocks within stream
            server_pattern = r'server\s*\{([^}]*)\}'
            servers = re.findall(server_pattern, stream_content, re.DOTALL)

            for server_content in servers:
                server_info = {}

                listen_match = re.search(r'listen\s+([^;]+);', server_content)
                if listen_match:
                    server_info['listen'] = listen_match.group(1).strip()

                proxy_pass_match = re.search(r'proxy_pass\s+([^;]+);', server_content)
                if proxy_pass_match:
                    server_info['proxy_pass'] = proxy_pass_match.group(1).strip()

                proxy_timeout_match = re.search(r'proxy_timeout\s+([^;]+);', server_content)
                if proxy_timeout_match:
                    server_info['proxy_timeout'] = proxy_timeout_match.group(1).strip()

                stream_config['servers'].append(server_info)

        if stream_upstreams:
            stream_config['upstreams'] = stream_upstreams

        return {'stream': stream_config} if stream_config['servers'] or stream_config.get('upstreams') else {}

    def parse_grpc_module(self, content):
        """解析gRPC模块配置 (TASK #33)"""
        grpc_locations = []

        # Find all locations with grpc directives
        location_pattern = r'location\s+([^\{]+)\{([^\}]*grpc[^\}]*)\}'
        location_matches = re.findall(location_pattern, content, re.DOTALL)

        for path, loc_content in location_matches:
            grpc_config = {'path': path.strip()}

            # Parse grpc_pass
            grpc_pass_match = re.search(r'grpc_pass\s+([^;]+);', loc_content)
            if grpc_pass_match:
                grpc_config['grpc_pass'] = grpc_pass_match.group(1).strip()

            # Parse grpc_set_header
            grpc_headers = re.findall(r'grpc_set_header\s+([^\s]+)\s+([^;]+);', loc_content)
            if grpc_headers:
                grpc_config['grpc_headers'] = {h[0]: h[1].strip() for h in grpc_headers}

            # Parse grpc timeouts
            grpc_connect_timeout = re.search(r'grpc_connect_timeout\s+([^;]+);', loc_content)
            if grpc_connect_timeout:
                grpc_config['grpc_connect_timeout'] = grpc_connect_timeout.group(1).strip()

            grpc_read_timeout = re.search(r'grpc_read_timeout\s+([^;]+);', loc_content)
            if grpc_read_timeout:
                grpc_config['grpc_read_timeout'] = grpc_read_timeout.group(1).strip()

            grpc_send_timeout = re.search(r'grpc_send_timeout\s+([^;]+);', loc_content)
            if grpc_send_timeout:
                grpc_config['grpc_send_timeout'] = grpc_send_timeout.group(1).strip()

            # Parse grpc SSL
            grpc_ssl_cert = re.search(r'grpc_ssl_certificate\s+([^;]+);', loc_content)
            if grpc_ssl_cert:
                grpc_config['grpc_ssl_certificate'] = grpc_ssl_cert.group(1).strip()

            grpc_ssl_cert_key = re.search(r'grpc_ssl_certificate_key\s+([^;]+);', loc_content)
            if grpc_ssl_cert_key:
                grpc_config['grpc_ssl_certificate_key'] = grpc_ssl_cert_key.group(1).strip()

            grpc_locations.append(grpc_config)

        return {'grpc_locations': grpc_locations} if grpc_locations else {}


def main():
    """CLI tool entry point (TASK #34-36)"""
    import sys
    import json
    import argparse

    parser = argparse.ArgumentParser(
        description='nginxparser - Comprehensive nginx configuration parser',
        prog='nginxparser'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse nginx configuration file')
    parse_parser.add_argument('config_file', help='Path to nginx configuration file')
    parse_parser.add_argument('--output', '-o', choices=['json', 'yaml', 'toml', 'xml'],
                             default='json', help='Output format (default: json)')
    parse_parser.add_argument('--pretty', '-p', action='store_true',
                             help='Pretty print output')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate nginx configuration')
    validate_parser.add_argument('config_file', help='Path to nginx configuration file')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query specific directives')
    query_parser.add_argument('config_file', help='Path to nginx configuration file')
    query_parser.add_argument('--directive', '-d', help='Directive to query')
    query_parser.add_argument('--server', '-s', help='Filter by server name')
    query_parser.add_argument('--location', '-l', help='Filter by location path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'parse':
        try:
            nginx = NGINX(args.config_file)
            config = nginx.get_all_config()

            if args.output == 'json':
                if args.pretty:
                    print(json.dumps(config, indent=2, default=str))
                else:
                    print(json.dumps(config, default=str))
            elif args.output == 'yaml':
                try:
                    import yaml
                    print(yaml.dump(config, default_flow_style=False))
                except ImportError:
                    print("Error: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
                    sys.exit(1)
            elif args.output == 'toml':
                try:
                    import tomli_w
                    print(tomli_w.dumps(config))
                except ImportError:
                    print("Error: tomli_w not installed. Install with: pip install tomli_w", file=sys.stderr)
                    sys.exit(1)
            elif args.output == 'xml':
                import xml.etree.ElementTree as ET
                root = ET.Element('nginx')
                def dict_to_xml(parent, data):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            child = ET.SubElement(parent, str(key))
                            dict_to_xml(child, value)
                    elif isinstance(data, list):
                        for item in data:
                            item_elem = ET.SubElement(parent, 'item')
                            dict_to_xml(item_elem, item)
                    else:
                        parent.text = str(data)
                dict_to_xml(root, config)
                tree = ET.ElementTree(root)
                ET.indent(tree, space='  ')
                tree.write(sys.stdout.buffer, encoding='utf-8', xml_declaration=True)
                print()

            sys.exit(0)
        except Exception as e:
            print(f"Error parsing configuration: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'validate':
        try:
            nginx = NGINX(args.config_file)
            print(f"✓ Configuration is valid: {args.config_file}")
            print(f"  - Servers: {len(nginx.servers)}")
            print(f"  - Upstreams: {len(nginx.backend)}")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Configuration validation failed: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'query':
        try:
            nginx = NGINX(args.config_file)
            config = nginx.get_all_config()

            # Filter by server if specified
            if args.server:
                config['servers'] = [s for s in config['servers'] if args.server in s.get('server_name', '')]

            # Filter by location if specified
            if args.location:
                for server in config['servers']:
                    server['backend'] = [l for l in server.get('backend', []) if args.location in l.get('path', '')]

            # Query specific directive
            if args.directive:
                result = {}
                for server in config['servers']:
                    if args.directive in server:
                        result[server['server_name']] = server[args.directive]
                print(json.dumps(result, indent=2))
            else:
                print(json.dumps(config, indent=2, default=str))

            sys.exit(0)
        except Exception as e:
            print(f"Error querying configuration: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
