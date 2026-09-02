#!/usr/bin/env python3
"""Audited history-free host boundary for Practical Coding execution state."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime._skill_state_host_types import *  # noqa: E402,F403
from runtime._skill_state_host_codec import *
from runtime._skill_state_host_config import *
from runtime._skill_state_host_contract import *  # noqa: E402,F403
from runtime._skill_state_host_audit import *
from runtime._skill_state_host_response import *  # noqa: E402,F403
from runtime._skill_state_host_runtime import *  # noqa: E402,F403

def _read_bytes(path: Path, max_bytes: int, label: str) -> bytes:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise HostBoundaryError(f"cannot read {path}: {exc}") from exc
    if len(payload) > max_bytes:
        raise HostBoundaryError(f"{label} exceeds {max_bytes} bytes")
    return payload


def _read_text(path: Path, max_bytes: int, label: str) -> str:
    payload = _read_bytes(path, max_bytes, label)
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HostBoundaryError(f"{label} is not valid UTF-8: {exc}") from exc


def _read_json_file(path: Path, max_bytes: int, label: str) -> Any:
    return _parse_json_bytes(_read_bytes(path, max_bytes, label), label, max_bytes)


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def _write_pretty_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = json.dumps(
        dict(value),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ).encode("utf-8") + b"\n"
    _atomic_write_bytes(path, payload)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build and audit one exact history-free request")
    build.add_argument("--model", required=True)
    build.add_argument("--procedure", type=Path, required=True)
    build.add_argument("--state", type=Path, required=True)
    build.add_argument("--observation", type=Path, required=True)
    build.add_argument("--validation-error", type=Path)
    build.add_argument("--options", type=Path)
    build.add_argument("--tools", type=Path)
    build.add_argument("--request-output", type=Path, required=True)
    build.add_argument("--audit-output", type=Path, required=True)
    build.add_argument("--manifest-output", type=Path)

    audit = subparsers.add_parser("audit", help="audit an already serialized request file")
    audit.add_argument("request", type=Path)
    audit.add_argument("--manifest", type=Path)
    audit.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "build":
            procedure = _read_text(
                args.procedure,
                MAX_RUNTIME_TEXT_BYTES,
                f"procedure {args.procedure}",
            )
            state = _read_json_file(
                args.state,
                MAX_STATE_BYTES + 8 * 1024,
                f"state {args.state}",
            )
            observation = _read_text(
                args.observation,
                MAX_RUNTIME_TEXT_BYTES,
                f"observation {args.observation}",
            )
            validation_error = (
                None
                if args.validation_error is None
                else _read_text(
                    args.validation_error,
                    MAX_VALIDATION_ERROR_BYTES,
                    f"validation error {args.validation_error}",
                )
            )
            options = (
                None
                if args.options is None
                else _read_json_file(args.options, MAX_OPTIONS_BYTES, f"options {args.options}")
            )
            tools = (
                None
                if args.tools is None
                else _read_json_file(args.tools, MAX_TOOLS_BYTES, f"tools {args.tools}")
            )
            host = HistoryFreeHost(
                model=args.model,
                procedure=procedure,
                options=options,
                tools=tools,
            )
            prepared = host.prepare_request(
                state,
                observation,
                validation_error=validation_error,
            )
            _atomic_write_bytes(args.request_output, prepared.wire_bytes)
            _write_pretty_json(args.audit_output, prepared.audit)
            if args.manifest_output is not None:
                _write_pretty_json(args.manifest_output, host.manifest())
            return 0
        if args.command == "audit":
            request = _read_bytes(
                args.request,
                MAX_WIRE_REQUEST_BYTES,
                f"request {args.request}",
            )
            if args.manifest is None:
                result = audit_wire_request(request)
            else:
                manifest = _read_json_file(
                    args.manifest,
                    MAX_OPTIONS_BYTES,
                    f"manifest {args.manifest}",
                )
                result = audit_wire_request_against_manifest(request, manifest)
            _write_pretty_json(args.output, result)
            return 0
    except (OSError, HostBoundaryError, StateValidationError) as exc:
        print(f"skill-state-host error: {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
