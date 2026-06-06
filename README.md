# TrueNAS ZFS Replication Hardening

All available tutorials on how to do ZFS replication on TrueNAS assume that the remote backup machine is never compromised. Some say that "pull replication" is safer, which it is, but the way TrueNAS operates just assumes that the backup machine is never compromised. 

There has been some talk about [hardening the replication setup](https://www.youtube.com/watch?v=AvYx9O6wN20), but TrueNAS does NOT support this out of the box, and tutorials are almost nonexistent. Worse, some, like [this one](https://www.youtube.com/watch?v=uEJq2UW_Ct8), **confidently tell you to allow the replication user to run "sudo zfs", meaning that if the backup machine is ever compromised, a malicious actor can just destroy the data on the backup machine and then run "sudo zfs destroy" on the main machine**. 

This repo contains instructions on how to do proper hardening. It disables password login, disables funny business like allowing the compromised backup machine to SSH hop into other machines in the main machine's network, does NOT use sudo, properly uses ZFS delegation instead of handling a hacker a way to destroy all of your data. It also runs strict validation of the commands that the backup machine issues, so that a backup machine may NEVER run unauthorized commands beyond retrieving the datasets to be backed up.

This tutorial uses the following names for the two machines:
- Local  - The machine which contains the dataset
- Remote - The backup machine which will 

## 1) Remote - Create SSH Keypair
- Go to "Credential" > "Backup Credentials".
- Go to "SSH Keypairs" > "Add".
- Choose a name for the SSH Keypair, and press "Generate Keypair". Here, we will assume the name is "replication_keypair".
- Copy the contents inside the "Public Key" field, you will need to paste it later on the local machine.

## 2) Local - Create a new dataset for storing user homes
- Assuming you don't already have a dataset for storing user homes, go to Datasets > Add Dataset.
- For the "Name", write "User_Homes". Here, we will assume this will be under "Data/User_Homes".
- For the "Dataset Preset", select "Generic".
- Optionally, select Advanced Options and enable encription on this dataset. Don't forget to securely store the generated key.

## 3) Local- Create the user zfs_replication
- Go to "Credentials" > "Users".
- Select "Add".
- For the username, write zfs_replication.
- In the "Allow Access" area, make sure to deselect all options, except for "SSH Access".
- Select "Disable Password"
- In the "Public SSH Key", paste the public key you copied from the Remote machine in Step 1).
- Edit the "Home Directory" field, ensure "Create Home Directory" is set, ensure "Default Permissions" is set, and then select /mnt/Data/User_Homes.
- Press "Save".

## 4) Local - Setup port forwarding
- Go to the settings of the router in the local machine's network. 
- Forward a port of your choosing (can be the default 22) to your local machine's internal IP address. 
- Ensure you ONLY allow the remote machine's IP and reject all others.

## 5) Local - Enable SSH
- Go to "System" > "Services".
- Edit the SSH options, ensure the TCP port is the one which you forwarded to in your router, and ensure "Allow Password Authentication", "Allow Kerberos Authentication" and "Allow TCP Port Forwarding" are ALL disabled.
- Enable SSH.

## 6) Remote - Create SSH Connection
- Go to "Credential" > "Backup Credentials".
- Go to "SSH Connections" > "Add".
- Choose a name for the SSH connection. Here, we will assume the name is "replication_ssh_connection".
- Change the "Setup Method" to "Manual".
- In the "Host", write the Local machine IP address.
- In the "Port", choose the port which you forwarded in Step 4).
- For the "Username", write "zfs_replication"
- In the "Private Key" section, select "replication_keypair"
- Select "Discover Remote Host Key". If everything is set up correctly up to this point, you should see a key appearing. Otherwise, you've probably messed up your router config or forgot to enable SSH in Step 5).

## 7) Local - Set up the scripts that will validate the incoming SSH commands
- Go to "System" > "Shell".
- Execute `sudo su` and write your password.
- Execute `cd /mnt/Data/User_Homes/zfs_replication`.
- Execute `touch cmd.sh && touch command_parser.py`.
- Edit the contents of cmd.sh and command_parser.py (using "vi", "nano" or equivalent), and paste the respective contens of those files in this repo.
- Run `chown zfs_replication:zfs_replication cmd.sh`.
- Run `chmod +x cmd.sh`.
- Run `chown zfs_replication:zfs_replication command_parser.sh`.


## 8) Local - Enable SSH forced command and harder the connection
- Go to "Credentials" > "Users".
- Edit the "zfs_replication" user.
- In the "Public SSH Key" you should see something like "ssh-rsa ...". Edit this such that it now begins with:
"command="/mnt/Data/User_Homes/zfs_replication/cmd.sh",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty ssh-rsa ..."

## 9) Local - Setup ZFS delegation
- For each dataset you wish to replicate, you must allow the user zfs_replication to run "zfs send": `zfs allow -u zfs_replication send DATASET_NAME`
  - Example: `zfs allow -u zfs_replication send Data/my_dataset`

## 10) Remote - Set up a replication task via the UI as usual
Ensure that you do NOT use sudo for the replication task. TrueNAS will show you a popup with this, where you need to select "Cancel", otherwise this will not work.
