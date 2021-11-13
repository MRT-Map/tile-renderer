import blessed
import re
import json

import renderer.internals.internal as internal
term = blessed.Terminal()

print(term.yellow("Welcome to the node JSON builder!\n--------------------------------"))

nodes, file_path = internal._ask_file_name("Node") # pylint: disable=no-member

print(term.yellow("Ingame, press F3+C once, and paste it here.\nType 'exit' to exit."))
new_nodes = {}
e = False
while not e:
    pasted = input(term.yellow("Paste: "))
    if pasted == "exit":
        e = True
        print(term.yellow("Exited"))
        continue
    groups = re.search(r"@s (\S+) \S+ (\S+)", pasted)
    if groups is None:
        print(term.red("Invalid paste"))
        continue
    x = int(float(groups.group(1)))
    y = int(float(groups.group(2)))

    name_confirmed = False
    while not name_confirmed:
        name = input(term.yellow("Node name: "))
        if name in nodes.keys() or name in new_nodes.keys():
            print(term.red("Node already exists; do you want to override its current value?"))
            print(term.red(nodes[name] if name in nodes.keys() else new_nodes[name]))
            if input(term.red("Type 'y' to confirm: ")) != "y":
                continue
        name_confirmed = True

    new_nodes[name] = {"x": x, "y": y, "connections": []}

with open(file_path, "r+") as f:
    d = json.load(f)
    d.update(new_nodes)
    f.seek(0)
    f.truncate()
    json.dump(d, f, indent=4)
    f.close()

print(term.yellow("Written to " + file_path))