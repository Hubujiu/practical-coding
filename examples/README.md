# Examples

真实任务里，装与不装 Practical Coding 的差别。每个例子都是同一个请求的两种产出。

What the same request produces with and without Practical Coding.

---

## 1. Over-building a simple capability

**Request:** "Add a date picker to the signup form."

**Without the skill:**

```text
+ package.json          (new dependency: a date-picker library)
+ src/components/DatePicker.tsx   (wrapper component, 60 lines)
+ src/components/DatePicker.css
+ src/utils/dateFormat.ts         (timezone helpers "for later")
```

**With the skill** (Decision module: platform-native beats a new dependency):

```html
<input type="date" name="birthdate" required>
```

---

## 2. Defensive bloat around a config read

**Request:** "Read the API base URL from the config file."

**Without the skill:**

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

Retries for a local file read, a fallback chain nobody asked for, and a broad catch that hides a malformed config instead of reporting it.

**With the skill** (Implementation module: every failure path corresponds to a real boundary):

```ts
function getApiBaseUrl(): string {
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
  return config.api.baseUrl;
}
```

A missing or malformed config file is a startup error the operator must see, not a condition to silently paper over. If a demonstrated failure mode appears later, handle that specific one and name it.

---

## 3. Process overhead on a trivial edit

**Request:** "Change the button text from 'Submit' to 'Save'."

**Without the skill (fixed-pipeline workflow):**

```text
1. Brainstorming session about button copy
2. PLAN.md written and confirmed
3. New branch + worktree created
4. Unit test asserting the button label
5. The one-line change
6. Two review passes, checkpoint commit, execution log updated
```

**With the skill** (router: Implementation only, evidence = the diff):

```diff
- <button>Submit</button>
+ <button>Save</button>
```

One file changed, verified by reading the diff. Necessary gates the project itself defines (CI, required reviews) still apply; the skill only removes ceremony no one required.
