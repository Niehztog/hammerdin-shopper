import os
import math
from PIL import Image

# Specify your folder here
# folder = r'C:\Users\nilsg\Desktop\items\belts'
# folder = r'C:\Users\nilsg\Desktop\items\body armor'
folder = r'C:\Users\nilsg\Desktop\items\boots'
# folder = r'C:\Users\nilsg\Desktop\items\gloves'
# folder = r'C:\Users\nilsg\Desktop\items\helmet'
# folder = r'C:\Users\nilsg\Desktop\items\jewelery'


def get_png_images(folder):
    """Returns a list of PIL Images for all PNG files in the folder."""
    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
    files.sort()  # Optional: sort files alphabetically
    return [Image.open(os.path.join(folder, f)).convert("RGB") for f in files]

def compute_grid(n):
    """Returns (rows, cols) for a grid as square as possible for n images."""
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return rows, cols

def pad_image(img, target_width, target_height):
    """Pads the image with black pixels to fit the target size, keeping aspect ratio."""
    # Calculate new size keeping aspect ratio
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Image is wider relative to target: fit width
        new_width = target_width
        new_height = round(target_width / img_ratio)
    else:
        # Image is taller relative to target: fit height
        new_height = target_height
        new_width = round(target_height * img_ratio)

    resized = img.resize((new_width, new_height), Image.LANCZOS)
    # Create black background
    new_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
    # Center the image
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2
    new_img.paste(resized, (x, y))
    return new_img

# Main process
images = get_png_images(folder)
if not images:
    raise ValueError("No PNG images found in the specified folder.")

# Determine max width and height
max_width = max(img.width for img in images)
max_height = max(img.height for img in images)

# Pad all images to the same size, keeping aspect ratio
padded_images = [pad_image(img, max_width, max_height) for img in images]

rows, cols = compute_grid(len(padded_images))

# Create grid image
grid_img = Image.new('RGB', (cols * max_width, rows * max_height), (0, 0, 0))

for idx, img in enumerate(padded_images):
    row = idx // cols
    col = idx % cols
    grid_img.paste(img, (col * max_width, row * max_height))

output_path = os.path.join(folder, "grid_output.jpg")
grid_img.save(output_path)
print(f"Grid image saved as {output_path}")
