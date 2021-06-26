import blessed
import re
import json
import click
term = blessed.Terminal()

import renderer.internals.internal as internal
import renderer.misc as misc

print(term.yellow("Welcome to the plaJson builder!\n-------------------------------"))

plas, plaFile = internal.askFileName("PLA") # pylint: disable=no-member
nodes, _ = internal.askFileName("Node") # pylint: disable=no-member
skinName = input(term.yellow("Name of skin [blank for default]: "))
try:
    skin = misc.getSkin(skinName if skinName != '' else 'default')
except FileNotFoundError:
    skin = misc.getSkin('default')

newPlas = {}
e = False
while not e:
    nameConfirmed = False
    while not nameConfirmed:
        name = input(term.yellow("Name of new PLA (type 'exit' to exit): "))
        if name in plas.keys() or name in newPlas.keys():
            print(term.red("PLA already exists; do you want to override its current value?"))
            print(term.red(plas[name] if name in plas.keys() else newPlas[name]))
            if input(term.red("Type 'y' to confirm: ")) != "y":
                continue
        nameConfirmed = True
    
    if name == "exit":
        e = True
        print(term.yellow("Exited"))
        continue

    typeConfirmed = False
    while not typeConfirmed:
        type_ = input(term.yellow(f"PLA type of {name}: "))
        if not type_.split(" ")[0] in skin['types'].keys():
            print(term.red(f"Type {type_.split(' ')[0]} does not exist"))
            continue
        typeConfirmed = True
    displayname = input(term.yellow(f"Display name of {name}: "))
    description = input(term.yellow(f"Description of {name}: "))
    try:
        layer = float(input(term.yellow(f"Layer for {name}: ")))
    except ValueError: 
        layer = 0
    layer = int(layer) if int(layer) == layer else layer

    if skin['types'][type_.split(" ")[0]]['type'] == "point":
        nodeConfirmed = False
        while not nodeConfirmed:
            node = input(term.yellow("Node attached: "))
            if node not in nodes.keys():
                print(term.red("Node does not exist"))
                continue
            nodeConfirmed = True
        newNodes = [node]
    else:
        print(term.yellow("Nodes for {name}: Choose what to pre-write in node list editor: "), end="")
        option = input(term.yellow(f"Input\n'r' for regex search of nodes\n's' for basic search of nodes\n'a' to include all nodes\n'n' for an automatic and sorted search (based on name+number)\nanything else for nothing\n"))
        if option == 'r':
            regex = input(term.yellow("Regex: "))
            preNodes = filter(lambda x: re.search(regex, x), nodes.keys())
        elif option == 's':
            substring = input(term.yellow("Substring: "))
            preNodes = filter(lambda x: substring in x, nodes.keys())
        elif option == 'a':
            preNodes = list(nodes.keys())
        elif option == 'n':
            index = []
            for n in nodes.keys():
                if ss := re.search(fr"{name}(\d*)\d", n):
                    index.append((ss.group(1) if ss.group(1) != '' else 0, n))
            preNodes = [n[1] for n in sorted(index, key=lambda a,b: a[0]-b[0])]
        else:
            preNodes = []
        print(term.yellow("Your text editor will open; input a list of nodes, one node per line. ") + term.bright_yellow("Remember to save before closing."))
        nodeConfirmed = False
        while not nodeConfirmed:
            input(term.yellow("Press enter to launch editor..."))
            nodeList = click.edit('\n'.join(preNodes), require_save=False).strip()
            if nodeList == "":
                print(term.red("No nodes given"))
                continue

            class exiter(Exception):
                pass
            try:
                for n in nodeList.split('\n'):
                    if n not in nodes.keys():
                        print(term.red(f"Node {n} does not exist"))
                        raise exiter
            except exiter:
                preNodes = nodeList.split('\n')
                continue
            newNodes = nodeList.split('\n')
            nodeConfirmed = True

    newPla = {
        name: {
            'type': type_,
            'displayname': displayname,
            'description': description,
            'layer': layer,
            'nodes': newNodes,
            'attrs': {}
        }
    }

    print(term.yellow("Confirm new PLA (type 'c' to cancel, anything else to confirm):"))
    res = input(term.yellow(str(newPla)))
    if res == 'c':
        print(term.yellow("Cancelled"))
        continue
    newPlas.update(newPla)

with open(plaFile, "r+") as f:
    d = json.load(f)
    d.update(newPlas)
    f.seek(0)
    f.truncate()
    json.dump(d, f, indent=4)
    f.close()

print(term.yellow("Written to " + plaFile))
    
