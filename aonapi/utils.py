import threading
from sqlmodel import Session
from aonapi.models import engine


def get_db():
    """Dependency to get a new database session."""
    with Session(engine) as session:
        yield session


class SingletonMeta(type):
    """
    A thread-safe singleton metaclass with cache invalidation and timer functionality.

    This metaclass ensures that only one instance of a class is created (singleton pattern).
    It also provides cache invalidation and timer functionality to automatically refresh
    the cached value after a specified duration.

    To Use:
        To use this metaclass, set the metaclass attribute of the class to SingletonMeta.
        In your __init__ method, set the _cache_duration attribute to the desired cache duration.
        Implement a method to refresh the cache (e.g., _refresh_cache).
        To get the cached value, use the get_cached_value method with the refresh method.
        To invalidate the cache, use the invalidate_cache method.

    Example:
    ```python
        class ConfigCache(metaclass=SingletonMeta):
            def __init__(self):
                self._cache_duration = 1800 # Cache duration in seconds (30 minutes)

            def _refresh_cache(self):
                response = requests.get(config_url)
                if response.status_code != 200:
                    raise Exception(f"Failed to get configuration data. Status code: {response.status_code}")
                return response.json()

            def get_config(self):
                return SingletonMeta.get_cached_value(self, self._refresh_cache)

            def invalidate_cache(self):
                SingletonMeta.invalidate_cache(self)

        def get_config():
            cache = ConfigCache()
            return cache.get_config()
    ```

    Attributes:
        _instances (dict): A dictionary to store instances of singleton classes.
        _lock (threading.Lock): A lock to ensure thread safety during instance creation.

    Methods:
        __call__(cls, *args, **kwargs): Creates or returns the singleton instance of the class.
        _set_invalidation_timer(instance): Sets a timer to invalidate the cache after the specified duration.
        invalidate_cache(instance): Invalidates the cache and resets the invalidation timer.
        get_cached_value(instance, refresh_method): Retrieves the cached value or refreshes it using the provided method.
    """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Creates or returns the singleton instance of the class.

        This method ensures that only one instance of the class is created.
        It also initializes cache-related attributes and sets the invalidation timer.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The singleton instance of the class.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
                instance._cache = None
                instance._timer = None
                instance._cache_duration = getattr(
                    instance, "_cache_duration", 300
                )  # Default to 300 seconds if not set
                cls._set_invalidation_timer(instance)
        return cls._instances[cls]

    @staticmethod
    def _set_invalidation_timer(instance):
        """
        Sets a timer to invalidate the cache after the specified duration.

        This method cancels any existing timer and sets a new timer to call
        the invalidate_cache method after the cache duration.

        Args:
            instance: The singleton instance of the class.
        """
        if instance._timer is not None:
            instance._timer.cancel()
        instance._timer = threading.Timer(
            instance._cache_duration, lambda: instance.invalidate_cache()
        )
        instance._timer.start()

    @staticmethod
    def invalidate_cache(instance):
        """
        Invalidates the cache and resets the invalidation timer.

        This method sets the cache to None and resets the invalidation timer.

        Args:
            instance: The singleton instance of the class.
        """
        instance._cache = None
        SingletonMeta._set_invalidation_timer(instance)

    @staticmethod
    def get_cached_value(instance, refresh_method):
        """
        Retrieves the cached value or refreshes it using the provided method.

        This method checks if the cache is None and, if so, calls the refresh_method
        to refresh the cache. It also sets the invalidation timer.

        Args:
            instance: The singleton instance of the class.
            refresh_method (callable): The method to call to refresh the cache.

        Returns:
            The cached value.
        """
        if instance._cache is None:
            instance._cache = refresh_method()
            SingletonMeta._set_invalidation_timer(instance)
        return instance._cache
