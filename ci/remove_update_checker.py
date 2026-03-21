import os
import re

def replace_in_file(file_path, pattern, replacement, multi_line=True):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    flags = re.DOTALL if multi_line else 0
    new_content = re.sub(pattern, replacement, content, flags=flags)
    if new_content != content:
        print(f"Successfully modified: {file_path}")
    else:
        print(f"No changes made to: {file_path} (pattern not found)")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    print("Removing update checker...")

    app_updater_path = (
        "app/src/main/java/org/thunderdog/challegram/util/AppUpdater.java"
    )

    # 1. Neuter checkForUpdates()
    # Uses flexible whitespace matching to handle different formatting
    replace_in_file(
        app_updater_path,
        r"public void checkForUpdates\s*\(\)\s*\{.*?\}",
        r"public void checkForUpdates() {\n    // Disabled by CI\n  }"
    )

    # 2. Neuter Google Play update manager initialization in constructor
    replace_in_file(
        app_updater_path,
        r"AppUpdateManager appUpdateManager = null;.*?this\.googlePlayUpdateManager = appUpdateManager;",
        r"this.googlePlayUpdateManager = null;"
    )

    # 3. Neuter checkForTelegramChannelUpdates()
    replace_in_file(
        app_updater_path,
        r"private void checkForTelegramChannelUpdates\s*\(\)\s*\{.*?\}",
        r"private void checkForTelegramChannelUpdates() {\n    onUpdateUnavailable();\n  }"
    )

    print("Update checker removal complete.")

if __name__ == "__main__":
    main()
