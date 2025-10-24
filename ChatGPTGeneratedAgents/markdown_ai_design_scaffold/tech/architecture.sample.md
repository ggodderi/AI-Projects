---
constraints:
  - "Keep bundle increase ≤ 30KB gz"
  - "SSR for landing route"
acceptance_criteria:
  - "API contract specified with request/response examples"
signoff_required_from: ["developer"]
---

## Architecture
- Client: React Native
- Web landing: Next.js SSR for /join
- Auth: OAuth (Google/Apple), email magic link
## API Contracts
POST /api/signup
- request: { email?, oauth_provider? }
- response: { user_id, next_step }
