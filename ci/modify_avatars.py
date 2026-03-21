import os
import re


def find_file(name):
    for root, dirs, files in os.walk("."):
        if ".git" in root or "build" in root or "helpers" in root:
            continue
        if name in files:
            return os.path.join(root, name)
    return None


def replace_in_file(file_path, pattern, replacement, multi_line=True):
    if not file_path or not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    flags = re.DOTALL if multi_line else 0
    try:
        new_content = re.sub(pattern, replacement, content, flags=flags)
        if new_content != content:
            print(f"Successfully modified: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
    except re.error as e:
        print(f"Regex error in {file_path}: {e}")


def main():
    print("Modifying avatars to be square...")

    # 1. ImageReceiver: Force drawRect instead of drawRoundRect
    replace_in_file(
        find_file("ImageReceiver.java"),
        r"drawRoundRect\s*\([^)]+\);",
        "c.drawRect(roundRect, roundPaint);",
    )

    # 2. AvatarView: Force needRounds() to return false
    replace_in_file(
        find_file("AvatarView.java"),
        r"private boolean needRounds\s*\(\)\s*\{[^}]+\}",
        "private boolean needRounds() {\n    return false;\n  }",
    )

    # 3. TripleAvatarView: Force radius to 0 and change placeholders to squares
    triple_path = find_file("TripleAvatarView.java")
    if triple_path:
        replace_in_file(
            triple_path,
            r"receiver\.setRadius\s*\([^)]+/ 2\);",
            "receiver.setRadius(0);",
        )
        replace_in_file(
            triple_path,
            r"c\.drawCircle\([^,]+,[^,]+, receiver\.getRadius\(\) \+ Screen\.dp\(AVATAR_PADDING\) \), clearPaint\);",
            "c.drawRect(receiver.getLeft() - Screen.dp(AVATAR_PADDING), receiver.getTop() - Screen.dp(AVATAR_PADDING), receiver.getRight() + Screen.dp(AVATAR_PADDING), receiver.getBottom() + Screen.dp(AVATAR_PADDING), clearPaint);",
        )
        replace_in_file(
            triple_path,
            r"c\.drawCircle\([^,]+,[^,]+, receiver\.getRadius\(\), Paints\.fillingPaint\(Theme\.placeholderColor\(\)\)\);",
            "c.drawRect(receiver.getLeft(), receiver.getTop(), receiver.getRight(), receiver.getBottom(), Paints.fillingPaint(Theme.placeholderColor()));",
        )

    # 4. AvatarPlaceholder: Change initial-based placeholders to square
    replace_in_file(
        find_file("AvatarPlaceholder.java"),
        r"if\s*\(drawCircle\)\s*\{[^}]+\}",
        "if (drawCircle) {\n      c.drawRect(centerX - radiusPx, centerY - radiusPx, centerX + radiusPx, centerY + radiusPx, Paints.fillingPaint(ColorUtils.alphaColor(alpha, metadata.accentColor.getPrimaryColor())));\n    }",
    )

    # 5. JoinedUsersView: Force square avatars in contact sync view
    joined_path = find_file("JoinedUsersView.java")
    if joined_path:
        replace_in_file(
            joined_path,
            r"new ImageReceiver\(this, Screen\.dp\(AVATAR_RADIUS\)\)",
            "new ImageReceiver(this, 0)",
        )
        replace_in_file(
            joined_path,
            r"c\.drawCircle\(cx, cy, Screen\.dp\(AVATAR_RADIUS\), Paints\.fillingPaint\([^)]+\)\);",
            "float r_ = Screen.dp(AVATAR_RADIUS); c.drawRect(cx - r_, cy - r_, cx + r_, cy + r_, Paints.fillingPaint(ColorUtils.alphaColor(factor, info.accentColor.getPrimaryColor())));",
        )
        replace_in_file(
            joined_path,
            r"c\.drawCircle\(cx, centerY, avatarRadius, Paints\.fillingPaint\([^)]+\)\);",
            "c.drawRect(cx - avatarRadius, centerY - avatarRadius, cx + avatarRadius, centerY + avatarRadius, Paints.fillingPaint(ColorUtils.alphaColor(factor, Theme.getColor(ColorId.avatarSavedMessages))));",
        )
        replace_in_file(
            joined_path,
            r"c\.drawCircle\(cx, centerY, avatarRadius, paint\);",
            "c.drawRect(cx - avatarRadius, centerY - avatarRadius, cx + avatarRadius, centerY + avatarRadius, paint);
",
        )

    print("Avatar modification complete.")


if __name__ == "__main__":
    main()
