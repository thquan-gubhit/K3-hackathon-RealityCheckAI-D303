"""Stable application errors shared by API and domain layers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class AppError(Exception):
    """An expected application failure with a transport-safe error contract.

    ``status_code`` is the canonical HTTP-facing name.  ``status`` is retained
    as a read-only alias so non-HTTP callers can inspect the same stable value.
    Details must contain structured, non-sensitive context only.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Mapping[str, Any] | None = None,
        *,
        status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status if status is not None else status_code
        self.details = dict(details or {})

    @property
    def status(self) -> int:
        """Return the HTTP status using the domain-friendly attribute name."""

        return self.status_code

    def to_dict(self, *, request_id: str | None = None) -> dict[str, Any]:
        """Build the documented API error envelope."""

        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": request_id,
            }
        }
