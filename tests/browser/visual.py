import io
import os

from PIL import Image


def generate_diff(baseline_path, actual_bytes, diff_path, tolerance=0):
    """
    Compare baseline image with actual image bytes.
    If they differ beyond `tolerance` (number of pixels),
    generate a diff image highlighting differences in red and save to diff_path.
    Returns (True, "") if match, (False, error_msg) if mismatch.
    """
    if not os.path.exists(baseline_path):
        return False, f"Baseline image not found: {baseline_path}"

    with Image.open(baseline_path) as b_img:
        baseline_img = b_img.convert("RGBA")

    with Image.open(io.BytesIO(actual_bytes)) as a_img:
        actual_img = a_img.convert("RGBA")

    if baseline_img.size != actual_img.size:
        actual_img.save(diff_path)  # Just save the actual as diff for now
        return False, f"Size mismatch: {baseline_img.size} vs {actual_img.size}"

    width, height = baseline_img.size
    b_data = baseline_img.load()
    a_data = actual_img.load()

    diff_img = Image.new("RGBA", (width, height))
    d_data = diff_img.load()

    mismatches = 0

    for y in range(height):
        for x in range(width):
            bp = b_data[x, y]
            ap = a_data[x, y]

            # Simple absolute difference check
            # Check RGB channels (ignore alpha or include alpha)
            diff = sum(abs(bp[i] - ap[i]) for i in range(3))

            if diff > 0:  # Even slight difference
                d_data[x, y] = (255, 0, 0, 255)  # Red highlight
                mismatches += 1
            else:
                # Dim the original pixel for context
                gray = int(0.3 * bp[0] + 0.59 * bp[1] + 0.11 * bp[2])
                d_data[x, y] = (gray, gray, gray, 128)

    if mismatches > tolerance:
        diff_img.save(diff_path)
        return False, f"Images differ by {mismatches} pixels (tolerance: {tolerance})"

    return True, ""
