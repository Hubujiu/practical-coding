from __future__ import annotations

from runtime._skill_state_host_types import *
from runtime._skill_state_host_codec import *
from runtime._skill_state_host_config import *
from runtime._skill_state_host_contract import *
from runtime._skill_state_host_audit import *
from runtime._skill_state_host_response import *

class _HistoryFreeHostTransitionMixin:
    def run_transition(
        self,
        state: Mapping[str, Any],
        latest_observation: str,
        *,
        transport: ByteTransport,
        persist_successor: PersistSuccessor,
        step_id: str | int | None = None,
        max_attempts: int = 2,
    ) -> HistoryFreeStepResult:
        if type(max_attempts) is not int or not (1 <= max_attempts <= self._limits.max_retry_attempts):
            raise HostBoundaryError(
                f"max_attempts must be between 1 and {self._limits.max_retry_attempts}"
            )
        try:
            original_state = copy.deepcopy(state)
        except Exception as exc:
            raise HostBoundaryError(f"state could not be snapshotted: {exc}") from exc
        validate_state(original_state)
        _utf8_bytes(latest_observation, "latest_observation")

        attempts: list[Mapping[str, Any]] = []
        feedback: str | None = None
        for attempt_number in range(1, max_attempts + 1):
            prepared = self.prepare_request(
                original_state,
                latest_observation,
                validation_error=feedback,
                step_id=step_id,
                attempt=attempt_number,
            )
            started = time.perf_counter_ns()
            try:
                raw_response = transport(prepared.wire_bytes)
            except Exception as exc:
                raise HostTransportError(f"transport failed before a response was returned: {exc}") from exc
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
            response = _normalize_transport_response(raw_response)
            if not 200 <= response.status_code < 300:
                raise HostTransportError(f"transport returned HTTP status {response.status_code}")
            if len(response.body) > self._limits.max_response_bytes:
                raise HostBoundaryError(
                    f"model response exceeds {self._limits.max_response_bytes} bytes"
                )

            attempt_record = dict(prepared.audit)
            attempt_record.update(
                {
                    "transport_elapsed_ms": elapsed_ms,
                    "http_status": response.status_code,
                    "response_bytes": len(response.body),
                    "response_sha256": _sha256(response.body),
                    "request_id": response.headers.get("x-request-id"),
                }
            )
            try:
                parsed_response = _parse_json_bytes(
                    response.body,
                    "model response",
                    self._limits.max_response_bytes,
                )
                if not isinstance(parsed_response, dict):
                    raise HostBoundaryError("model response must be a JSON object")
                attempt_record.update(_usage_summary(parsed_response))
                response_id = parsed_response.get("id")
                attempt_record["response_id"] = (
                    response_id if isinstance(response_id, str) else None
                )
                transition_text = _extract_output_text(parsed_response)
                attempt_record["transition_text_sha256"] = _sha256(
                    _utf8_bytes(transition_text, "transition output")
                )
                successor, action = apply_transition(original_state, transition_text)
            except (HostBoundaryError, StateValidationError) as exc:
                feedback = _compact_validation_error(exc, self._limits)
                attempt_record.update(
                    {
                        "transition_status": "rejected",
                        "validation_error": feedback,
                    }
                )
                attempts.append(MappingProxyType(attempt_record))
                continue

            try:
                persist_successor(copy.deepcopy(successor))
            except Exception as exc:
                attempt_record.update(
                    {
                        "transition_status": "persistence_failed",
                        "validation_error": None,
                    }
                )
                attempts.append(MappingProxyType(attempt_record))
                raise StatePersistenceError(
                    "successor persistence failed; the action proposal was not released"
                ) from exc

            successor_bytes = _canonical_json_bytes(successor, "successor state")
            attempt_record.update(
                {
                    "transition_status": "accepted",
                    "validation_error": None,
                    "successor_state_sha256": _sha256(successor_bytes),
                    "action_sha256": _sha256(_utf8_bytes(action, "action")),
                }
            )
            attempts.append(MappingProxyType(attempt_record))
            return HistoryFreeStepResult(
                successor_state=copy.deepcopy(successor),
                action=action,
                attempts=tuple(attempts),
            )

        raise TransitionRetriesExhausted(tuple(attempts))

__all__ = [name for name in globals() if not name.startswith('__')]
