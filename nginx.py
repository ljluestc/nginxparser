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

            self.servers.append(server)

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


