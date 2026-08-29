"""Reference fixes used only to validate the expanded deterministic debug scorers."""

DEBUG_ORACLES = {
    "security-path-containment": {
        "storage.py": """from pathlib import Path\n\ndef storage_path(root, name):\n    root = Path(root).resolve()\n    candidate = (root / name).resolve()\n    if candidate != root and root not in candidate.parents:\n        raise ValueError(\"path escapes storage root\")\n    return candidate\n\ndef avatar_path(root, name):\n    return storage_path(root, name)\n\ndef document_path(root, name):\n    return storage_path(root, name)\n""",
    },
    "security-tenant-authorization": {
        "authorization.py": """def owns_record(user, record):\n    return (\n        user[\"tenant_id\"] == record[\"tenant_id\"]\n        and user[\"id\"] == record[\"owner_id\"]\n    )\n\ndef can_view_invoice(user, invoice):\n    return owns_record(user, invoice)\n\ndef can_view_profile(user, profile):\n    return owns_record(user, profile)\n""",
    },
    "trace-header-normalize": {
        "headers.py": """def normalize_header(name):\n    return name.strip().lower()\n\ndef get_header(headers, target):\n    wanted = normalize_header(target)\n    for name, value in headers.items():\n        if normalize_header(name) == wanted:\n            return value\n    return None\n\ndef auth_header(headers):\n    return get_header(headers, \"Authorization\")\n\ndef trace_header(headers):\n    return get_header(headers, \"X-Trace-Id\")\n""",
    },
    "trace-cache-tenant": {
        "cache_keys.py": """def cache_key(tenant, namespace, key):\n    return f\"{tenant}:{namespace}:{key}\"\n\ndef profile_cache_key(tenant, user_id):\n    return cache_key(tenant, \"profile\", user_id)\n\ndef invoice_cache_key(tenant, invoice_id):\n    return cache_key(tenant, \"invoice\", invoice_id)\n""",
    },
    "trace-page-window": {
        "paging.py": """def page_bounds(page, size):\n    start = (page - 1) * size\n    return start, start + size\n\ndef list_orders(rows, page, size):\n    start, end = page_bounds(page, size)\n    return rows[start:end]\n\ndef list_users(rows, page, size):\n    start, end = page_bounds(page, size)\n    return rows[start:end]\n""",
    },
    "trace-duration-units": {
        "timeouts.py": """def parse_duration(value):\n    value = str(value).strip().lower()\n    if value.endswith(\"ms\"):\n        return float(value[:-2]) / 1000.0\n    return float(value)\n\ndef request_timeout(env):\n    return parse_duration(env.get(\"REQUEST_TIMEOUT\", \"5\"))\n\ndef background_timeout(env):\n    return parse_duration(env.get(\"BACKGROUND_TIMEOUT\", \"30\"))\n""",
    },
    "trace-csv-blank": {
        "rows.py": """def parse_rows(text):\n    return [line.split(\",\") for line in text.splitlines() if line.strip()]\n\ndef invoice_rows(text):\n    return parse_rows(text)\n\ndef audit_rows(text):\n    return parse_rows(text)\n""",
    },
    "trace-stock-debit": {
        "inventory.py": """def _debit(stock, sku, quantity):\n    available = stock.get(sku, 0)\n    if quantity > available:\n        return False\n    stock[sku] = available - quantity\n    return True\n\ndef reserve(stock, sku, quantity):\n    return _debit(stock, sku, quantity)\n\ndef consume(stock, sku, quantity):\n    return _debit(stock, sku, quantity)\n""",
    },
    "trace-ttl-zero": {
        "ttl.py": """def parse_ttl(value, default):\n    if value is None:\n        return default\n    return int(value)\n\ndef session_ttl(env):\n    return parse_ttl(env.get(\"SESSION_TTL\"), 300)\n\ndef cache_ttl(env):\n    return parse_ttl(env.get(\"CACHE_TTL\"), 60)\n""",
    },
    "trace-null-sort": {
        "sorting.py": """def name_key(value):\n    return (value is None, \"\" if value is None else value.lower())\n\ndef sort_products(rows):\n    return sorted(rows, key=lambda row: name_key(row.get(\"name\")))\n\ndef sort_customers(rows):\n    return sorted(rows, key=lambda row: name_key(row.get(\"name\")))\n""",
    },
}
