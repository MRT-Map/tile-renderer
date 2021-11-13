import blessed
import re
import json
import click

import renderer.internals.internal as internal
import renderer.misc as misc

term = blessed.Terminal()

print(term.yellow("Welcome to the component JSON builder!\n-------------------------------"))

components, component_file = internal._ask_file_name("Component") # pylint: disable=no-member
nodes, _ = internal._ask_file_name("Node") # pylint: disable=no-member
skin_name = input(term.yellow("Name of skin [blank for default]: "))
try:
    skin = misc.get_skin(skin_name if skin_name != '' else 'default')
except FileNotFoundError:
    skin = misc.get_skin('default')

new_components = {}
e = False
while not e:
    name_confirmed = False
    while not name_confirmed:
        name = input(term.yellow("Name of new component (type 'exit' to exit): "))
        if name in components.keys() or name in new_components.keys():
            print(term.red("component already exists; do you want to override its current value?"))
            print(term.red(components[name] if name in components.keys() else new_components[name]))
            if input(term.red("Type 'y' to confirm: ")) != "y":
                continue
        name_confirmed = True
    
    if name == "exit":
        e = True
        print(term.yellow("Exited"))
        continue

    typeConfirmed = False
    while not typeConfirmed:
        type_ = input(term.yellow(f"component type of {name}: "))
        if not type_.split(" ")[0] in skin['types'].keys():
            print(term.red(f"Type {type_.split(' ')[0]} does not exist"))
            internal._similar(type_.split(' ')[0], skin['types'].keys()) # pylint: disable=no-member
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
        node_confirmed = False
        while not node_confirmed:
            node = input(term.yellow("Node attached: "))
            if node not in nodes.keys():
                print(term.red("Node does not exist"))
                internal._similar(node, nodes) # pylint: disable=no-member
                continue
            node_confirmed = True
        new_nodes = [node]
    else:
        print(term.yellow("Nodes for {name}: Choose what to pre-write in node list editor: "), end="")
        option = input(term.yellow(f"Input\n'r' for regex search of nodes\n's' for basic search of nodes\n'a' to include all nodes\n'n' for an automatic and sorted search (based on name+number)\nanything else for nothing\n"))
        if option == 'r':
            regex = input(term.yellow("Regex: "))
            pre_nodes = filter(lambda x: re.search(regex, x), nodes.keys())
        elif option == 's':
            substring = input(term.yellow("Substring: "))
            pre_nodes = filter(lambda x: substring in x, nodes.keys())
        elif option == 'a':
            pre_nodes = list(nodes.keys())
        elif option == 'n':
            index = []
            for n in nodes.keys():
                if ss := re.search(fr"{name}(\d*)\D", n):
                    index.append((ss.group(1) if ss.group(1) != '' else 0, n))
            pre_nodes = [n[1] for n in sorted(index, key=lambda a, b: a[0] - b[0])]
        else:
            pre_nodes = []
        print(term.yellow("Your text editor will open; input a list of nodes, one node per line. ") + term.bright_yellow("Remember to save before closing."))
        node_confirmed = False
        while not node_confirmed:
            input(term.yellow("Press enter to launch editor..."))
            node_list = click.edit('\n'.join(pre_nodes), require_save=False).strip()
            if node_list == "":
                print(term.red("No nodes given"))
                continue

            class Exiter(Exception):
                pass
            try:
                for n in node_list.split('\n'):
                    if n not in nodes.keys():
                        print(term.red(f"Node {n} does not exist"))
                        internal._similar(n, nodes.keys()) # pylint: disable=no-member
                        raise Exiter
            except Exiter:
                pre_nodes = node_list.split('\n')
                continue
            new_nodes = node_list.split('\n')
            node_confirmed = True

    newPla = {
        name: {
            'type': type_,
            'displayname': displayname,
            'description': description,
            'layer': layer,
            'nodes': new_nodes,
            'attrs': {}
        }
    }

    print(term.yellow("Confirm new component (type 'c' to cancel, anything else to confirm):"))
    res = input(term.yellow(str(newPla)))
    if res == 'c':
        print(term.yellow("Cancelled"))
        continue
    new_components.update(newPla)

with open(component_file, "r+") as f:
    d = json.load(f)
    d.update(new_components)
    f.seek(0)
    f.truncate()
    json.dump(d, f, indent=4)
    f.close()

print(term.yellow("Written to " + component_file))
    
