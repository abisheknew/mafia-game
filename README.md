Mafia Game

This is an Online Mafia game where a moderator can host a game, have people join and then assign the roles. Each individual player can see their role and the moderator can see all assignments.

Recent changes
---------------
- 2026-06-10: Fix session/cookie collision bug where multiple visitors (for example, behind the same NAT or with identical browser fingerprints) could receive the same `device_id` and be treated as the same player. The server now generates a secure random `device_id` for visitors who don't already have a cookie, and caches it per-request. The player entry append is also now performed while holding the room lock to avoid a race condition.

Files added/updated for this fix
-------------------------------
- `mafia.py` — updated `get_device_id()` to generate secure random ids when no cookie exists and moved player append inside the lock.
- `simulate_joins.py` — helper script to simulate multiple clients joining a room and verify unique `device_id` assignment.
- `ChangeLog` — recorded the fix.

Running locally
---------------
Install requirements and run the server:

```bash
pip install -r requirements.txt
python mafia.py
```

Run the simulation (server must be running):

```bash
python simulate_joins.py
```

Notes
-----
- For production, set a strong `SECRET_KEY` environment variable. The `device_id` cookie is set with an expiration matching the room TTL by default.
- If you want additional protection, consider enforcing server-side validation that the number of joined players does not exceed the total configured roles (optional enhancement).
