# Bug Report Templates

Standard templates for clear, reproducible, actionable bug documentation.

---

## 跨项目禅道 Bug 模板

适用于在不同项目的禅道产品、项目和模块下创建 Bug。填写前先确认当前项目的产品 ID、项目 ID、模块 ID，以及已导入禅道的来源用例 ID。

### 禅道字段填写规则

| 禅道字段 | 填写规则 |
|----------|----------|
| **Bug 标题** | 只写清晰、具体的问题描述；不要写 `REQ-xxx` 或用例编号。 |
| **产品 / 项目 / 模块** | 使用当前项目对应的禅道 ID。 |
| **来源用例** | 在选择框中选择禅道数字用例 ID，例如 `47542`；不要填写 `TC-xxx` 文本。 |
| **关键词** | 填写 `REQ-xxx` 和来源用例编号；已导入禅道时可追加真实 `zentao_case_id`。 |
| **优先级 / 严重程度 / Bug 类型** | 按项目规则和实际影响填写，不从标题推断。 |
| **重现步骤** | 使用下方中文分段格式，确保每个区块单独换行。 |

### 可直接填写的重现步骤模板

填写前必须先清空重现步骤编辑器（全选删除默认、占位或预填内容），再输入/粘贴下方模板内容；禁止在残留内容上追加。

```html
<p><span>[前置条件]</span></p>
<p><span>{{前置条件}}</span></p>
<p></p>

<p><span>[步骤]</span></p>
<p><span>1. {{操作步骤}}</span></p>
<p><span>2. {{操作步骤}}</span></p>
<p></p>

<p><span>[结果]：</span></p>
<p><span>{{实际结果}}</span></p>
<p></p>

<p><span>[期望]</span></p>
<p><span>{{期望结果}}</span></p>
<p></p>

<p><span>[证据]</span></p>
<p><img src="{{截图}}" /></p>
```

### 证据处理规则

1. 优先将截图直接嵌入禅道“证据”区域。
2. 只有截图无法嵌入时，才通过禅道附件上传。
3. 不填写本地截图路径、`file://` 地址或仅本机可访问的链接。
4. 使用附件时，在“证据”区注明附件名称。
5. 截图应与当前 Bug、来源用例和实际失败结果对应。

### 创建前检查清单

- [ ] 标题只描述问题，不含 REQ 或用例编号。
- [ ] “来源用例”已选择禅道数字用例 ID，例如 `47542`。
- [ ] 关键词已包含 REQ 和来源用例信息。
- [ ] 前置条件、步骤、结果、期望、证据分别换行。
- [ ] 截图已优先嵌入证据区；无法嵌入时才上传附件。
- [ ] 证据区没有本地路径或本机链接。

---

## Standard Bug Report Template

