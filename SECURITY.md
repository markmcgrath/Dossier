# Security Policy

## Supported Versions

Only the latest release on the `main` branch is supported. There is no backport policy.

## Reporting a Vulnerability

If you discover a security issue, please report it privately:

- **GitHub:** Use [Security Advisories](../../security/advisories/new) to open a private disclosure.
- **Email:** If GitHub private disclosure is unavailable, email the repository maintainer (see profile).

**Expected response:** Acknowledgment within 72 hours. Fix targeted within 14 days for confirmed issues.

Please do not open public issues for security vulnerabilities.

## Scope

The following are considered security issues:

- Data leakage — personal data (CV content, company names, email addresses) exposed through generated artifacts or logs
- Prompt injection — external content (job descriptions, emails, pasted text) manipulating the skill into unsafe behavior
- Credential exposure — API keys, tokens, or passwords stored in or surfaced through vault files
- Unsafe handling of untrusted content — the skill executing instructions embedded in job postings or email bodies

## Out of Scope

- User misuse (e.g., intentionally pasting secrets into vault files)
- Integrations not documented in the project (third-party tools, custom MCP servers)
- AI model accuracy — the skill produces advisory output, not authoritative decisions

## Disclosure Policy

We follow coordinated disclosure:

1. Reporter submits privately.
2. Maintainer acknowledges and investigates.
3. Fix is developed and tested.
4. Fix is released before public announcement.
5. Reporter is credited (unless they prefer anonymity).
