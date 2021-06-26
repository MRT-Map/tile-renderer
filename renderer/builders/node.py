import blessed
import re
import json
term = blessed.Terminal()

import renderer.internals.internal as internal

print(term.yellow("Welcome to the nodeJson builder!\n--------------------------------"))

nodes, filePath = internal.askFileName("Node") # pylint: disable=no-member

print(term.yellow("Ingame, press F3+C once, and paste it here.\nType 'exit' to exit."))
newNodes = {}
e = False
while not e:
    pasted = input(term.yellow("Paste: "))
    if pasted == "exit":
        e = True
        print(term.yellow("Exited"))
        continue
    groups = re.search(r"@s (\S+) \S+ (\S+)", pasted)
    if groups == None:
        print(term.red("Invalid paste"))
        continue
    x = int(float(groups.group(1)))
    y = int(float(groups.group(2)))

    nameConfirmed = False
    while not nameConfirmed:
        name = input(term.yellow("Node name: "))
        if name in nodes.keys() or name in newNodes.keys():
            print(term.red("Node already exists; do you want to override its current value?"))
            print(term.red(nodes[name] if name in nodes.keys() else newNodes[name]))
            if input(term.red("Type 'y' to confirm: ")) != "y":
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

print(term.yellow("Written to " + filePath))