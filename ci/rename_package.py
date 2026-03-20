import os
import sys
import shutil
import re

def multiple_replace(text, adict):
    if not adict:
        return text
    # Sort keys by length descending to match longest possible strings first
    keys = sorted(adict.keys(), key=len, reverse=True)
    regex = re.compile("|".join(map(re.escape, keys)))
    return regex.sub(lambda match: adict[match.group(0)], text)

def fix_buildSrc_files(new_package):
    print("Fixing buildSrc source files...")
    new_path_part = new_package.replace('.', '/')
    
    old_package_dots = [
        # "io.github.vomw.im.square",
        # "io.github.vomw.im",
        "org.thunderdog.challegram"
    ]
    
    replacements = {}
    for old_dot in old_package_dots:
        if old_dot == new_package: continue
        old_slash = old_dot.replace('.', '/')
        
        replacements[f"package {old_dot}"] = f"package {new_package}"
        replacements[f"import {old_dot}"] = f"import {new_package}"
        replacements[old_dot] = new_package
        replacements[old_slash] = new_path_part
        # JNI underscore notation
        replacements[old_dot.replace('.', '_')] = new_package.replace('.', '_')

    for root, dirs, files in os.walk('buildSrc'):
        for file in files:
            if file.endswith('.kt') or file.endswith('.java'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    new_content = multiple_replace(content, replacements)
                        
                    if new_content != content:
                        print(f"Patched buildSrc file: {file_path}")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error patching {file_path}: {e}")

def rename_package(old_packages, new_package):
    print(f"Renaming packages {old_packages} to {new_package}...")
    new_path_rel = new_package.replace('.', os.sep)
    
    # First, fix buildSrc tasks
    fix_buildSrc_files(new_package)

    extensions_to_process = ('.java', '.kt', '.xml', '.gradle', '.kts', '.pro', '.json', '.sh', '.c', '.cpp', '.h', '.cmake', '.txt', '.md', '.yml', '.yaml', '.gitignore')
    
    # Filter out target from old packages to avoid self-moves
    old_packages = [p for p in old_packages if p != new_package and p]
    # Sort by length descending to handle nested packages correctly
    old_packages.sort(key=len, reverse=True)

    # Move all directories
    for old_package in old_packages:
        print(f"Processing directory moves for old package: {old_package}")
        old_path_rel = old_package.replace('.', os.sep)
        
        source_roots = []
        for root, dirs, files in os.walk('.'):
            # Better path exclusion
            path_parts = root.split(os.sep)
            if '.git' in path_parts or 'build' in path_parts or 'buildSrc' in path_parts:
                continue
            if root.endswith(os.sep + 'java') or root.endswith(os.sep + 'kotlin'):
                source_roots.append(root)
                
        for source_root in source_roots:
            old_dir = os.path.normpath(os.path.join(source_root, old_path_rel))
            new_dir = os.path.normpath(os.path.join(source_root, new_path_rel))
            
            if os.path.exists(old_dir):
                if old_dir == new_dir:
                    print(f"Skip move: same directory {old_dir}")
                    continue
                    
                print(f"Moving source files: {old_dir} -> {new_dir}")
                
                temp_dir = old_dir + '__temp__'
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
                shutil.move(old_dir, temp_dir)
                os.makedirs(os.path.dirname(new_dir), exist_ok=True)
                
                if os.path.exists(new_dir):
                    # Merge contents
                    for item in os.listdir(temp_dir):
                        s = os.path.join(temp_dir, item)
                        d = os.path.join(new_dir, item)
                        if os.path.exists(d) and os.path.isdir(d) and os.path.isdir(s):
                            # Recursively move items
                            for sub_item in os.listdir(s):
                                shutil.move(os.path.join(s, sub_item), os.path.join(d, sub_item))
                            os.rmdir(s)
                        else:
                            shutil.move(s, d)
                    shutil.rmtree(temp_dir)
                else:
                    shutil.move(temp_dir, new_dir)

                # Cleanup empty parent directories
                parent = os.path.dirname(old_dir)
                while parent and parent != source_root:
                    if os.path.exists(parent) and not os.listdir(parent):
                        os.rmdir(parent)
                        print(f"Removed empty directory: {parent}")
                        parent = os.path.dirname(parent)
                    else:
                        break

    # Replace all strings
    replacements = {}
    for old_pkg in old_packages:
        if not old_pkg: continue
        # Dot notation
        replacements[old_pkg] = new_package
        # Slashes (handle both for cross-platform files)
        replacements[old_pkg.replace('.', '/')] = new_package.replace('.', '/')
        replacements[old_pkg.replace('.', '\\')] = new_package.replace('.', '\\')
        # Underscores (JNI)
        replacements[old_pkg.replace('.', '_')] = new_package.replace('.', '_')

    for root, dirs, files in os.walk('.'):
        path_parts = root.split(os.sep)
        if '.git' in path_parts or 'build' in path_parts or 'buildSrc' in path_parts:
            continue
        for file in files:
            if file.endswith(extensions_to_process) or file == '.gitignore':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    new_content = multiple_replace(content, replacements)

                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rename_package.py <old_packages_comma_separated> <new_package>")
        sys.exit(1)
    
    old_pkgs_str = sys.argv[1]
    new_pkg = sys.argv[2]
    
    old_pkgs_set = set(old_pkgs_str.split(','))
    # old_pkgs_set.add("io.github.vomw.im")
    # old_pkgs_set.add("org.thunderdog.challegram")
    # old_pkgs_set.add("io.github.vomw.im.square")
    
    rename_package(list(old_pkgs_set), new_pkg)
