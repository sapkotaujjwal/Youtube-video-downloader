import os
import sys
from PIL import Image

def compress_image(input_path, target_size_kb, output_path=None):
    """
    Compress an image to approximately the target file size in KB while maintaining aspect ratio.

    Args:
        input_path (str): Path to the input image
        target_size_kb (float): Target file size in KB
        output_path (str, optional): Path for output image. If None, adds '_compressed' to input name.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        return

    # Determine output path
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

    # Open image
    try:
        img = Image.open(input_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # Get original size
    original_size = os.path.getsize(input_path) / 1024  # KB
    print(f"Original size: {original_size:.2f} KB")

    if original_size <= target_size_kb:
        print("Image is already smaller than or equal to target size.")
        img.save(output_path)
        return

    # Convert to RGB if necessary (for JPEG)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    width, height = img.size
    aspect_ratio = width / height

    # Binary search for quality
    min_quality = 10
    max_quality = 95
    best_quality = max_quality
    best_size = original_size

    for _ in range(10):  # Limit iterations
        quality = (min_quality + max_quality) // 2
        img_copy = img.copy()

        # Resize if needed
        scale_factor = (target_size_kb / original_size) ** 0.5
        if scale_factor < 1:
            new_width = max(1, int(width * scale_factor))
            new_height = max(1, int(height * scale_factor))
            img_copy = img_copy.resize((new_width, new_height), Image.Resampling.LANCZOS)

        img_copy.save(output_path, 'JPEG', quality=quality, optimize=True)
        current_size = os.path.getsize(output_path) / 1024

        if abs(current_size - target_size_kb) < abs(best_size - target_size_kb):
            best_size = current_size
            best_quality = quality

        if current_size > target_size_kb:
            max_quality = quality - 1
        else:
            min_quality = quality + 1

    # Final save with best quality
    scale_factor = (target_size_kb / original_size) ** 0.5
    if scale_factor < 1:
        new_width = max(1, int(width * scale_factor))
        new_height = max(1, int(height * scale_factor))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    img.save(output_path, 'JPEG', quality=best_quality, optimize=True)
    final_size = os.path.getsize(output_path) / 1024
    print(f"Compressed image saved to: {output_path}")
    print(f"Final size: {final_size:.2f} KB (target: {target_size_kb} KB)")

def main():
    if len(sys.argv) < 3:
        print("Usage: python imageSizeCompressoer.py <input_image> <target_size_kb> [output_image]")
        print("Example: python imageSizeCompressoer.py photo.jpg 500")
        return

    input_path = sys.argv[1]
    try:
        target_size_kb = float(sys.argv[2])
    except ValueError:
        print("Error: Target size must be a number (in KB)")
        return

    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    compress_image(input_path, target_size_kb, output_path)

if __name__ == "__main__":
    main()
