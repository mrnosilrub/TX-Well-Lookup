## Sprint P7 — Alerts & Notifications

### Goal
Users can watch an area and receive notifications on new nearby activity.

### Outcomes
- CRUD for alerts; delta pollers trigger notifications when matches occur

### You — Manual Tasks
- Choose notification provider (email or Slack); provision API keys and from-address/channel.

### Agent A — Backend Tasks
- Endpoints: `/v1/alerts` (CRUD: create, list, delete) with fields (user, center, radius, filters).
- Worker or job to receive matches from ingest and send notifications (provider SDK).

### Agent B — Data Pipeline Tasks
- Delta pollers for SDR (and RRC later) to detect new rows; publish matched events to the backend worker.

### Agent C — Web Tasks
- UI to create/list/delete alerts; validate inputs; show last-triggered time.

### Agent D — DevOps Tasks
- Store provider secrets; configure rate limiting and retry policies.

### Acceptance
- Creating an alert and simulating a new matched row sends a notification.

### Verification
```bash
curl -s -X POST https://api.<domain>/v1/alerts -d '{...}'
```


