import os
import ast

CORE_DIR = "core"

def find_classes_in_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=filename)
    return [n.name for n in ast.walk(node) if isinstance(n, ast.ClassDef)]

def scan_core_for_classes():
    class_map = {}  # class_name -> module_path
    for root, _, files in os.walk(CORE_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            classes = find_classes_in_file(path)
            if classes:
                # convert root/core/path/to/file.py to dot path core.path.to.file
                relative_path = os.path.relpath(path, ".").replace(os.sep, ".")
                # remove .py extension
                module_name = relative_path[:-3] if relative_path.endswith(".py") else relative_path
                for cl in classes:
                    class_map[cl] = module_name
    return class_map

def create_patch_suggestions(class_map, classes_of_interest):
    print("# Suggested monkeypatch paths for fixtures:\n")
    for cl in classes_of_interest:
        if cl in class_map:
            print(f"# {cl} found in {class_map[cl]}")
            print(f'monkeypatch.setattr("{class_map[cl]}.{cl}", lambda *args, **kwargs: Dummy{cl}())')
        else:
            print(f"# WARNING: {cl} class not found in {CORE_DIR}, please check manually")

if __name__ == "__main__":
    # List all classes you want to mock/patch here:
    classes_to_patch = ["BrokerAPI", "DataManager", "RiskManager", "LiveBroker", "AIStrategy"]
    found_classes = scan_core_for_classes()
    create_patch_suggestions(found_classes, classes_to_patch)
