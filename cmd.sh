#!/bin/sh

log_file="/mnt/Data/User_Homes/zfs_replication/log.txt"

python command_parser.py >> $log_file

if [ $? -ne 0 ]; then
    exit 1
fi

exec /bin/sh -c "$SSH_ORIGINAL_COMMAND"
