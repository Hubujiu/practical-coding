#!/usr/bin/env python3
"""
Practical Coding embedded codebase graph runtime.

Zero third-party dependencies. It builds a persistent SQLite graph of files,
symbols, imports, and call edges, then exposes a small CLI for architecture,
search, trace, impact, and read-only SQL queries.

This is an original lightweight runtime inspired by the data model and
agent-facing workflows of DeusData/codebase-memory-mcp (MIT). It does not
vendor that project's MCP server, daemon, UI, semantic model, or parser bundle.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

SCHEMA_VERSION = 1
MAX_FILE_BYTES = 2 * 1024 * 1024
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".next", ".nuxt",
    ".svelte-kit", ".gradle", ".mvn", ".cache", ".venv", "venv",
    "node_modules", "vendor", "dist", "build", "target", "coverage",
    "__pycache__", ".pytest_cache", ".mypy_cache",
}
EXT_LANG = {
    ".py": "python",
    ".js": "javascript", ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".go": "go", ".rs": "rust",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp",
    ".hpp": "cpp", ".hh": "cpp",
    ".cs": "csharp", ".php": "php", ".rb": "ruby",
    ".vue": "vue", ".svelte": "svelte",
    ".scala": "scala", ".swift": "swift",
}
CALL_STOPWORDS = {
    "if", "for", "while", "switch", "catch", "return", "sizeof", "typeof",
    "new", "throw", "assert", "print", "println", "console", "super", "this",
    "function", "fn", "func", "def", "class", "interface", "enum",
}
GENERIC_FUNC_PATTERNS = {
    "javascript": [
        re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\("),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"),
        re.compile(r"^\s*(?:async\s+)?([A-Za-z_$][\w$]*)\s*\([^;{}]*\)\s*\{"),
    ],
    "typescript": [],
    "java": [re.compile(r"^\s*(?:public|protected|private|static|final|synchronized|abstract|native|\s)+[\w<>\[\], ?.@]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:throws [^{]+)?\{")],
    "kotlin": [re.compile(r"^\s*(?:suspend\s+)?fun\s+(?:<[^>]+>\s*)?([A-Za-z_]\w*)\s*\(")],
    "go": [re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(")],
    "rust": [re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)\s*\(")],
    "c": [re.compile(r"^\s*(?!if\b|for\b|while\b|switch\b)(?:[\w*&:<>,\[\]\s]+)\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{")],
    "cpp": [],
    "csharp": [re.compile(r"^\s*(?:public|protected|private|internal|static|virtual|override|async|sealed|abstract|\s)+[\w<>\[\],?.]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{")],
    "php": [re.compile(r"^\s*(?:public|protected|private|static|\s)*function\s+([A-Za-z_]\w*)\s*\(")],
    "ruby": [re.compile(r"^\s*def\s+([A-Za-z_]\w*[!?=]?)")],
    "scala": [re.compile(r"^\s*(?:private\s+|protected\s+)?def\s+([A-Za-z_]\w*)\s*(?:\(|:)")],
    "swift": [re.compile(r"^\s*(?:public|private|internal|fileprivate|open|static|class|mutating|override|\s)*func\s+([A-Za-z_]\w*)\s*\(")],
}
GENERIC_FUNC_PATTERNS["typescript"] = GENERIC_FUNC_PATTERNS["javascript"]
GENERIC_FUNC_PATTERNS["cpp"] = GENERIC_FUNC_PATTERNS["c"]
GENERIC_FUNC_PATTERNS["vue"] = GENERIC_FUNC_PATTERNS["typescript"]
GENERIC_FUNC_PATTERNS["svelte"] = GENERIC_FUNC_PATTERNS["typescript"]

CLASS_PATTERNS = [
    re.compile(r"^\s*(?:export\s+)?(?:public\s+|private\s+|protected\s+|abstract\s+|final\s+|sealed\s+|open\s+)*class\s+([A-Za-z_]\w*)"),
    re.compile(r"^\s*(?:export\s+)?interface\s+([A-Za-z_]\w*)"),
    re.compile(r"^\s*(?:export\s+)?enum\s+([A-Za-z_]\w*)"),
    re.compile(r"^\s*(?:pub\s+)?(?:struct|trait|enum)\s+([A-Za-z_]\w*)"),
]
IMPORT_PATTERNS = [
    re.compile(r"^\s*import\s+(?:.+?\s+from\s+)?[\"']([^\"']+)[\"']"),
    re.compile(r"^\s*import\s+([\w.]+)"),
    re.compile(r"^\s*from\s+([\w.]+)\s+import\s+"),
    re.compile(r"^\s*#include\s*[<\"]([^>\"]+)[>\"]"),
    re.compile(r"^\s*use\s+([^;]+);"),
    re.compile(r"^\s*require(?:_once)?\s*\(?[\"']([^\"']+)[\"']"),
]
CALL_RE = re.compile(r"\b([A-Za-z_][\w$]*)\s*\(")


@dataclass
class Symbol:
    name: str
    qualified: str
    kind: str
    line: int
    end_line: int | None = None


@dataclass
class ParsedFile:
    symbols: list[Symbol]
    imports: list[tuple[str, int]]
    # (index into symbols of the enclosing definition, or None for module
    # level, callee name, line). Binding callers by index instead of by name
    # keeps attribution exact even when a file has same-named definitions.
    calls: list[tuple[int | None, str, int]]


def _json(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def repo_root(path: str | Path) -> Path:
    return Path(path).resolve()


def cache_root() -> Path:
    override = os.environ.get("PRACTICAL_CODING_CACHE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "practical-coding" / "cache"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "practical-coding"
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "practical-coding"


def default_db(repo: Path) -> Path:
    digest = hashlib.sha256(str(repo).encode("utf-8", "surrogateescape")).hexdigest()[:16]
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", repo.name) or "repo"
    return cache_root() / "codebase-memory" / f"{safe_name}-{digest}.sqlite3"


def connect(db: Path) -> sqlite3.Connection:
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA synchronous=NORMAL")
    return con


def stored_schema_version(con: sqlite3.Connection) -> str | None:
    try:
        row = con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    except sqlite3.DatabaseError:
        return None
    return row["value"] if row else None


def init_schema(con: sqlite3.Connection) -> None:
    has_meta = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='meta'"
    ).fetchone()
    if has_meta and stored_schema_version(con) != str(SCHEMA_VERSION):
        con.executescript(
            """
            DROP TABLE IF EXISTS call_edges;
            DROP TABLE IF EXISTS calls;
            DROP TABLE IF EXISTS imports;
            DROP TABLE IF EXISTS symbols;
            DROP TABLE IF EXISTS files;
            DROP TABLE IF EXISTS meta;
            """
        )
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS files(
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            language TEXT NOT NULL,
            mtime_ns INTEGER NOT NULL,
            size INTEGER NOT NULL,
            sha1 TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS symbols(
            id INTEGER PRIMARY KEY,
            file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            qualified_name TEXT NOT NULL,
            kind TEXT NOT NULL,
            line INTEGER NOT NULL,
            end_line INTEGER,
            UNIQUE(file_id, qualified_name, line)
        );
        CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
        CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_id);

        CREATE TABLE IF NOT EXISTS imports(
            id INTEGER PRIMARY KEY,
            file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            target TEXT NOT NULL,
            line INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_imports_target ON imports(target);

        CREATE TABLE IF NOT EXISTS calls(
            id INTEGER PRIMARY KEY,
            file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            caller_symbol_id INTEGER REFERENCES symbols(id) ON DELETE CASCADE,
            callee_name TEXT NOT NULL,
            line INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_name);
        CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_symbol_id);

        CREATE TABLE IF NOT EXISTS call_edges(
            caller_symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
            callee_symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
            call_id INTEGER NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
            PRIMARY KEY(caller_symbol_id, callee_symbol_id, call_id)
        );
        CREATE INDEX IF NOT EXISTS idx_call_edges_callee ON call_edges(callee_symbol_id);
        """
    )
    con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))


