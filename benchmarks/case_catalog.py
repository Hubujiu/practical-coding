"""Extended benchmark cases kept separate from the core runner.

The catalog favors distinct failure mechanisms and routing boundaries over paraphrases of
existing cases.  Every custom debug task has a deterministic verifier with a reported
caller (`correct`) and a sibling/shared-boundary check (`safe`).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


EXTRA_ROUTER_CASES = {
    "direct-existing-prop": (
        "DIRECT",
        "The existing Button already has a loading prop. Make CheckoutButton use it while submit is pending and run its existing component test.",
    ),
    "direct-private-dto": (
        "DIRECT",
        "All three known internal consumers already accept user_id. Rename the private DTO field and update those known callers.",
    ),
    "decision-job-runner": (
        "DECISION",
        "We need scheduled jobs in this service. Pick a separate queue worker or the database-backed scheduler; operational ownership and latency needs have not been decided.",
    ),
    "decision-webhook-compat": (
        "DECISION",
        "We need to change a public webhook payload shape, but we do not know whether external consumers can migrate together or need a compatibility window.",
    ),
    "debug-flaky-retry": (
        "DEBUGGING",
        "The retry test fails about one run in twenty with an assertion mismatch. We have not established which state first becomes wrong.",
    ),
    "debug-performance-regression": (
        "DEBUGGING",
        "Opening the analytics dashboard became roughly five times slower after last week's change; no hotspot has been profiled yet.",
    ),
    "implementation-event-tenant": (
        "IMPLEMENTATION",
        "Add tenant_id to a versioned event across its producer, schema, consumers, and replay path; the exact coordinated contract surface has not been mapped yet.",
    ),
    "implementation-known-callers": (
        "DIRECT",
        "The new helper signature is already decided and the four affected callers are known. Update those callers and run their focused tests.",
    ),
    "exploration-auth-context": (
        "EXPLORATION",
        "Before changing AuthContext in this monorepo, identify every package that creates it, transforms it, or depends on the transformed shape.",
    ),
    "exploration-plugin-loading": (
        "EXPLORATION",
        "Find which payment adapter implementations can be loaded at runtime and where their registration and dispatch happen across this large repository.",
    ),
    "verification-payment-retry": (
        "IMPLEMENTATION",
        "The retry-policy patch is complete. Decide what evidence is sufficient to support the claim that it cannot create duplicate charges.",
    ),
    "verification-performance-claim": (
        "IMPLEMENTATION",
        "The optimization is implemented. Decide whether unit timings, a benchmark, or a load test is sufficient evidence for the performance claim.",
    ),
    "direct-persistence-known-helper": (
        "DIRECT",
        "Repository evidence confirms append_audit_event() is the authoritative transactional persistence boundary and its focused test is sufficient. Call it from the one known handler and run that test.",
    ),
    "direct-security-known-guard": (
        "DIRECT",
        "The permission policy, require_admin() guard, rejection-before-side-effect invariant, affected route, and focused tests are already established. Apply that guard to the known route and run those tests.",
    ),
    "direct-compat-known-adapter": (
        "DIRECT",
        "The approved one-release compatibility alias and its sole public serialization adapter are already identified. Add the alias there and run the existing old/new-client contract test.",
    ),
    "implementation-single-file-persistence": (
        "IMPLEMENTATION",
        "Change the persisted status encoding in serializer.py from integer codes to strings. The edit appears confined to one file, but existing on-disk data, readers, rollback, and compatibility guarantees have not been mapped.",
    ),
    "implementation-sqlite-transaction-unknown": (
        "IMPLEMENTATION",
        "Implement the body of save_history() with sqlite3. The function and dependency are fixed, but atomicity, concurrent callers, restart behavior, and the authoritative transaction boundary are unknown.",
    ),
    "implementation-one-line-irreversible": (
        "IMPLEMENTATION",
        "Flip purge_after_sync from false to true in one configuration file. The flag permanently deletes local records, and retry, rollback, idempotency, and ownership of that guarantee are not mapped.",
    ),
    "implementation-security-local-boundary": (
        "IMPLEMENTATION",
        "Add one authorization check to download(). The code edit is local, but tenant ownership, rejection-before-read behavior, indirect callers, and the authoritative permission boundary are unknown.",
    ),
    "decision-migration-policy-open": (
        "DECISION",
        "Choose an offline rewrite or a dual-read rolling migration for persisted session records. Downtime tolerance and cross-version compatibility policy are unresolved and would change the implementation surface.",
    ),
    "debug-persistence-corruption": (
        "DEBUGGING",
        "Some command-history rows disappear after two CLI processes exit at nearly the same time. The sqlite write path is named, but the earliest incorrect state and cause are not diagnosed.",
    ),
    "debug-security-symptom": (
        "DEBUGGING",
        "A user sometimes downloads another tenant's invoice through download(). The permission boundary may be involved, but the failing execution path and cause have not been traced.",
    ),
}


EXTRA_BEHAVIOR_CASES = {
    "native-direct-known-transaction": {
        "prompt": "Repository evidence already establishes append_audit_event() as the authoritative transactional persistence boundary, this handler as the only affected caller, and test_audit_handler as the sufficient check. Replace the handler's placeholder with that existing helper and run the test.",
        "files": {
            "audit.py": "def append_audit_event(connection, event):\n    with connection:\n        connection.execute('insert into audit(event) values (?)', (event,))\n\ndef handle_login(connection):\n    pass\n",
        },
        "module": None,
    },
    "native-direct-known-permission": {
        "prompt": "The repository's settled policy requires require_admin() on administrative routes, its rejection-before-side-effect contract is already tested, and delete_report() is the only missing known caller. Add the existing guard there and run the focused test.",
        "files": {
            "reports.py": "def require_admin(user):\n    if not user.get('admin'):\n        raise PermissionError\n\ndef delete_report(user, store, report_id):\n    store.delete(report_id)\n",
        },
        "module": None,
    },
    "native-direct-known-compatibility": {
        "prompt": "Compatibility policy is settled: emit old_name beside new_name for one release. serialize_user() is the sole public adapter, all affected callers are mapped, and its existing contract test is sufficient. Make that local edit and run the test.",
        "files": {
            "users.py": "def serialize_user(user):\n    return {'new_name': user['name']}\n",
        },
        "module": None,
    },
    "native-implementation-local-persistence": {
        "prompt": "Change serializer.py so persisted account status uses strings instead of integer codes. It looks like a one-file edit, but existing data, every reader, mixed-version compatibility, rollback, and the authoritative storage contract have not been mapped. Determine the safe implementation surface before editing.",
        "files": {
            "serializer.py": "def encode_status(status):\n    return 1 if status == 'active' else 2\n",
        },
        "module": "implementation.md",
    },
    "native-implementation-local-transaction": {
        "prompt": "Python sqlite3 is already mandated and save_history() is the named function. Implementing it is locally small, but atomicity, concurrent writers, restart guarantees, and transaction ownership are unknown. Map those guarantees and sufficient evidence before editing.",
        "files": {
            "history.py": "import sqlite3\n\ndef save_history(connection, command):\n    pass\n",
        },
        "module": "implementation.md",
    },
    "native-implementation-one-line-irreversible": {
        "prompt": "Set purge_after_sync=true in settings.py. Although this is one line, it permanently deletes local records, and retry, rollback, idempotency, affected callers, and ownership of the deletion guarantee are unknown. Determine the safe change and evidence first.",
        "files": {"settings.py": "purge_after_sync = False\n"},
        "module": "implementation.md",
    },
    "native-decision-migration-policy": {
        "prompt": "Choose an offline rewrite or a dual-read rolling migration for persisted session records. Downtime tolerance and mixed-version compatibility policy are unresolved and the choice changes the next implementation action. Resolve the choice before implementation.",
        "files": {"sessions.py": "def decode_session(raw):\n    return raw\n"},
        "module": "decision.md",
    },
    "native-debug-persistent-corruption": {
        "prompt": "Some sqlite command-history rows disappear when two CLI processes exit at nearly the same time. save_history() is named, but no trace has established the earliest incorrect state or cause. Diagnose the observed failure before deciding the fix.",
        "files": {
            "history.py": "def save_history(connection, command):\n    connection.execute('insert into history(command) values (?)', (command,))\n",
        },
        "module": "debugging.md",
    },
}


EXTRA_DECISION_CASES = {
    "pagination-contract": {
        "prompt": "Choose cursor or offset pagination for a public activity API. Dataset size, mutation rate, stable continuation needs, and client ergonomics are unresolved.",
        "reply": "The dataset is large and changes continuously; clients need stable continuation while new rows arrive and can store an opaque token. Resolve the decision now.",
        "expected": ("cursor", "opaque token"),
    },
    "file-storage": {
        "prompt": "Choose database blobs or object storage for user-uploaded media. Size distribution, delivery path, transactional coupling, and lifecycle needs are unresolved.",
        "reply": "Files reach hundreds of MB, are immutable after upload, are served through a CDN, and only metadata must be transactional with the database. Resolve the decision now.",
        "expected": ("object storage", "object store"),
    },
    "deployment-rollout": {
        "prompt": "Choose blue-green or rolling deployment for this service. Capacity headroom, compatibility between versions, rollback expectations, and session behavior are unresolved.",
        "reply": "We cannot afford double capacity; adjacent versions are backward compatible; instances are stateless; gradual rollback is acceptable. Resolve the decision now.",
        "expected": ("rolling", "rollout"),
    },
    "distributed-consistency": {
        "prompt": "Choose a distributed transaction or a saga for an order workflow spanning payment and inventory services. Failure recovery and atomicity requirements are unresolved.",
        "reply": "The services own separate databases, partial progress is acceptable temporarily, and every step has a tested compensating action. Resolve the decision now.",
        "expected": ("saga", "compensat"),
    },
    "identifier-strategy": {
        "prompt": "Choose database-generated integer IDs or UUIDs for records created by intermittently connected clients. Merge behavior, ordering, and privacy requirements are unresolved.",
        "reply": "Clients must create IDs offline without coordination; merges happen later; exposing record counts is undesirable; sortable IDs are preferred but not mandatory. Resolve the decision now.",
        "expected": ("uuid", "uuidv7", "uuid v7"),
    },
    "sync-async-boundary": {
        "prompt": "Choose a synchronous service call or asynchronous queue for invoice validation. Latency, failure coupling, throughput, and user-visible consistency are unresolved.",
        "reply": "The user must receive validation errors in the same request; p99 is under 80 ms; both services share the same availability target; throughput is modest. Resolve the decision now.",
        "expected": ("synchronous", "sync", "direct call"),
    },
}


EXTRA_DEBUG_CASES = {
    "security-path-containment": {
        "prompt": "avatar_path() lets an uploaded name such as '../secrets.txt' escape the storage root. Fix the shared storage boundary, keep legitimate nested names working, and do not weaken document_path().",
        "files": {
            "storage.py": """from pathlib import Path\n\ndef storage_path(root, name):\n    return Path(root) / name\n\ndef avatar_path(root, name):\n    return storage_path(root, name)\n\ndef document_path(root, name):\n    return storage_path(root, name)\n""",
        },
        "score": "path-containment",
        "risk": "security",
    },
    "security-tenant-authorization": {
        "prompt": "can_view_invoice() authorizes a record from another tenant when owner ids collide. Fix authorization at the shared ownership boundary without breaking valid same-tenant access or can_view_profile().",
        "files": {
            "authorization.py": """def owns_record(user, record):\n    return user[\"id\"] == record[\"owner_id\"]\n\ndef can_view_invoice(user, invoice):\n    return owns_record(user, invoice)\n\ndef can_view_profile(user, profile):\n    return owns_record(user, profile)\n""",
        },
        "score": "tenant-authorization",
        "risk": "security",
    },
    "trace-header-normalize": {
        "prompt": "auth_header() misses Authorization when a proxy supplies header names with surrounding whitespace. Fix the bug without breaking other header lookups.",
        "files": {
            "headers.py": """def normalize_header(name):\n    return name.lower()\n\ndef get_header(headers, target):\n    wanted = normalize_header(target)\n    for name, value in headers.items():\n        if normalize_header(name) == wanted:\n            return value\n    return None\n\ndef auth_header(headers):\n    return get_header(headers, \"Authorization\")\n\ndef trace_header(headers):\n    return get_header(headers, \"X-Trace-Id\")\n""",
        },
        "score": "headers",
    },
    "trace-cache-tenant": {
        "prompt": "profile_cache_key() collides for users with the same id in different tenants. Fix the bug; other cache namespaces use the same key builder.",
        "files": {
            "cache_keys.py": """def cache_key(tenant, namespace, key):\n    return f\"{namespace}:{key}\"\n\ndef profile_cache_key(tenant, user_id):\n    return cache_key(tenant, \"profile\", user_id)\n\ndef invoice_cache_key(tenant, invoice_id):\n    return cache_key(tenant, \"invoice\", invoice_id)\n""",
        },
        "score": "cache-tenant",
    },
    "trace-page-window": {
        "prompt": "list_orders() returns the second page when page=1. Fix the pagination bug without changing the public one-based page contract used by sibling lists.",
        "files": {
            "paging.py": """def page_bounds(page, size):\n    start = page * size\n    return start, start + size\n\ndef list_orders(rows, page, size):\n    start, end = page_bounds(page, size)\n    return rows[start:end]\n\ndef list_users(rows, page, size):\n    start, end = page_bounds(page, size)\n    return rows[start:end]\n""",
        },
        "score": "paging",
    },
    "trace-duration-units": {
        "prompt": "request_timeout() crashes when REQUEST_TIMEOUT is configured as '2500ms'. Fix duration parsing; background jobs use the same configuration format.",
        "files": {
            "timeouts.py": """def parse_duration(value):\n    return float(value)\n\ndef request_timeout(env):\n    return parse_duration(env.get(\"REQUEST_TIMEOUT\", \"5\"))\n\ndef background_timeout(env):\n    return parse_duration(env.get(\"BACKGROUND_TIMEOUT\", \"30\"))\n""",
        },
        "score": "duration",
    },
    "trace-csv-blank": {
        "prompt": "invoice_rows() produces empty records for blank lines in uploaded CSV text. Fix the shared row parsing behavior without breaking audit imports.",
        "files": {
            "rows.py": """def parse_rows(text):\n    return [line.split(\",\") for line in text.split(\"\\n\")]\n\ndef invoice_rows(text):\n    return parse_rows(text)\n\ndef audit_rows(text):\n    return parse_rows(text)\n""",
        },
        "score": "csv-blank",
    },
    "trace-stock-debit": {
        "prompt": "reserve() can drive stock negative when quantity exceeds availability. Fix the invariant; another inventory path shares the debit primitive.",
        "files": {
            "inventory.py": """def _debit(stock, sku, quantity):\n    stock[sku] = stock.get(sku, 0) - quantity\n    return True\n\ndef reserve(stock, sku, quantity):\n    return _debit(stock, sku, quantity)\n\ndef consume(stock, sku, quantity):\n    return _debit(stock, sku, quantity)\n""",
        },
        "score": "stock",
    },
    "trace-ttl-zero": {
        "prompt": "session_ttl() ignores an explicit TTL of zero and silently restores the default. Fix TTL parsing without changing sibling cache semantics.",
        "files": {
            "ttl.py": """def parse_ttl(value, default):\n    if value is None:\n        return default\n    return int(value) or default\n\ndef session_ttl(env):\n    return parse_ttl(env.get(\"SESSION_TTL\"), 300)\n\ndef cache_ttl(env):\n    return parse_ttl(env.get(\"CACHE_TTL\"), 60)\n""",
        },
        "score": "ttl-zero",
    },
    "trace-null-sort": {
        "prompt": "sort_products() crashes when a product has no name; unnamed entries should sort last. Fix the shared ordering rule without breaking customer sorting.",
        "files": {
            "sorting.py": """def name_key(value):\n    return value.lower()\n\ndef sort_products(rows):\n    return sorted(rows, key=lambda row: name_key(row.get(\"name\")))\n\ndef sort_customers(rows):\n    return sorted(rows, key=lambda row: name_key(row.get(\"name\")))\n""",
        },
        "score": "null-sort",
    },
}


