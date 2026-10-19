# Nexus directory auth (Investors + Funders)

Gated paths on `nexus.cleantechhub.net`:

- `/investors` and all subpaths (including `/investors/data/investors.json`)
- `/p/funders`

Public paths remain unchanged: `/p/home`, `/ideas`, `/p/startup-portfolio`, `/mentor-directory`, etc.

## Access policy (staff only)

**Only `@cleantechhub.net` emails** may sign in or use magic links. Public self-registration is **disabled** (`403 registration_disabled`); staff accounts are provisioned via magic link or ops.

| Action | Non-CTH email | `@cleantechhub.net` |
|--------|---------------|---------------------|
| Register | `403 registration_disabled` | `403 registration_disabled` |
| Login | `403 staff_email_required` | Allowed |
| Magic link | `403 staff_email_required` | Allowed (auto-provisions account) |

Non-staff accounts created during testing are purged on API startup (`purge_users_outside_domain`).

Override domain (rare): `NEXUS_AUTH_ALLOWED_DOMAIN=cleantechhub.net` in `.env`.

## How it works

1. **Caddy `forward_auth`** calls `GET /nexus-auth/check` on the Flask API (`127.0.0.1:5050`) before serving gated content.
2. Valid **`nexus_dir_session`** cookie for an allowed email → `200` → content served.
3. Unauthenticated JSON → `401` JSON.
4. Unauthenticated HTML → redirect to `/nexus-auth/?next=…` (staff login/register wall).

## User flows

| Flow | Endpoint |
|------|----------|
| Register (disabled) | `POST /nexus-auth/api/register` → `403 registration_disabled` |
| Login | `POST /nexus-auth/api/login` |
| Magic link | `POST /nexus-auth/api/magic-link` → email → `GET /nexus-auth/verify/<token>` |
| Logout | `POST /nexus-auth/api/logout` |
| Session probe | `GET /nexus-auth/api/me` |

SQLite DB: `/opt/cth-nexus/data/nexus_auth.db`

## Staff bypass

Configure in `/opt/cth-nexus/.env`:

```env
NEXUS_AUTH_STAFF_EMAILS=gideon.blaauw@cleantechhub.net
NEXUS_AUTH_STAFF_TOKEN=<secret>
NEXUS_AUTH_ALLOWED_DOMAIN=cleantechhub.net
```

**Bearer token (curl / scripts):** bypasses cookie auth for gated JSON/HTML.

```bash
curl -sI -H "Authorization: Bearer $NEXUS_AUTH_STAFF_TOKEN" \
  https://nexus.cleantechhub.net/investors/data/investors.json
```

**Allowlisted emails** in `NEXUS_AUTH_STAFF_EMAILS` remain documented for ops; all `@cleantechhub.net` addresses follow the same register/login/magic-link rules.

## UI copy

- Gate page (`static/nexus-auth/gate.html`): staff-only messaging, not “register for investor network”.
- Nav lock tooltip (`/var/www/nexus-assets/nexus-nav.js`): “Solo staff CTH (@cleantechhub.net) / CTH staff only”.

## Test checklist

```bash
# Unauthenticated → gate or 401
curl -sI https://nexus.cleantechhub.net/investors | head -5
curl -sI https://nexus.cleantechhub.net/p/funders | head -5
curl -sI https://nexus.cleantechhub.net/investors/data/investors.json | head -5

# Public still OK
curl -sI https://nexus.cleantechhub.net/p/home | head -3
curl -sI https://nexus.cleantechhub.net/mentor-directory | head -3

# Staff bearer → 200 on JSON
curl -sI -H "Authorization: Bearer $NEXUS_AUTH_STAFF_TOKEN" \
  https://nexus.cleantechhub.net/investors/data/investors.json | head -3

# Non-CTH register/login → 403
curl -s -X POST https://nexus.cleantechhub.net/nexus-auth/api/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","name":"Test","password":"password123"}'
curl -s -X POST https://nexus.cleantechhub.net/nexus-auth/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"password123"}'

# Register disabled for all emails
curl -s -X POST https://nexus.cleantechhub.net/nexus-auth/api/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@cleantechhub.net","name":"You","password":"password123"}'

# CTH login → cookie → gated 200 (after account exists)
curl -s -c /tmp/nexus-cookie.txt -X POST https://nexus.cleantechhub.net/nexus-auth/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@cleantechhub.net","password":"your-password"}'
curl -sI -b /tmp/nexus-cookie.txt https://nexus.cleantechhub.net/investors | head -3
```

## Service reload

```bash
sudo systemctl restart cth-nexus
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```
