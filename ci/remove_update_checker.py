import os
import re


def find_file(name):
    for root, dirs, files in os.walk("."):
        if ".git" in root or "build" in root:
            continue
        if name in files:
            return os.path.join(root, name)
    return None


def replace_in_file(file_path, pattern, replacement, multi_line=True):
    if not file_path or not os.path.exists(file_path):
        print(f"File not found for pattern: {pattern}")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    flags = re.DOTALL if multi_line else 0
    new_content = re.sub(pattern, replacement, content, flags=flags)
    if new_content != content:
        print(f"Successfully modified: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    else:
        print(f"No changes made to: {file_path} (pattern not found)")


def main():
    print("Removing update checker...")

    app_updater_path = find_file("AppUpdater.java")

    # 1. Neuter checkForUpdates()
    replace_in_file(
        app_updater_path,
        r"public void checkForUpdates\s*\(\)\s*\{.*?\}",
        r"public void checkForUpdates() {\n    // Disabled by CI\n  }",
    )

    # 2. Neuter Google Play update manager initialization in constructor
    replace_in_file(
        app_updater_path,
        r"AppUpdateManager appUpdateManager = null;.*?this\.googlePlayUpdateManager = appUpdateManager;",
        r"this.googlePlayUpdateManager = null;",
    )

    # 3. Neuter checkForTelegramChannelUpdates()
    replace_in_file(
        app_updater_path,
        r"private void checkForTelegramChannelUpdates\s*\(\)\s*\{.*?\}",
        r"private void checkForTelegramChannelUpdates() {\n    onUpdateUnavailable();\n  }",
    )

    print("Update checker removal complete.")


if __name__ == "__main__":
    main()
