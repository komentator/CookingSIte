"""
Простая система кэширования результатов поиска
"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class Cache:
    """In-memory кэш для результатов поиска"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds

    def _generate_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Генерирует ключ кэша из параметров"""
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_obj = hashlib.md5(param_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    def set(self, prefix: str, params: Dict[str, Any], value: Any) -> None:
        """Сохраняет значение в кэш"""
        key = self._generate_key(prefix, params)
        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now(),
            "ttl": self.ttl,
        }
        logger.debug(f"Cache SET: {key}")

    def get(self, prefix: str, params: Dict[str, Any]) -> Optional[Any]:
        """Получает значение из кэша"""
        key = self._generate_key(prefix, params)

        if key not in self.cache:
            return None

        cached = self.cache[key]
        age = (datetime.now() - cached["timestamp"]).total_seconds()

        if age > cached["ttl"]:
            del self.cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None

        logger.debug(f"Cache HIT: {key} (age: {age:.1f}s)")
        return cached["value"]

    def invalidate(self, prefix: str) -> int:
        """Инвалидирует все ключи с данным префиксом"""
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del self.cache[key]
        logger.debug(f"Cache INVALIDATED: {prefix} ({len(keys_to_delete)} keys)")
        return len(keys_to_delete)

    def clear(self) -> None:
        """Очищает весь кэш"""
        self.cache.clear()
        logger.debug("Cache CLEARED")

    def stats(self) -> Dict[str, Any]:
        """Статистика кэша"""
        return {
            "total_keys": len(self.cache),
            "ttl_seconds": self.ttl,
            "memory_usage_estimate": len(str(self.cache)),
        }


# Глобальный экземпляр кэша
cache = Cache(ttl_seconds=3600)  # 1 час


def cached_search(prefix: str):
    """Декоратор для кэширования результатов поиска"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Преобразуем параметры в словарь
            params = {
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }

            # Пытаемся получить из кэша
            cached_result = cache.get(prefix, params)
            if cached_result is not None:
                return cached_result

            # Выполняем функцию
            result = func(*args, **kwargs)

            # Сохраняем в кэш
            cache.set(prefix, params, result)

            return result

        return wrapper

    return decorator
