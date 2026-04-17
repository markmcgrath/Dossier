# Open Source Release Hardening Specification

## Project: Career Ops Skill (Vault-First System)

## Objective

Prepare the repository for a high-quality public open-source release.

This is a release-hardening pass, not a feature expansion. Focus on correctness, clarity, security posture, and contributor readiness.

All changes must be:

- minimal and targeted
    
- deterministic
    
- aligned with current architecture (vault-first, human-in-the-loop)
    
- free of speculative features
    

---

## Global Constraints

1. Do not introduce new runtime dependencies unless explicitly required.
    
2. Do not change the core architecture or workflows.
    
3. Do not remove existing functionality.
    
4. All documentation must be precise, not aspirational.
    
5. If something is not implemented, do not describe it as automated.
    
6. All changes must be production-quality, not placeholders.
    

---

## Task 1: Add SECURITY.md

### Create file:

`/SECURITY.md`

### Requirements

Include the following sections:

1. Supported Versions
    
    - State current version support policy (e.g., latest only)
        
2. Reporting a Vulnerability
    
    - Provide a clear reporting path:
        
        - email placeholder: security@
            
        - or GitHub private disclosure
            
    - State expected response timeline (e.g., 72 hours acknowledgment)
        
3. Scope of Security Issues  
    Explicitly include:
    
    - data leakage
        
    - prompt injection vulnerabilities
        
    - unsafe handling of external/untrusted content
        
    - improper storage of sensitive data
        
    - integration credential exposure
        
4. Out-of-Scope
    
    - user misuse (e.g., pasting secrets into vault files)
        
    - unsupported integrations
        
5. Disclosure Policy
    
    - coordinated disclosure
        
    - fix before public announcement
        

Tone: professional, direct, not verbose.

---

## Task 2: Add GitHub Actions CI

### Create directory:

`.github/workflows/`

### Create file:

`.github/workflows/ci.yml`

### Requirements

Workflow must:

Trigger on:

- push
    
- pull_request
    

Jobs:

- run pytest
    
- fail on any test failure
    

Steps:

1. checkout
    
2. setup Python (use version from repo or default 3.11)
    
3. install dependencies (detect requirements.txt or equivalent)
    
4. run pytest
    

Constraints:

- no unnecessary matrix builds
    
- keep it simple and fast
    

---

## Task 3: Remove Development Artifacts

### Remove:

- `.pytest_cache/`
    
- any OS artifacts (e.g., .DS_Store)
    

### Add `.gitignore` entries if missing:

```
.pytest_cache/
__pycache__/
*.pyc
.DS_Store
```

Ensure repo reflects a clean publish state.

---

## Task 4: Fix START_HERE.md

### Problem

START_HERE.md references `/vault-template/` which does not exist.

### Required Action

Choose ONE:

Option A (preferred):

- Add `/vault-template/` directory
    
- Include minimal working structure:
    
    - cv.md
        
    - profile.md
        
    - dashboard.md
        
    - example eval/outreach files
        

Option B:

- Remove reference and rewrite instructions to use existing repo structure
    

### Additional Requirement

Ensure onboarding:

- works with zero ambiguity
    
- requires no guessing
    
- matches actual repo contents exactly
    

---

## Task 5: Correct Automation Claims

### Scope

Search all documentation for claims like:

- "automatically moves"
    
- "auto-generates"
    
- "system performs"
    

### Replace with:

If Claude-driven:

- "Claude can assist with…"
    

If manual:

- "manually move…"
    

If partially implemented:

- explicitly state limitation
    

No ambiguous wording allowed.

---

## Task 6: Add GitHub Issue and PR Templates

### Create directory:

`.github/`

### Files:

1. `.github/ISSUE_TEMPLATE/bug_report.md`
    
2. `.github/ISSUE_TEMPLATE/feature_request.md`
    
3. `.github/pull_request_template.md`
    

### Requirements

Bug report:

- steps to reproduce
    
- expected vs actual behavior
    
- environment
    

Feature request:

- problem statement
    
- proposed solution
    
- alternatives considered
    

PR template:

- summary of changes
    
- test coverage
    
- checklist:
    
    - tests pass
        
    - docs updated
        
    - no breaking changes (or documented)
        

Keep concise and structured.

---

## Task 7: Add CHANGELOG.md

### Create:

`/CHANGELOG.md`

### Format

Use Keep a Changelog style:

- versioned entries
    
- Added / Changed / Fixed sections
    

Initial version:

- describe current repo state as initial public release
    

---

## Task 8: Add Support Matrix to README

### Modify:

`README.md`

### Add section:

## Support Matrix

Include:

Supported:

- vault-first workflow
    
- Claude-assisted artifact generation
    
- local markdown-based system
    

Optional:

- Notion mirroring (if still transitional)
    

Not Supported:

- autonomous job applications
    
- unsupervised outbound messaging
    
- scraping bypasses or automation against platform TOS
    

Be explicit. No ambiguity.

---

## Task 9: Add Threat Model Summary to README

### Add section:

## Security Model (Summary)

Must include:

1. Human-in-the-loop requirement
    
2. External content is untrusted
    
    - job postings
        
    - emails
        
    - copied text
        
3. No automatic execution of instructions from external content
    
4. No credential storage in markdown files
    
5. User responsibility boundaries
    

Reference deeper docs (PRIVACY.md, DATA_CONTRACT.md).

---

## Task 10: Add Secrets Handling Guidelines

### Location:

README.md (summary) + optional separate doc

### Requirements

Clearly state:

- Never store:
    
    - API keys
        
    - tokens
        
    - credentials  
        in markdown files
        
- Use:
    
    - environment variables
        
    - platform secret stores
        
- Example:
    

```
DO NOT:
paste API keys into vault files

DO:
store secrets in environment variables
```

---

## Task 11: Align Notion Migration Messaging

### Problem

Tests indicate migration is incomplete.

### Required Action

Update all docs to:

- reflect current state truthfully
    
- remove implication that migration is complete
    

Example:

Replace:  
"Notion is no longer used"

With:  
"Notion support is being phased out; vault is the primary system"

Ensure consistency across:

- README
    
- docs
    
- tests (if needed)
    

---

## Task 12: Add Minimal LLM Safety Section

### Location:

README.md

### Content

Short, explicit:

- system does not execute arbitrary instructions
    
- model output is advisory, not authoritative
    
- external content may contain malicious instructions
    
- user must review all generated artifacts
    

Do not overcomplicate.

---

## Task 13: Final Consistency Pass

Claude must:

1. Validate:
    
    - all referenced files exist
        
    - no broken paths
        
    - no contradictory statements
        
2. Ensure:
    
    - terminology is consistent:
        
        - "vault"
            
        - "artifact"
            
        - "eval"
            
        - "outreach"
            
3. Ensure:
    
    - no placeholder text remains
        
    - no TODOs remain
        

---

## Deliverables

Claude must produce:

1. All new files listed above
    
2. All modified files updated in-place
    
3. A summary of changes including:
    
    - files added
        
    - files modified
        
    - files removed
        

---

## Acceptance Criteria

This release is considered ready when:

- tests pass locally and via CI
    
- onboarding works without confusion
    
- documentation matches actual behavior
    
- security reporting path exists
    
- no development artifacts remain
    
- repo appears intentional, not incidental
    

---

## Non-Goals

Do NOT:

- add new features
    
- redesign architecture
    
- introduce complex automation
    
- expand scope beyond release readiness
    

---

## Execution Instruction

Perform all tasks in a single pass.

If any ambiguity arises:

- choose the simplest, most conservative interpretation
    
- do not invent functionality
    
- document assumptions in the summary output