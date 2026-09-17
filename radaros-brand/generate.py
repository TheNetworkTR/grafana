#!/usr/bin/env python3
"""Render The Network. artwork into the filenames Grafana's own code imports.

    ./generate.py <logo-kit-svg-dir> <agencyos-logo.svg>

Writes into ../public/img/, replacing Grafana's artwork in place. Doing it by
filename rather than by adding new files keeps the patch to Branding.tsx down to
text constants: the imports there already point at these three names, so a
rebase onto a new upstream tag never has to re-point them.

TWO SCALES, WHICH IS THE WHOLE POINT OF THIS FILE. The Network. kit ships a
compact monogram for small surfaces and a full three-line mark for large ones,
and `agencyos/docs/LOGO_USAGE.md` is explicit about which goes where. The menu
logo and the favicon live in a 32px box, where the full mark renders as mud —
measured by rendering both at 32px and comparing. Everything at that size gets
the monogram; only the login backdrop, which is 1920x1080, gets the full mark.
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

# Brand tokens — agencyos/docs/LOGO_USAGE.md is the source of truth.
INK = "#000000"      # black mark, for light surfaces
PAPER = "#ffffff"    # white mark, for dark surfaces
DARK_BG = "#171717"  # brand dark background

OUT = Path(__file__).resolve().parent.parent / "public" / "img"
PATH_RE = re.compile(r"<path\b.*?/>", re.S)
VIEWBOX_RE = re.compile(r'viewBox="([\d.\s-]+)"')


def read(src: Path):
    text = src.read_text()
    box = [float(v) for v in VIEWBOX_RE.search(text).group(1).split()]
    return PATH_RE.findall(text), box


def measure(src: Path, box):
    """Ink bounds in viewBox units — the kit pads its canvas, Grafana does not."""
    png = OUT / ".measure.png"
    subprocess.run(["rsvg-convert", "-w", str(int(box[2])), "-h", str(int(box[3])),
                    "-o", str(png), str(src)], check=True)
    left, top, right, bottom = Image.open(png).getbbox()
    png.unlink()
    return [box[0] + left, box[1] + top, right - left, bottom - top]


def mark(paths, box, light_fill, dark_fill=None):
    """One file answering to both colourways when dark_fill is given.

    The query reads the BROWSER's theme rather than Grafana's, which is why the
    systemd drop-in sets GF_USERS_DEFAULT_THEME=system: it ties the two to one
    source instead of letting a dark sidebar show a black logo.
    """
    style = f".m{{fill:{light_fill}}}"
    if dark_fill:
        style += f"@media(prefers-color-scheme:dark){{.m{{fill:{dark_fill}}}}}"
    body = "".join(p.replace("<path ", '<path class="m" ') for p in paths)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s">'
            "<style>%s</style>%s</svg>"
            % (" ".join(f"{v:g}" for v in box), style, body))


def backdrop(paths, box, ground, watermark):
    """Login backdrop: flat brand ground, the full mark held well back."""
    w, h = 1920, 1080
    scale = (h * 0.62) / box[3]
    tx = (w - box[2] * scale) / 2 - box[0] * scale
    ty = (h - box[3] * scale) / 2 - box[1] * scale
    body = "".join(p.replace("<path ", f'<path fill="{watermark}" ') for p in paths)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'preserveAspectRatio="xMidYMid slice">'
            '<rect width="%d" height="%d" fill="%s"/>'
            '<g opacity="0.05" transform="translate(%.2f %.2f) scale(%.4f)">%s</g>'
            "</svg>" % (w, h, w, h, ground, tx, ty, scale, body))


def app_icon(bg_path, paths, box):
    """Tab and touch icon: the kit's own rounded ground, white monogram on it.

    Its own dark ground is what keeps the icon legible against a light AND a
    dark browser chrome — a transparent mark would disappear into one of them.
    """
    side = 512
    scale = (side * 0.68) / box[2]
    tx = (side - box[2] * scale) / 2 - box[0] * scale
    ty = (side - box[3] * scale) / 2 - box[1] * scale
    body = "".join(p.replace("<path ", f'<path fill="{PAPER}" ') for p in paths)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">%s'
            '<g transform="translate(%.2f %.2f) scale(%.4f)">%s</g></svg>'
            % (side, side, bg_path, tx, ty, scale, body))


def main(kit_dir: Path, mark_src: Path):
    monogram_src = kit_dir / "thenetworktr_logo_s.svg"
    favicon_src = kit_dir / "thenetworktr_favicon.svg"
    for src in (monogram_src, favicon_src, mark_src):
        if not src.is_file():
            sys.exit(f"missing source: {src}")
    OUT.mkdir(parents=True, exist_ok=True)

    mono_paths, mono_raw = read(monogram_src)
    mono = measure(monogram_src, mono_raw)
    full_paths, full_raw = read(mark_src)
    full = measure(mark_src, full_raw)

    # The kit's favicon ground: its first path is the rounded square, the rest
    # are the three-line mark we are replacing with the monogram.
    ground = read(favicon_src)[0][0]

    files = {
        # Imported by Branding.tsx as the menu logo, the login logo and the
        # preloader mark — every one of them a small box.
        "grafana_icon.svg": mark(mono_paths, mono, INK, PAPER),
        "grafana_mask_icon.svg": mark(mono_paths, mono, INK),
        "grafana_mask_icon_white.svg": mark(mono_paths, mono, PAPER),
        # 1920x1080, the one surface with room for the full mark.
        "g8_login_dark.svg": backdrop(full_paths, full, DARK_BG, PAPER),
        "g8_login_light.svg": backdrop(full_paths, full, PAPER, INK),
    }
    for name, text in files.items():
        (OUT / name).write_text(text)

    icon_svg = OUT / ".app-icon.svg"
    icon_svg.write_text(app_icon(ground, mono_paths, mono))
    for name, px in (("fav32.png", 32), ("apple-touch-icon.png", 180)):
        subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px),
                        "-o", str(OUT / name), str(icon_svg)], check=True)
    icon_svg.unlink()
    # Apple forbids alpha on the touch icon.
    touch = OUT / "apple-touch-icon.png"
    Image.open(touch).convert("RGB").save(touch)

    print(f"monogram {mono_raw} -> {[round(v, 1) for v in mono]}")
    print(f"full mark {full_raw} -> {[round(v, 1) for v in full]}")
    print(f"{len(files) + 2} files written to {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).expanduser(), Path(sys.argv[2]).expanduser())
