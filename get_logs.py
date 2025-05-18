#!/usr/bin/env python3

import paramiko
import re
import os

LOG_DIR = "./SQL2019/Logs"
STATE_FILE = "last_log_collected.txt"
LOCAL_DIR = "new_logs"


def parse_timestamp(filename):
    m = re.search(r"(\d{10})", filename)
    return m.group(1) if m else None


def find_new_logs(filenames, last_ts):
    new = []
    for fn in filenames:
        ts = parse_timestamp(fn)
        if ts and ts > last_ts:
            new.append((ts, fn))
    return [fn for ts, fn in sorted(new, key=lambda x: x[0])]


def get_logs():
    host = "ftpus.pointclickcare.com"
    port = 22
    username = "bdrkrrdbuser"
    password = "YkOcpadSzXH02NB1"

    os.makedirs(LOCAL_DIR, exist_ok=True)

    if not os.path.exists(STATE_FILE):
        print(f"{STATE_FILE} not found")
        return
    with open(STATE_FILE, "r") as f:
        last_ts = f.read().strip()

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    all_files = sftp.listdir(LOG_DIR)
    new_files = find_new_logs(all_files, last_ts)

    if not new_files:
        print("No new logs to download")
    else:
        for fn in new_files:
            remote = f"{LOG_DIR}/{fn}"
            local = os.path.join(LOCAL_DIR, fn)
            print(f"Downloading {remote} → {local}")
            sftp.get(remote, local)
        latest_ts = parse_timestamp(new_files[-1])
        with open(STATE_FILE, "w") as f:
            f.write(latest_ts)
        print(f"Updated {STATE_FILE} to {latest_ts}")

    sftp.close()
    transport.close()
