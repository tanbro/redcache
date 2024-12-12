from ..mixins.md5hash import Md5PickleMixin
from ..mixins.policies import LruScriptsMixin, MruExtArgsMixin
from .base import BaseClusterMultiplePolicy, BaseClusterSinglePolicy, BaseMultiplePolicy, BaseSinglePolicy

__all__ = ("MruPolicy", "MruMultiplePolicy", "MruClusterPolicy", "MruClusterMultiplePolicy")


class MruPolicy(LruScriptsMixin, MruExtArgsMixin, Md5PickleMixin, BaseSinglePolicy):
    """All functions are cached in a single sorted-set/hash-map pair of redis, with Most Recently Used eviction policy."""

    __key__ = "mru"


class MruMultiplePolicy(LruScriptsMixin, MruExtArgsMixin, Md5PickleMixin, BaseMultiplePolicy):
    """Each function is cached in its own sorted-set/hash-map pair of redis, with Most Recently Used eviction policy."""

    __key__ = "mru-m"


class MruClusterPolicy(LruScriptsMixin, MruExtArgsMixin, Md5PickleMixin, BaseClusterSinglePolicy):
    """All functions are cached in a single sorted-set/hash-map pair of redis with cluster support, with Most Recently Used eviction policy."""

    __key__ = "mru-c"


class MruClusterMultiplePolicy(LruScriptsMixin, MruExtArgsMixin, Md5PickleMixin, BaseClusterMultiplePolicy):
    """Each function is cached in its own sorted-set/hash-map pair of redis with cluster support, with Most Recently Used eviction policy."""

    __key__ = "mru-cm"
