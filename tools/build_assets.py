#!/usr/bin/env python3
"""Rebuild public/img from the sibling checkouts.

The meerverse site owns no artwork of its own yet: every logo and screenshot
belongs to one of the apps, and this pulls them in from checkouts that sit next
to this repo (../meercal, ../meerail, ../meerato, ../meerpic, ../meerink), so a
new logo or a re-shot screenshot there is one command away from being here.
meerpad joined them (../meerpad).

    python3 tools/build_assets.py

Needs Pillow. Writes WebP for everything the page shows and PNG for the
favicons, which is what browsers still expect there, and JPEG for the link
preview card, which is what link unfurlers still expect there.

The family picture in the hero and the waving meerkat used as the brand mark
are stand-ins until meerverse has artwork of its own: replace
public/img/family.webp and public/img/brand-*.png and drop the matching steps
below.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT.parent
OUT = ROOT / "public" / "img"

# Which picture stands for each app: the small in-app logo, the meerkat peeking
# over the thing the app is about, not the full-body one some websites use in
# their hero. meerink's logo-square sits on a coloured tile, so its plain logo
# is used instead.
LOGOS = {
    "meercal": "meercal/website/public/img/logo-square.png",
    "meerail": "meerail/app/static/img/logo-square.png",
    "meerato": "meerato/app/static/logo-512.png",
    "meerpic": "meerpic/app/static/img/logo.png",
    "meerink": "meerink/app/static/img/logo.png",
    "meerpad": "meerpad/app/static/img/logo.png",
}

# (output name, source, dark source or None). Screenshots are 2880x1800 in the
# sibling sites, 16:10, which is the frame the slider shows them in.
SHOTS = [
    ("meercal-ribbon", "meercal/website/public/img/screenshots/ribbon.png",
     "meercal/website/public/img/screenshots/ribbon-dark.png"),
    ("meerail-inbox", "meerail/website/public/img/screenshots/inbox.png",
     "meerail/website/public/img/screenshots/inbox-dark.png"),
    ("meerpad-page", "meerpad/app/static/img/screenshots/page.png",
     "meerpad/app/static/img/screenshots/page-dark.png"),
]
MEERATO_SHOT = "meerato/app/static/img/screenshots/overview.webp"


def load(rel: str | Path) -> Image.Image:
    """Open an RGBA image and trim it to its visible pixels."""
    im = Image.open(CODE / rel).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


def fit_height(im: Image.Image, h: int) -> Image.Image:
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def fit_box(im: Image.Image, size: int) -> Image.Image:
    scale = size / max(im.size)
    return im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)


def save_webp(im: Image.Image, path: Path, quality: int = 86) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=quality, method=6)
    print(f"{path.relative_to(ROOT)}  {im.width}x{im.height}  {path.stat().st_size // 1024} KB")


def square(im: Image.Image, size: int, pad: float = 0.04) -> Image.Image:
    """Centre an image on a transparent square canvas."""
    inner = round(size * (1 - 2 * pad))
    im = fit_box(im, inner)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return canvas


def app_logos() -> None:
    # Shown at 88px; 192 keeps them sharp at 2x.
    for name, rel in LOGOS.items():
        save_webp(fit_box(load(rel), 192), OUT / "apps" / f"{name}.webp")


def family() -> Image.Image:
    """The five shipping apps' meerkats as one group, for the hero: calendar and
    mail above, photos and tasks below, and meerpad's in the middle, drawn last
    so it sits in front. Sized and placed so no two of them touch."""
    w, h = 680, 640
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cal = fit_height(load(LOGOS["meercal"]), 225)
    mail = fit_height(load(LOGOS["meerail"]), 200)
    pic = fit_height(load(LOGOS["meerpic"]), 200)
    todo = fit_height(load(LOGOS["meerato"]), 222)
    pad = fit_height(load(LOGOS["meerpad"]), 212)
    canvas.alpha_composite(cal, (18, 4))
    canvas.alpha_composite(mail, (w - mail.width - 12, 36))
    canvas.alpha_composite(pic, (8, h - pic.height - 24))
    canvas.alpha_composite(todo, (w - todo.width - 34, h - todo.height - 4))
    canvas.alpha_composite(pad, ((w - pad.width) // 2 + 4, (h - pad.height) // 2 + 6))
    save_webp(canvas, OUT / "family.webp", quality=88)
    return canvas


def og_card(group: Image.Image) -> None:
    """1200x630 link preview: the family on white. The title comes from og:title."""
    card = Image.new("RGBA", (1200, 630), (255, 255, 255, 255))
    g = fit_height(group, 560)
    card.alpha_composite(g, ((1200 - g.width) // 2, 35))
    path = OUT / "og.jpg"
    card.convert("RGB").save(path, "JPEG", quality=88, optimize=True)
    print(f"{path.relative_to(ROOT)}  1200x630  {path.stat().st_size // 1024} KB")


def brand() -> None:
    """Nav mark and favicons: the waving meerkat, the family's neutral mascot."""
    mark = square(load("meerato/app/static/img/meerkat-waving.png"), 512, pad=0.02)
    for size in (32, 64, 180):
        path = OUT / f"brand-{size}.png"
        mark.resize((size, size), Image.LANCZOS).save(path, "PNG", optimize=True)
        print(f"{path.relative_to(ROOT)}  {size}x{size}")
    save_webp(mark.resize((128, 128), Image.LANCZOS), OUT / "brand.webp", quality=90)


def screenshots() -> None:
    for name, light, dark in SHOTS:
        save_webp(Image.open(CODE / light).convert("RGB"), OUT / "screenshots" / f"{name}.webp", 82)
        if dark:
            save_webp(Image.open(CODE / dark).convert("RGB"),
                      OUT / "screenshots" / f"{name}-dark.webp", 82)

    # meerato's shot is wider than 16:10 (1600x847). Its task rows have nothing
    # between the title and the status tags, so taking a strip out of that
    # empty middle gives the same picture a narrower window would draw, rather
    # than cropping the tags off the right edge.
    im = Image.open(CODE / MEERATO_SHOT).convert("RGB")
    target = round(im.height * 16 / 10)
    cut = im.width - target
    x0 = 1100
    out = Image.new("RGB", (target, im.height))
    out.paste(im.crop((0, 0, x0, im.height)), (0, 0))
    out.paste(im.crop((x0 + cut, 0, im.width, im.height)), (x0, 0))
    save_webp(out, OUT / "screenshots" / "meerato-overview.webp", 86)


if __name__ == "__main__":
    app_logos()
    og_card(family())
    brand()
    screenshots()
