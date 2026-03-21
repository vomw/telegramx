import os
import re


def find_file(name):
    for root, dirs, files in os.walk("."):
        if ".git" in root or "build" in root or "helpers" in root:
            continue
        if name in files:
            return os.path.join(root, name)
    return None


def replace_method_body(file_path, method_signature, new_body):
    if not file_path or not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_idx = content.find(method_signature)
    if start_idx == -1:
        print(f"Method signature not found: {method_signature}")
        return

    # Find the opening brace of the method after the signature
    brace_start = content.find("{", start_idx)
    if brace_start == -1:
        return

    # Find the matching closing brace
    brace_count = 0
    brace_end = -1
    for i in range(brace_start, len(content)):
        if content[i] == "{":
            brace_count += 1
        elif content[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                brace_end = i
                break

    if brace_end != -1:
        new_content = (
            content[:brace_start]
            + "{\n    "
    + new_body
    + "\n  }"
  + content[brace_end + 1 :]
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully modified method in: {file_path}")


def main():
    print("Removing update checker...")

    app_updater_path = find_file("AppUpdater.java")
    if not app_updater_path:
        return

    # 1. Neuter checkForUpdates()
    replace_method_body(
        app_updater_path, "public void checkForUpdates ()", "// Disabled by CI"
    )

    # 2. Neuter checkForTelegramChannelUpdates()
    replace_method_body(
        app_updater_path,
        "private void checkForTelegramChannelUpdates ()",
        "onUpdateUnavailable();",
    )

    # 3. Neuter Google Play update manager in constructor
    with open(app_updater_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Escape the dots to be safe and match the constructor part exactly
    # We use non-greedy matching .*? for safety
    new_content = re.sub(
        r"AppUpdateManager appUpdateManager = null;.*?this\.googlePlayUpdateManager = appUpdateManager;",
        r"this.googlePlayUpdateManager = null;",
        content,
        flags=re.DOTALL,
    )
    if new_content != content:
        with open(app_updater_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully modified constructor in: {app_updater_path}")

    # 4. Neuter offerUpdate() methods if they exist
    replace_method_body(
        app_updater_path, "public void offerUpdate ()", "// Disabled by CI"
    )
    replace_method_body(
        app_updater_path, "private boolean offerGooglePlayUpdate ()", "return false;"
    )
    replace_method_body(
        app_updater_path, "private boolean offerTelegramChannelUpdate ()", "return false;"
    )

    print("Update checker removal complete.")


if __name__ == "__main__":
    main()
