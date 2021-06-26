import blessed
import re
import json
import click
term = blessed.Terminal()

import renderer.internals.internal as internal
import renderer.misc as misc

print(term.yellow("Welcome to the plaJson builder!\n-------------------------------"))

plas, plaFile = internal.askFile("PLA")
nodes, nodeFile = internal.askFile("Node")
skinName = input(term.yellow("Name of skin [blank for default]: "))
skin = misc.getSkin(skinName if skinName else 'default')

newPlas = {}
e = False
while not e:
    nameConfirmed = False
    while not nameConfirmed:
        name = input(term.yellow("Name of new PLA: "))
        if name in plas.keys() or name in newPlas.keys():
            print(term.red("PLA already exists; do you want to override its current value?"))
            print(term.red(plas[name] if name in plas.keys() else newPlas[name]))
            if input(term.red("Type 'y' to confirm: ")) != "y":
                continue
        nameConfirmed = True
    type_ = input(term.yellow(f"PLA type of {name}: "))
    displayname = input(term.yellow(f"Display name of {name}: "))
    displayname = input(term.yellow(f"Description of {name}: "))
    try:
        layer = float(input(term.yellow(f"Layer for {name}: ")))
    except ValueError: 
        layer = 0
    layer = int(layer) if int(layer) == layer else layer

    if skin['types'][type_]['type'] == "point":
        nodeConfirmed = False
        while not nodeConfirmed:
            node = input(term.yellow("Node attached: "))
            if node not in nodes.keys():
                print(term.red("Node does not exist"))
                continue
            nodeConfirmed = True
        node = [node]
    else:
        pass
    
