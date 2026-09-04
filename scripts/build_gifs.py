#!/usr/bin/env python3
"""Bakes the animated SVGs into GIFs, because GitHub cannot animate the SVGs.

Verified in a real browser: an SVG loaded through <img> — exactly how GitHub
embeds README images — runs neither its CSS nor its SMIL animations. An animated
GIF does. So the SVGs stay the editable source of the artwork and this renders
them to a format that actually moves in a README.

Frames come from laying N copies of the SVG on one page, each with its animation
paused at a different negative delay, then screenshotting once and slicing that
sheet. One browser launch per batch instead of one per frame.

Usage: python3 scripts/build_gifs.py            # both
       python3 scripts/build_gifs.py hero       # just one
"""
import os
import re
import subprocess
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
TMP = os.path.join(ROOT, ".gifbuild")

JOBS = {
    # name: (width, height, loop seconds, frame count, colours, retimes)
    "hero": dict(w=1000, h=320, loop=4.0, frames=32, colors=64, retime=[
        ("animation: float 7s", "animation: float 4s"),
        ("animation: drift 11s", "animation: drift 4s"),
        ("animation: spin 40s", "animation: spin 8s"),
    ], strip_twinkle=True, shift_delays=False),
    "terminal": dict(w=900, h=399, loop=9.0, frames=54, colors=16,
                     retime=[], strip_twinkle=False, shift_delays=True, hold_first=2600,
                     loop_from_svg=True, tail=1.2, fps=9),
}


END_RE = re.compile(r"animation:\s*[\w-]+\s+([\d.]+)s\s+[\w-]+(?:\([^)]*\))?\s+([\d.]+)s\s+(?:both|forwards)")


def timeline_end(svg):
    """When the last non-repeating animation in the SVG finishes.

    Hardcoding the loop length silently truncated the terminal: the typing ran
    to 13s while the GIF was built for 9s, so the final lines never appeared and
    the "hold the finished state" frame was not actually finished.
    """
    return max((float(a) + float(b) for a, b in END_RE.findall(svg)), default=0.0)


def load(name, cfg):
    svg = open(os.path.join(ASSETS, name + ".svg")).read()
    for a, b in cfg["retime"]:
        svg = svg.replace(a, b)
    if cfg["strip_twinkle"]:
        # Twinkling stars repaint the whole frame and destroy GIF delta
        # compression; the float is what actually reads as motion anyway.
        svg = re.sub(r'style="animation:tw [^"]*"', "", svg)
    return svg


DELAY_RE = re.compile(r"(animation:\s*[\w-]+\s+[\d.]+s\s+[\w-]+(?:\([^)]*\))?\s+)"
                      r"(-?[\d.]+)(s\s+(?:both|forwards|infinite))")


def frozen(svg, t, shift_delays):
    """The same SVG with every animation held still at offset t.

    Two ways to reach offset t. Where all the animations start together (the
    hero) a single negative animation-delay is enough. Where they are staggered
    (the terminal types one line after another) that would flatten every line's
    own delay to the same value and they would all type at once — so there each
    existing delay is shifted by t instead of replaced.
    """
    if shift_delays:
        svg = DELAY_RE.sub(lambda m: "%s%.4f%s" % (m.group(1), float(m.group(2)) - t,
                                                   m.group(3)), svg)
        extra = "  * { animation-play-state: paused !important; }"
    else:
        extra = ("  * { animation-play-state: paused !important; "
                 "animation-delay: -%.4fs !important; }" % t)
    return svg.replace("<style>", "<style>\n" + extra, 1)


def shoot(svg, times, w, h, out_png, shift_delays):
    body = "".join('<div style="width:%dpx;height:%dpx;overflow:hidden">%s</div>'
                   % (w, h, frozen(svg, t, shift_delays)) for t in times)
    page = os.path.join(TMP, "_frames.html")
    open(page, "w").write('<html><body style="margin:0;background:#0a0f1c">'
                          + body + "</body></html>")
    # Pad the window well beyond the content. Sized exactly, headless Chrome
    # renders the SVG shorter than its declared height and silently crops the
    # bottom — that is what cut the last two terminal lines out of every frame.
    # The crop below still starts at (0,0), so the padding costs nothing.
    subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=%d,%d" % (w + 80, h * len(times) + 240),
                    "--screenshot=" + out_png, "file://" + page],
                   capture_output=True, timeout=300)


def build(name):
    cfg = JOBS[name]
    os.makedirs(TMP, exist_ok=True)
    svg = load(name, cfg)
    w = cfg["w"]
    h = cfg["h"]
    loop = cfg["loop"]
    if cfg.get("loop_from_svg"):
        loop = round(timeline_end(svg) + cfg.get("tail", 1.0), 2)
    n = max(2, int(round(loop * cfg["fps"]))) if cfg.get("fps") else cfg["frames"]
    times = [loop * i / n for i in range(n)]

    frames, batch = [], 8
    for start in range(0, n, batch):
        chunk = times[start:start + batch]
        png = os.path.join(TMP, "_b%d.png" % start)
        shoot(svg, chunk, w, h, png, cfg["shift_delays"])
        sheet = Image.open(png).convert("RGB")
        for i in range(len(chunk)):
            frames.append(sheet.crop((0, i * h, w, (i + 1) * h)))
    if len(frames) != n:
        sys.exit("%s: expected %d frames, got %d" % (name, n, len(frames)))

    # One palette shared by every frame, dithering off. Per-frame adaptive
    # palettes give the same background pixel a different index each frame, so
    # nothing compresses as unchanged and the file balloons — 3.4MB vs 855KB on
    # the hero when this was first built.
    base = frames[len(frames) // 2].convert("P", palette=Image.ADAPTIVE,
                                            colors=cfg["colors"], dither=Image.NONE)
    pal = [f.quantize(palette=base, dither=Image.NONE) for f in frames]

    # Merge runs of identical frames into one frame with a longer duration.
    # A typing animation holds still between lines, and Pillow's optimizer turns
    # those zero-difference frames into empty deltas that stop playback dead —
    # the terminal froze on its fourth frame until this was added. Merging is
    # also how a GIF is supposed to express "hold here", and it shrinks the file.
    step = loop * 1000 / n

    # Open on the finished state and hold it. Whatever a viewer's browser does
    # with animation, the first frame is what they are guaranteed to see, and an
    # empty terminal window says nothing. Holding the completed frame first also
    # gives the loop a natural beat: read it, clear, retype.
    if cfg.get("hold_first"):
        pal = [pal[-1]] + pal
        holds = [cfg["hold_first"]] + [step] * (len(pal) - 1)
    else:
        holds = [step] * len(pal)

    kept, durs = [], []
    for f, hold in zip(pal, holds):
        if kept and f.tobytes() == kept[-1].tobytes():
            durs[-1] += hold
        else:
            kept.append(f)
            durs.append(hold)
    durs = [max(20, int(round(d))) for d in durs]

    out = os.path.join(ASSETS, name + ".gif")
    kept[0].save(out, save_all=True, append_images=kept[1:],
                 duration=durs, loop=0, optimize=True, disposal=1)
    print("%-13s %4d KB  %d frames (%d after merging identical)  %dx%d  %.1fs loop"
          % (name + ".gif", os.path.getsize(out) // 1024, n, len(kept), w, h, loop))


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(JOBS)
    for name in wanted:
        if name not in JOBS:
            sys.exit("unknown asset %r (have: %s)" % (name, ", ".join(JOBS)))
        build(name)
    if os.path.isdir(TMP):
        for f in os.listdir(TMP):
            os.remove(os.path.join(TMP, f))
        os.rmdir(TMP)
