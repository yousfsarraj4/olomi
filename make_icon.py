# يرسم أيقونة التطبيق: منظر جبلي طبيعي + كلمة «علومي» كبيرة في المنتصف
import os, random, math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

S = 1024
OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets'
os.makedirs(OUT, exist_ok=True)
WORD = 'علومي'
FONTS = ['fonts/ArefRuqaa-Bold.ttf', 'fonts/ArefRuqaa-Regular.ttf', 'fonts/NotoNastaliqUrdu-Bold.ttf',
         '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf']
if not features.check('raqm'):
    sys.exit('raqm غير متوفر: لا يمكن تشكيل الحروف العربية')

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def scene():
    img = Image.new('RGB', (S, S))
    d = ImageDraw.Draw(img)
    top, mid, low = (22, 40, 92), (214, 96, 90), (255, 190, 110)       # سماء الفجر
    for y in range(S):
        t = y / (S * 0.62)
        c = lerp(top, mid, t / 0.6) if t < 0.6 else lerp(mid, low, min(1, (t - 0.6) / 0.4))
        d.line([(0, y), (S, y)], fill=c)
    # نجوم خفيفة
    rnd = random.Random(7)
    for _ in range(60):
        x, y = rnd.randint(0, S), rnd.randint(0, int(S * 0.35)); r = rnd.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    # شمس بتوهج
    glow = Image.new('RGB', (S, S), (0, 0, 0)); g = ImageDraw.Draw(glow)
    cx, cy = int(S * 0.5), int(S * 0.56)
    for r, a in [(330, 40), (240, 80), (170, 140), (120, 255)]:
        g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(a, int(a * .78), int(a * .45)))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.composite(Image.blend(img, Image.new('RGB', (S, S), (255, 214, 140)), .0), img, Image.new('L', (S, S), 255))
    from PIL import ImageChops
    img = ImageChops.add(img, glow)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 95, cy - 95, cx + 95, cy + 95], fill=(255, 236, 170))

    def ridge(base, amp, seed, rough, col, snow=False):
        r = random.Random(seed); pts = []
        n = 120; h = 0
        for i in range(n + 1):
            x = S * i / n
            h += r.uniform(-rough, rough); h *= .96
            y = base - amp * (abs(math.sin(i / n * math.pi * 2.2 + seed)) * .8 + .2) + h
            pts.append((x, y))
        poly = pts + [(S, S), (0, S)]
        d.polygon(poly, fill=col)
        if snow:
            for i in range(1, n):
                if pts[i][1] < base - amp * .78 and pts[i][1] <= pts[i - 1][1] and pts[i][1] <= pts[i + 1][1]:
                    x, y = pts[i]
                    d.polygon([(x - 34, y + 34), (x, y), (x + 34, y + 34), (x + 16, y + 26), (x, y + 38), (x - 14, y + 27)], fill=(246, 248, 255))
    ridge(640, 330, 1.3, 9, (88, 98, 148), True)       # جبال بعيدة
    ridge(700, 260, 2.1, 12, (52, 82, 112))             # وسطى
    ridge(780, 190, 4.4, 14, (30, 76, 70))              # قريبة خضراء
    # بحيرة
    lake_y = 800
    d.rectangle([0, lake_y, S, S], fill=(52, 96, 140))
    refl = img.crop((0, 560, S, lake_y)).transpose(Image.FLIP_TOP_BOTTOM).resize((S, S - lake_y))
    refl = refl.filter(ImageFilter.GaussianBlur(6)); refl = Image.blend(refl, Image.new('RGB', refl.size, (52, 96, 140)), .5)
    img.paste(refl, (0, lake_y))
    d = ImageDraw.Draw(img)
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for i in range(16):
        y = lake_y + 16 + i * 13; w = 60 + i * 22
        ld.line([(S / 2 - w, y), (S / 2 + w, y)], fill=(255, 214, 150, max(40, 190 - i * 10)), width=3)
    img = Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB'); d = ImageDraw.Draw(img)
    # صنوبر على الجانبين
    def pine(x, base, h, col):
        for k in range(5):
            w = h * (.16 + k * .06); y0 = base - h + k * h * .17
            d.polygon([(x, y0), (x - w, y0 + h * .3), (x + w, y0 + h * .3)], fill=col)
        d.rectangle([x - 6, base - h * .08, x + 6, base + 6], fill=col)
    for x, h in [(70, 250), (150, 190), (230, 140), (S - 80, 270), (S - 170, 200), (S - 250, 150)]:
        pine(x, 800, h, (14, 40, 40))
    # طيور
    for bx, by in [(300, 250), (360, 210), (700, 280)]:
        d.arc([bx - 22, by - 10, bx, by + 8], 200, 340, fill=(30, 30, 50), width=4)
        d.arc([bx, by - 10, bx + 22, by + 8], 200, 340, fill=(30, 30, 50), width=4)
    return img

def font(size):
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size, layout_engine=ImageFont.Layout.RAQM), f
    raise SystemExit('لا يوجد خط عربي')

def text_layer(fill=True):
    size = 460
    while True:
        ft, used = font(size)
        L = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        bb = d.textbbox((0, 0), WORD, font=ft, direction='rtl', language='ar', features=['-kern'] if False else None)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        if w <= S * 0.66 or size < 120: break
        size -= 12
    x = (S - w) / 2 - bb[0]; y = (S - h) / 2 - bb[1] - 10
    sh = Image.new('RGBA', (S, S), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.text((x + 10, y + 14), WORD, font=ft, fill=(0, 0, 0, 170), direction='rtl', language='ar')
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(L)
    d.text((x, y), WORD, font=ft, fill=(255, 250, 235, 255), direction='rtl', language='ar',
           stroke_width=10, stroke_fill=(150, 92, 20, 255))
    d.text((x, y), WORD, font=ft, fill=(255, 250, 235, 255), direction='rtl', language='ar')
    out = Image.alpha_composite(sh, L)
    return out, used

bg = scene()
txt, used = text_layer()
full = bg.convert('RGBA'); full.alpha_composite(txt)
full.convert('RGB').save(os.path.join(OUT, 'icon-only.png'))
bg.save(os.path.join(OUT, 'icon-background.png'))
txt.save(os.path.join(OUT, 'icon-foreground.png'))
print('font used:', used)
