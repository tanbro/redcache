from random import randint, random
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from redis import Redis

from redcache import FifoPolicy, LfuPolicy, LruPolicy, MruPolicy, RedCache, RrPolicy

REDIS_URL = "redis://"


def _echo(x):
    return x


class BasicTest(TestCase):
    maxsize = 8
    redis_factory = lambda: Redis.from_url(REDIS_URL)  # noqa: E731
    caches = {
        "lru": RedCache(__name__, LruPolicy, redis_factory=redis_factory, maxsize=maxsize),
        "mru": RedCache(__name__, MruPolicy, redis_factory=redis_factory, maxsize=maxsize),
        "rr": RedCache(__name__, RrPolicy, redis_factory=redis_factory, maxsize=maxsize),
        "fifo": RedCache(__name__, FifoPolicy, redis_factory=redis_factory, maxsize=maxsize),
        "lfu": RedCache(__name__, LfuPolicy, redis_factory=redis_factory, maxsize=maxsize),
    }

    def setup(self):
        for cache in self.caches.values():
            cache.policy.purge()

    def tearDown(self):
        for cache in self.caches.values():
            cache.policy.purge()

    def test_basic(self):
        for cache in self.caches.values():

            @cache
            def echo(x):
                return _echo(x)

            # mock hit
            for i in range(cache.maxsize):
                with (
                    patch.object(cache, "exec_get_script", return_value=cache.serialize_return_value(i)) as mock_get,
                    patch.object(cache, "exec_put_script") as mock_put,
                ):
                    echo(i)
                    mock_get.assert_called_once()
                    mock_put.assert_not_called()

            # mock not hit
            for i in range(cache.maxsize):
                with (
                    patch.object(cache, "exec_get_script", return_value=None) as mock_get,
                    patch.object(cache, "exec_put_script") as mock_put,
                ):
                    echo(i)
                    mock_get.assert_called_once()
                    mock_put.assert_called_once()

            # first run, fill the cache to max size. then second run, to hit the cache
            for i in range(cache.maxsize):
                self.assertEqual(_echo(i), echo(i))
                self.assertEqual(i + 1, cache.policy.size)
                with patch.object(cache, "exec_put_script") as mock_put:
                    self.assertEqual(i, echo(i))
                    mock_put.assert_not_called()
            self.assertEqual(cache.maxsize, cache.policy.size)

    def test_oversize(self):
        for cache in self.caches.values():

            @cache
            def echo(x):
                return _echo(x)

            for i in range(cache.maxsize):
                self.assertEqual(_echo(i), echo(i))
            self.assertEqual(cache.maxsize, cache.policy.size)
            # assert not hit
            with patch.object(cache, "exec_put_script") as mock_put:
                v = random()
                self.assertEqual(echo(v), v)
                mock_put.assert_called_once()
            # an actual put, then assert max size
            self.assertEqual(echo(v), v)
            self.assertEqual(cache.maxsize, cache.policy.size)

    def test_str(self):
        for cache in self.caches.values():

            @cache
            def echo(x):
                return _echo(x)

            size = randint(1, cache.maxsize)
            values = [uuid4().hex for _ in range(size)]
            for v in values:
                self.assertEqual(_echo(v), echo(v))
            self.assertEqual(size, cache.policy.size)
            for v in values:
                self.assertEqual(v, echo(v))
            self.assertEqual(size, cache.policy.size)

    def test_lru(self):
        cache = self.caches["lru"]

        @cache
        def echo(x):
            return _echo(x)

        for x in range(self.maxsize):
            self.assertEqual(_echo(x), echo(x))

        echo(self.maxsize)

        k0, k1 = cache.policy.calc_keys()
        rc = cache.get_redis_client()

        card = rc.zcard(k0)
        members = rc.zrange(k0, 0, card - 1)
        values = [cache.deserialize_return_value(x) for x in rc.hmget(k1, members)]  # type: ignore
        self.assertListEqual(sorted(values), list(range(1, self.maxsize + 1)))

    def test_mru(self):
        cache = self.caches["mru"]

        @cache
        def echo(x):
            return _echo(x)

        for x in range(self.maxsize):
            self.assertEqual(_echo(x), echo(x))

        echo(self.maxsize)

        k0, k1 = cache.policy.calc_keys()
        rc = cache.get_redis_client()

        card = rc.zcard(k0)
        members = rc.zrange(k0, 0, card - 1)
        values = [cache.deserialize_return_value(x) for x in rc.hmget(k1, members)]  # type: ignore
        self.assertListEqual(sorted(values), list(range(self.maxsize - 1)) + [self.maxsize])

    def test_fifo(self):
        cache = self.caches["fifo"]

        @cache
        def echo(x):
            return _echo(x)

        for x in range(self.maxsize):
            self.assertEqual(_echo(x), echo(x))

        for _ in range(self.maxsize):
            v = randint(0, self.maxsize - 1)
            echo(v)

        echo(self.maxsize)

        k0, k1 = cache.policy.calc_keys()
        rc = cache.get_redis_client()

        card = rc.zcard(k0)
        members = rc.zrange(k0, 0, card - 1)
        values = [cache.deserialize_return_value(x) for x in rc.hmget(k1, members)]  # type: ignore
        self.assertListEqual(sorted(values), list(range(1, self.maxsize)) + [self.maxsize])

    def test_lfu(self):
        cache = self.caches["lfu"]

        @cache
        def echo(x):
            return _echo(x)

        for x in range(self.maxsize):
            self.assertEqual(_echo(x), echo(x))

        v = randint(0, self.maxsize - 1)
        for i in range(self.maxsize):
            if i != v:
                echo(i)

        echo(self.maxsize)

        k0, k1 = cache.policy.calc_keys()
        rc = cache.get_redis_client()

        card = rc.zcard(k0)
        members = rc.zrange(k0, 0, card - 1)
        values = [cache.deserialize_return_value(x) for x in rc.hmget(k1, members)]  # type: ignore
        self.assertListEqual(sorted(values), list(range(0, v)) + list(range(v + 1, self.maxsize + 1)))

    def test_rr(self):
        cache = self.caches["rr"]

        @cache
        def echo(x):
            return _echo(x)

        for x in range(self.maxsize):
            self.assertEqual(_echo(x), echo(x))

        for _ in range(self.maxsize):
            v = randint(0, self.maxsize - 1)
            echo(v)

        echo(self.maxsize)

        k0, k1 = cache.policy.calc_keys()
        rc = cache.get_redis_client()

        members = rc.smembers(k0)
        values = [cache.deserialize_return_value(x) for x in rc.hmget(k1, members)]  # type: ignore
        self.assertIn(self.maxsize, values)