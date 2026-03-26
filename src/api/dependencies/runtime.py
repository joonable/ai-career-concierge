from functools import lru_cache

from common.config import get_settings
from api.services.runtime import RuntimeServices, build_default_runtime


@lru_cache(maxsize=1)
def get_runtime() -> RuntimeServices:
    return build_default_runtime(get_settings())
