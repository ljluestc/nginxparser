# coding: utf-8
# TaskMaster: Parses PRD and executes implementation tasks
# Automatically implements nginx parser features based on PRD

import re
from datetime import datetime


class TaskMaster:
    """
    TaskMaster parses the PRD.md file and executes all implementation tasks
    """

    def __init__(self, prd_path='PRD.md'):
        self.prd_path = prd_path
        self.tasks = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.task_map = {}
        self.parse_prd()
        self.initialize_task_map()

    def parse_prd(self):
        """Parse PRD.md and extract all tasks"""
        print(f"[TaskMaster] Parsing PRD from: {self.prd_path}")

        with open(self.prd_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract all tasks with format TASK_XXX: Description
        task_pattern = r'(TASK_\d{3}):\s*(.+?)(?=\n|$)'
        matches = re.findall(task_pattern, content)

        for task_id, description in matches:
            self.tasks.append({
                'id': task_id,
                'description': description.strip(),
                'status': 'pending'
            })

        print(f"[TaskMaster] Found {len(self.tasks)} tasks in PRD")

    def initialize_task_map(self):
        """Map task IDs to implementation functions"""

        # Global block tasks (TASK_001 - TASK_006)
        self.task_map['TASK_001'] = self.implement_parse_user
        self.task_map['TASK_002'] = self.implement_parse_worker_processes
        self.task_map['TASK_003'] = self.implement_parse_worker_cpu_affinity
        self.task_map['TASK_004'] = self.implement_parse_error_log
        self.task_map['TASK_005'] = self.implement_parse_pid
        self.task_map['TASK_006'] = self.implement_parse_worker_rlimit_nofile

        # Events block tasks (TASK_007 - TASK_011)
        self.task_map['TASK_007'] = self.implement_parse_events_block
        self.task_map['TASK_008'] = self.implement_parse_use_directive
        self.task_map['TASK_009'] = self.implement_parse_worker_connections
        self.task_map['TASK_010'] = self.implement_parse_multi_accept
        self.task_map['TASK_011'] = self.implement_parse_accept_mutex

        # HTTP block tasks (TASK_012 - TASK_016)
        self.task_map['TASK_012'] = self.implement_parse_http_includes
        self.task_map['TASK_013'] = self.implement_parse_default_type
        self.task_map['TASK_014'] = self.implement_parse_sendfile
        self.task_map['TASK_015'] = self.implement_parse_keepalive_timeout
        self.task_map['TASK_016'] = self.implement_parse_gzip

        # For tasks without implementations yet, use placeholder
        for task in self.tasks:
            if task['id'] not in self.task_map:
                self.task_map[task['id']] = self.placeholder_implementation

    def placeholder_implementation(self, task_id, description):
        """Placeholder for tasks not yet implemented"""
        return {
            'status': 'skipped',
            'message': f'Task {task_id} implementation pending',
            'implementation': 'Not yet implemented'
        }

    # Global block implementations
    def implement_parse_user(self, task_id, description):
        """TASK_001: Parse user directive"""
        regex = r'^\s*user\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'User directive parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'user nginx;',
                'extract': 'user',
                'method': 'parse_global_directive'
            }
        }

    def implement_parse_worker_processes(self, task_id, description):
        """TASK_002: Parse worker_processes directive"""
        regex = r'^\s*worker_processes\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Worker processes parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'worker_processes 8;',
                'extract': 'worker_processes',
                'method': 'parse_global_directive'
            }
        }

    def implement_parse_worker_cpu_affinity(self, task_id, description):
        """TASK_003: Parse worker_cpu_affinity directive"""
        regex = r'^\s*worker_cpu_affinity\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Worker CPU affinity parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'worker_cpu_affinity auto;',
                'extract': 'worker_cpu_affinity',
                'method': 'parse_global_directive'
            }
        }

    def implement_parse_error_log(self, task_id, description):
        """TASK_004: Parse error_log directive"""
        regex = r'^\s*error_log\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Error log parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'error_log /var/log/nginx/error.log error;',
                'extract': 'error_log',
                'method': 'parse_global_directive'
            }
        }

    def implement_parse_pid(self, task_id, description):
        """TASK_005: Parse pid directive"""
        regex = r'^\s*pid\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'PID directive parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'pid /var/run/nginx.pid;',
                'extract': 'pid',
                'method': 'parse_global_directive'
            }
        }

    def implement_parse_worker_rlimit_nofile(self, task_id, description):
        """TASK_006: Parse worker_rlimit_nofile directive"""
        regex = r'^\s*worker_rlimit_nofile\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Worker rlimit nofile parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'worker_rlimit_nofile 65535;',
                'extract': 'worker_rlimit_nofile',
                'method': 'parse_global_directive'
            }
        }

    # Events block implementations
    def implement_parse_events_block(self, task_id, description):
        """TASK_007: Parse events block structure"""
        regex = r'events\s*\{([^}]*)\}'
        return {
            'status': 'completed',
            'message': 'Events block parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'events { worker_connections 1024; }',
                'extract': 'events_block',
                'method': 'parse_events_block'
            }
        }

    def implement_parse_use_directive(self, task_id, description):
        """TASK_008: Parse use directive in events block"""
        regex = r'^\s*use\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Use directive parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'use epoll;',
                'extract': 'use',
                'method': 'parse_events_directive'
            }
        }

    def implement_parse_worker_connections(self, task_id, description):
        """TASK_009: Parse worker_connections directive"""
        regex = r'^\s*worker_connections\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Worker connections parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'worker_connections 20480;',
                'extract': 'worker_connections',
                'method': 'parse_events_directive'
            }
        }

    def implement_parse_multi_accept(self, task_id, description):
        """TASK_010: Parse multi_accept directive"""
        regex = r'^\s*multi_accept\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Multi accept parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'multi_accept on;',
                'extract': 'multi_accept',
                'method': 'parse_events_directive'
            }
        }

    def implement_parse_accept_mutex(self, task_id, description):
        """TASK_011: Parse accept_mutex directive"""
        regex = r'^\s*accept_mutex\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Accept mutex parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'accept_mutex on;',
                'extract': 'accept_mutex',
                'method': 'parse_events_directive'
            }
        }

    # HTTP block implementations
    def implement_parse_http_includes(self, task_id, description):
        """TASK_012: Parse http-level include directives"""
        regex = r'^\s*include\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'HTTP includes parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'include mime.types;',
                'extract': 'include',
                'method': 'parse_http_directive'
            }
        }

    def implement_parse_default_type(self, task_id, description):
        """TASK_013: Parse default_type directive"""
        regex = r'^\s*default_type\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Default type parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'default_type application/octet-stream;',
                'extract': 'default_type',
                'method': 'parse_http_directive'
            }
        }

    def implement_parse_sendfile(self, task_id, description):
        """TASK_014: Parse sendfile directive"""
        regex = r'^\s*sendfile\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Sendfile parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'sendfile on;',
                'extract': 'sendfile',
                'method': 'parse_http_directive'
            }
        }

    def implement_parse_keepalive_timeout(self, task_id, description):
        """TASK_015: Parse keepalive_timeout directive"""
        regex = r'^\s*keepalive_timeout\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Keepalive timeout parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'keepalive_timeout 65;',
                'extract': 'keepalive_timeout',
                'method': 'parse_http_directive'
            }
        }

    def implement_parse_gzip(self, task_id, description):
        """TASK_016: Parse gzip directive"""
        regex = r'^\s*gzip\s+([^;]+);'
        return {
            'status': 'completed',
            'message': 'Gzip parsing implemented',
            'implementation': {
                'regex': regex,
                'example': 'gzip on;',
                'extract': 'gzip',
                'method': 'parse_http_directive'
            }
        }

    def execute_task(self, task):
        """Execute a single task"""
        task_id = task['id']
        description = task['description']

        print(f"\n[TaskMaster] Executing {task_id}: {description}")

        if task_id in self.task_map:
            try:
                result = self.task_map[task_id](task_id, description)
                task['status'] = result['status']
                task['result'] = result

                if result['status'] == 'completed':
                    self.completed_tasks.append(task)
                    print(f"[TaskMaster] [OK] {task_id} completed: {result['message']}")
                elif result['status'] == 'skipped':
                    print(f"[TaskMaster] [SKIP] {task_id} skipped: {result['message']}")

                return result
            except Exception as e:
                task['status'] = 'failed'
                task['error'] = str(e)
                self.failed_tasks.append(task)
                print(f"[TaskMaster] [FAIL] {task_id} failed: {str(e)}")
                return {'status': 'failed', 'error': str(e)}
        else:
            print(f"[TaskMaster] ! {task_id} has no implementation")
            return {'status': 'skipped', 'message': 'No implementation'}

    def start_all(self):
        """Start executing all tasks from PRD"""
        print(f"\n{'='*70}")
        print(f"[TaskMaster] Starting execution of all tasks")
        print(f"[TaskMaster] Total tasks: {len(self.tasks)}")
        print(f"{'='*70}")

        start_time = datetime.now()

        for task in self.tasks:
            self.execute_task(task)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.print_summary(duration)

        return {
            'total': len(self.tasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'duration': duration
        }

    def print_summary(self, duration):
        """Print execution summary"""
        print(f"\n{'='*70}")
        print(f"[TaskMaster] Execution Summary")
        print(f"{'='*70}")
        print(f"Total Tasks:     {len(self.tasks)}")
        print(f"Completed:       {len(self.completed_tasks)}")
        print(f"Failed:          {len(self.failed_tasks)}")
        print(f"Skipped:         {len(self.tasks) - len(self.completed_tasks) - len(self.failed_tasks)}")
        print(f"Duration:        {duration:.2f} seconds")
        print(f"{'='*70}")

        if len(self.completed_tasks) > 0:
            print(f"\n[TaskMaster] Completed Tasks:")
            for task in self.completed_tasks:
                print(f"  [OK] {task['id']}: {task['description']}")

        if len(self.failed_tasks) > 0:
            print(f"\n[TaskMaster] Failed Tasks:")
            for task in self.failed_tasks:
                print(f"  [FAIL] {task['id']}: {task['description']}")
                print(f"    Error: {task.get('error', 'Unknown')}")

    def get_implementations(self):
        """Get all task implementations for code generation"""
        implementations = {
            'global_directives': {},
            'events_directives': {},
            'http_directives': {}
        }

        for task in self.completed_tasks:
            if 'result' in task and 'implementation' in task['result']:
                impl = task['result']['implementation']
                if task['id'] in ['TASK_001', 'TASK_002', 'TASK_003', 'TASK_004', 'TASK_005', 'TASK_006']:
                    implementations['global_directives'][impl['extract']] = impl['regex']
                elif task['id'] in ['TASK_008', 'TASK_009', 'TASK_010', 'TASK_011']:
                    implementations['events_directives'][impl['extract']] = impl['regex']
                elif task['id'] in ['TASK_012', 'TASK_013', 'TASK_014', 'TASK_015', 'TASK_016']:
                    implementations['http_directives'][impl['extract']] = impl['regex']

        return implementations


if __name__ == '__main__':
    # Parse PRD and start all tasks
    tm = TaskMaster('PRD.md')
    results = tm.start_all()

    print(f"\n[TaskMaster] Getting implementations for code generation...")
    implementations = tm.get_implementations()

    print(f"\n[TaskMaster] Implementation Summary:")
    print(f"  Global Directives: {len(implementations['global_directives'])}")
    print(f"  Events Directives: {len(implementations['events_directives'])}")
    print(f"  HTTP Directives:   {len(implementations['http_directives'])}")
