import os
import re

# Define protobuf modules to replace and the new import
PROTO_MODULES = ['bars_pb2', 'fundamentals_pb2']
PROTO_IMPORT_RE = re.compile(r'from core import (.+_pb2)')
PROTO_PARSE_RE = re.compile(r'(\w+)\.ParseFromString\(([^\)]+)\)')
PROTO_ATTR_ACCESS_RE = re.compile(r'(\w+)\.(\w+)')

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace protobuf imports with JSON decoder import if protobuf module imported
    if any(mod in content for mod in PROTO_MODULES):
        # Remove protobuf imports
        content = PROTO_IMPORT_RE.sub('', content)
        # Add new import at top
        content = "from core.upstox_protobuf_decoder import decode_message\n" + content

        # Replace ParseFromString calls with decode_message
        def repl_parse(m):
            var_name = m.group(1)
            arg = m.group(2)
            return f"{var_name} = decode_message({arg})"
        content = PROTO_PARSE_RE.sub(repl_parse, content)

        # Replace attribute access on protobuf objects with dict .get() calls
        # This will replace e.g., msg.symbol -> msg.get('symbol')
        # Note: this is a simple heuristic and may produce false positives if variable names overlap
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if '=' in line or 'def ' in line or line.strip().startswith('#'):
                # Skip assignments, function defs and comments to reduce false positives
                continue
            # Replace matches on this line
            matches = list(PROTO_ATTR_ACCESS_RE.finditer(line))
            new_line = line
            for m in reversed(matches):  # reverse to not mess up indices
                var_name = m.group(1)
                attr = m.group(2)
                # Naive check if var_name was assigned from decode_message in the file
                if f"{var_name} =" in content:
                    start, end = m.span()
                    new_line = new_line[:start] + f"{var_name}.get('{attr}')" + new_line[end:]
            lines[i] = new_line
        content = "\n".join(lines)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Refactored protobuf usage in {filepath}")

def refactor_project(root_dir='core'):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                refactor_file(filepath)

if __name__ == '__main__':
    refactor_project()
