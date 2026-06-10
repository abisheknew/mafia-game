#!/usr/bin/env python3
import time, sys

# ensure requests is installed
try:
    import requests
except Exception:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

BASE = 'http://127.0.0.1:5051'

def wait_for_server(timeout=10.0):
    import time
    for _ in range(int(timeout * 5)):
        try:
            r = requests.get(BASE + '/healthz', timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False

if not wait_for_server(10):
    print('Server not reachable, exiting', file=sys.stderr)
    sys.exit(2)

ROOM = 'testroom_sim_' + str(int(time.time()))
HOST_PW = 'hp'

hs = requests.Session()
print('Creating room', ROOM)
resp = hs.post(BASE + '/create_room', data={'room_name': ROOM, 'host_password': HOST_PW}, allow_redirects=True, timeout=5)
print('create_room status', resp.status_code)
host_token = hs.cookies.get('host_token')
print('host_token cookie present:', bool(host_token))
if not host_token:
    print('No host token; abort', file=sys.stderr)
    sys.exit(3)

# Add a single role with count=2 (total roles < expected number of clients)
resp = hs.post(f'{BASE}/api/rooms/{ROOM}/roles', data={'role_name': 'Villager', 'role_count': '2', 'role_faction': ''}, timeout=5)
print('/roles add', resp.status_code, resp.text)

NUM_CLIENTS = 4
clients = []
names = []
for i in range(NUM_CLIENTS):
    s = requests.Session()
    name = f'Player{i+1}'
    r = s.get(f'{BASE}/room/{ROOM}', timeout=5)
    print(f'Client {name} GET /room status', r.status_code)
    r2 = s.post(f'{BASE}/room/{ROOM}/join', data={'name': name, 'password': ''}, allow_redirects=True, timeout=5)
    print(f'Client {name} POST /join status', r2.status_code)
    clients.append(s)
    names.append(name)
    time.sleep(0.05)

# Query debug info
dbg = hs.get(f'{BASE}/api/rooms/{ROOM}/debug', timeout=5)
print('DEBUG status', dbg.status_code)
try:
    js = dbg.json()
except Exception as e:
    print('Failed to parse debug json', dbg.text, file=sys.stderr)
    sys.exit(4)

print('Players in room:', len(js.get('players', [])))
for p in js.get('players', []):
    print(' -', p.get('name'), p.get('device_id'))

device_ids = [p.get('device_id') for p in js.get('players', [])]
unique = set(device_ids)
print('Unique device_ids:', len(unique), 'Expected:', NUM_CLIENTS)
for idx, s in enumerate(clients):
    print('Client', names[idx], 'cookies device_id=', s.cookies.get('device_id'), 'player_name=', s.cookies.get('player_name'))

if len(unique) == NUM_CLIENTS:
    print('PASS: all device_ids unique')
    sys.exit(0)
else:
    print('FAIL: duplicate device_ids found', file=sys.stderr)
    sys.exit(5)
