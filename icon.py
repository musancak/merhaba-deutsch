# Zeichnet das App-Icon (Sprechblase mit „Hallo!“). Aufruf mit einem Python, das Pillow hat.
import os
from PIL import Image, ImageDraw, ImageFont

HIER = os.path.dirname(os.path.abspath(__file__))
N = 1024
GRUEN, CREME, ORANGE = (31, 92, 74), (250, 244, 230), (200, 115, 47)

img = Image.new("RGB", (N, N), GRUEN)
d = ImageDraw.Draw(img)
# Sprechblase
d.rounded_rectangle((150, 230, 874, 700), radius=150, fill=CREME)
d.polygon([(300, 660), (290, 860), (470, 690)], fill=CREME)
schrift = None
for pfad in ["/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
             "/System/Library/Fonts/Helvetica.ttc"]:
    if os.path.exists(pfad):
        schrift = ImageFont.truetype(pfad, 210)
        break
d.text((512, 462), "Hallo!", font=schrift, fill=GRUEN, anchor="mm")
d.ellipse((780, 150, 900, 270), fill=ORANGE)

ziel = os.path.join(HIER, "dist")
os.makedirs(ziel, exist_ok=True)
for groesse in (180, 192, 512):
    img.resize((groesse, groesse), Image.LANCZOS).save(os.path.join(ziel, f"icon-{groesse}.png"))
print("Icons geschrieben")
