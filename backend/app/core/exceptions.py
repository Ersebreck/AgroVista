"""
Custom exception classes for the application.
Provides structured error handling across the system.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class AgroVistaException(Exception):
    """Base exception for all AgroVista custom exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class DomainException(AgroVistaException):
    """Base exception for domain-specific errors."""

    pass


class RepositoryException(AgroVistaException):
    """Base exception for repository layer errors."""

    pass


class ServiceException(AgroVistaException):
    """Base exception for service layer errors."""

    pass


# Specific domain exceptions
class TerrainNotFoundException(DomainException):
    """Raised when a terrain is not found."""

    def __init__(self, terrain_id: int):
        super().__init__(
            message=f"Terrain with ID {terrain_id} not found",
            error_code="TERRAIN_NOT_FOUND",
            details={"terrain_id": terrain_id},
        )


class ParcelNotFoundException(DomainException):
    """Raised when a parcel is not found."""

    def __init__(self, parcel_id: int):
        super().__init__(
            message=f"Parcel with ID {parcel_id} not found",
            error_code="PARCEL_NOT_FOUND",
            details={"parcel_id": parcel_id},
        )


class ActivityNotFoundException(DomainException):
    """Raised when an activity is not found."""

    def __init__(self, activity_id: int):
        super().__init__(
            message=f"Activity with ID {activity_id} not found",
            error_code="ACTIVITY_NOT_FOUND",
            details={"activity_id": activity_id},
        )


class InvalidOperationException(DomainException):
    """Raised when an invalid operation is attempted."""

    pass


class InsufficientInventoryException(DomainException):
    """Raised when inventory quantity is insufficient."""

    def __init__(self, item_name: str, requested: float, available: float):
        super().__init__(
            message=f"Insufficient inventory for {item_name}. Requested: {requested}, Available: {available}",
            error_code="INSUFFICIENT_INVENTORY",
            details={
                "item_name": item_name,
                "requested_quantity": requested,
                "available_quantity": available,
            },
        )


class ValidationException(DomainException):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation failed for {field}: {message}",
            error_code="VALIDATION_ERROR",
            details={"field": field, "validation_message": message},
        )


class AuthorizationException(AgroVistaException):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, action: str, resource: str):
        super().__init__(
            message=f"Not authorized to {action} {resource}",
            error_code="AUTHORIZATION_ERROR",
            details={"action": action, "resource": resource},
        )


# HTTP exception converters
def domain_exception_to_http(exc: DomainException) -> HTTPException:
    """Convert domain exception to HTTP exception."""
    status_map = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "INSUFFICIENT_INVENTORY": status.HTTP_400_BAD_REQUEST,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
    }

    # Determine status code based on error code suffix
    status_code = status.HTTP_400_BAD_REQUEST
    for suffix, code in status_map.items():
        if exc.error_code.endswith(suffix):
            status_code = code
            break

    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )
