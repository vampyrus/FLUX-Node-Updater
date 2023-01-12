import json
import datetime


def node_info():
    properties = {}
    nodes_list = []
    while True:
        data = input("How many nodes would you set-up for auto update?\n")
        if not data.isnumeric():
            print("Please use only digits.")
        else:
            number_of_nodes = int(data)
            break
    for i in range(number_of_nodes):
        print(f"Now configuring node {i+1}")
        prop = {}
        while True:
            data = ""
            data = input("Please enter the name of your node\n")
            if data:
                nodes_list.append(data)
                break
        while True:
            data = ""
            data = input("Please enter the username of your node\n")
            if data:
                prop["username"] = data
                break
        while True:
            data = ""
            data = input("Please enter the password of your node\n")
            if data:
                prop["password"] = data
                break
        while True:
            data = ""
            data = input("Please enter the SUDO password of your node\n")
            if data:
                prop["sudo_password"] = data
                break
        while True:
            data = ""
            data = input("Please enter the local IP of your node\n")
            if data:
                prop["local_ip"] = data
                break
        while True:
            data = ""
            data = input(
                "Please enter the real IP of your node with the port (if applicable)\n"
            )
            if data:
                prop["real_ip"] = data
                break
        prop["updated"] = False
        prop["wait"] = 0
        properties[nodes_list[i]] = prop
    file = open("config.json", "w")
    file.write(json.dumps(properties, indent=4))
    file.close()
    file = open("update_times.json", "w")
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(1)
    obj = {}
    for key in properties:
        obj[key] = str(yesterday)
    file.write(json.dumps(obj, indent=4))
    file.close()
