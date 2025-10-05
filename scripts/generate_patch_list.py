import os
import ast

CORE_DIR = "core"

def find_classes_in_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            file_content = f.read()
        tree = ast.parse(file_content)
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        return classes
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return []

def get_module_path(file_path):
    # Convert filepath to python module notation
    if file_path.endswith(".py"):
        file_path = file_path[:-3]  # remove .py
    return file_path.replace(os.sep, ".")

def scan_core_package(core_dir=CORE_DIR):
    patch_lines = []
    for root, dirs, files in os.walk(core_dir):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(root, filename)
            classes = find_classes_in_file(filepath)
            if classes:
                module_path = get_module_path(os.path.relpath(filepath))
                for cls in classes:
                    patch_line = f"monkeypatch.setattr(\"{module_path}.{cls}\", lambda *args, **kwargs: Dummy{cls}())"
                    patch_lines.append(patch_line)
    return patch_lines

if __name__ == "__main__":
    patches = scan_core_package()
    print("# Recommended monkeypatch lines for dummy mocks")
    for line in patches:
        print(line)
