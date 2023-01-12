# FLUX Node Updater

## Description

This is a simple script that will update your nodes every day (if set with a cron job) one by one.

## How it works

The script uses [paramiko](https://www.paramiko.org/) to establish SSH connection with the node, and then runs the following command

`sudo apt-get update -y && sudo apt-get --with-new-pkgs upgrade -y && sudo apt autoremove -y && cd zelflux && git checkout . && git checkout master && git reset --hard origin/master && git pull && echo "UPDATE FINISHED" && sudo reboot`

Once the node has been restarted, it will wait for it to fully start and finish benchmarks. After that, it will continue with other nodes.

**IMPORTANT** - the script will automatically check whether it has enough time to do the upgrade and restart the node. If the maintenance window is 30 minutes or less, the script will wait patiently until the maintenance window has been reset.

## How to configure the script

1. Clone the repo and cd into the folder
2. Create a virtual environment - `python3 -m venv env`
3. Activate the environment - `source env/bin/activate`
4. Install the requirements - `pip3 install -r requirements.txt`
5. Deactivate the environment - `deactivate`
6. Run the script - `env/bin/python3 main.py`

Once you run the script, it will go over the configuration first. You will have to enter the following details for all of your nodes:

* Node name - enter the alias of your node.
* Username - the node username (to establish SSH connection).
* Password - the node password (to establish SSH connection).
* Sudo password - to successfully run the above mentioned command.
* Local IP - the local IP of your node (without the port)  (to establish SSH connection).
* Real IP - the real IP with the port ending on 7. For example 176.12.10.10:16177.

## Donations

If you want to buy me a coffee, feel free to donate any FLUX amount to **t1P2GfcmF9HBEFTuoCGNNqXKuPgCjEjCHFw**

Happy FLUXing :-)