STANDARD_EXTRA_DEBUG = [
    "security-path-containment",
    "security-tenant-authorization",
    "trace-header-normalize",
    "trace-cache-tenant",
    "trace-page-window",
    "trace-duration-units",
]

STANDARD_EXTRA_DECISION = [
    "pagination-contract",
    "file-storage",
]


def _load_module(workspace: Path, filename: str, name: str) -> Any:
    path = workspace / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _result(correct: bool, safe: bool, reason: str) -> dict[str, Any]:
    return {"correct": int(bool(correct)), "safe": int(bool(safe)), "reason": reason}


def score_extra_debug(case: str, workspace: Path) -> dict[str, Any]:
    spec = EXTRA_DEBUG_CASES[case]
    score = spec["score"]
    try:
        if score == "path-containment":
            module = _load_module(workspace, "storage.py", "debug_path_containment")
            root = workspace / "uploads"

            def contained_or_rejected(call: Any) -> bool:
                try:
                    value = call()
                except Exception:
                    return True
                if value is None:
                    return True
                candidate = Path(value).resolve()
                return candidate == root.resolve() or root.resolve() in candidate.parents

            valid = module.avatar_path(root, "users/42/avatar.png")
            correct = (
                contained_or_rejected(lambda: module.avatar_path(root, "../secrets.txt"))
                and Path(valid).resolve() == (root / "users/42/avatar.png").resolve()
            )
            safe = contained_or_rejected(lambda: module.document_path(root, "../../outside.txt"))
            return _result(correct, safe, "shared storage boundary contains untrusted paths")

        if score == "tenant-authorization":
            module = _load_module(workspace, "authorization.py", "debug_tenant_authorization")
            user = {"id": "42", "tenant_id": "tenant-a"}
            own_invoice = {"owner_id": "42", "tenant_id": "tenant-a"}
            foreign_invoice = {"owner_id": "42", "tenant_id": "tenant-b"}
            own_profile = {"owner_id": "42", "tenant_id": "tenant-a"}
            foreign_profile = {"owner_id": "42", "tenant_id": "tenant-b"}
            correct = bool(module.can_view_invoice(user, own_invoice)) and not bool(module.can_view_invoice(user, foreign_invoice))
            safe = bool(module.can_view_profile(user, own_profile)) and not bool(module.can_view_profile(user, foreign_profile))
            return _result(correct, safe, "shared ownership boundary enforces tenant and owner")

        if score == "headers":
            module = _load_module(workspace, "headers.py", f"debug_{score}")
            correct = module.auth_header({" Authorization ": "Bearer abc"}) == "Bearer abc"
            safe = module.trace_header({" X-Trace-Id ": "trace-1"}) == "trace-1"
            return _result(correct, safe, "shared header normalization")

        if score == "cache-tenant":
            module = _load_module(workspace, "cache_keys.py", "debug_cache_tenant")
            correct = module.profile_cache_key("tenant-a", "42") != module.profile_cache_key("tenant-b", "42")
            safe = module.invoice_cache_key("tenant-a", "9") != module.invoice_cache_key("tenant-b", "9")
            return _result(correct, safe, "tenant isolation in shared cache_key")

        if score == "paging":
            module = _load_module(workspace, "paging.py", "debug_paging")
            correct = module.list_orders(["o1", "o2", "o3", "o4"], 1, 2) == ["o1", "o2"]
            safe = module.list_users(["u1", "u2", "u3", "u4"], 2, 2) == ["u3", "u4"]
            return _result(correct, safe, "one-based page_bounds shared by callers")

        if score == "duration":
            module = _load_module(workspace, "timeouts.py", "debug_duration")
            correct = abs(float(module.request_timeout({"REQUEST_TIMEOUT": "2500ms"})) - 2.5) < 1e-9
            safe = (
                abs(float(module.background_timeout({"BACKGROUND_TIMEOUT": "1500ms"})) - 1.5) < 1e-9
                and abs(float(module.background_timeout({"BACKGROUND_TIMEOUT": "3"})) - 3.0) < 1e-9
            )
            return _result(correct, safe, "shared duration parser preserves seconds and ms")

        if score == "csv-blank":
            module = _load_module(workspace, "rows.py", "debug_csv_blank")
            correct = module.invoice_rows("a,b\n\nc,d\n") == [["a", "b"], ["c", "d"]]
            safe = module.audit_rows("x,y\n\nq,r") == [["x", "y"], ["q", "r"]]
            return _result(correct, safe, "shared row parser drops blank records")

        if score == "stock":
            module = _load_module(workspace, "inventory.py", "debug_stock")
            reported = {"sku": 3}
            try:
                outcome = module.reserve(reported, "sku", 5)
            except Exception:
                outcome = False
            correct = reported == {"sku": 3} and outcome is not True

            sibling = {"sku": 2}
            try:
                sibling_outcome = module.consume(sibling, "sku", 4)
            except Exception:
                sibling_outcome = False
            safe = sibling == {"sku": 2} and sibling_outcome is not True
            return _result(correct, safe, "shared debit boundary preserves non-negative stock")

        if score == "ttl-zero":
            module = _load_module(workspace, "ttl.py", "debug_ttl_zero")
            correct = module.session_ttl({"SESSION_TTL": "0"}) == 0
            safe = module.cache_ttl({"CACHE_TTL": "0"}) == 0 and module.cache_ttl({}) == 60
            return _result(correct, safe, "explicit zero survives shared TTL parsing")

        if score == "null-sort":
            module = _load_module(workspace, "sorting.py", "debug_null_sort")
            products = module.sort_products([{"name": "Beta"}, {"name": None}, {"name": "alpha"}])
            customers = module.sort_customers([{"name": None}, {"name": "Zed"}, {"name": "amy"}])
            correct = [row.get("name") for row in products] == ["alpha", "Beta", None]
            safe = [row.get("name") for row in customers] == ["amy", "Zed", None]
            return _result(correct, safe, "shared nullable name ordering")

        raise KeyError(score)
    except Exception as error:
        return {"correct": 0, "safe": 0, "reason": str(error)}


