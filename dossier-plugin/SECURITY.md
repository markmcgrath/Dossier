# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✓ Current |

Only the latest release on the `main` branch is supported. There is no backport policy.

## What Dossier Is

Dossier is a prompt-based Claude Code plugin — a collection of skill files, agent definitions, shell scripts, and hook configuration. It has no server-side components, no authentication system, and no network-accessible attack surface. Security concerns are primarily about data handling within the local vault and prompt-injection resilience.

## Threat Model

| Threat | Description |
|--------|-------------|
| Indirect prompt injection | A job description, recruiter email, or web page contains instruction-like text that manipulates the skill into unsafe behavior |
| PII leakage | Personal data (CV content, compensation, email addresses, Notion IDs) surfaces in generated artifacts or open-source files |
| Unauthorized external writes | The skill drafts or sends outreach, calendar invites, or tracker updates without explicit user approval |
| Credential exposure | API keys, tokens, or OAuth secrets are stored in vault files and accidentally committed |

## Reporting a Vulnerability

If you discover a security issue, please report it privately:

- **GitHub:** Use [Security Advisories](../../security/advisories/new) to open a private disclosure.
- **Email:** If GitHub private disclosure is unavailable, contact the repository maintainer (see profile).

**Please do not open public issues for security vulnerabilities.**

Expected response: acknowledgment within 72 hours. Fix targeted within 14 days for confirmed issues.

## Scope

The following are in scope:

- **Prompt injection** — external content (job descriptions, emails, pasted text) bypassing the Content Trust Boundary and triggering unintended tool actions
- **PII leakage** — personal data (CV content, company names, email addresses, Notion IDs) exposed through generated artifacts or logs
- **Credential exposure** — API keys, tokens, or passwords stored in or surfaced through vault files or the `bin/` scripts
- **Unauthorized side effects** — skill-triggered writes to external services (Notion, Gmail, Calendar) without user confirmation

## Out of Scope

- User misuse (e.g., intentionally pasting secrets into vault files)
- Integrations not documented in this project (third-party tools, custom MCP servers)
- AI model accuracy — the skill produces advisory output, not authoritative decisions
- Issues in Claude Code itself — report those to Anthropic

## Disclosure Policy

We follow coordinated disclosure:

1. Reporter submits privately.
2. Maintainer acknowledges and investigates.
3. Fix is developed and tested.
4. Fix is released before public announcement.
5. Reporter is credited (unless they prefer anonymity).
