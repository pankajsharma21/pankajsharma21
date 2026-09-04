#!/usr/bin/env python3
"""Builds assets/stack.svg — the tech-stack pills.

Drawn here rather than pulled from shields.io or devicon: those are third-party
endpoints that see every profile view, can rate-limit, and occasionally change
what they return. A committed SVG cannot break.
"""
CW, FS, PAD = 7.5, 13.5, 15          # char width at 13.5px, font size, pill padding
GAP_X, GAP_Y, ROW_H = 9, 40, 30

GROUPS = [
    ("LANGUAGE & FRAMEWORK", [
        ("Java", "#e76f00"), ("Spring Boot", "#6db33f"), ("Hibernate / JPA", "#59666c"),
        ("REST APIs", "#4c7dff"), ("Python", "#3572A5"),
    ]),
    ("DATA & MESSAGING", [
        ("PostgreSQL", "#336791"), ("MySQL", "#00758f"), ("Redis", "#d82c20"),
        ("Kafka", "#231f20"), ("RabbitMQ", "#ff6600"),
    ]),
    ("INFRA & OBSERVABILITY", [
        ("AWS", "#ff9900"), ("Docker", "#2496ed"), ("Kubernetes", "#326ce5"),
        ("ELK Stack", "#00bfb3"), ("CloudWatch", "#c925d1"), ("Kibana", "#e8478b"),
    ]),
    ("PATTERNS", [
        ("Microservices", "#4c7dff"), ("Spring Cloud", "#6db33f"),
        ("Circuit Breaker", "#8b5cf6"), ("Eureka / Gateway", "#0ea5e9"),
    ]),
]

W = 900
BG, EDGE, MUTED = "#0b1120", "#233149", "#8095bd"
FONT = "'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif"


def esc(t):
    """Group titles contain '&', which is not valid raw text in XML."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def readable(bg):
    """Pick black or white text so every pill stays legible — a few brand colours
    (Kafka's near-black, Java's orange) sit on opposite sides of the line."""
    r, g, b = hex_to_rgb(bg)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0b1120" if lum > 0.62 else "#ffffff"


parts = []
TITLE_GAP = 16     # title baseline -> top of its pill row
GROUP_GAP = 26     # bottom of a group's last row -> next title baseline
ROW_GAP = 8

y = 30                                   # baseline of the first group title
for title, items in GROUPS:
    parts.append(f'<text x="26" y="{y}" font-size="11.5" fill="{MUTED}" letter-spacing="1.4" '
                 f'font-family="{FONT}">{esc(title)}</text>')
    row_top = y + TITLE_GAP
    x = 26
    for label, color in items:
        w = len(label) * CW + PAD * 2
        if x + w > W - 26:                # wrap before running off the card
            x = 26
            row_top += ROW_H + ROW_GAP
        parts.append(
            f'<g><rect x="{x:.1f}" y="{row_top}" width="{w:.1f}" height="{ROW_H}" rx="{ROW_H/2}" '
            f'fill="{color}" fill-opacity="0.92"/>'
            f'<text x="{x + w/2:.1f}" y="{row_top + 20}" text-anchor="middle" font-size="{FS}" '
            f'font-weight="600" fill="{readable(color)}" font-family="{FONT}">{esc(label)}</text></g>')
        x += w + GAP_X
    y = row_top + ROW_H + GROUP_GAP       # baseline of the next group title

H = y - GROUP_GAP + 20                    # last row's bottom plus breathing room

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'role="img" aria-label="Tech stack">\n'
       f'<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{EDGE}"/>\n'
       + "\n".join(parts) + "\n</svg>")

open("assets/stack.svg", "w").write(svg)
print("stack.svg written:", W, "x", H)
