import paramiko
import requests
import logging
import datetime
import time
import os.path
from config import *

if os.path.exists("config.json") == False:
    node_info()

logging.basicConfig(
    format="%(levelname)s - %(asctime)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    filename="update.log",
    encoding="utf-8",
    level=logging.INFO,
)

logging.getLogger("paramiko").setLevel(logging.WARNING)

command = 'sudo apt-get update -y && sudo apt-get --with-new-pkgs upgrade -y && sudo apt autoremove -y && cd zelflux && git checkout . && git checkout master && git reset --hard origin/master && git pull && echo "UPDATE FINISHED" && sudo reboot'

file = open("config.json", "r")
json_obj = json.loads(file.read())
file.close()

nodes_list = []
for key in json_obj:
    nodes_list.append(key)

properties = json_obj

block_rate = 120


def check_if_restart_finished(node_real_ip):
    if ":" not in node_real_ip:
        node_real_ip = node_real_ip + ":16127"
    response = requests.get(
        f"https://fluxnode.app.runonflux.io/api/v1/node-single/{node_real_ip}"
    ).json()
    try:
        tier = response["node"]["results"]["benchmarks"]["data"]["status"]
    except:
        return "not ready"
    if tier != "CUMULUS" and tier != "STRATUS" and tier != "NIMBUS":
        return "not ready"
    else:
        return "finished"


def get_time_difference(node_name):
    file = open(f"update_times.json", "r")
    json_obj = json.loads(file.read())
    file.close()
    last_date = datetime.datetime.strptime(json_obj[node_name], "%Y-%M-%d").date()
    today = datetime.datetime.now().date()
    difference = (today - last_date).days
    return difference


def get_last_date(node_name):
    file = open(f"update_times.json", "r")
    json_obj = json.loads(file.read())
    file.close()
    last_date = datetime.datetime.strptime(json_obj[node_name], "%Y-%M-%d").date()
    return last_date


def get_last_confirmed_height(node_real_ip):
    flux_nodes = requests.get(
        "https://explorer.runonflux.io/api/status?q=getFluxNodes"
    ).json()
    for item in flux_nodes["fluxNodes"]:
        if item["ip"] == node_real_ip:
            last_confirmed_height = int(item["last_confirmed_height"])
            break
    if last_confirmed_height:
        return last_confirmed_height
    else:
        return 0


def get_current_height():
    explorer = requests.get("https://explorer.runonflux.io/api/sync").json()
    if explorer["status"] == "finished":
        current_height = int(explorer["height"])
        return current_height
    else:
        return 0


def upgrade_node(
    node_real_ip, node_local_ip, node_username, node_password, sudo_password, node_name
):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        node_local_ip,
        username=node_username,
        password=node_password,
    )
    stdin, stdout, stderr = client.exec_command(command)
    stdin.write(sudo_password + "\n")
    stdin.flush()
    output = stdout.read()
    if "UPDATE FINISHED" in str(output):
        client.close()
        today = datetime.datetime.now().date()
        file = open(f"update_times.json", "w")
        json_obj = json.loads(file.read())
        json_obj[node_name] = str(today)
        file.write(json_obj)
        file.close()
        logging.info("Update finished. Waiting for node to restart.")
        while check_if_restart_finished(node_real_ip) == "not ready":
            logging.info("Sleeping for 1 minute.")
            time.sleep(60)
        else:
            logging.info(f"Finished updating {node_name}.")
            return "finished"
    else:
        print(output)
        logging.error(f"There was an error updating {node_name}.")


def update(
    node_name, node_real_ip, node_local_ip, node_username, node_password, sudo_password
):
    diff = get_time_difference(node_name)
    if diff > 0:
        last_date = get_last_date(node_name)
        logging.info(f"The node {node_name} was updated on {last_date}.")
        node_updateable = True
    else:
        logging.info(f"The node {node_name} was updated today.")
        return "today"
    last_confirmed_height = get_last_confirmed_height(node_real_ip)
    if last_confirmed_height == 0:
        logging.critical(f"The last confirmed height could not be determined.")
        node_updateable = False
    else:
        logging.info(f"The last confirmed height is {last_confirmed_height}.")
        node_updateable = True
    current_height = get_current_height()
    if current_height > 0:
        logging.info(f"Current height is {current_height}.")
        node_updateable = True
    else:
        logging.critical(f"The current height could not be determined.")
        node_updateable = False
    win = block_rate - (current_height - last_confirmed_height)
    if win <= 0:
        logging.warning(f"Maintenance window for {node_name} is closed.")
        return "wait for maintenance"
    elif win * 2 >= 30:
        logging.info(f"Maintenance window is {win*2} minutes.")
    if node_updateable:
        upgrade_node(
            node_real_ip,
            node_local_ip,
            node_username,
            node_password,
            sudo_password,
            node_name,
        )
        return "finished"


for node in nodes_list:
    while properties[node]["updated"] == False:
        node_props = properties[node]
        if node_props["wait"] == 10:
            time.sleep(600)
        update_result = update(
            node,
            node_props["real_ip"],
            node_props["local_ip"],
            node_props["username"],
            node_props["password"],
            node_props["sudo_password"],
        )
        if update_result == "wait for maintenance":
            properties[node]["wait"] = 10
        elif update_result == "finished":
            properties[node]["updated"] = True
        elif update_result == "today":
            properties[node]["updated"] = True
