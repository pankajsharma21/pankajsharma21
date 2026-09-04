#!/usr/bin/env python3
"""Animated terminal: lines type themselves out in sequence, then a cursor blinks.

The typing effect is a clip rect whose width animates from 0. That means text is
hidden until its animation runs, so a reduced-motion rule reveals everything at
once rather than leaving a blank box for anyone who has motion turned off.
"""
CW = 8.42          # DejaVu Sans Mono advance width at 14px
FS = 14
LH = 23
PAD_X, TOP = 26, 74
W = 900

# (prompt, text, css class for the text colour)
LINES = [
    ("$ ", "whoami",                              "cmd"),
    ("",   "pankaj — java backend engineer",      "out"),
    ("",   "",                                    "out"),
    ("$ ", "cat stack.txt",                       "cmd"),
    ("",   "java · spring boot · kafka · redis",  "out"),
    ("",   "postgres · docker · aws · elk",       "out"),
    ("",   "",                                    "out"),
    ("$ ", "ls ~/projects --featured",            "cmd"),
    ("",   "CHINTU/       offline AI assistant",  "hi"),
    ("",   "AI_Debugger/  logs → root cause",     "hi"),
    ("",   "",                                    "out"),
    ("$ ", "git log --oneline | wc -l",           "cmd"),
    ("",   "156",                                 "num"),
]

H = TOP + LH * len(LINES) + 26

rows, clips, css = [], [], []
t = 0.25                                   # running start time, seconds
for i, (prompt, text, cls) in enumerate(LINES):
    y = TOP + i * LH
    full = prompt + text
    width = max(len(full) * CW, 1)
    dur = max(len(full) * 0.022, 0.12) if full else 0.08
    clips.append(
        f'<clipPath id="c{i}"><rect id="r{i}" x="{PAD_X}" y="{y-14}" width="{width:.1f}" height="20"/></clipPath>')
    css.append(f'  #r{i} {{ animation: type{i} {dur:.2f}s steps({max(len(full),1)}) {t:.2f}s both }}')
    css.append(f'  @keyframes type{i} {{ from {{ width:0 }} to {{ width:{width:.1f}px }} }}')
    seg = ''
    if prompt:
        seg += f'<tspan class="pr">{prompt}</tspan>'
    if text:
        esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        seg += f'<tspan class="{cls}">{esc}</tspan>'
    if seg:
        rows.append(f'<g clip-path="url(#c{i})"><text x="{PAD_X}" y="{y}" class="mono">{seg}</text></g>')
    t += dur + (0.10 if full else 0.04)

cursor_x = PAD_X + len(LINES[-1][0] + LINES[-1][1]) * CW + 2
cursor_y = TOP + (len(LINES) - 1) * LH

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal introduction">
<defs>
  <linearGradient id="win" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#0f1524"/><stop offset="100%" stop-color="#0a0f1c"/>
  </linearGradient>
  {"".join(clips)}
</defs>
<style>
  .mono {{ font-family: ui-monospace,SFMono-Regular,Menlo,Consolas,"DejaVu Sans Mono",monospace; font-size:{FS}px }}
  .pr  {{ fill:#5cff9d }}
  .cmd {{ fill:#e8eefc }}
  .out {{ fill:#8ea0c4 }}
  .hi  {{ fill:#7fb0ff }}
  .num {{ fill:#ffd15c }}
  .cur {{ fill:#5cff9d; animation: blink 1.05s steps(1) 0.2s infinite }}
  @keyframes blink {{ 0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }} }}
{chr(10).join(css)}
  /* With motion turned off the clip rects would stay at width 0 and the box
     would read as empty — so show every line at once instead. */
  @media (prefers-reduced-motion: reduce) {{
    [id^="r"] {{ animation: none !important }}
    .cur {{ animation: none !important }}
  }}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#win)" stroke="#243049"/>
<path d="M 1 13 A 12 12 0 0 1 13 1 L {W-13} 1 A 12 12 0 0 1 {W-1} 13 L {W-1} 42 L 1 42 Z" fill="#151d30"/>
<circle cx="26" cy="22" r="6" fill="#ff5f57"/><circle cx="46" cy="22" r="6" fill="#febc2e"/><circle cx="66" cy="22" r="6" fill="#28c840"/>
<text x="{W/2}" y="27" text-anchor="middle" class="mono" font-size="12.5" fill="#61708f">pankaj@github — zsh</text>
{"".join(rows)}
<rect class="cur" x="{cursor_x:.1f}" y="{cursor_y-11}" width="8" height="15"/>
</svg>'''

open("/home/pankaj/pankajsharma21/assets/terminal.svg", "w").write(svg)
print("terminal.svg written:", len(svg), "bytes  size:", W, "x", H)
