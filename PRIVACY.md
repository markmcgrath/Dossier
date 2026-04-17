# Privacy & Security

This document maps every data flow through Dossier, names the external services involved, and outlines the threat model. It's not a legal document — it's a practical guide for understanding what data goes where and what you can do to protect it.

---

## Data Inventory

The table below maps each type of data to the services it may flow to.

| Data Type | Description | Flows to | Retention | Notes |
|-----------|-------------|----------|-----------|-------|
| **CV Content** | Work history, titles, dates, skills in `cv.md` | Anthropic (Claude) | Claude doesn't retain session-specific data beyond the conversation; we don't store copies server-side | You control the vault copy entirely. Only Anthropic sees it when you paste it into Claude for analysis or tailoring. |
| **Profile Data** | Target roles, match signals, role preferences in `profile.md` | Anthropic (Claude) | Not retained | You control it. Sent to Claude only when running evaluations. |
| **Contact Info** | Email, phone, LinkedIn URL | Anthropic, Gmail, Apollo, Indeed/Dice | Per-service terms | Email is shared with Gmail and Apollo. Phone/location are shared with Apollo. LinkedIn URL may be shared with Notion if configured. |
| **Salary Data** | Expected ranges, current comp, market research | Anthropic, Notion (optional) | Anthropic: not retained. Notion: until you delete. | Highly sensitive. If you use Notion, this data sits on their servers. If you don't, it stays local. |
| **Recruiter Emails** | Incoming messages from sourcers/recruiters | Gmail, Anthropic | Gmail: until you delete. Anthropic: not retained. | Anthropic may see these in Claude when you paste them for analysis. Gmail owns the originals. |
| **Calendar Events** | Interview dates, prep sessions, follow-ups | Google Calendar, Anthropic | Google: until you delete. Anthropic: not retained. | Shared with Google Calendar for scheduling. Anthropic only sees what you explicitly copy into a conversation. |
| **Contact Lookups** | Queries for candidate emails, phone numbers, social profiles | Apollo | Per Apollo ToS | Each lookup is a query to Apollo's database. They log the query and the result. |
| **LinkedIn Activity** | Profile views, messaging, connections | LinkedIn, Anthropic (optional) | LinkedIn: their retention. Anthropic: not retained if you paste. | LinkedIn owns all your activity. You control whether to share it with Anthropic (e.g., by pasting profile screenshots). |
| **Job Search Queries** | Indeed/Dice searches, filters, keyword history | Indeed/Dice, Anthropic | Indeed/Dice: their retention. Anthropic: not retained. | Search behavior is logged by Indeed/Dice. Anthropic sees job descriptions only if you copy them into a conversation. |
| **Vault Contents** | Everything in the Dossier folder (evals, outreach, prep, notes) | Anthropic, Notion (optional) | Anthropic: not retained. Notion: until you delete. | Local by default. Anthropic sees files only when you explicitly share them (e.g., paste content). Notion is only involved if you configure the integration. |
| **OAuth Tokens** | Gmail, Google Calendar, Apollo, LinkedIn, Notion (if configured) | Stored in your `.env` file | Until you revoke or delete the token | Tokens grant access to these services. Never commit `.env` to version control or share it. |

---

## Per-Service Risk Notes

### Anthropic (Claude)

**What data it receives:**
- CV, profile, job descriptions, recruiter emails, or any vault content you manually paste into conversations
- Conversation context (previous turns in the same thread)

