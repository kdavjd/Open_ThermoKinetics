# Question Templates

Clarifying questions organized by feature type for requirement gathering.

## New Feature Questions

### Core Requirements (Round 1)

**Functionality**
- What is the primary user goal this feature enables?
- What specific actions can users perform?
- What are the inputs (user data, files, selections)?
- What are the expected outputs (displayed data, files, state changes)?

**Users & Roles**
- Who can access this feature? (all users, specific roles, admins only)
- Are there different experiences for different roles?
- Should this be visible in navigation or accessed via URL?

**Success Criteria**
- What defines "done" for this feature?
- How will we know it works correctly?
- What are the key performance indicators? (response time, user engagement)

### Technical Details (Round 2)

**Database**
- Do we need new tables? What entities?
- Any new relationships between existing tables?
- Do we need to track history/audit trail?

**API**
- What API endpoints are needed? (GET, POST, PUT, DELETE)
- What data formats? (JSON, file upload, form data)
- Are there rate limits or quotas?

**Frontend**
- New pages or changes to existing pages?
- Any new UI components needed?
- Real-time updates needed? (WebSocket, polling)
- Mobile responsive requirements?

### Implementation (Round 3)

**Stages**
- What's the minimum viable version? (MVP)
- What can be added in future iterations?
- Are there dependencies on other features?

**Testing**
- What edge cases should be tested?
- What are the failure scenarios?
- How to simulate production-like conditions?

---

## Bug Fix Questions

### Core Requirements (Round 1)

**Problem Definition**
- What is the exact bug behavior? (error message, incorrect output, crash)
- What is the expected behavior?
- How often does this occur? (always, intermittent, specific conditions)

**Reproduction**
- What steps trigger the bug?
- Are there specific data values or states that cause it?
- Browser/environment specific? (Chrome only, production only)

**Impact**
- Who is affected? (all users, specific subset)
- What is the business impact? (blocked workflow, data loss, annoyance)
- Is there a workaround?

### Technical Details (Round 2)

**Root Cause**
- Where in the code is the issue? (module, function, line)
- What is the actual vs expected code behavior?
- Are there multiple code paths affected?

**Fix Approach**
- What's the proposed fix?
- Are there side effects of changing this code?
- Do we need to refactor or can we patch?

### Implementation (Round 3)

**Testing**
- How to verify the fix works?
- How to ensure we haven't broken anything else?
- Should we add a regression test?

**Deployment**
- Is this a hotfix or scheduled release?
- Any data migration needed?

---

## UI Enhancement Questions

### Core Requirements (Round 1)

**User Experience**
- What is the current user pain point?
- What is the improved experience?
- Which page(s) are affected?

**Visual Design**
- Are there design mockups or references?
- Any brand/style guidelines?
- Mobile, desktop, or both?

### Technical Details (Round 2)

**Components**
- New components needed or modify existing?
- Any third-party UI libraries?
- Responsive breakpoints?

**Interactions**
- User interactions needed? (click, drag, keyboard)
- Animations or transitions?
- Real-time feedback?

### Implementation (Round 3)

**Browser Support**
- Which browsers to support?
- Minimum versions?

**Accessibility**
- WCAG compliance needed?
- Screen reader support?
- Keyboard navigation?

---

## Integration Questions

### Core Requirements (Round 1)

**External Service**
- What service are we integrating with? (API name, documentation)
- What data flows in/out?
- What triggers the integration?

**Authentication**
- How do we authenticate? (API key, OAuth, client certificate)
- Where are credentials stored?

### Technical Details (Round 2)

**API**
- What are the endpoints? (URL, method, parameters)
- What is the rate limit?
- How do we handle errors? (retries, fallbacks, notifications)

**Data Mapping**
- How does external data map to our models?
- Any transformations needed?
- How to handle missing/invalid data?

### Implementation (Round 3)

**Testing**
- How to test without hitting production API?
- Mock API or test environment?
- What responses to simulate?

**Monitoring**
- How to monitor integration health?
- Alert on failures?
- Logging level?

---

## Refactoring Questions

### Core Requirements (Round 1)

**Current State**
- What is the problem with current code? (maintainability, performance, technical debt)
- Why refactor now? (blocked feature, too complex, bug-prone)

**Goals**
- What is the desired state?
- What are the success metrics? (code quality, test coverage, performance)

### Technical Details (Round 2)

**Scope**
- Which files/modules are affected?
- Are we breaking existing APIs?
- Do we need backward compatibility?

**Approach**
- What refactoring pattern? (extract method, rename, move, simplify)
- Any new patterns or frameworks?

### Implementation (Round 3)

**Testing**
- How to ensure behavior hasn't changed?
- Do we have tests for old code?
- What tests to add?

**Migration**
- Is there a data migration?
- Can we deploy incrementally?
- Rollback plan?
