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
        "VERIFICATION",
        "The retry-policy patch is complete. Decide what evidence is sufficient to support the claim that it cannot create duplicate charges.",
    ),
    "verification-performance-claim": (
        "VERIFICATION",
        "The optimization is implemented. Decide whether unit timings, a benchmark, or a load test is sufficient evidence for the performance claim.",
    ),
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

    bench._extended_case_catalog_installed = True