def candidate_files(repo: Path) -> list[Path]:
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-co", "--exclude-standard", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        rels = [Path(x.decode("utf-8", "surrogateescape")) for x in p.stdout.split(b"\0") if x]
        files = [repo / r for r in rels]
    except (OSError, subprocess.CalledProcessError):
        files = []
        for base, dirs, names in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for name in names:
                files.append(Path(base) / name)

    out = []
    for p in files:
        if p.suffix.lower() not in EXT_LANG:
            continue
        try:
            if not p.is_file() or p.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        out.append(p)
    return sorted(set(out))


def file_sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(131072), b""):
            h.update(chunk)
    return h.hexdigest()


class PythonParser(ast.NodeVisitor):
    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.symbols: list[Symbol] = []
        self.imports: list[tuple[str, int]] = []
        self.calls: list[tuple[int | None, str, int]] = []
        self.stack: list[str] = []
        self.scope_indices: list[int] = []

    def _qualified(self, name: str) -> str:
        return ".".join([self.rel_path.replace("/", "."), *self.stack, name])

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append((alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        target = "." * node.level + (node.module or "")
        self.imports.append((target, node.lineno))
        self.generic_visit(node)

    def _visit_scope(self, node: ast.AST, name: str, kind: str) -> None:
        q = self._qualified(name)
        self.symbols.append(Symbol(name, q, kind, node.lineno, getattr(node, "end_lineno", None)))
        self.stack.append(name)
        self.scope_indices.append(len(self.symbols) - 1)
        self.generic_visit(node)
        self.scope_indices.pop()
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_scope(node, node.name, "class")

    def _visit_func(self, node: ast.AST, name: str) -> None:
        self._visit_scope(node, name, "function")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node, node.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node, node.name)

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        if name:
            caller = self.scope_indices[-1] if self.scope_indices else None
            self.calls.append((caller, name, getattr(node, "lineno", 0)))
        self.generic_visit(node)


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def parse_python(text: str, rel_path: str) -> ParsedFile:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ParsedFile([], [], [])
    p = PythonParser(rel_path)
    p.visit(tree)
    return ParsedFile(p.symbols, p.imports, p.calls)


def parse_generic(text: str, lang: str, rel_path: str) -> ParsedFile:
    symbols: list[Symbol] = []
    imports: list[tuple[str, int]] = []
    calls: list[tuple[int | None, str, int]] = []
    module = rel_path.replace("/", ".")
    patterns = GENERIC_FUNC_PATTERNS.get(lang, [])
    # Brace scopes are bound to the actual "{" that opens each definition, so
    # single-line bodies close on the same line and Allman-style braces on the
    # following line still open the right scope. Braces inside strings or
    # comments are not understood; this stays a heuristic parser. Ruby uses
    # def/end blocks and keeps the flat "latest definition" behavior.
    track_braces = lang != "ruby"
    # Open blocks: (index into symbols, depth its opening brace created).
    scope: list[tuple[int, int]] = []
    # Definition seen but its "{" not yet: (index into symbols, depth at the
    # definition). The next "{" opens its scope; a ";" at the same depth or a
    # block ending below it cancels it (forward declarations, braceless
    # arrow-function bodies).
    pending: tuple[int, int] | None = None
    depth = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat in IMPORT_PATTERNS:
            m = pat.search(line)
            if m:
                imports.append((m.group(1).strip(), lineno))
                break

        defined: str | None = None
        kind = "function"
        for pat in patterns:
            m = pat.search(line)
            if m:
                defined = m.group(1)
                break
        if defined is None:
            for pat in CLASS_PATTERNS:
                m = pat.search(line)
                if m:
                    defined = m.group(1)
                    kind = "type"
                    break
        if defined is not None:
            prefix = [symbols[i].name for i, _ in scope] if track_braces else []
            symbols.append(Symbol(defined, ".".join([module, *prefix, defined]), kind, lineno))
            if track_braces:
                pending = (len(symbols) - 1, depth)
            elif kind == "function":
                scope[:] = [(len(symbols) - 1, 0)]

        events: list[tuple[int, str, str | None]] = [
            (m.start(), "call", m.group(1)) for m in CALL_RE.finditer(line)
        ]
        if track_braces:
            events.extend((i, ch, None) for i, ch in enumerate(line) if ch in "{};")
            events.sort(key=lambda e: e[0])

        def_token_skipped = defined is None
        for _, event, payload in events:
            if event == "call":
                name = payload
                if name in CALL_STOPWORDS:
                    continue
                if not def_token_skipped and name == defined:
                    def_token_skipped = True
                    continue
                if pending is not None:
                    caller = pending[0]
                elif scope:
                    caller = scope[-1][0]
                else:
                    caller = None
                calls.append((caller, name, lineno))
            elif event == "{":
                depth += 1
                if pending is not None:
                    scope.append((pending[0], depth))
                    pending = None
            elif event == "}":
                depth -= 1
                while scope and depth < scope[-1][1]:
                    scope.pop()
                if pending is not None and depth < pending[1]:
                    pending = None
            elif pending is not None and depth <= pending[1]:  # ";"
                pending = None
    return ParsedFile(symbols, imports, calls)


def parse_file(path: Path, repo: Path) -> ParsedFile:
    rel = path.relative_to(repo).as_posix()
    lang = EXT_LANG[path.suffix.lower()]
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ParsedFile([], [], [])
    if lang == "python":
        return parse_python(text, rel)
    return parse_generic(text, lang, rel)


def replace_file_graph(con: sqlite3.Connection, repo: Path, path: Path, sha1: str) -> tuple[int, int, int]:
    rel = path.relative_to(repo).as_posix()
    st = path.stat()
    lang = EXT_LANG[path.suffix.lower()]
    row = con.execute("SELECT id FROM files WHERE path=?", (rel,)).fetchone()
    if row:
        file_id = row["id"]
        con.execute("DELETE FROM calls WHERE file_id=?", (file_id,))
        con.execute("DELETE FROM imports WHERE file_id=?", (file_id,))
        con.execute("DELETE FROM symbols WHERE file_id=?", (file_id,))
        con.execute(
            "UPDATE files SET language=?,mtime_ns=?,size=?,sha1=? WHERE id=?",
            (lang, st.st_mtime_ns, st.st_size, sha1, file_id),
        )
    else:
        cur = con.execute(
            "INSERT INTO files(path,language,mtime_ns,size,sha1) VALUES(?,?,?,?,?)",
            (rel, lang, st.st_mtime_ns, st.st_size, sha1),
        )
        file_id = cur.lastrowid

    parsed = parse_file(path, repo)
    symbol_rowids: list[int] = []
    for s in parsed.symbols:
        cur = con.execute(
            "INSERT INTO symbols(file_id,name,qualified_name,kind,line,end_line) VALUES(?,?,?,?,?,?)",
            (file_id, s.name, s.qualified, s.kind, s.line, s.end_line),
        )
        symbol_rowids.append(cur.lastrowid)
    for target, line in parsed.imports:
        con.execute("INSERT INTO imports(file_id,target,line) VALUES(?,?,?)", (file_id, target, line))
    for caller_idx, callee, line in parsed.calls:
        caller_id = symbol_rowids[caller_idx] if caller_idx is not None else None
        con.execute(
            "INSERT INTO calls(file_id,caller_symbol_id,callee_name,line) VALUES(?,?,?,?)",
            (file_id, caller_id, callee, line),
        )
    return len(parsed.symbols), len(parsed.imports), len(parsed.calls)


def rebuild_call_edges(con: sqlite3.Connection) -> int:
    con.execute("DELETE FROM call_edges")
    rows = con.execute(
        """
        SELECT c.id AS call_id, c.file_id, c.caller_symbol_id, c.callee_name
        FROM calls c
        WHERE c.caller_symbol_id IS NOT NULL
        """
    ).fetchall()
    inserted = 0
    for r in rows:
        targets = con.execute(
            "SELECT id FROM symbols WHERE name=? AND file_id=?",
            (r["callee_name"], r["file_id"]),
        ).fetchall()
        if not targets:
            targets = con.execute("SELECT id FROM symbols WHERE name=? LIMIT 32", (r["callee_name"],)).fetchall()
        for t in targets:
            if t["id"] == r["caller_symbol_id"]:
                continue
            con.execute(
                "INSERT OR IGNORE INTO call_edges(caller_symbol_id,callee_symbol_id,call_id) VALUES(?,?,?)",
                (r["caller_symbol_id"], t["id"], r["call_id"]),
            )
            inserted += 1
    return inserted


def cmd_index(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    db = Path(args.db).resolve() if args.db else default_db(repo)
    con = connect(db)
    init_schema(con)
    current = {p.relative_to(repo).as_posix(): p for p in candidate_files(repo)}
    existing = {r["path"]: r for r in con.execute("SELECT path,sha1 FROM files").fetchall()}

    removed = sorted(set(existing) - set(current))
    for rel in removed:
        con.execute("DELETE FROM files WHERE path=?", (rel,))

    changed = 0
    unchanged = 0
    symbols = imports = calls = 0
    for rel, path in current.items():
        sha1 = file_sha1(path)
        old = existing.get(rel)
        if old and old["sha1"] == sha1:
            unchanged += 1
            continue
        s, i, c = replace_file_graph(con, repo, path, sha1)
        symbols += s
        imports += i
        calls += c
        changed += 1

    edge_count = rebuild_call_edges(con)
    now = str(int(time.time()))
    con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('repo',?)", (str(repo),))
    con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('indexed_at',?)", (now,))
    con.commit()

    totals = con.execute(
        "SELECT (SELECT count(*) FROM files) files,"
        "(SELECT count(*) FROM symbols) symbols,"
        "(SELECT count(*) FROM imports) imports,"
        "(SELECT count(*) FROM calls) calls,"
        "(SELECT count(*) FROM call_edges) call_edges"
    ).fetchone()
    con.close()
    _json({
        "status": "indexed",
        "database": str(db),
        "changed_files": changed,
        "unchanged_files": unchanged,
        "removed_files": len(removed),
        "parsed_this_run": {"symbols": symbols, "imports": imports, "calls": calls},
        "totals": dict(totals),
        "resolved_call_edges": edge_count,
    })
    return 0


def open_existing(repo: Path, db_arg: str | None) -> tuple[sqlite3.Connection, Path]:
    db = Path(db_arg).resolve() if db_arg else default_db(repo)
    if not db.exists():
        raise SystemExit(f"codebase graph not indexed: {db}\nRun: python runtime/codebase_memory.py index --repo {repo}")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    if stored_schema_version(con) != str(SCHEMA_VERSION):
        raise SystemExit(
            f"codebase graph schema is outdated: {db}\n"
            f"Run: python runtime/codebase_memory.py index --repo {repo}"
        )
    return con, db


def cmd_status(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    db = Path(args.db).resolve() if args.db else default_db(repo)
    if not db.exists():
        _json({"status": "missing", "database": str(db)})
        return 1
    con, _ = open_existing(repo, args.db)
    meta = {r["key"]: r["value"] for r in con.execute("SELECT key,value FROM meta")}
    totals = con.execute(
        "SELECT (SELECT count(*) FROM files) files,"
        "(SELECT count(*) FROM symbols) symbols,"
        "(SELECT count(*) FROM imports) imports,"
        "(SELECT count(*) FROM calls) calls,"
        "(SELECT count(*) FROM call_edges) call_edges"
    ).fetchone()
    _json({"status": "ready", "database": str(db), "meta": meta, "totals": dict(totals)})
    return 0


def cmd_architecture(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    con, db = open_existing(repo, args.db)
    langs = [dict(r) for r in con.execute(
        "SELECT language,count(*) files FROM files GROUP BY language ORDER BY files DESC,language"
    )]
    dirs = Counter()
    for r in con.execute("SELECT path FROM files"):
        p = Path(r["path"])
        dirs[p.parts[0] if len(p.parts) > 1 else "."] += 1
    hotspots = [dict(r) for r in con.execute(
        """
        SELECT s.name,s.qualified_name,f.path,count(e.caller_symbol_id) inbound_calls
        FROM symbols s
        JOIN files f ON f.id=s.file_id
        LEFT JOIN call_edges e ON e.callee_symbol_id=s.id
        GROUP BY s.id
        ORDER BY inbound_calls DESC,s.name
        LIMIT ?
        """, (args.limit,)
    )]
    _json({
        "database": str(db),
        "languages": langs,
        "top_level_areas": [{"path": k, "files": v} for k, v in dirs.most_common(args.limit)],
        "hotspots": hotspots,
    })
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    con, _ = open_existing(repo, args.db)
    q = f"%{args.name}%"
    rows = [dict(r) for r in con.execute(
        """
        SELECT s.id,s.name,s.qualified_name,s.kind,f.path,s.line,s.end_line
        FROM symbols s JOIN files f ON f.id=s.file_id
        WHERE s.name LIKE ? OR s.qualified_name LIKE ?
        ORDER BY CASE WHEN s.name=? THEN 0 ELSE 1 END,s.name,f.path
        LIMIT ?
        """, (q, q, args.name, args.limit)
    )]
    _json({"query": args.name, "results": rows})
    return 0


def _find_symbol(con: sqlite3.Connection, name: str) -> sqlite3.Row:
    rows = con.execute(
        """
        SELECT s.id,s.name,s.qualified_name,s.kind,f.path,s.line
        FROM symbols s JOIN files f ON f.id=s.file_id
        WHERE s.name=? OR s.qualified_name=?
        ORDER BY CASE WHEN s.qualified_name=? THEN 0 ELSE 1 END,f.path
        LIMIT 20
        """, (name, name, name)
    ).fetchall()
    if not rows:
        raise SystemExit(f"symbol not found: {name}")
    if len(rows) > 1 and not any(r["qualified_name"] == name for r in rows):
        _json({"status": "ambiguous", "symbol": name, "candidates": [dict(r) for r in rows]})
        raise SystemExit(2)
    return rows[0]


def cmd_trace(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    con, _ = open_existing(repo, args.db)
    start = _find_symbol(con, args.symbol)
    direction = args.direction
    depth = max(1, min(args.depth, 8))
    seen = {start["id"]}
    q = deque([(start["id"], 0)])
    edges = []
    while q:
        node, d = q.popleft()
        if d >= depth:
            continue
        queries = []
        if direction in ("out", "both"):
            queries.append((
                "out",
                """
                SELECT e.callee_symbol_id AS next_id,a.name from_name,a.qualified_name from_q,
                       b.name to_name,b.qualified_name to_q,fb.path to_path
                FROM call_edges e
                JOIN symbols a ON a.id=e.caller_symbol_id
                JOIN symbols b ON b.id=e.callee_symbol_id
                JOIN files fb ON fb.id=b.file_id
                WHERE e.caller_symbol_id=?
                GROUP BY e.caller_symbol_id,e.callee_symbol_id
                """
            ))
        if direction in ("in", "both"):
            queries.append((
                "in",
                """
                SELECT e.caller_symbol_id AS next_id,a.name from_name,a.qualified_name from_q,
                       b.name to_name,b.qualified_name to_q,fa.path to_path
                FROM call_edges e
                JOIN symbols a ON a.id=e.caller_symbol_id
                JOIN symbols b ON b.id=e.callee_symbol_id
                JOIN files fa ON fa.id=a.file_id
                WHERE e.callee_symbol_id=?
                GROUP BY e.caller_symbol_id,e.callee_symbol_id
                """
            ))
        for dir_name, sql in queries:
            for r in con.execute(sql, (node,)):
                edges.append({
                    "depth": d + 1,
                    "direction": dir_name,
                    "from": r["from_q"],
                    "to": r["to_q"],
                    "path": r["to_path"],
                })
                nxt = r["next_id"]
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
    _json({"symbol": dict(start), "direction": direction, "depth": depth, "edges": edges[:args.limit]})
    return 0


def git_changed_files(repo: Path) -> list[str]:
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain=v1", "-z"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    out = []
    parts = p.stdout.split(b"\0")
    i = 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if not entry:
            continue
        text = entry.decode("utf-8", "replace")
        # Porcelain v1 -z renames/copies emit "XY new-path\0orig-path\0".
        # Keep both: the new path exists in the refreshed graph, the original
        # path still matters for stale imports of the old module name.
        paths = [text[3:]]
        if text[:2].strip()[:1] in {"R", "C"} and i < len(parts) and parts[i]:
            paths.append(parts[i].decode("utf-8", "replace"))
            i += 1
        out.extend(p.replace("\\", "/") for p in paths)
    return sorted(set(out))


def _like_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")


def _module_import_filter(module: str) -> tuple[str, list[str]]:
    """Match import targets on module boundaries ('.', '/') instead of substrings."""
    esc = _like_escape(module)
    patterns = [
        f"{esc}.%", f"{esc}/%",
        f"%.{esc}", f"%/{esc}",
        f"%.{esc}.%", f"%/{esc}/%", f"%/{esc}.%",
    ]
    clause = " OR ".join(["i.target = ?"] + ["i.target LIKE ? ESCAPE '\\'"] * len(patterns))
    return f"({clause})", [module, *patterns]


def cmd_impact(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    con, _ = open_existing(repo, args.db)
    if args.git_diff:
        changed = git_changed_files(repo)
    else:
        changed = [x.strip().replace("\\", "/") for x in args.files.split(",") if x.strip()]
    if not changed:
        _json({"changed_files": [], "affected": []})
        return 0

    placeholders = ",".join("?" for _ in changed)
    source_symbols = [dict(r) for r in con.execute(
        f"""
        SELECT s.id,s.name,s.qualified_name,f.path,s.line
        FROM symbols s JOIN files f ON f.id=s.file_id
        WHERE f.path IN ({placeholders})
        """, changed
    )]
    source_ids = [s["id"] for s in source_symbols]
    affected = []
    if source_ids:
        ph = ",".join("?" for _ in source_ids)
        affected = [dict(r) for r in con.execute(
            f"""
            SELECT DISTINCT caller.qualified_name symbol,ff.path,caller.line,'caller' reason
            FROM call_edges e
            JOIN symbols caller ON caller.id=e.caller_symbol_id
            JOIN files ff ON ff.id=caller.file_id
            WHERE e.callee_symbol_id IN ({ph})
            ORDER BY ff.path,caller.line
            LIMIT ?
            """, (*source_ids, args.limit)
        )]

    modules = {Path(p).stem for p in changed}
    modules |= {Path(p).with_suffix("").as_posix().replace("/", ".") for p in changed}
    import_hits = []
    for m in sorted(modules):
        clause, params = _module_import_filter(m)
        import_hits.extend(dict(r) for r in con.execute(
            f"""
            SELECT DISTINCT f.path,i.line,i.target,'import' reason
            FROM imports i JOIN files f ON f.id=i.file_id
            WHERE {clause}
            LIMIT ?
            """, (*params, args.limit)
        ))
    combined = affected + import_hits
    seen = set()
    uniq = []
    for x in combined:
        key = tuple(sorted(x.items()))
        if key not in seen:
            seen.add(key)
            uniq.append(x)
    _json({
        "changed_files": changed,
        "changed_symbols": source_symbols,
        "affected": uniq[:args.limit],
        "note": "Impact is structural evidence, not proof of completeness; verify decisive source paths.",
    })
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    con, _ = open_existing(repo, args.db)
    sql = args.sql.strip()
    if not re.match(r"^(SELECT|WITH)\b", sql, re.I):
        raise SystemExit("query is read-only: SQL must start with SELECT or WITH")
    rows = [dict(r) for r in con.execute(sql).fetchmany(args.limit)]
    _json({"rows": rows})
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Practical Coding embedded codebase graph")
    p.add_argument("--repo", default=".", help="repository root (default: current directory)")
    p.add_argument("--db", help="override SQLite graph path")
    sub = p.add_subparsers(dest="command", required=True)

    x = sub.add_parser("index", help="create or incrementally refresh the graph")
    x.set_defaults(func=cmd_index)

    x = sub.add_parser("status", help="show graph status and counts")
    x.set_defaults(func=cmd_status)

    x = sub.add_parser("architecture", help="show languages, top-level areas, and call hotspots")
    x.add_argument("--limit", type=int, default=20)
    x.set_defaults(func=cmd_architecture)

    x = sub.add_parser("search", help="search indexed symbols")
    x.add_argument("name")
    x.add_argument("--limit", type=int, default=50)
    x.set_defaults(func=cmd_search)

    x = sub.add_parser("trace", help="trace callers/callees of a symbol")
    x.add_argument("symbol")
    x.add_argument("--direction", choices=["in", "out", "both"], default="both")
    x.add_argument("--depth", type=int, default=3)
    x.add_argument("--limit", type=int, default=200)
    x.set_defaults(func=cmd_trace)

    x = sub.add_parser("impact", help="estimate blast radius for changed files")
    g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--git-diff", action="store_true", help="use files currently changed according to git status")
    g.add_argument("--files", help="comma-separated repository-relative paths")
    x.add_argument("--limit", type=int, default=200)
    x.set_defaults(func=cmd_impact)

    x = sub.add_parser("query", help="run read-only SQLite SELECT/WITH against the graph")
    x.add_argument("sql")
    x.add_argument("--limit", type=int, default=200)
    x.set_defaults(func=cmd_query)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
