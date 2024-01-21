

from builtin_redis import BuiltinRedis
from redis import Redis

redis_server = BuiltinRedis(port=16379)
redis_server.start()

r = Redis(port=16379)
r.set('foo', 'bar')
if r.get('foo') == b'bar':
    print('BuiltinRedis works.')
redis_server.stop()