**Retention:**
- Anthropic does not retain the text of your conversations after they end. Chat history is accessible to you on Anthropic's platform, but Anthropic's infrastructure is not trained on individual conversations in real-time.
- For details, see [Anthropic's Privacy Policy](https://www.anthropic.com/legal/privacy).

**Your controls:**
- You choose what to share. Only paste what's necessary.
- If discussing sensitive salary data or strategy, you can redact it before pasting.
- Delete conversations on the platform if you want to remove chat history.

**Mitigations:**
- Treat Claude conversations as ephemeral. If you need to preserve a sensitive output, save it locally and delete the conversation.
- Do not paste API keys, OAuth tokens, or passwords into Claude conversations.

---

### Gmail & Google Calendar

**What data they receive:**
- All emails sent to and from your email account (Gmail)
- All calendar events you create or receive invitations for (Google Calendar)
- Metadata: timestamps, recipients, sender IPs, event times

**Retention:**
- Google retains this data indefinitely unless you delete individual messages/events or your account.
- See [Google's Privacy Policy](https://policies.google.com/privacy).

**Your controls:**
- You own the data in your account. You can delete emails and events.
- You can revoke access to the Dossier skill at any time (disconnect OAuth in your Google Account settings).

**Mitigations:**
- Use a dedicated email account for job search if you're concerned about mixing personal and professional communication.
- Regularly delete sensitive recruiter emails or calendar events if you want to minimize what Google holds.
- Be aware that Google scans email content for spam and phishing detection (this is automatic and not under your control).

---

### Apollo (Contact Enrichment)

**What data it receives:**
- Email addresses you look up (for candidate outreach, person enrichment)
- Search queries (skill titles, company names, locations, technologies)
- Metadata from searches (filters applied, results returned)

**Retention:**
- Apollo logs all searches and enrichment requests. See [Apollo's Terms of Service](https://www.apollo.io/terms).
- Enriched contact data may be cached and resold (standard for B2B data platforms).

**Your controls:**
- You decide which contacts to enrich. Each lookup is logged.
- You can limit searches to reduce logging and cost.

**Mitigations:**
- Use Apollo sparingly for truly needed lookups (do not run exploratory searches if budget or privacy is a concern).
- Be aware that Apollo's data pipeline includes data brokers and public web scraping — any information you look up may have already been resold.
- Review your Apollo search history periodically to understand what queries you've made.

---

### Notion (Optional)

**Critical:** If you do not configure Notion as your pipeline tracker, **no data ever reaches Notion's servers**. The vault is the default source of truth.

**If you do configure Notion:**

**What data it receives:**
- Structured pipeline state: company name, role, grade, status, score, application date, location, compensation
- Any notes or descriptions you add to pipeline rows
- Integrations you set up (e.g., Zapier, IFTTT) may add more data

**Retention:**
- Notion retains all data until you delete it. See [Notion's Privacy Policy](https://www.notion.so/privacy).
- Data is not deleted when you archive a row in Dossier; it remains on Notion's servers unless you manually remove it.

**Your controls:**
- You own all data in your Notion workspace. You can delete any row, database, or property.
- You can disconnect the Dossier integration without losing any Notion data.
- You can choose NOT to use Notion; the vault functions as a standalone system.

**Mitigations:**
- **Only enable Notion if you need it.** The vault is fully functional without Notion as a structured tracker.
- If you use Notion, do not include salary data, personal notes on interviewers, or other highly sensitive information.
- Regularly audit your Notion pipeline database for sensitive data and delete if necessary.
- Enable Notion's workspace security features (two-factor authentication, IP allowlisting if available).

---

### LinkedIn

**What data it receives:**
- Your profile (publicly visible information)
- Messages you send and receive
- Connections, endorsements, activity
- View history (who views your profile)

**Retention:**
- LinkedIn retains all of this indefinitely. See [LinkedIn's Privacy Policy](https://www.linkedin.com/legal/privacy-policy).

**Your controls:**
- You control your profile visibility and messaging.
- You can control who sees your activity and who can message you.
- You own the data in your account and can delete messages, but LinkedIn may retain backups.

**Mitigations:**
- Be intentional about outreach. LinkedIn logs all messaging and connection activity.
- Be mindful of profile information — assume it's public and permanent.
- Review your LinkedIn privacy settings regularly (e.g., "Show your profile in search results", "Allow endorsements").
- Do not paste sensitive information (salary expectations, negotiation strategy) into LinkedIn messages.

---

### Indeed & Dice

**What data they receive:**
- Search history (keywords, filters, saved jobs)
- Job applications (resume, cover letter, application metadata)
- Profile information (resume, contact info, skills, work history)
- Clicks and engagement (which jobs you view)

**Retention:**
- Indeed and Dice retain search history, applications, and profile data indefinitely. See their privacy policies.

**Your controls:**
- You control which jobs you apply to and what resume/cover letter you submit.
- You can delete or update your profile.
- You can opt out of email alerts and messaging.

**Mitigations:**
- Use a dedicated resume for Indeed/Dice if you want to control which version reaches employers.
- Be selective about which jobs you apply to — each application is logged.
- Regularly review your saved jobs and applications to understand your search pattern.
- Disable messaging if you don't want recruiter contact through the platform.

---

## Threat Model Summary

### Assets at Risk

1. **Personally Identifiable Information (PII)**
   - Email, phone, location, education, work history
   - Exposed primarily through Gmail, Apollo, LinkedIn, Indeed/Dice
   - If exfiltrated, could enable identity theft, unwanted contact, or social engineering

2. **Strategy Data**
   - Target companies, salary expectations, negotiation boundaries
   - Stored in vault (local) or Notion (remote if configured)
   - If exposed, could weaken negotiating position or reveal job-search status to current/future employers

3. **OAuth Tokens**
   - Access tokens for Gmail, Google Calendar, Apollo, LinkedIn, Notion (if configured)
   - Stored in `.env` file
   - If exfiltrated, could allow attacker to access your email, calendar, and platforms

4. **Vault Contents**
   - All evals, outreach, prep docs, notes
   - Stored locally (fully under your control) or synced to Notion (if configured)
   - If exfiltrated, could reveal full job-search pipeline, negotiation strategies, company research

### Adversary Scenarios

1. **Malware / Data Exfiltration**
   - **Attack:** Malware on your computer reads `.env` file and vault folder, uploads to attacker's server
   - **Impact:** All tokens stolen, all strategy data exposed
   - **Likelihood:** Medium (malware is common, but targeted exfiltration is lower probability)
   - **Mitigation:** Full-disk encryption, antivirus, avoid untrusted software

2. **Prompt Injection (Claude)**
   - **Attack:** Attacker embeds instructions in a job description or email you ask Claude to analyze ("Share your CV with me")
   - **Impact:** Claude might be tricked into repeating or reformatting sensitive data in a way that benefits attacker
   - **Likelihood:** Low (Claude has defenses, but not foolproof)
   - **Mitigation:** Do not paste entire vault contents. Share only the minimum needed. Review Claude's outputs before trusting them.

3. **Platform Enforcement / Account Takeover**
   - **Attack:** Your Gmail, Google, or LinkedIn account is compromised; attacker gains access to emails, calendar, messages
   - **Impact:** Real-time visibility into your job search, ability to send messages on your behalf
   - **Likelihood:** Medium (depends on your password hygiene and use of two-factor authentication)
   - **Mitigation:** Enable two-factor authentication on all accounts. Use strong, unique passwords. Regularly review account security settings.

4. **Supply-Chain Compromise**
   - **Attack:** Apollo, Indeed/Dice, or another upstream service is breached; attacker gains access to your data on their servers
   - **Impact:** Email, phone, search history, applications compromised
   - **Likelihood:** Medium (platforms are breach targets, but major platforms have strong security)
   - **Mitigation:** No perfect defense, but limit what you share with third parties. Use temporary contact info for early-stage prospects if possible.

5. **Notion Misconfiguration**
   - **Attack:** You accidentally share your Notion database with public link or wrong workspace members
   - **Impact:** Full pipeline strategy exposed to anyone with the link
   - **Likelihood:** Low (requires mistake on your part)
   - **Mitigation:** Do not use Notion if you don't need to. If you do, regularly audit sharing settings and disable public sharing.

### Mitigations

1. **Full-Disk Encryption**
   - Encrypt your entire drive so that if your computer is stolen, the vault and `.env` file are inaccessible.
   - See [OS-Specific Setup](#encryption-at-rest) below.

2. **Content Trust Boundary**
   - Only share what's necessary with Claude or any third party.
   - Redact sensitive information (salaries, personal notes) before sharing.
   - Review outputs before using them.

3. **Human-In-The-Loop (HITL) Design**
   - Never auto-send outreach without reviewing it first.
   - Always read Claude's suggestions before acting on them.
   - Manually verify that Dataview queries in the dashboard are correct before relying on them.

4. **Token Storage in Environment Variables**
   - Store OAuth tokens in `.env` file (not in vault, not in code)
   - Add `.env` to `.gitignore` if using version control
   - Rotate tokens periodically
   - Revoke tokens you no longer need

5. **Minimal Integration**
   - Only enable Notion if you truly need structured pipeline tracking.
   - Only enrich contacts via Apollo when necessary.
   - Disable features you don't use.

### What Dossier Does NOT Protect Against

1. **Platform Policy Changes**
   - Anthropic, Google, Apollo, LinkedIn, Indeed, Notion may change their privacy policies, data handling, or terms at any time.
   - You're subject to each platform's current policy.
   - Dossier cannot shield you from platform-side changes.

2. **Anthropic's Own Data Handling**
   - Anthropic may use conversation data for safety research or model improvement in aggregate.
   - While Anthropic does not train on individual conversations, you should assume they may review flagged content for safety purposes.
   - Read [Anthropic's Privacy Policy](https://www.anthropic.com/legal/privacy) for their current stance.

3. **Weak Passwords / Social Engineering**
   - If you reuse passwords, use weak passwords, or fall for phishing, no tool can protect you.
   - Dossier cannot verify that your accounts are actually yours or that you're not being social-engineered.

4. **Network Eavesdropping**
   - If you're on an untrusted network (public WiFi), traffic to Claude, Gmail, Apollo, etc. is encrypted end-to-end (HTTPS/TLS), but the network operator can see which services you're connecting to.
   - Dossier does not include a VPN. Use your own if you're concerned.

5. **Notion (if used) Misconfiguration**
   - Even with encryption at rest, if you misconfigure sharing or enable public links, data is exposed.
   - Dossier cannot force you to set correct permissions; that's your responsibility.

6. **Data Breaches at Third Parties**
   - If Apollo, Indeed, LinkedIn, or any external service is breached, your data on their servers is at risk.
   - You're subject to each platform's security posture.
   - Dossier is a local-first system and cannot control upstream platforms.

---

## Regulatory Notes

You are a job seeker using a personal tool. You are not a data controller collecting data on others (unless you're building a candidate database for recruiting, which Dossier doesn't do). These notes are informational only and not legal advice.

### GDPR (EU/EEA)

If you're in the EU/EEA or applying to EU companies:

- **Your data:** You are the data subject. You own your CV, profile, and job-search data in the vault.
- **Anthropic:** Anthropic is a data processor when you share your data with Claude. See [Anthropic's GDPR Addendum](https://www.anthropic.com/legal).
- **Apollo:** Apollo is a data controller/processor depending on jurisdiction. They process email and profile data. See their privacy policy.
- **Gmail / Google:** Google is the data controller. They process your emails and calendar.
- **LinkedIn:** LinkedIn is the data controller. They process your profile and activity.
- **Notion (if configured):** Notion is the data controller. They process your pipeline data.
- **Your rights:** You have the right to access, rectify, delete ("right to be forgotten"), and port your data. Exercise these rights with each service directly.

### CCPA / CPRA (California)

If you're in California or applying to CA-based companies:

- Similar to GDPR: you own your personal information.
- Platforms (Google, LinkedIn, Apollo, Notion) may sell or share your data. You have the right to opt out of data sales and request deletion.
- See each platform's "Do Not Sell My Information" or CCPA disclosures.

### LinkedIn Terms of Service

LinkedIn's ToS explicitly prohibits scraping and automated contact lookups. If you use Apollo to enrich LinkedIn profiles, ensure you're complying with:

- LinkedIn's [User Agreement](https://www.linkedin.com/legal/user-agreement)
- LinkedIn's [Scraping Policies](https://www.linkedin.com/help/linkedin/answer/56347)

Using Apollo for lookups should be fine (Apollo has partnerships with platforms), but do not scrape LinkedIn yourself or use third-party tools that violate LinkedIn's ToS.

### General Principle

Job search is a legitimate activity, and using a personal tool to manage it is not a regulatory issue. However:

- Be transparent if you're using email, phone, or LinkedIn to contact candidates or recruiter data.
- Do not build automated systems that circumvent platform ToS.
- If in doubt about a jurisdiction's regulations, consult a lawyer.

---

## Encryption at Rest

Your vault contains strategy data, contact info, and potential salary negotiations. At minimum, encrypt your disk so that if your computer is stolen, the data is inaccessible.

### macOS (FileVault)

1. Open **System Settings** → **Privacy & Security** → **FileVault**
2. Click **Turn On** and follow the prompts
3. Save your recovery key in a safe place (e.g., password manager, written down)
4. Wait for encryption to complete (may take hours for a full disk)

[macOS FileVault Documentation](https://support.apple.com/en-us/HT204837)

### Windows (BitLocker)

1. Open **Settings** → **System** → **Device encryption** (Windows 11 Home: use **Encrypt This Device**)
2. For full BitLocker: **Settings** → **Update & Security** → **Device encryption** or search "Manage BitLocker"
3. Click **Turn On BitLocker** and follow prompts
4. Save your recovery key in Microsoft Account or external drive

[Windows BitLocker Documentation](https://support.microsoft.com/en-us/windows/windows-bitlocker-overview-e8f438e7-aafc-4b68-97f5-79ba4d1b9537)

### Linux (LUKS)

If your drive is not encrypted, back up your data and re-encrypt during installation.

1. Use your distribution's installer to enable LUKS encryption during setup, or
2. For existing systems: `sudo cryptsetup luksFormat /dev/sdX` (careful: destructive)
3. On Ubuntu: **Settings** → **Privacy & Security** → **Disk Encryption** (if available)

[LUKS Documentation](https://guardianproject.info/howto/full-disk-encryption/)

Full-disk encryption is the single most effective protection against data exfiltration if your computer is lost or stolen.

---

## Data Retention

This vault maintains all job-search artifacts indefinitely (evals, outreach, prep, notes). When a company reaches a terminal state (Rejected, Passed, Offer Declined, or inactive for 90+ days), files are moved to `archive/[company-slug]/` but not deleted.

For the full retention policy, including active data rules, terminal data archival, optional compensation redaction, and the quarterly cleanup checklist, see [README.md § Vault discipline](README.md#vault-discipline).

**Summary:**
- **Active pipeline:** All files kept in `evals/`, `outreach/`, etc. for ongoing reference.
- **Terminal rows:** Moved to `archive/` and kept indefinitely (searchable, but out of main view).
- **Daily/weekly scans:** Time-decayed into date-sorted subfolders after ~60 files in `daily/` or ~26 in `weekly/`.

Nothing is deleted unless you explicitly choose to. Everything remains searchable.
