"""
Generate sample images for cv-07 Pose Detection Fitness Trainer.
Run: pip install Pillow && python generate_samples.py
Output: 5 images — standing, squat, lunge, arms raised, plank.
"""
from PIL import Image, ImageDraw
import os, math

OUT = os.path.dirname(__file__)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def draw_stick(d, joints, connections, color=(60, 120, 200), r=8):
    for a, b in connections:
        d.line([joints[a], joints[b]], fill=color, width=4)
    for pt in joints.values():
        d.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=(220, 100, 60))


def standing():
    img = Image.new("RGB", (400, 600), (220, 235, 250))
    d = ImageDraw.Draw(img)
    j = {
        "head": (200, 80), "neck": (200, 130),
        "lshoulder": (150, 160), "rshoulder": (250, 160),
        "lelbow": (120, 240), "relbow": (280, 240),
        "lwrist": (110, 310), "rwrist": (290, 310),
        "lhip": (170, 310), "rhip": (230, 310),
        "lknee": (165, 410), "rknee": (235, 410),
        "lankle": (160, 510), "rankle": (240, 510),
    }
    c = [("head","neck"),("neck","lshoulder"),("neck","rshoulder"),
         ("lshoulder","lelbow"),("lelbow","lwrist"),
         ("rshoulder","relbow"),("relbow","rwrist"),
         ("lshoulder","lhip"),("rshoulder","rhip"),("lhip","rhip"),
         ("lhip","lknee"),("lknee","lankle"),
         ("rhip","rknee"),("rknee","rankle")]
    d.ellipse([170, 40, 230, 100], fill=(220, 180, 140))
    draw_stick(d, j, c)
    d.text((130, 540), "Standing", fill=(60, 60, 60))
    return img


def squat():
    img = Image.new("RGB", (400, 600), (235, 220, 250))
    d = ImageDraw.Draw(img)
    j = {
        "head": (200, 100), "neck": (200, 150),
        "lshoulder": (150, 180), "rshoulder": (250, 180),
        "lelbow": (110, 250), "relbow": (290, 250),
        "lwrist": (90, 310), "rwrist": (310, 310),
        "lhip": (165, 310), "rhip": (235, 310),
        "lknee": (130, 400), "rknee": (270, 400),
        "lankle": (120, 490), "rankle": (280, 490),
    }
    c = [("head","neck"),("neck","lshoulder"),("neck","rshoulder"),
         ("lshoulder","lelbow"),("lelbow","lwrist"),
         ("rshoulder","relbow"),("relbow","rwrist"),
         ("lshoulder","lhip"),("rshoulder","rhip"),("lhip","rhip"),
         ("lhip","lknee"),("lknee","lankle"),
         ("rhip","rknee"),("rknee","rankle")]
    d.ellipse([170, 60, 230, 120], fill=(220, 180, 140))
    draw_stick(d, j, c)
    d.text((140, 540), "Squat", fill=(60, 60, 60))
    return img


def arms_raised():
    img = Image.new("RGB", (400, 600), (220, 250, 235))
    d = ImageDraw.Draw(img)
    j = {
        "head": (200, 80), "neck": (200, 130),
        "lshoulder": (150, 160), "rshoulder": (250, 160),
        "lelbow": (100, 100), "relbow": (300, 100),
        "lwrist": (70, 50), "rwrist": (330, 50),
        "lhip": (170, 310), "rhip": (230, 310),
        "lknee": (165, 420), "rknee": (235, 420),
        "lankle": (160, 520), "rankle": (240, 520),
    }
    c = [("head","neck"),("neck","lshoulder"),("neck","rshoulder"),
         ("lshoulder","lelbow"),("lelbow","lwrist"),
         ("rshoulder","relbow"),("relbow","rwrist"),
         ("lshoulder","lhip"),("rshoulder","rhip"),("lhip","rhip"),
         ("lhip","lknee"),("lknee","lankle"),
         ("rhip","rknee"),("rknee","rankle")]
    d.ellipse([170, 40, 230, 100], fill=(220, 180, 140))
    draw_stick(d, j, c)
    d.text((110, 550), "Arms Raised", fill=(60, 60, 60))
    return img


def lunge():
    img = Image.new("RGB", (500, 600), (250, 235, 220))
    d = ImageDraw.Draw(img)
    j = {
        "head": (220, 80), "neck": (220, 130),
        "lshoulder": (170, 160), "rshoulder": (270, 160),
        "lelbow": (140, 240), "relbow": (300, 240),
        "lwrist": (130, 310), "rwrist": (310, 310),
        "lhip": (190, 310), "rhip": (250, 310),
        "lknee": (160, 420), "rknee": (320, 400),
        "lankle": (140, 520), "rankle": (380, 490),
    }
    c = [("head","neck"),("neck","lshoulder"),("neck","rshoulder"),
         ("lshoulder","lelbow"),("lelbow","lwrist"),
         ("rshoulder","relbow"),("relbow","rwrist"),
         ("lshoulder","lhip"),("rshoulder","rhip"),("lhip","rhip"),
         ("lhip","lknee"),("lknee","lankle"),
         ("rhip","rknee"),("rknee","rankle")]
    d.ellipse([190, 40, 250, 100], fill=(220, 180, 140))
    draw_stick(d, j, c)
    d.text((170, 550), "Lunge", fill=(60, 60, 60))
    return img


def plank():
    img = Image.new("RGB", (600, 400), (240, 240, 220))
    d = ImageDraw.Draw(img)
    j = {
        "head": (100, 180), "neck": (150, 190),
        "lshoulder": (200, 200), "rshoulder": (200, 220),
        "lelbow": (200, 260), "relbow": (200, 280),
        "lwrist": (200, 310), "rwrist": (200, 330),
        "lhip": (350, 200), "rhip": (350, 220),
        "lknee": (450, 200), "rknee": (450, 220),
        "lankle": (540, 200), "rankle": (540, 220),
    }
    c = [("head","neck"),("neck","lshoulder"),("neck","rshoulder"),
         ("lshoulder","lelbow"),("lelbow","lwrist"),
         ("rshoulder","relbow"),("relbow","rwrist"),
         ("lshoulder","lhip"),("rshoulder","rhip"),("lhip","rhip"),
         ("lhip","lknee"),("lknee","lankle"),
         ("rhip","rknee"),("rknee","rankle")]
    d.ellipse([70, 155, 130, 205], fill=(220, 180, 140))
    draw_stick(d, j, c)
    d.rectangle([0, 340, 600, 360], fill=(160, 140, 100))
    d.text((220, 360), "Plank", fill=(60, 60, 60))
    return img


if __name__ == "__main__":
    print("Generating cv-07 samples...")
    save(standing(), "sample_standing.jpg")
    save(squat(), "sample_squat.jpg")
    save(arms_raised(), "sample_arms_raised.jpg")
    save(lunge(), "sample_lunge.jpg")
    save(plank(), "sample_plank.jpg")
    print("Done — 5 images in samples/")
