import copy
import importlib.resources
import tempfile
import shutil
import os
import platform
import subprocess

DEFAULT_CONF = {
    'activerehashing': 'yes',
    'always-show-logo': 'yes',
    'aof-load-truncated': 'yes',
    'aof-rewrite-incremental-fsync': 'yes',
    'aof-use-rdb-preamble': 'yes',
    'appendfilename': '"appendonly.aof"',
    'appendfsync': 'everysec',
    'appendonly': 'no',
    'auto-aof-rewrite-min-size': '64mb',
    'auto-aof-rewrite-percentage': '100',
    'bind': '127.0.0.1',
    'client-output-buffer-limit': [   'normal 0 0 0',
                                      'replica 256mb 64mb 60',
                                      'pubsub 32mb 8mb 60'],
    'databases': '16',
    'dbfilename': 'dump.rdb',
    'dir': './',
    'dynamic-hz': 'yes',
    'hash-max-ziplist-entries': '512',
    'hash-max-ziplist-value': '64',
    'hll-sparse-max-bytes': '3000',
    'hz': '10',
    'latency-monitor-threshold': '0',
    'lazyfree-lazy-eviction': 'no',
    'lazyfree-lazy-expire': 'no',
    'lazyfree-lazy-server-del': 'no',
    'list-compress-depth': '0',
    'list-max-ziplist-size': '-2',
    'logfile': '""',
    'loglevel': 'notice',
    'lua-time-limit': '5000',
    'no-appendfsync-on-rewrite': 'no',
    'notify-keyspace-events': '""',
    'port': '6379',
    'protected-mode': 'yes',
    'rdb-save-incremental-fsync': 'yes',
    'rdbchecksum': 'yes',
    'rdbcompression': 'yes',
    'repl-disable-tcp-nodelay': 'no',
    'repl-diskless-sync': 'no',
    'repl-diskless-sync-delay': '5',
    'replica-lazy-flush': 'no',
    'replica-priority': '100',
    'replica-read-only': 'yes',
    'replica-serve-stale-data': 'yes',
    'save': ['900 1', '300 10', '60 10000'],
    'set-max-intset-entries': '512',
    'slowlog-log-slower-than': '10000',
    'slowlog-max-len': '128',
    'stop-writes-on-bgsave-error': 'yes',
    'stream-node-max-bytes': '4096',
    'stream-node-max-entries': '100',
    'tcp-backlog': '511',
    'tcp-keepalive': '300',
    'timeout': '0',
    'zset-max-ziplist-entries': '128',
    'zset-max-ziplist-value': '64'
}

QUOTED_KEYS = [
    'notify-keyspace-events',
    'logfile', 'appendfilename',

]
class BuiltinRedis:
    def __init__(self, port=16379, bind='127.0.0.1', dbfilename='builtin_redis_dump.rdb'):
        self.redis_process = None
        self.conf = copy.deepcopy(DEFAULT_CONF)
        self.temp_root = None
        self.set_conf('port', port)
        self.set_conf('bind', bind)
        self.set_conf('dbfilename', dbfilename)

    def get_platform_name(self):
        system = platform.system().lower()
        machine = platform.machine().lower()
        arch = 'unknown'
        if machine in ['amd64']:
            arch = machine
        return '{}_{}'.format(system, arch)

    def get_bin_name(self):
        system = platform.system().lower()
        if system == 'windows':
            return 'redis-server.exe'
        else:
            return 'redis-server'

    def prepare_redis_bin(self):
        self.temp_root = tempfile.mkdtemp(prefix="builtin_redis")
        root = importlib.resources.files('builtin_redis')
        target = root.joinpath('bin', self.get_platform_name(),  self.get_bin_name())

        with importlib.resources.as_file(target) as taret_path:
            name = target.name
            redis_bin = os.path.join(self.temp_root, name)
            shutil.copy2(taret_path, redis_bin)

        conf_name = 'builtin_redis.conf'
        conf_path = os.path.join(self.temp_root, conf_name)
        with open(conf_path, 'w') as f:
            f.write(self.get_conf_content())
            f.flush()
        return redis_bin, conf_path

    def set_conf(self, key, value):
        if isinstance(value, bool):
            formated_val = 'yes' if value == True else 'no'
        elif isinstance(value, (int, float)):
            formated_val = '{}'.format(value)
        elif isinstance(value, (list, tuple)):
            formated_val = []
            for it in value:
                formated_val.append('{}'.format(it))
        elif isinstance(value, (str)):
            formated_val = value
        else:
            raise Exception("No supported value type: {}".format(type(value)))
        if key in QUOTED_KEYS:
            formated_val = '"{}"'.format(formated_val)
        self.conf[key] = formated_val


    def get_conf_content(self):
        content = []
        for key, value in self.conf.items():
            if isinstance(value, (str, int)):
                content.append('{} {}'.format(key, value))
            elif isinstance(value, (list, tuple)):
                for itvalue in value:
                    content.append('{} {}'.format(key, itvalue))
        return '\n'.join(content)


    def start(self):
        if self.redis_process != None:
            return
        redis_bin, redis_confpath = self.prepare_redis_bin()
        self.redis_process = subprocess.Popen([redis_bin, redis_confpath], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            outs, errs = self.redis_process.communicate(timeout=3)
            self.redis_process.kill()
            self.redis_process = None
            raise Exception('BuiltRedis Start Failed.')
        except subprocess.TimeoutExpired:
            return


    def stop(self):
        if self.redis_process != None:
            self.redis_process.kill()
            self.redis_process.wait(3)
            self.redis_process = None

        if self.temp_root != None:
            # clear temp directory content
            try:
                shutil.rmtree(self.temp_root)
                self.temp_root = None
            except Exception as e:
                # ignore
                pass