```markdown
# BUG-[ID]: [Clear, Specific Title]

**Severity:** Critical | High | Medium | Low
**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Performance | Security | Data | Crash
**Status:** Open | In Progress | In Review | Fixed | Verified | Closed
**Assignee:** [Developer name]
**Reporter:** [Your name]
**Reported Date:** YYYY-MM-DD

---

## Environment

| Property | Value |
|----------|-------|
| **OS** | [Windows 11 / macOS 14 / Ubuntu 22.04] |
| **Browser** | [Chrome 120 / Firefox 121 / Safari 17] |
| **Device** | [Desktop / iPhone 15 / Samsung S23] |
| **Build/Version** | [v2.5.0 / commit abc123] |
| **Environment** | [Production / Staging / Dev] |
| **URL** | [Exact page URL] |

---

## Description

[2-3 sentences clearly describing what the bug is and its impact]

---

## Steps to Reproduce

**Preconditions:**
- [Any setup required before reproduction]
- [Test account: user@test.com]

**Steps:**
1. [Navigate to specific URL]
2. [Perform specific action]
3. [Enter specific data: "example"]
4. [Click specific button]
5. [Observe the issue]

**Reproduction Rate:** [Always / 8 out of 10 times / Intermittent]

---

## Expected Behavior

[Clearly describe what SHOULD happen]

---

## Actual Behavior

[Clearly describe what ACTUALLY happens]

---

## Visual Evidence

**Screenshots:**
- [ ] Before state: [attached]
- [ ] After state: [attached]
- [ ] Error message: [attached]

**Video Recording:** [Link if available]

**Console Errors:**
```
[Paste any console errors here]
```

**Network Errors:**
```
[Paste any failed requests here]
```

---

## Impact Assessment

| Aspect | Details |
|--------|---------|
| **Users Affected** | [All users / Subset / Specific role] |
| **Frequency** | [Every time / Sometimes / Rarely] |
| **Data Impact** | [Data loss / Corruption / None] |
| **Business Impact** | [Revenue loss / User frustration / Minimal] |
| **Workaround** | [Describe workaround if exists, or "None"] |

---

## Additional Context

**Related Items:**
- Feature: [FEAT-123]
- Test Case: [TC-xxx]
- Similar Bug: [BUG-789]
- Figma Design: [URL if UI bug]

**Regression Information:**
- Is this a regression? [Yes / No]
- Last working version: [v2.4.0]
- First broken version: [v2.5.0]

**Notes:**
[Any additional context that might help fix the issue]

---

## Developer Section (To Be Filled)

### Root Cause
[Developer fills in after investigation]

### Fix Description
[Developer describes the fix approach]

### Files Changed
- [file1.js]
- [file2.css]

### Fix PR
[Link to pull request]

---

## QA Verification

- [ ] Fix verified in dev environment
- [ ] Fix verified in staging
- [ ] Regression tests passed
- [ ] Related test cases updated
- [ ] Ready for production

**Verified By:** [QA name]
**Verification Date:** [Date]
**Verification Build:** [Build number]
```

---

## Quick Bug Report Template

For minor issues or fast documentation.

```markdown
# BUG-[ID]: [Title]

**Severity:** Low | Medium
**Environment:** [Browser, OS, Build]

## Issue
[One paragraph description]

## Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected
[What should happen]

## Actual
[What happens]

## Screenshot
[Attached]
```

---

## UI/Visual Bug Template

For design discrepancy reports.

```markdown
# BUG-[ID]: [Component] Visual Mismatch

**Severity:** Medium
**Type:** UI
**Figma Design:** [URL to specific component]

## Design vs Implementation

### Expected (Figma)
| Property | Value |
|----------|-------|
| Background | #0066FF |
| Font Size | 16px |
| Font Weight | 600 |
| Padding | 12px 24px |
| Border Radius | 8px |

### Actual (Implementation)
| Property | Expected | Actual | Match |
|----------|----------|--------|-------|
| Background | #0066FF | #0052CC | No |
| Font Size | 16px | 16px | Yes |
| Font Weight | 600 | 400 | No |
| Padding | 12px 24px | 12px 24px | Yes |
| Border Radius | 8px | 8px | Yes |

## Screenshots

**Figma Design:**
[Screenshot of Figma component]

**Current Implementation:**
[Screenshot of implemented component]

**Side-by-Side:**
[Comparison image]

## Impact
Users see inconsistent branding. Component appears different from approved design.
```

---

## Performance Bug Template

For speed, memory, or resource issues.

```markdown
# BUG-[ID]: [Feature] Performance Degradation

**Severity:** High
**Type:** Performance

## Performance Issue

**Affected Area:** [Page/Feature/API]
**User Impact:** [Page load slow / App unresponsive / High resource usage]

## Metrics

| Metric | Expected | Actual | Variance |
|--------|----------|--------|----------|
| Page Load Time | < 2s | 8s | +300% |
| API Response | < 200ms | 1500ms | +650% |
| Memory Usage | < 100MB | 450MB | +350% |
| CPU Usage | < 30% | 95% | +217% |

## Environment
- Data size: [Number of records]
- Network: [Connection type]
- Device specs: [RAM, CPU]

## Reproduction
1. [Load page with X records]
2. [Perform action]
3. [Observe slow response]

## Evidence
- Performance trace: [Link]
- Network waterfall: [Screenshot]
- Memory profile: [Screenshot]

## Baseline
- Previous version: [v2.4.0]
- Previous metric: [2s load time]
- Regression since: [v2.5.0]
```

