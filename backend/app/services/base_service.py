"""
Base Service Module

Provides base classes and utilities for service singletons to eliminate
code duplication and ensure consistent patterns across all services.
"""

from typing import TypeVar, Generic, Optional, Type
from abc import ABC


# Type variable for service classes
T = TypeVar('T', bound='BaseService')


class BaseService(ABC):
    """
    Abstract base class for singleton service instances.

    Provides a standardized singleton pattern that all services can inherit,
    eliminating duplicate singleton implementation code.
    """

    _instance: Optional['BaseService'] = None

    def __init__(self):
        """Initialize the service."""
        pass


def get_or_create_service(
    service_class: Type[T],
    instance_holder: dict,
    instance_key: str = 'instance'
) -> T:
    """
    Get or create a singleton service instance.

    This helper function provides a reusable singleton pattern for all services,
    eliminating the need for duplicate `get_*_service()` functions.

    Args:
        service_class: The service class to instantiate
        instance_holder: Dictionary to hold the instance (module-level dict)
        instance_key: Key name in the instance holder dict

    Returns:
        The singleton service instance

    Example:
        ```python
        _services = {}

        def get_my_service() -> MyService:
            return get_or_create_service(MyService, _services, 'my_service')
        ```
    """
    if instance_key not in instance_holder or instance_holder[instance_key] is None:
        instance_holder[instance_key] = service_class()
    return instance_holder[instance_key]
