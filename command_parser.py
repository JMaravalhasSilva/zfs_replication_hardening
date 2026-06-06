import os
import re
import sys
from datetime import datetime, UTC


dataset_regex  = r"[A-Za-z0-9._/-]+"
snapshot_regex = r"[A-Za-z0-9._:-]+"
flags          = r"-[A-Za-z](?: -[A-Za-z])*" # Match multiple flags like -V -p -w -L -c -i
zfs_opts       = r"[a-z]+(?:[ ,][a-z]+)*"    # Match comma-separated lowercase options like "filesystem,volume"

ALLOWED_CMDS = [
      r"",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs list -t snapshot -H -o name -s name (-r|-d\ \d+) {dataset_regex} 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs get {flags} {zfs_opts} type {dataset_regex} 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs list -t {zfs_opts} -H -o name -s name (-r|-d\ \d+) {dataset_regex} 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs list -t {zfs_opts} -H -o {zfs_opts} -s name (-r|-d\ \d+) {dataset_regex} 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs get {flags} {zfs_opts} {zfs_opts} {dataset_regex} 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs send -V 2>&1'",
    rf"""sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin sh -c '"'"'\(zfs send {flags} {dataset_regex}@{snapshot_regex} -L -c {dataset_regex}@{snapshot_regex} & PID=\$!; echo "zettarepl: zfs send PID is \$PID" 1>&2; wait \$PID\)'"'"''""",
    rf"""sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin sh -c '"'"'\(zfs send {flags} {dataset_regex}@{snapshot_regex} & PID=\$!; echo "zettarepl: zfs send PID is \$PID" 1>&2; wait \$PID\)'"'"''""",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin ps -o command -p \d+ 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs get {flags} {zfs_opts} used {dataset_regex} 2>&1'",
      rf"sh -c 'PATH=\$PATH:/usr/local/sbin:/usr/sbin:/sbin zfs list {flags} {zfs_opts} {flags} name -s name -r 2>&1'",
]

date = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
original_cmd = os.environ['SSH_ORIGINAL_COMMAND']

for allowed_command in ALLOWED_CMDS:
    if re.fullmatch(allowed_command, original_cmd):
        print("[ALLOWED] " + date + ": " + original_cmd)
        sys.exit(0)

print("[DENIED] " + date + ": " + original_cmd)
sys.exit(1)