---

## Security Bug Template

For vulnerabilities and security concerns.

```markdown
# BUG-[ID]: [Security Issue Title]

**Severity:** Critical
**Type:** Security
**OWASP Category:** [A01-A10]
**CONFIDENTIAL - DO NOT SHARE PUBLICLY**

## Vulnerability

**Type:** [XSS / SQL Injection / Auth Bypass / etc.]
**Risk Level:** Critical | High | Medium | Low
**Exploitability:** [Easy / Moderate / Difficult]

## Description
[Describe the vulnerability without providing exploit code]

## Impact
- [ ] Data exposure
- [ ] Privilege escalation
- [ ] Account takeover
- [ ] Service disruption
- [ ] Other: [specify]

**Affected Data:** [User PII / Payment info / etc.]

## Proof of Concept
[Describe how to verify the issue exists - sanitize any sensitive data]

## Recommended Fix
[High-level recommendation for remediation]

## References
- [CVE if applicable]
- [OWASP reference]

## Disclosure
- Internal report date: [Date]
- Expected fix date: [Date]
- Public disclosure: [N/A / Date if applicable]
```

---

## Crash/Error Bug Template

For application crashes and unhandled errors.

```markdown
# BUG-[ID]: [Crash/Error Description]

**Severity:** Critical
**Type:** Crash

## Error Details

**Error Type:** [Crash / Exception / Hang / White Screen]
**Error Message:**
```
[Exact error message]
```

**Stack Trace:**
```
[Full stack trace]
```

## Reproduction

**Frequency:** [Always / Intermittent]

1. [Step to trigger crash]
2. [Step 2]
3. [App crashes / shows error]

## Environment
- OS: [Version]
- App Version: [Build]
- Memory available: [If relevant]
- Device: [Model]

## Logs
```
[Relevant log entries before crash]
```

## Impact
- User data lost: [Yes/No]
- Session terminated: [Yes/No]
- Recovery possible: [Yes/No]
```

---

## Severity Definitions

| Level | Criteria | Response Time | Examples |
|-------|----------|---------------|----------|
| **Critical** | System down, data loss, security breach | < 4 hours | Login broken, payment fails, data exposed |
| **High** | Major feature broken, no workaround | < 24 hours | Search not working, checkout fails |
| **Medium** | Feature partial, workaround exists | < 1 week | Filter missing option, slow load |
| **Low** | Cosmetic, rare edge case | Next release | Typo, minor alignment, rare crash |

---

## Priority vs Severity Matrix

|  | Low Impact | Medium Impact | High Impact | Critical Impact |
|--|-----------|---------------|-------------|-----------------|
| **Rare** | P3 | P3 | P2 | P1 |
| **Sometimes** | P3 | P2 | P1 | P0 |
| **Often** | P2 | P1 | P0 | P0 |
| **Always** | P2 | P1 | P0 | P0 |

---

## Bug Title Best Practices

**Good Titles:**
- "[Login] Password reset email not sent for valid email addresses"
- "[Checkout] Cart total shows $0 when discount code applied twice"
- "[Dashboard] Page crashes when loading more than 1000 records"

**Bad Titles:**
- "Bug in login" (too vague)
- "It doesn't work" (no context)
- "Please fix ASAP!!!" (emotional, no information)
- "Minor issue" (unclear what the issue is)

---

## Bug Report Checklist

Before submitting:
- [ ] Title is specific and descriptive
- [ ] Steps can be reproduced by someone else
- [ ] Expected vs actual clearly stated
- [ ] Environment details complete
- [ ] Screenshots/evidence attached
- [ ] Severity/priority assigned
- [ ] Checked for duplicates
- [ ] Related items linked
