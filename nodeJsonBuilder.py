from colorama import Fore, Style, init
import re
import json
init()

print(Fore.YELLOW + "Welcome to the nodeJson builder!\n--------------------------------" + Style.RESET_ALL)

fileConfirmed = False
while not fileConfirmed:
    filePath = input(Fore.YELLOW + "Which Node JSON file are you writing to? " + Style.RESET_ALL)
    try:
        open(filePath, "r")
        if filePath.endswith(".json"):
            fileConfirmed = True
        else:
            print(Fore.RED + "File is not a JSON file" + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + "File does not exist" + Style.RESET_ALL)

with open(filePath, "r") as f:
    nodes = json.load(f)
    f.close()

print(Fore.YELLOW + "Ingame, press F3+C once, and paste it here.\nType 'exit' to exit." + Style.RESET_ALL)
newNodes = {}
e = False
while not e:
    pasted = input(Fore.YELLOW + "Paste: " + Style.RESET_ALL)
    if pasted == "exit":
        e = True
        print(Fore.YELLOW + "Exited" + Style.RESET_ALL)
        continue
    groups = re.search(r"@s (\S+) \S+ (\S+)", pasted)
    if groups == None:
        print(Fore.RED + "Invalid paste" + Style.RESET_ALL)
        continue
    x = int(float(groups.group(1)))
    y = int(float(groups.group(2)))

    nameConfirmed = False
    while not nameConfirmed:
        name = input(Fore.YELLOW + "Node name: " + Style.RESET_ALL)
        if name in nodes.keys() or name in newNodes.keys():
            print(Fore.RED + "Node already exists; do you want to override its current value?")
            print(nodes[name] if name in nodes.keys() else newNodes[name])
            if input("Type 'y' to confirm: " + Style.RESET_ALL) != "y":
                continue
        nameConfirmed = True

    newNodes[name] = {"x": x, "y": y, "connections": []}

with open(filePath, "r+") as f:
    d = json.load(f)
    d.update(newNodes)
    f.seek(0)
    f.truncate()
    json.dump(d, f, indent=4)
    f.close()

print(Fore.YELLOW + "Written to " + filePath + Style.RESET_ALL)