# Examples

每个例子展示 Practical Coding 如何同时控制实现成本与上下文成本。示例描述的是策略，不代表任何特定 agent 的固定行为。

Each example shows how Practical Coding controls both implementation cost and context cost. These are policy examples, not guaranteed behavior of any particular agent.

---

## 1. Over-building a simple capability

**Request:** "Add a date picker to the signup form."

**Typical over-engineered outcome:**

```text
+ package.json                    (new dependency)
+ src/components/DatePicker.tsx   (wrapper component)
+ src/components/DatePicker.css
+ src/utils/dateFormat.ts         (timezone helpers "for later")
```

**With the skill** — Direct Path / Core ladder:

```html
<input type="date" name="birthdate" required>
```

The native platform feature satisfies the current requirement, so the ladder stops there.

---

## 2. Defensive bloat around a config read

**Request:** "Read the API base URL from the config file."

**Typical over-engineered outcome:**

```ts
function getApiBaseUrl(): string {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const raw = fs.readFileSync(CONFIG_PATH, "utf8");
      const parsed = JSON.parse(raw ?? "{}");
      return parsed?.api?.baseUrl ?? DEFAULT_BASE_URL ?? "";
    } catch {
      // swallow and retry
    }
  }
  return "";
}
```

**With the skill** — use the established contract unless a real failure boundary requires more:

```ts
function getApiBaseUrl(): string {
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
  return config.api.baseUrl;
}
```

Retries, fallback chains, and broad catches are not added speculatively.

---

## 3. Process overhead on a trivial edit

**Request:** "Change the button text from 'Submit' to 'Save'."

**With a fixed-pipeline workflow:**

```text
1. Brainstorming
2. PLAN.md
3. New branch/worktree
4. New unit test for the literal label
5. One-line change
6. Review/checkpoint ceremony
```

**With the skill** — Direct Path:

```diff
- <button>Submit</button>
+ <button>Save</button>
```

Run only the cheapest focused check actually required by the repository or the requested success condition.

---

## 4. Routine code lookup does not load Navigation

**Request:** "Where is `normalize_header()` defined, and which nearby caller uses it for Authorization?"

The location can be established with a narrow symbol/text lookup and two targeted reads:

```text
symbol/text search: normalize_header
  -> headers.py::normalize_header
  -> headers.py::get_header
  -> headers.py::auth_header
```

No reasoning module is selected, `references/navigation.md` is not loaded, and no graph backend is required. Search is ordinary Direct work because the next action is already clear.

---

## 5. Ranked retrieval is an optional accelerator

**Request:** "Find the likely authentication implementation in this unfamiliar repository."

If the host already exposes bounded/ranked retrieval — for example a native ranked code search or FFF-style search — use it to return a small candidate set:

```text
1. src/auth/JwtService.ts
2. src/middleware/AuthMiddleware.ts
3. src/routes/login.ts
```

Then read only the material candidates. If no ranked capability exists, fall back to narrow filename/text/symbol search such as `rg`, `grep`, or the host equivalent. Practical Coding does not install FFF or another search engine merely for this task.

---

## 6. Structural retrieval is used for structural questions

**Request:** "Map every service that calls the billing client and where each response is transformed."

This is relationship-heavy. If an already-integrated structural index such as Codebase Memory is available and materially reduces repeated source exploration, query the graph for the relevant callers/paths and then verify the material files in current source.

If no structural backend is available, continue with bounded source search. Do not create `.practical-coding.yaml`, install Codebase Memory, or add a persistent MCP/service solely to complete the lookup.

The desired output is a compact evidence map such as:

```text
services/api.py::checkout
  -> shared/billing.py::charge
  -> services/api.py::to_checkout_response

services/jobs.py::retry_invoice
  -> shared/billing.py::charge
  -> services/jobs.py::to_retry_record
```

not a raw repository tour, grep dump, or graph transcript.
