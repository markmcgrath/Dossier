# Mode 10: Calendar Ops (Google Calendar) — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User mentions scheduling an interview, wants a prep block before an upcoming interview, asks to set up follow-up reminders, wants a standing pipeline-review slot, or asks "what interviews do I have coming up." Also triggers automatically as a follow-on action from Modes 1, 3, and 9 when the right moment arises.

**Why this mode exists:** Job searches run on cadence — 24-hour thank-yous, 7-day follow-ups, 90-minute prep blocks the day before an interview. Without calendar scaffolding, these slip. This mode uses Google Calendar's `create_event`, `list_events`, `find_free_time`, and `update_event` to put structure around the pipeline.

**Core workflows:**

**Interview Prep Blocking.** When an interview is confirmed (via email, user statement, or Mode 3 invocation):
1. Use `list_events` to find the interview event on the user's calendar.
2. Use `find_free_time` to locate a 90-minute slot within 24 hours before the interview (prefer the evening before, or morning-of if unavoidable).
3. Create a calendar event titled `Prep: [Company] — [Role]` with:
   - The Mode 3 prep doc pasted into the description (or a link to the file in Dossier folder)
   - A 15-minute reminder
   - Marked as busy
4. Tell the user the block is set and point to the prep doc.

**Follow-up Reminders.** When the user indicates they've applied (or when Mode 9 status sync changes status to Applied):
1. Create a private all-day event titled `Follow up: [Company] — [Role]` at day 7 after application.
2. Event description includes: the role, the eval file path and `dashboard.md`, and suggested action ("Check Gmail thread; if no response, draft a follow-up via Mode 9").
3. Optionally create a second reminder at day 14 for a final nudge before marking the application dormant.

**Post-Interview Task Scheduling.** When an interview is logged as complete:
1. Create an event `Thank-you due: [Company]` the same day (or next morning if the interview was late), as a reminder to run Mode 9's thank-you flow within the 24-hour window.
2. Create a follow-up reminder at day 7 if no update has been received.

**Weekly Pipeline Review.** On demand or as a standing setup:
1. Use `find_free_time` to locate a 30-minute slot each Monday morning (check user's preference if not known).
2. Create a recurring event titled `Pipeline review — Dossier` with a description that points to `dashboard.md` and lists the review checklist: new grades > B to apply to, stale "Applied" rows needing follow-up, interviews this week needing prep, offers pending decision.
3. This becomes the weekly cadence that keeps the pipeline from drifting.

**Interview Roster View.** When the user asks "what interviews do I have this week":
1. Use `list_events` with a date range filter and search terms like `interview` or specific company names from eval files with `status: Interviewing`.
2. Surface them with date, time, company, role, interviewer (if visible in the event), and whether prep is done (check for a matching `Prep:` event).
3. Offer to run Mode 3 for any without a prep doc.

**Operating principles:**

- **Don't pollute the calendar.** All dossier events should be on a specific calendar if the user has one set up for this, or marked private otherwise. Never invite other people to these events.
- **Confirm before creating.** For anything other than a straightforward prep block tied to an already-confirmed interview, show the user what you plan to create and wait for approval.
- **Use titles with a consistent prefix** (`Prep:`, `Follow up:`, `Thank-you due:`, `Pipeline review —`) so events are easy to find and delete in bulk later.
- **Respect busy/free signals.** When scheduling prep, `find_free_time` should avoid stacking dossier events over actual work meetings. If there's no clean slot, tell the user rather than forcing it in.
- **Don't delete user events.** Only delete or update events this skill previously created.
