from __future__ import annotations

from runtime._skill_state_host_types import *

def _normalize_transport_response(value: bytes | TransportResponse) -> TransportResponse:
    if isinstance(value, bytes):
        return TransportResponse(body=value)
    if not isinstance(value, TransportResponse):
        raise HostTransportError("transport must return bytes or TransportResponse")
    if not isinstance(value.body, bytes):
        raise HostTransportError("transport response body must be bytes")
    if type(value.status_code) is not int:
        raise HostTransportError("transport status_code must be an integer")
    if not isinstance(value.headers, Mapping):
        raise HostTransportError("transport response headers must be an object")
    headers: dict[str, str] = {}
    for key, item in value.headers.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise HostTransportError("transport response header names and values must be strings")
        headers[key.lower()] = item
    return TransportResponse(body=value.body, status_code=value.status_code, headers=headers)

__all__ = [name for name in globals() if not name.startswith('__')]
