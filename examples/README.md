# Examples

每个例子展示 Practical Coding 如何同时控制实现成本与上下文成本。示例描述的是策略，不代表任何特定 agent 的固定行为。

Each example shows how Practical Coding controls both implementation cost and context cost. These are policy examples, not guaranteed behavior of any particular agent.

---

## 1. Over-building a simple capability

**Request:** "Add a date picker to the signup form."

A native platform control satisfies the current requirement:

```html
<input type="date" name="birthdate" required>
```

No dependency, wrapper component, timezone helper, or speculative configuration is added.

---

## 2. R0 Direct Locate

**Request:** "Where is `normalize_header()` defined, and which nearby caller uses it for Authorization?"

The symbol is exact, so Retrieval starts and stops at R0:

```text
exact symbol lookup: normalize_header
  -> headers.py::normalize_header
  -> headers.py::auth_header
```

Read only the definition and material caller. Navigation, ranked discovery, evidence expansion, and graph tracing are unnecessary.

---

## 3. R1 Ranked Discovery

**Request:** "Where is login state restored in this unfamiliar application?"

The intent is known but file and symbol names are not. R0 cannot identify a target, so it loads only R1. A ranked hybrid provider may return:

```text
1. src/session/SessionBootstrap.ts
2. src/auth/restoreSession.ts
3. src/routes/AppGuard.tsx
```

The provider is an implementation of R1, not a tree node. Verify the best candidates in current source. If one candidate proves the answer, return without R2.

---

## 4. R2 Evidence Expansion

**Request:** "Why does refresh-token rotation behave this way?"

R1 locates `TokenService`, but the claim also depends on one filter, authoritative configuration, and focused tests. R2 builds only that evidence set:

```text
TokenService
AuthFilter
SecurityConfig
TokenServiceTest
```

It does not read adjacent authentication modules merely because they are related.

---

## 5. R3 Structural Trace

**Request:** "Map every service that calls the billing client and where each response is transformed."

The answer is relational. R2 loads R3, which uses an available graph provider and verifies the resulting paths in current source:

```text
services/api.py::checkout
  -> shared/billing.py::charge
  -> services/api.py::to_checkout_response

services/jobs.py::retry_invoice
  -> shared/billing.py::charge
  -> services/jobs.py::to_retry_record
```

At runtime, if no graph provider exists, R3 reconstructs only the required edges with bounded reference tracing. It remains a leaf; there is no whole-repository "stronger search" stage.

---

## 6. Navigation is not Retrieval

**Request:** "In this unfamiliar monorepo, which package owns plugin lifecycle execution?"

Navigation may first return a bounded map from root module declarations:

```text
platform API -> progress-core -> lifecycle package
```

Retrieval then starts at R0 inside that scope. Navigation does not run semantic search or trace callers itself.

---

## 7. Output compaction is not a route

A noisy focused test can pass through an output adapter:

```text
npm test -- src/lib/exportFilename.test.ts
  -> output compaction layer
  -> exit status + failures or concise pass evidence
```

The execution and Retrieval paths do not change. If the compact result omits one diagnostic needed for a failure, retrieve that bounded detail rather than disabling compaction globally.
