import blessed
import re
import json
from pyautogui import typewrite

import renderer.internals.internal as internal
term = blessed.Terminal()

def input_default(msg: str, default: str):
    print(msg, end="")
    typewrite(default)
    return input()

print(term.yellow("Welcome to the node JSON builder!\n--------------------------------"))

nodes, file_path = internal._ask_file_name("NodeJson") # pylint: disable=no-member

print(term.yellow("Ingame, press F3+C once, and paste it here.\n" +
                  "Type '.exit' to exit\n" +
                  "Type '.default <name>' to set default name\n" +
                  "Type '.delete <node>' to delete node"))
new_nodes = {}
default_name = ""
count = 1
e = False
while not e:
    pasted = input(term.yellow("Paste: "))
    if pasted == ".exit":
        e = True
        print(term.yellow("Exited"))
        continue
    elif pasted.startswith(".default"):
        if pasted.strip() == ".default":
            default_name = ""
            print(term.yellow("Default name is now empty"))
            count = 1
        else:
            default_name = pasted.replace(".default ", "")
            print(term.yellow(f"Default name is now {default_name}"))
            count = 1
        continue
    elif pasted.startswith(".delete"):
        if pasted.strip() == "default":
            print(term.red("Syntax: .delete <node>"))
        else:
            to_delete = pasted.replace(".delete ", "")
            if to_delete not in new_nodes:
                print(term.red(f"NodeJson '{to_delete}' does not exist"))
            else:
                print(term.red(f"Do you want to delete '{to_delete}'?"))
                print(term.red(str(new_nodes[to_delete])))
                if input(term.red("Type 'y' to confirm: ")) == "y":
                    del new_nodes[to_delete]
                    print(term.yellow("Deleted"))
        continue
    groups = re.search(r"@s (\S+) \S+ (\S+)", pasted)
    if groups is None:
        print(term.red("Invalid paste"))
        continue
    x = int(float(groups.group(1)))
    y = int(float(groups.group(2)))

    name_confirmed = False
    while not name_confirmed:
        name = input_default(term.yellow("NodeJson name: "), default_name.replace("{num}", str(count)))
        if name in nodes.keys() or name in new_nodes.keys():
            print(term.red("NodeJson already exists; do you want to override its current value?"))
            print(term.red(str(nodes[name] if name in nodes.keys() else new_nodes[name])))
            if input(term.red("Type 'y' to confirm: ")) != "y":
                print(term.yellow("Overwritten"))
                continue
        name_confirmed = True

    new_nodes[name] = {"x": x, "y": y, "connections": []}
    count += 1

with open(file_path, "r+") as f:
    d = json.load(f)
    d.update(new_nodes)
    f.seek(0)
    f.truncate()
    json.dump(d, f, indent=4)
    f.close()

print(term.yellow("Written to " + file_path))