def install(bench: Any) -> None:
    """Install the extended cases into run_benchmarks without duplicating the runner."""
    if getattr(bench, "_extended_case_catalog_installed", False):
        return

    base_decision = list(bench.DECISION_CASES)
    base_debug = list(bench.PROFILE_CASES["full"]["debug"])

    bench.ROUTER_CASES.update(EXTRA_ROUTER_CASES)
    bench.DECISION_CASES.update(EXTRA_DECISION_CASES)
    bench.CUSTOM_DEBUG.update(EXTRA_DEBUG_CASES)
    bench.BEHAVIOR_CASES.update(EXTRA_BEHAVIOR_CASES)
    bench.STRICT_SAFETY_CASES.update(
        case for case, spec in EXTRA_DEBUG_CASES.items() if spec.get("risk") == "security"
    )

    original_debug_score = bench.custom_debug_score

    def combined_debug_score(case: str, workspace: Path) -> dict[str, Any]:
        if case in EXTRA_DEBUG_CASES:
            return score_extra_debug(case, workspace)
        return original_debug_score(case, workspace)

    bench.custom_debug_score = combined_debug_score

    # Smoke remains deliberately tiny. Standard is broader but bounded; full carries the
    # complete public regression matrix.
    bench.PROFILE_CASES["standard"]["router"] = list(bench.ROUTER_CASES)
    bench.PROFILE_CASES["full"]["router"] = list(bench.ROUTER_CASES)
    bench.PROFILE_CASES["standard"]["decision"] = [*base_decision, *STANDARD_EXTRA_DECISION]
    bench.PROFILE_CASES["full"]["decision"] = list(bench.DECISION_CASES)
    bench.PROFILE_CASES["standard"]["debug"] = [*base_debug, *STANDARD_EXTRA_DEBUG]
    bench.PROFILE_CASES["full"]["debug"] = [*base_debug, *EXTRA_DEBUG_CASES]
    bench.PROFILE_CASES["standard"]["behavior"] = list(bench.BEHAVIOR_CASES)
    bench.PROFILE_CASES["full"]["behavior"] = list(bench.BEHAVIOR_CASES)

    bench._extended_case_catalog_installed = True
