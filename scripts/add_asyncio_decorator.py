import os
import re

def add_asyncio_decorator_to_tests(test_dir='tests'):
    marker = '@pytest.mark.asyncio'
    async_test_pattern = re.compile(r'^\s*async def (test_\w+)\s*\(.*\):', re.MULTILINE)

    for dirpath, _, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(dirpath, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_content = content
                matches = list(async_test_pattern.finditer(content))
                offset = 0

                for m in matches:
                    start_index = m.start()
                    # Check if marker already present on previous line
                    prev_line_start = content.rfind('\n', 0, start_index) + 1
                    prev_line = content[prev_line_start:start_index].strip()
                    if prev_line != marker:
                        insertion_pos = prev_line_start
                        new_content = new_content[:insertion_pos + offset] + marker + '\n' + new_content[insertion_pos + offset:]
                        offset += len(marker) + 1

                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Added @pytest.mark.asyncio decorators in {path}")

if __name__ == "__main__":
    add_asyncio_decorator_to_tests()
