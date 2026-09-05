"""Public code-delivery regression fixtures with executable, post-run oracles.

These are controlled fixtures, not held-out real-project performance evidence.
No expected automatic route appears in a task. Oracles never enter its workspace.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def case(name: str, filename: str, prompt: str, source: str, oracle: str, *, safety: bool = False) -> dict[str, Any]:
    return {"task_id": name, "repository": "delivery-fixtures", "family": "executable-delivery",
            "manual_request": None, "filename": filename, "files": {filename: source},
            "prompt": prompt + f" Only edit {filename}; focused test_*.py files may be added. Run a focused check.",
            "oracle": oracle, "safety_critical": safety}


CASES = [
    case("delivery-known-label", "greeting.py",
         "Change greet(name) to return 'Hello, <name>!' rather than 'Hi, <name>!'. Keep main() using that function.",
         "def greet(name):\n    return f'Hi, {name}!'\n\ndef main():\n    print(greet('world'))\n",
         '''
def valid():
    assert m.greet('Ada') == 'Hello, Ada!'
    assert m.greet('') == 'Hello, !'
    import contextlib, io
    output = io.StringIO()
    with contextlib.redirect_stdout(output): m.main()
    assert output.getvalue() == 'Hello, world!\\n'
check('public-entry-point', valid)
'''),
    case("delivery-shared-parser", "settings.py",
         "FEATURE and AUDIT share a case-insensitive boolean format with surrounding whitespace. Repair parse_bool so ' Yes ' is true and ' false ' is false for both callers; retain existing true spellings and missing-setting defaults.",
         "def parse_bool(value):\n    return value.lower() in {'1', 'true', 'yes'}\n\ndef feature(env):\n    return parse_bool(env.get('FEATURE', 'false'))\n\ndef audit(env):\n    return parse_bool(env.get('AUDIT', 'false'))\n",
         '''
def valid():
    for text in ('1', ' true ', '\\tYES\\n'):
        assert m.parse_bool(text) is True
        assert m.feature({'FEATURE': text}) is True
        assert m.audit({'AUDIT': text}) is True
    for text in ('0', ' false ', 'NO', ''): assert m.parse_bool(text) is False
    assert m.feature({}) is False and m.audit({}) is False
check('shared-callers-and-defaults', valid)
'''),
    case("delivery-confined-read", "documents.py",
         "read_document(root, name) must read UTF-8 files only within root. Allow normal nested files and symlinks that stay inside; reject absolute or parent/symlink escapes with ValueError before reading external content. Missing files should still raise FileNotFoundError.",
         "from pathlib import Path\n\ndef read_document(root, name):\n    return (Path(root) / name).read_text(encoding='utf-8')\n",
         '''
import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory); root = base / 'root'; root.mkdir()
    (root / 'ok.txt').write_text('allowed', encoding='utf-8')
    (base / 'secret.txt').write_text('private', encoding='utf-8')
    (root / 'inside.txt').symlink_to(root / 'ok.txt')
    (root / 'outside.txt').symlink_to(base / 'secret.txt')
    def valid():
        assert m.read_document(root, 'ok.txt') == 'allowed'
        assert m.read_document(root, 'inside.txt') == 'allowed'
        raises(FileNotFoundError, lambda: m.read_document(root, 'missing.txt'))
    def reject():
        for name in ('../secret.txt', str(base / 'secret.txt'), 'outside.txt'):
            raises(ValueError, lambda name=name: m.read_document(root, name))
    check('valid-and-missing', valid)
    check('traversal-and-symlink-rejection', reject, True)
''', safety=True),
    case("delivery-atomic-transfer", "ledger.py",
         "transfer(conn, source, target, amount) runs on a SQLite connection with no active transaction. Both accounts must exist, amount must be a positive integer (not bool), IDs must differ, and funds must suffice. Invalid requests raise ValueError without effects. Debit and credit must commit together; on a database error roll back and re-raise. Do not leave a transaction open.",
         "def transfer(conn, source, target, amount):\n    conn.execute('UPDATE accounts SET balance=balance-? WHERE id=?', (amount, source))\n    conn.execute('UPDATE accounts SET balance=balance+? WHERE id=?', (amount, target))\n    conn.commit()\n",
         '''
import sqlite3
def connection():
    c = sqlite3.connect(':memory:', isolation_level=None)
    c.execute('CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL)')
    c.executemany('INSERT INTO accounts VALUES (?, ?)', [(1, 10), (2, 0)])
    return c
def balances(c): return list(c.execute('SELECT balance FROM accounts ORDER BY id'))
def valid():
    c = connection(); m.transfer(c, 1, 2, 4)
    assert balances(c) == [(6,), (4,)] and not c.in_transaction
    c.close()
def reject():
    for source, target, amount in [(1, 2, -1), (1, 2, True), (1, 2, 11), (1, 9, 1), (9, 2, 1), (1, 1, 1)]:
        c = connection()
        raises(ValueError, lambda: m.transfer(c, source, target, amount))
        assert balances(c) == [(10,), (0,)] and not c.in_transaction
        c.close()
def rollback():
    c = connection()
    c.execute("CREATE TRIGGER reject_credit BEFORE UPDATE ON accounts WHEN NEW.id=2 BEGIN SELECT RAISE(ABORT, 'blocked'); END")
    raises(sqlite3.DatabaseError, lambda: m.transfer(c, 1, 2, 4))
    assert balances(c) == [(10,), (0,)] and not c.in_transaction
    c.close()
check('committed-transfer', valid)
check('invalid-before-effects', reject, True)
check('database-error-rollback', rollback, True)
''', safety=True),
    case("delivery-reservation-race", "inventory.py",
         "Multiple threads share Inventory. Fix reserve() so each success atomically consumes one item, returns bool, and stock never goes negative or oversells. Preserve the public stock field and independent instances.",
         "import time\n\nclass Inventory:\n    def __init__(self, stock):\n        self.stock = stock\n\n    def reserve(self):\n        if self.stock <= 0:\n            return False\n        remaining = self.stock - 1\n        time.sleep(0.002)\n        self.stock = remaining\n        return True\n",
         '''
import concurrent.futures, threading
def races():
    for stock in (1, 3, 7):
        for _ in range(3):
            inv = m.Inventory(stock); barrier = threading.Barrier(16)
            def reserve():
                barrier.wait(timeout=5)
                return inv.reserve()
            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
                results = list(pool.map(lambda _: reserve(), range(16)))
            assert all(type(value) is bool for value in results)
            assert sum(results) == stock and inv.stock == 0
    a, b = m.Inventory(1), m.Inventory(1)
    assert a.reserve() is True and b.reserve() is True
check('concurrent-stock-conservation', races, True)
''', safety=True),
    case("delivery-status-compatibility", "status.py",
         "normalize_status(value) is the single compatibility boundary: accept legacy integers 1/2 and public strings 'active'/'disabled', returning the public string. Reject bool, other integers, unknown strings, and None with ValueError. Do not change callers to bypass this function.",
         "def normalize_status(value):\n    return {1: 'active', 2: 'disabled'}[value]\n",
         '''
def valid():
    for value, expected in [(1, 'active'), (2, 'disabled'), ('active', 'active'), ('disabled', 'disabled')]:
        assert m.normalize_status(value) == expected
def invalid():
    for value in (True, False, 0, 3, None, 'unknown', '1'):
        raises(ValueError, lambda value=value: m.normalize_status(value))
check('old-and-new-callers', valid)
check('invalid-contract', invalid)
'''),
    case("delivery-cancel-export", "exporter.py",
         "export(encode, sink, cancelled) must raise asyncio.CancelledError with no sink call when its asyncio.Event is set before encoding or while awaiting encode(). A pre-cancelled call must not invoke encode at all. Uncancelled work calls sink exactly once; preserve encoder exceptions.",
         "async def export(encode, sink, cancelled):\n    data = await encode()\n    sink(data)\n",
         '''
import asyncio
async def exercise():
    writes = []; called = []
    async def encoder(): called.append(True); return b'data'
    event = asyncio.Event()
    await m.export(encoder, writes.append, event)
    assert writes == [b'data'] and called == [True]
    writes.clear(); called.clear(); event.set()
    try: await m.export(encoder, writes.append, event)
    except asyncio.CancelledError: pass
    else: raise AssertionError('pre-cancel must propagate')
    assert not writes and not called
    entered = asyncio.Event(); finish = asyncio.Event(); event.clear()
    async def delayed(): entered.set(); await finish.wait(); return b'data'
    task = asyncio.create_task(m.export(delayed, writes.append, event))
    await entered.wait(); event.set(); finish.set()
    try: await task
    except asyncio.CancelledError: pass
    else: raise AssertionError('mid-encode cancel must propagate')
    assert not writes
    event.clear()
    async def broken(): raise RuntimeError('encoder failure')
    try: await m.export(broken, writes.append, event)
    except RuntimeError: pass
    else: raise AssertionError('encoder error must propagate')
    assert not writes
check('normal-cancelled-and-error-paths', lambda: asyncio.run(exercise()), True)
''', safety=True),
    case("delivery-authorized-delete", "access.py",
         "delete_document(actor, document, repository) may delete only for its owner or an actor with role 'admin'. Otherwise raise PermissionError before any repository mutation. actor and document are dicts with id/role and id/owner_id. Keep repository.delete(document_id) as the side-effect boundary.",
         "def delete_document(actor, document, repository):\n    repository.delete(document['id'])\n    if actor['id'] != document['owner_id'] and actor['role'] != 'admin':\n        raise PermissionError('forbidden')\n",
         '''
class Repository:
    def __init__(self): self.deleted = []
    def delete(self, ident): self.deleted.append(ident)
def valid():
    for actor in ({'id': 1, 'role': 'user'}, {'id': 2, 'role': 'admin'}):
        r = Repository(); m.delete_document(actor, {'id': 9, 'owner_id': 1}, r)
        assert r.deleted == [9]
def reject():
    r = Repository()
    raises(PermissionError, lambda: m.delete_document({'id': 2, 'role': 'user'}, {'id': 9, 'owner_id': 1}, r))
    assert not r.deleted
check('owner-and-admin', valid)
check('rejected-before-delete', reject, True)
''', safety=True),
]


def prepare_workspace(workspace: Path, item: dict[str, Any]) -> None:
    workspace.mkdir(parents=True, exist_ok=False)
    for name, text in item["files"].items():
        (workspace / name).write_text(text, encoding="utf-8")
    (workspace / ".gitignore").write_text("__pycache__/\n*.pyc\n.zvec-grep/\n", encoding="utf-8")
    for args in (["init", "-q"], ["add", "."],
                 ["-c", "user.name=Fixture", "-c", "user.email=fixture@invalid", "commit", "-qm", "frozen fixture"]):
        subprocess.run(["git", *args], cwd=workspace, capture_output=True, check=True, timeout=30)


def submitted_files(workspace: Path) -> dict[str, str]:
    """Archive only public fixture files; never follow a contestant symlink."""
    result = {}
    for path in sorted(workspace.iterdir()):
        if path.is_symlink():
            raise ValueError("submission contains a symlink")
        if path.is_file() and (path.suffix == ".py" or path.name == ".gitignore"):
            result[path.name] = path.read_text(encoding="utf-8")
    return result


def score_workspace(workspace: Path, item: dict[str, Any]) -> dict[str, Any]:
    # Compile/load only the submitted module in a disposable child interpreter.
    # The independent assertions are supplied after the model process has exited.
    if (workspace / item["filename"]).is_symlink():
        return {"passed": False, "behavior_passed": False, "safety_passed": False,
                "oracle_valid": True, "oracle_checks": [], "workspace_scope_ok": False}
    script = '''import importlib.util, json, sys
from pathlib import Path
checks = []
def check(name, fn, safety=False):
    try: fn(); checks.append(dict(name=name, passed=True, safety=safety))
    except BaseException as exc: checks.append(dict(name=name, passed=False, safety=safety, error=type(exc).__name__))
def raises(kind, fn):
    try: fn()
    except kind: return
    raise AssertionError('expected rejection')
try:
    spec = importlib.util.spec_from_file_location('submitted', Path(sys.argv[1]) / sys.argv[2])
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    exec(compile(ORACLE, '<independent-oracle>', 'exec'))
except BaseException as exc:
    checks.append(dict(name='oracle-execution', passed=False, safety=True, error=type(exc).__name__))
print(json.dumps(checks))
'''.replace("ORACLE", repr(item["oracle"]))
    try:
        proc = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(workspace), item["filename"]],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
        checks = json.loads(proc.stdout.splitlines()[-1]) if proc.returncode == 0 and proc.stdout.strip() else []
    except (OSError, subprocess.TimeoutExpired, ValueError):
        checks = []
    if not isinstance(checks, list) or not checks:
        return {"passed": False, "behavior_passed": False, "safety_passed": False,
                "oracle_valid": False, "oracle_checks": [], "workspace_scope_ok": False}
    paths = []
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace)
        if any(part in {".git", "__pycache__", ".zvec-grep"} for part in relative.parts) or not path.is_file():
            continue
        paths.append(relative.as_posix())
    allowed = set(item["files"]) | {".gitignore"}
    scope_ok = all(name in allowed or ("/" not in name and name.startswith("test_") and name.endswith(".py")) for name in paths)
    try:
        scope_ok &= (workspace / ".gitignore").read_text(encoding="utf-8") == "__pycache__/\n*.pyc\n.zvec-grep/\n"
    except (OSError, UnicodeError):
        scope_ok = False
    behavior = all(check.get("passed") is True for check in checks)
    safety = all(check.get("passed") is True for check in checks if check.get("safety"))
    return {"passed": behavior and scope_ok, "behavior_passed": behavior, "safety_passed": safety,
            "oracle_valid": True, "oracle_checks": checks, "workspace_scope_ok": scope_ok}
