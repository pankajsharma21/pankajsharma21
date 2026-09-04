#!/usr/bin/env python3
"""Generates the animated space hero banner. Star positions are generated rather
than hand-written so the field looks scattered instead of patterned."""
import random

random.seed(21)          # fixed seed: the same stars every rebuild, no churn in git
W, H = 1000, 320

stars = []
for i in range(70):
    x = random.uniform(4, W - 4)
    y = random.uniform(4, H - 4)
    r = random.choice([0.7, 0.9, 1.1, 1.4, 1.8])
    dur = round(random.uniform(2.2, 5.5), 2)
    delay = round(random.uniform(0, 5), 2)
    base = round(random.uniform(0.25, 0.75), 2)
    stars.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" '
                 f'style="animation:tw {dur}s ease-in-out {delay}s infinite" opacity="{base}"/>')

# A few larger four-point sparkles for depth.
sparkles = []
for i in range(6):
    x = random.uniform(60, W - 60)
    y = random.uniform(30, H - 40)
    s = random.uniform(3.5, 6)
    d = round(random.uniform(3, 6), 2)
    dl = round(random.uniform(0, 4), 2)
    sparkles.append(
        f'<path d="M {x:.1f} {y-s:.1f} Q {x:.1f} {y:.1f} {x+s:.1f} {y:.1f} '
        f'Q {x:.1f} {y:.1f} {x:.1f} {y+s:.1f} Q {x:.1f} {y:.1f} {x-s:.1f} {y:.1f} '
        f'Q {x:.1f} {y:.1f} {x:.1f} {y-s:.1f} Z" fill="#cfe3ff" '
        f'style="animation:tw {d}s ease-in-out {dl}s infinite"/>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Pankaj Sharma — Java backend engineer">
<defs>
  <linearGradient id="space" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#070b18"/><stop offset="55%" stop-color="#0d1430"/><stop offset="100%" stop-color="#131a3d"/>
  </linearGradient>
  <radialGradient id="glow" cx="50%" cy="50%">
    <stop offset="0%" stop-color="#4c7dff" stop-opacity=".33"/><stop offset="100%" stop-color="#4c7dff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="planet" cx="35%" cy="30%">
    <stop offset="0%" stop-color="#3f6ae0"/><stop offset="60%" stop-color="#24408f"/><stop offset="100%" stop-color="#152354"/>
  </radialGradient>
  <linearGradient id="suit" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#ffffff"/><stop offset="55%" stop-color="#e4e9f5"/><stop offset="100%" stop-color="#bcc5da"/>
  </linearGradient>
  <linearGradient id="visor" x1="0.1" y1="0" x2="0.9" y2="1">
    <stop offset="0%" stop-color="#1b2a55"/><stop offset="45%" stop-color="#0a1330"/><stop offset="100%" stop-color="#254a9a"/>
  </linearGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#ffffff"/><stop offset="55%" stop-color="#bfd4ff"/><stop offset="100%" stop-color="#7fa9ff"/>
  </linearGradient>
</defs>
<style>
  @keyframes tw    {{ 0%,100% {{ opacity:.18 }} 50% {{ opacity:1 }} }}
  @keyframes float {{ 0%,100% {{ transform:translate(0,0) rotate(-6deg) }}
                     50%     {{ transform:translate(-10px,-18px) rotate(2deg) }} }}
  @keyframes drift {{ 0%,100% {{ transform:translate(0,0) }} 50% {{ transform:translate(0,-7px) }} }}
  @keyframes spin  {{ from {{ transform:rotate(0) }} to {{ transform:rotate(360deg) }} }}
  .astro  {{ animation: float 7s ease-in-out infinite; transform-origin: 815px 165px; }}
  .planet {{ animation: drift 11s ease-in-out infinite; }}
  .ring   {{ animation: spin 40s linear infinite; transform-origin: 690px 92px; }}
  @media (prefers-reduced-motion: reduce) {{
    .astro,.planet,.ring,circle,path {{ animation: none !important }}
  }}
</style>

<rect width="{W}" height="{H}" fill="url(#space)"/>
<ellipse cx="810" cy="160" rx="260" ry="190" fill="url(#glow)"/>
{"".join(stars)}
{"".join(sparkles)}

<!-- distant planet with an orbiting ring -->
<g class="planet">
  <circle cx="690" cy="92" r="30" fill="url(#planet)"/>
  <ellipse cx="690" cy="92" rx="46" ry="13" fill="none" stroke="#5f86ff" stroke-opacity=".55" stroke-width="2" class="ring" transform="rotate(-18 690 92)"/>
  <circle cx="678" cy="84" r="5" fill="#1a2c63" opacity=".65"/>
  <circle cx="700" cy="101" r="3.5" fill="#1a2c63" opacity=".5"/>
</g>

<!-- astronaut: tether first so it sits behind the suit -->
<g class="astro">
  <path d="M 762 196 C 726 214, 700 236, 668 244" fill="none" stroke="#8fa3c8" stroke-width="2" stroke-opacity=".7" stroke-linecap="round"/>
  <rect x="784" y="126" width="58" height="66" rx="16" fill="#9aa8c4"/>
  <rect x="792" y="134" width="42" height="20" rx="7" fill="#7e8ca8"/>
  <g>
    <rect x="789" y="150" width="52" height="62" rx="20" fill="url(#suit)"/>
    <rect x="801" y="168" width="28" height="18" rx="5" fill="#59657f"/>
    <circle cx="808" cy="177" r="3" fill="#5cff9d"/>
    <circle cx="818" cy="177" r="3" fill="#ffd15c"/>
    <rect x="765" y="156" width="26" height="14" rx="7" fill="url(#suit)" transform="rotate(-26 778 163)"/>
    <rect x="839" y="156" width="26" height="14" rx="7" fill="url(#suit)" transform="rotate(22 852 163)"/>
    <rect x="795" y="206" width="16" height="30" rx="8" fill="url(#suit)" transform="rotate(9 803 221)"/>
    <rect x="819" y="206" width="16" height="30" rx="8" fill="url(#suit)" transform="rotate(-13 827 221)"/>
    <circle cx="815" cy="132" r="30" fill="url(#suit)"/>
    <circle cx="815" cy="132" r="23" fill="url(#visor)"/>
    <path d="M 802 122 Q 810 116 820 119 Q 810 124 806 132 Z" fill="#9fc4ff" opacity=".75"/>
    <circle cx="824" cy="140" r="4" fill="#bcd8ff" opacity=".35"/>
  </g>
</g>

<g><text x="70" y="128" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif" font-size="52" font-weight="700" fill="url(#name)">Pankaj Sharma</text></g>
<g><text x="72" y="166" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif" font-size="20" fill="#8fa6d8" letter-spacing="3.5">JAVA  BACKEND  ENGINEER</text></g>
<g>
  <rect x="70" y="192" width="205" height="30" rx="15" fill="#4c7dff" fill-opacity=".13" stroke="#4c7dff" stroke-opacity=".4"/>
  <text x="88" y="212" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif" font-size="13.5" fill="#a9c2ff">Spring Boot · Kafka · AWS</text>
  <rect x="285" y="192" width="188" height="30" rx="15" fill="#5cff9d" fill-opacity=".1" stroke="#5cff9d" stroke-opacity=".33"/>
  <text x="303" y="212" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif" font-size="13.5" fill="#8ef0bd">Building local-first AI</text>
</g>
</svg>'''

open("/home/pankaj/pankajsharma21/assets/hero.svg", "w").write(svg)
print("hero.svg written:", len(svg), "bytes")
