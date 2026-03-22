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

    # 1. ImageReceiver: Change Canvas.drawRoundRect call in static helper to drawRect
    image_receiver = find_file("ImageReceiver.java")
    if image_receiver:
        # Surgical replacement of the call inside the static method
        replace_in_file(
            image_receiver,
            r"c\.drawRoundRect\s*\(\s*rect,\s*rx,\s*ry,\s*paint\s*\);",
            "c.drawRect(rect, paint);",
        )

    # 2. AvatarView: Force needRounds() to return false
    avatar_view = find_file("AvatarView.java")
    if avatar_view:
        replace_in_file(
            avatar_view,
            r"private boolean needRounds\s*\(\)\s*\{[^}]+\}",
            "private boolean needRounds() {\n    return false;\n  }",
        )

    # 3. TripleAvatarView: Force radius to 0 and change placeholders to squares
    triple_path = find_file("TripleAvatarView.java")
    if triple_path:
        # Match receiver.setRadius(...) call
        replace_in_file(
            triple_path, r"receiver\.setRadius\s*\([^;]+\);", "receiver.setRadius(0);"
        )
        # Clear paint placeholder: c.drawCircle(..., clearPaint);
        replace_in_file(
            triple_path,
            r"c\.drawCircle\s*\([^,]+,\s*[^,]+,\s*[^,]+,\s*clearPaint\s*\);",
            "c.drawRect(receiver.getLeft() - Screen.dp(AVATAR_PADDING), receiver.getTop() - Screen.dp(AVATAR_PADDING), receiver.getRight() + Screen.dp(AVATAR_PADDING), receiver.getBottom() + Screen.dp(AVATAR_PADDING), clearPaint);",
        )
        # Placeholder color: c.drawCircle(..., Paints.fillingPaint(Theme.placeholderColor()));
        replace_in_file(
            triple_path,
            r"c\.drawCircle\s*\([^,]+,\s*[^,]+,\s*receiver\.getRadius\(\),\s*Paints\.fillingPaint\(Theme\.placeholderColor\(\)\)\s*\);",
            "c.drawRect(receiver.getLeft(), receiver.getTop(), receiver.getRight(), receiver.getBottom(), Paints.fillingPaint(Theme.placeholderColor()));",
        )

    # 4. AvatarPlaceholder: Change initial-based placeholders to square
    placeholder_path = find_file("AvatarPlaceholder.java")
    if placeholder_path:
        # Match the entire if(drawCircle) block
        replace_in_file(
            placeholder_path,
            r"if\s*\(drawCircle\)\s*\{[^}]+\}",
            "if (drawCircle) {\n      c.drawRect(centerX - radiusPx, centerY - radiusPx, centerX + radiusPx, centerY + radiusPx, Paints.fillingPaint(ColorUtils.alphaColor(alpha, metadata.accentColor.getPrimaryColor())));\n    }",
        )

    # 5. JoinedUsersView: Force square avatars in contact sync view
    joined_path = find_file("JoinedUsersView.java")
    if joined_path:
        # Receiver initialization
        replace_in_file(
            joined_path,
            r"new ImageReceiver\s*\(\s*this,\s*Screen\.dp\(AVATAR_RADIUS\)\s*\)",
            "new ImageReceiver(this, 0)",
        )
        # Placeholder circle 1
        replace_in_file(
            joined_path,
            r"c\.drawCircle\(\s*cx,\s*cy,\s*Screen\.dp\(AVATAR_RADIUS\),\s*Paints\.fillingPaint\([^;]+\);",
            "float r_joined = Screen.dp(AVATAR_RADIUS); c.drawRect(cx - r_joined, cy - r_joined, cx + r_joined, cy + r_joined, Paints.fillingPaint(ColorUtils.alphaColor(factor, info.accentColor.getPrimaryColor())));",
        )
        # "More" counter circle
        replace_in_file(
            joined_path,
            r"c\.drawCircle\(\s*cx,\s*centerY,\s*avatarRadius,\s*Paints\.fillingPaint\([^;]+\);",
            "c.drawRect(cx - avatarRadius, centerY - avatarRadius, cx + avatarRadius, centerY + avatarRadius, Paints.fillingPaint(ColorUtils.alphaColor(factor, Theme.getColor(ColorId.avatarSavedMessages))));",
        )
        # Generic placeholder circle
        replace_in_file(
            joined_path,
            r"c\.drawCircle\(\s*cx,\s*centerY,\s*avatarRadius,\s*paint\s*\);",
            "c.drawRect(cx - avatarRadius, centerY - avatarRadius, cx + avatarRadius, centerY + avatarRadius, paint);",
        )

    print("Avatar modification complete.")


if __name__ == "__main__":
    main()
