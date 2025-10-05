import os
import re

# Modules to replace protobuf imports for
PROTO_MODULES = ['bars_pb2', 'fundamentals_pb2']
PROTO_IMPORT_RE = re.compile(r'from core import (.+_pb2)')
PARSE_FROM_STRING_RE = re.compile(r'(\w+)\.ParseFromString\(([^\)]+)\)')
ATTR_ACCESS_RE = re.compile(r'(\w+)\.(\w+)')

def refactor_protobuf_usage_in_file(filepath):
    """Refactor imports, parsing, and attribute access for protobuf removal."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # Detect protobuf import lines and replace
    if any(mod in content for mod in PROTO_MODULES):
        # Remove protobuf imports
        content = PROTO_IMPORT_RE.sub('', content)
        # Add JSON decoder import at the top if not already present
        if 'from core.upstox_protobuf_decoder import decode_message' not in content:
            content = "from core.upstox_protobuf_decoder import decode_message\n" + content
        modified = True

        # Replace ParseFromString calls with decode_message calls
        def replace_parse(m):
            var = m.group(1)
            data = m.group(2)
            return f"{var} = decode_message({data})"
        content = PARSE_FROM_STRING_RE.sub(replace_parse, content)

        # Replace protobuf attribute access `var.field` with `var.get('field')`
        lines = content.splitlines()
        new_lines = []

        for line in lines:
            # Skip lines with assignments or function defs lightly to reduce false positives
            if re.search(r'^\s*(def|class|import|from|#|\@|return|if|elif|else|for|while|with|try|except|assert|raise)\b', line):
                new_lines.append(line)
                continue

            matches = list(ATTR_ACCESS_RE.finditer(line))
            # Reverse to replace without index disturbance
            for m in reversed(matches):
                var_name = m.group(1)
                attr = m.group(2)
                # Basic heuristic: replace only if var_name assigned from decode_message in file
                if f"{var_name} =" in content:
                    start, end = m.span()
                    line = line[:start] + f"{var_name}.get('{attr}')" + line[end:]
            new_lines.append(line)

        content = "\n".join(new_lines)

    if modified and content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Refactored protobuf usage in: {filepath}")

def find_protobuf_generated_files(root_dir='core'):
    """Scan for protobuf-generated *_pb2.py files for cleanup."""
    pb_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.endswith('_pb2.py'):
                pb_files.append(os.path.join(dirpath, fn))
    return pb_files

def remove_files(file_list):
    for file_path in file_list:
        try:
            os.remove(file_path)
            print(f"Deleted protobuf generated file: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

def refactor_tests_mock_messages(test_dir='tests'):
    """
    Append or insert directive in tests to replace protobuf message mocks 
    with dict or JSON string mocks.
    Currently a placeholder: adjust based on your test structure.
    """
    # This can be expanded based on your tests
    print(f"Reminder: Manually update test mocks in {test_dir} to use dict/JSON mocks instead of protobuf objects.")

def run_full_refactor(root_dir='core', test_dir='tests'):
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.py'):
                filepath = os.path.join(dirpath, file)
                refactor_protobuf_usage_in_file(filepath)

    pb_files = find_protobuf_generated_files(root_dir)
    if pb_files:
        print("Protobuf generated files found for removal:")
        for f in pb_files:
            print(f"  {f}")
        confirm = input("Delete these protobuf-generated files? (y/n): ")
        if confirm.lower() == 'y':
            remove_files(pb_files)
        else:
            print("Protobuf-generated files NOT deleted.")

    refactor_tests_mock_messages(test_dir)
    print("Refactor complete. Please uninstall protobuf-related packages from your dependencies.")

if __name__ == "__main__":
    run_full_refactor()
