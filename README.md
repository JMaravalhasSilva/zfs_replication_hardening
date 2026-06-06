# TrueNAS ZFS Replication Hardening

Local  - The machine which contains the dataset
Remote - The machine which will store the backup of the dataset

## 1) Remote - Create SSH Keypair
Go to "Credential" > "Backup Credentials".
Go to "SSH Keypairs" > "Add".
Choose a name for the SSH Keypair, and press "Generate Keypair". Here, we will assume the name is "replication_keypair".
Copy the contents inside the "Public Key" field, you will need to paste it later on the local machine.

## 2) Local - Create a new dataset for storing user homes
Assuming you don't already have a dataset for storing user homes, go to Datasets > Add Dataset.
For the "Name", write "User_Homes". Here, we will assume this will be under "Data/User_Homes".
For the "Dataset Preset", select "Generic".
Optionally, select Advanced Options and enable encription on this dataset. Don't forget to securely store the generated key.

## 3) Local- Create the user zfs_replication
Go to "Credentials" > "Users".
Select "Add".
For the username, write zfs_replication.
In the "Allow Access" area, make sure to deselect all options, except for "SSH Access".
Select "Disable Password"
In the "Public SSH Key", paste the public key you copied from the Remote machine in Step 1).
Edit the "Home Directory" field, ensure "Create Home Directory" is set, ensure "Default Permissions" is set, and then select /mnt/Data/User_Homes.
Press "Save".

## 4) Local - Setup port forwarding
Go to the settings of the router in the local machine's network. 
Forward a port of your choosing (can be the default 22) to your local machine's internal IP address. 
Ensure you ONLY allow the remote machine's IP and reject all others.

## 5) Local - Enable SSH
Go to "System" > "Services".
Edit the SSH options, ensure the TCP port is the one which you forwarded to in your router, and ensure "Allow Password Authentication", "Allow Kerberos Authentication" and "Allow TCP Port Forwarding" are ALL disabled.
Enable SSH.

## 6) Remote - Create SSH Connection
Go to "Credential" > "Backup Credentials".
Go to "SSH Connections" > "Add".
Choose a name for the SSH connection. Here, we will assume the name is "replication_ssh_connection".
Change the "Setup Method" to "Manual".
In the "Host", write the Local machine IP address.
In the "Port", choose the port which you forwarded in Step 4).
For the "Username", write "zfs_replication"
In the "Private Key" section, select "replication_keypair"
Select "Discover Remote Host Key". If everything is set up correctly up to this point, you should see a key appearing. Otherwise, you've probably messed up your router config or forgot to enable SSH in Step 5).

## 7) Local - Set up the scripts to be executed
Go to "System" > "Shell".
Execute "sudo su" and write your password.
Execute "cd /mnt/Data/User_Homes/zfs_replication".
Execute "touch cmd.sh && touch command_parser.py".
Edit the contents of cmd.sh and command_parser.py (using "vi", "nano" or equivalent), and paste the respective contens of those files in this repo.
Run "chown zfs_replication:zfs_replication cmd.sh".
Run "chmod +x cmd.sh".
Run "chown zfs_replication:zfs_replication command_parser.sh".


## 8) Local - Enable SSH forced command and harder the connection
Go to "Credentials" > "Users".
Edit the "zfs_replication" user.
In the "Public SSH Key" you should see something like "ssh-rsa ...". Edit this such that it now begins with:
"command="/mnt/Data/User_Homes/zfs_replication/cmd.sh",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty ssh-rsa ..."

## 9) Local - Setup ZFS delegation
TODO: write me

## 10) Remote - Set up a replication task via the UI as usual
Ensure that you do NOT use sudo for the replication task. TrueNAS will show you a popup with this, where you need to select "Cancel", otherwise this will not work.
