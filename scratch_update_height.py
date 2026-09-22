import os

directory = r"d:\Buildlaunchs\Agni-Netra\frontend\src\app"
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.tsx'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # We want to replace 'min-h-screen' with 'h-screen' for the main wrapper div
            if 'min-h-screen' in content and 'flex' in content:
                # Replace only the first occurrence which is usually the root layout div
                content = content.replace('min-h-screen', 'h-screen', 1)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {filepath}")
