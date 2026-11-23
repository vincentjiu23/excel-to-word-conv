from pathlib import Path
from PIL import Image, ImageDraw

output = Path("src-tauri/icons/icon.ico")
output.parent.mkdir(parents=True, exist_ok=True)

img = Image.new("RGBA", (256, 256), (25, 45, 75, 255))
draw = ImageDraw.Draw(img)

# Document shape
draw.rounded_rectangle(
    (55, 35, 185, 220),
    radius=18,
    fill=(255, 255, 255, 255)
)

# Folded corner
draw.polygon(
    [(145, 35), (185, 75), (145, 75)],
    fill=(210, 220, 235, 255)
)

# Document lines
for y in (105, 135, 165):
    draw.rounded_rectangle(
        (78, y, 160, y + 9),
        radius=4,
        fill=(90, 120, 160, 255)
    )

# Green Excel-like accent
draw.rounded_rectangle(
    (25, 145, 100, 210),
    radius=12,
    fill=(30, 145, 90, 255)
)

draw.line((45, 165, 80, 190), fill="white", width=8)
draw.line((80, 165, 45, 190), fill="white", width=8)

img.save(
    output,
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48),
           (64, 64), (128, 128), (256, 256)]
)

print(f"Icon created: {output}")