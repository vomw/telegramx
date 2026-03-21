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
    print("Modifying avatars to be square...")

    # 1. ImageReceiver: Force drawRect instead of drawRoundRect
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/loader/ImageReceiver.java",
        r"drawRoundRect\s*\(\s*c,\s*roundRect,\s*radius,\s*radius,\s*roundPaint\s*\);",
        r"c.drawRect(roundRect, roundPaint);"
    )

    # 2. AvatarView: Force needRounds() to return false
    # This automatically fixes both the ImageReceiver radius and the placeholder drawing logic
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/AvatarView.java",
        r"private boolean needRounds\s*\(\)\s*\{.*?\n\s*\}",
        r"private boolean needRounds() {\n    return false;\n  }"
    )

    # 3. TripleAvatarView: Force radius to 0 and change placeholders to squares
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/TripleAvatarView.java",
        r"receiver\.setRadius\s*\(Math\.min\(receiver\.getWidth\(\),\s*receiver\.getHeight\(\)\)\s*/\s*2\);",
        r"receiver.setRadius(0);"
    )
    # Placeholder background (clear)
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/TripleAvatarView.java",
        r"c\.drawCircle\s*\(\s*receiver\.centerX\(\),\s*receiver\.centerY\(\),\s*receiver\.getRadius\(\)\s*\+\s*Screen\.dp\(AVATAR_PADDING\),\s*clearPaint\s*\);",
        r"c.drawRect(receiver.getLeft() - Screen.dp(AVATAR_PADDING), receiver.getTop() - Screen.dp(AVATAR_PADDING), receiver.getRight() + Screen.dp(AVATAR_PADDING), receiver.getBottom() + Screen.dp(AVATAR_PADDING), clearPaint);"
    )
    # Placeholder content
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/TripleAvatarView.java",
        r"c\.drawCircle\s*\(\s*receiver\.centerX\(\),\s*receiver\.centerY\(\),\s*receiver\.getRadius\(\),\s*Paints\.fillingPaint\(Theme\.placeholderColor\(\)\)\);",
        r"c.drawRect(receiver.getLeft(), receiver.getTop(), receiver.getRight(), receiver.getBottom(), Paints.fillingPaint(Theme.placeholderColor()));"
    )

    # 4. AvatarPlaceholder: Change initial-based placeholders to square
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/data/AvatarPlaceholder.java",
        r"if\s*\(drawCircle\)\s*\{\s*c\.drawCircle\s*\(\s*centerX,\s*centerY,\s*radiusPx,\s*Paints\.fillingPaint\(ColorUtils\.alphaColor\(alpha,\s*metadata\.accentColor\.getPrimaryColor\(\)\)\)\);\s*\}",
        r"if (drawCircle) {\n      c.drawRect(centerX - radiusPx, centerY - radiusPx, centerX + radiusPx, centerY + radiusPx, Paints.fillingPaint(ColorUtils.alphaColor(alpha, metadata.accentColor.getPrimaryColor())));\n    }"
    )

    # 5. JoinedUsersView: Force square avatars in contact sync view
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/JoinedUsersView.java",
        r"new ImageReceiver\s*\(\s*this,\s*Screen\.dp\(AVATAR_RADIUS\)\s*\)",
        r"new ImageReceiver(this, 0)"
    )
    # Placeholder circle
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/JoinedUsersView.java",
        r"c\.drawCircle\s*\(\s*cx,\s*cy,\s*Screen\.dp\(AVATAR_RADIUS\),\s*Paints\.fillingPaint\(ColorUtils\.alphaColor\(factor,\s*info\.accentColor\.getPrimaryColor\(\)\)\)\);",
        r"float r_ = Screen.dp(AVATAR_RADIUS); c.drawRect(cx - r_, cy - r_, cx + r_, cy + r_, Paints.fillingPaint(ColorUtils.alphaColor(factor, info.accentColor.getPrimaryColor())));"
    )
    # "More" counter circle
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/JoinedUsersView.java",
        r"c\.drawCircle\s*\(\s*cx,\s*centerY,\s*avatarRadius,\s*Paints\.fillingPaint\(ColorUtils\.alphaColor\(factor,\s*Theme\.getColor\(ColorId\.avatarSavedMessages\)\)\)\);",
        r"c.drawRect(cx - avatarRadius, centerY - avatarRadius, cx + avatarRadius, centerY + avatarRadius, Paints.fillingPaint(ColorUtils.alphaColor(factor, Theme.getColor(ColorId.avatarSavedMessages))));"
    )
    # Generic receiver placeholder circle
    replace_in_file(
        "app/src/main/java/org/thunderdog/challegram/widget/JoinedUsersView.java",
        r"c\.drawCircle\s*\(\s*cx,\s*centerY,\s*avatarRadius,\s*paint\s*\);",
        r"c.drawRect(cx - avatarRadius, centerY - avatarRadius, cx + avatarRadius, centerY + avatarRadius, paint);"
    )

    print("Avatar modification complete.")

if __name__ == "__main__":
    main()
