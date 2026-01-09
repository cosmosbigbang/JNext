from PIL import Image, ImageDraw, ImageFont
import os

# 1024x1024 이미지 생성
size = 1024
img = Image.new('RGB', (size, size))
draw = ImageDraw.Draw(img)

# Gradient background (Purple to Indigo)
for y in range(size):
    r = int(103 + (63 - 103) * y / size)  # 673AB7 -> 3F51B5
    g = int(58 + (81 - 58) * y / size)
    b = int(183 + (181 - 183) * y / size)
    draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))

# Rounded corners (간단한 버전)
corner_radius = 180
for i in range(corner_radius):
    for j in range(corner_radius):
        if (i - corner_radius)**2 + (j - corner_radius)**2 > corner_radius**2:
            # Top-left
            img.putpixel((i, j), (0, 0, 0, 0) if img.mode == 'RGBA' else (103, 58, 183))
            # Top-right
            img.putpixel((size-1-i, j), (0, 0, 0, 0) if img.mode == 'RGBA' else (103, 58, 183))
            # Bottom-left
            img.putpixel((i, size-1-j), (0, 0, 0, 0) if img.mode == 'RGBA' else (63, 81, 181))
            # Bottom-right
            img.putpixel((size-1-i, size-1-j), (0, 0, 0, 0) if img.mode == 'RGBA' else (63, 81, 181))

# Document icon (subtle background)
doc_x, doc_y, doc_w, doc_h = 650, 350, 100, 350
overlay = Image.new('RGBA', (size, size), (255, 255, 255, 0))
draw_overlay = ImageDraw.Draw(overlay)
draw_overlay.rectangle([doc_x, doc_y, doc_x + doc_w, doc_y + doc_h], fill=(255, 255, 255, 38))
draw_overlay.line([(680, 400), (720, 400)], fill=(255, 255, 255, 51), width=8)
draw_overlay.line([(680, 450), (720, 450)], fill=(255, 255, 255, 51), width=8)
draw_overlay.line([(680, 500), (720, 500)], fill=(255, 255, 255, 51), width=8)
img = Image.alpha_composite(img.convert('RGBA'), overlay)

# Draw "J" text
try:
    # Windows 시스템 폰트 사용
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 480)
except:
    font = ImageFont.load_default()

draw = ImageDraw.Draw(img)

# Shadow
shadow_color = (0, 0, 0, 38)
draw.text((512, 512), "J", font=font, fill=shadow_color, anchor="mm")

# Main text (white)
text_color = (255, 255, 255, 255)
draw.text((512, 508), "J", font=font, fill=text_color, anchor="mm")

# Save
output_path = os.path.join(os.path.dirname(__file__), '../jnext_mobile/assets/icon.png')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img = img.convert('RGB')  # PNG는 RGB로 저장
img.save(output_path, 'PNG')
print(f"✓ 아이콘 생성 완료: {output_path}")
