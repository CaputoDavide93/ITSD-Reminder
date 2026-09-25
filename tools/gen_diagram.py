#!/usr/bin/env python3
"""Draw every diagram in this repository as SVG, one file per colour scheme.

  docs/assets/<name>-light.svg
  docs/assets/<name>-dark.svg

The README used to carry a Mermaid flowchart. GitHub renders Mermaid on its own terms -- it decodes HTML entities
before parsing, ignores `%%{init}%%`, pins its own version and picks the
theme -- so a diagram cannot be art-directed there. Drawn here, it looks the
same on every page.

GitHub sanitises SVG in markdown, so no <style>, no <script>, no web font and
no <foreignObject>: everything is a presentation attribute and the type is a
system stack. Each pair is served from one <picture>, which GitHub switches on
prefers-color-scheme.

Layout is explicit rather than solved. The diagrams are small enough that
placing them by hand is cheaper than a layout engine nobody can predict.

House rules: a slate scale, a single accent on the one thing that matters in
each picture, drawn icons rather than emoji, monospace for anything that is
literally typed, and text contrast at or above 4.5:1 in both schemes.

After changing a diagram, run `python3 tools/gen_diagram.py` and commit the SVGs.
"""
from __future__ import annotations

import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parents[1]
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

SCHEMES = {
    "light": dict(card="#ffffff", border="#d8dee4", title="#0f172a", sub="#5b6673",
                  accent="#2b59c3", on_accent="#ffffff", soft="#f1f4f9",
                  line="#94a3b8", rule="#e6e9ee", chip="#475569",
                  warn="#9a3412", warn_soft="#fff4ed", group="#f7f9fb"),
    "dark":  dict(card="#161b22", border="#30363d", title="#e6edf3", sub="#9aa4b0",
                  accent="#4c7ef3", on_accent="#ffffff", soft="#1b2230",
                  line="#6b7684", rule="#232a33", chip="#aeb7c2",
                  warn="#ffa657", warn_soft="#2a1d14", group="#11151b"),
}

# Stroked glyphs on a 24x24 grid, drawn rather than typed.
ICONS = {
    "chip":    "M8 8h8v8H8z M5 5h14v14H5z M10 2v3 M14 2v3 M10 19v3 M14 19v3 M2 10h3 M2 14h3 M19 10h3 M19 14h3",
    "moon":    "M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z",
    "sliders": "M4 6h9 M17 6h3 M4 12h3 M11 12h9 M4 18h11 M19 18h1 M15 4v4 M9 10v4 M17 16v4",
    "chat":    "M4 5h16v11H9.5L5 20v-4H4z M8 9h8 M8 12h5",
    "heart":   "M12 20s-7.5-4.6-7.5-10A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 7.5 3c0 5.4-7.5 10-7.5 10z",
    "pulse":   "M3 12h4l2.5-6 5 12 2.5-6h4",
    "file":    "M6 3h8l4 4v14H6z M14 3v4h4 M9 12h6 M9 16h6",
    "search":  "M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 1 0 0-13z M15.5 15.5 20 20",
    "filter":  "M4 5h16l-6 7.5V19l-4 1.5v-8z",
    "send":    "M21 3 3 10.5l7.5 3 3 7.5z M10.5 13.5 21 3",
}


class Canvas:
    """Parts plus a size. No layout engine, on purpose."""

    def __init__(self, w: int, h: int, scheme: str, label: str) -> None:
        self.w, self.h, self.c, self.label = w, h, SCHEMES[scheme], label
        self.parts: list[str] = []

    def add(self, *svg: str) -> "Canvas":
        self.parts.extend(svg)
        return self

    # ── primitives ────────────────────────────────────────────────────────
    def icon(self, name, x, y, colour, size=21):
        s = size / 24
        return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" fill="none" '
                f'stroke="{colour}" stroke-width="1.7" stroke-linecap="round" '
                f'stroke-linejoin="round"><path d="{ICONS[name]}"/></g>')

    def text(self, x, y, s, *, size=13, colour=None, font=None, weight=None,
             anchor="start", opacity=None):
        c = colour or self.c["sub"]
        extra = (f' font-weight="{weight}"' if weight else "") + \
                (f' opacity="{opacity}"' if opacity else "")
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font or SANS}" '
                f'font-size="{size}" fill="{c}" text-anchor="{anchor}"{extra}>'
                f'{escape(s)}</text>')

    def box(self, x, y, w, h, title, subs=(), *, icon=None, tone="plain", rx=10):
        c = self.c
        fill, edge, tt = c["card"], c["border"], c["title"]
        st, op = c["sub"], ""
        if tone == "accent":
            fill = edge = c["accent"]; tt = st = c["on_accent"]; op = "0.85"
        elif tone == "soft":
            fill = c["soft"]
        elif tone == "warn":
            fill, edge, tt, st = c["warn_soft"], c["warn"], c["warn"], c["warn"]
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
               f'stroke="{edge}" stroke-width="1"/>']
        tx = x + 16
        ty = y + (28 if subs else h / 2 + 5)
        if icon:
            out.append(self.icon(icon, x + 16, y + (13 if subs else h / 2 - 10), tt))
            tx = x + 47
        out.append(self.text(tx, ty, title, size=15 if subs else 14,
                             colour=tt, weight="600"))
        for i, s in enumerate(subs):
            out.append(self.text(x + 16, y + 52 + i * 18, s, size=12.5,
                                 colour=st, opacity=op or None))
        return "".join(out)

    def diamond(self, cx, cy, w, h, lines):
        c = self.c
        pts = f"{cx},{cy - h/2} {cx + w/2},{cy} {cx},{cy + h/2} {cx - w/2},{cy}"
        out = [f'<polygon points="{pts}" fill="{c["soft"]}" stroke="{c["border"]}" '
               f'stroke-width="1"/>']
        n = len(lines)
        for i, s in enumerate(lines):
            out.append(self.text(cx, cy - (n - 1) * 7 + i * 14 + 4, s, size=12,
                                 colour=c["title"], anchor="middle"))
        return "".join(out)

    def pill(self, cx, cy, text, *, tone="plain", pad=16, size=13):
        c = self.c
        w = len(text) * size * 0.58 + pad * 2
        h = 32
        fill, edge, col = c["card"], c["border"], c["title"]
        if tone == "accent":
            fill = edge = c["accent"]; col = c["on_accent"]
        elif tone == "soft":
            fill = c["soft"]
        return (f'<rect x="{cx - w/2:.1f}" y="{cy - h/2}" width="{w:.1f}" height="{h}" '
                f'rx="{h/2}" fill="{fill}" stroke="{edge}" stroke-width="1"/>'
                + self.text(cx, cy + 4.5, text, size=size, colour=col, anchor="middle",
                            weight="500")), w

    def edge(self, pts, *, label=None, dash=False, both=False, label_at=0.5,
             label_dy=-9, label_anchor="middle", mono=True):
        c = self.c
        d = ' stroke-dasharray="5 4"' if dash else ""
        path = " ".join(f"{x},{y}" for x, y in pts)
        out = [f'<polyline points="{path}" fill="none" stroke="{c["line"]}" '
               f'stroke-width="1.5"{d} marker-end="url(#a)"'
               + (' marker-start="url(#a)"' if both else "") + "/>"]
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            lx = x1 + (x2 - x1) * label_at
            ly = y1 + (y2 - y1) * label_at
            out.append(self.text(lx, ly + label_dy, label, size=11.5,
                                 colour=c["chip"], font=MONO if mono else SANS,
                                 anchor=label_anchor))
        return "".join(out)

    def group(self, x, y, w, h, title):
        c = self.c
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
                f'fill="{c["group"]}" stroke="{c["border"]}" stroke-width="1" '
                f'stroke-dasharray="6 5"/>'
                + self.text(x + 18, y + 24, title, size=12, colour=c["sub"],
                            weight="600"))

    def footer(self, note):
        return (f'<line x1="24" y1="{self.h - 52}" x2="{self.w - 24}" y2="{self.h - 52}" '
                f'stroke="{self.c["rule"]}" stroke-width="1"/>'
                + self.text(24, self.h - 26, note, size=12.5, colour=self.c["sub"]))

    def render(self) -> str:
        c = self.c
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-label="{escape(self.label)}">'
            f'<defs>'
            f'<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 10 5 0 10z" fill="{c["line"]}"/></marker>'
            f'</defs>' + "".join(self.parts) + "</svg>"
        )


# ── the diagrams ──────────────────────────────────────────────────────────

def architecture(scheme):
    """One long-running container, one Slack channel, two small files."""
    k = Canvas(1180, 470, scheme,
               "The reminder bot runs in one Docker container configured from config/.env. It "
               "reads the service desk channel and posts reminders through the Slack Web API, "
               "keeps a log of reminded threads on the ./data volume, and touches a heartbeat "
               "file that the Docker health check watches.")
    c = k.c
    W, H = 268, 108
    xs, top = [24, 456, 888], 56
    mid = top + H / 2
    low, LH = 272, 96
    lmid = low + LH / 2
    hb_w = 210
    k.add(
        k.box(xs[0], top, W, H, "Environment", ["Slack token, channel and", "HelpDesk bot ID"], icon="sliders"),
        k.box(xs[1], top, W, H, "Reminder bot", ["Checks every 2 hours, reminds", "threads older than 3 hours"],
              icon="chip", tone="accent"),
        k.box(xs[2], top, W, H, "Slack channel", ["Tickets, HelpDesk bot replies", "and our reminders"], icon="chat"),
        k.box(xs[0], low, W, LH, "Docker health check", ["Unhealthy after 30 minutes", "without a heartbeat"],
              icon="heart"),
        k.box(xs[1], low, hb_w, LH, "Heartbeat file", ["Touched every 15 min"], icon="pulse"),
        k.box(xs[2], low, W, LH, "Reminded log", ["On the ./data volume,", "survives restarts"], icon="file"),
        k.edge([(xs[0] + W + 8, mid), (xs[1] - 8, mid)], label="config/.env"),
        k.edge([(xs[1] + W + 8, mid), (xs[2] - 8, mid)], both=True, label="history, replies"),
        k.text((xs[1] + W + xs[2]) / 2, mid + 21, "chat.postMessage", size=11.5, font=MONO,
               colour=c["chip"], anchor="middle"),
        # The heartbeat: written by the bot, read by Docker.
        k.edge([(xs[1] + hb_w / 2, top + H + 8), (xs[1] + hb_w / 2, low - 8)]),
        k.edge([(xs[1] - 8, lmid), (xs[0] + W + 8, lmid)], label="HEARTBEAT_FILE"),
        # The log: read at the start of a check, written at the end.
        k.edge([(xs[1] + W - 34, top + H + 8), (xs[1] + W - 34, lmid), (xs[2] - 8, lmid)], both=True),
        k.text((xs[1] + W - 34 + xs[2]) / 2 + 4, lmid - 9, "reminded_messages.json", size=11.5,
               font=MONO, colour=c["chip"], anchor="middle"),
        k.footer("A thread is reminded once: the log and a check for our own bot's reply "
                 "both stop a second nudge."),
    )
    return k.render()


def reminder_loop(scheme):
    """One check, then the sleep that brings it round again."""
    k = Canvas(1180, 452, scheme,
               "Each check fetches today's channel messages, keeps top-level human messages "
               "older than the age threshold that are not yet logged, and asks whether the "
               "HelpDesk bot or this bot already replied. If not, it posts a reminder in the "
               "thread. Either way the thread is logged, then the bot sleeps until the next check.")
    c = k.c
    y, H = 112, 96
    cy = y + H / 2
    b1 = (24, 190)
    b2 = (254, 210)
    dx, dw, dh = 598, 180, 104
    b4 = (736, 180)
    b5 = (958, 198)
    k.add(
        k.box(b1[0], y, b1[1], H, "Fetch today's", ["channel messages,", "every page"], icon="search"),
        k.box(b2[0], y, b2[1], H, "Filter messages", ["top-level, from a person,", "older than 3 h, not logged"],
              icon="filter"),
        k.diamond(dx, cy, dw, dh, ["HelpDesk bot or", "this bot replied?"]),
        k.box(b4[0], y, b4[1], H, "Post a reminder", ["in the thread,", "mentioning the author"],
              icon="send", tone="accent"),
        k.box(b5[0], y, b5[1], H, "Log the thread", ["saved when the pass ends"], icon="file"),
        k.edge([(b1[0] + b1[1] + 8, cy), (b2[0] - 8, cy)]),
        k.edge([(b2[0] + b2[1] + 8, cy), (dx - dw / 2 - 8, cy)]),
        k.edge([(dx + dw / 2 + 8, cy), (b4[0] - 8, cy)], label="no"),
        k.edge([(b4[0] + b4[1] + 8, cy), (b5[0] - 8, cy)]),
        # Already handled: straight to the log, over the top.
        k.edge([(dx, cy - dh / 2 - 8), (dx, 60), (b5[0] + b5[1] / 2, 60), (b5[0] + b5[1] / 2, y - 8)]),
        k.text(dx + 12, 80, "yes", size=11.5, font=MONO, colour=c["chip"]),
    )
    # The loop home, underneath, through the one state that is most of the bot's life.
    sx, sw, sy, sh = 470, 240, 286, 76
    smid = sy + sh / 2
    k.add(
        k.box(sx, sy, sw, sh, "Sleep 2 hours", ["touching the heartbeat"], icon="moon", tone="soft"),
        k.edge([(b5[0] + b5[1] / 2, y + H + 8), (b5[0] + b5[1] / 2, smid), (sx + sw + 8, smid)]),
        k.edge([(sx - 8, smid), (b1[0] + b1[1] / 2, smid), (b1[0] + b1[1] / 2, y + H + 8)]),
        k.text((b1[0] + b1[1] / 2 + sx) / 2, smid - 9, "CHECK_INTERVAL_HOURS", size=11.5, font=MONO,
               colour=c["chip"], anchor="middle"),
        k.footer("A thread the HelpDesk bot already answered is logged without a reminder, so "
                 "no thread's replies are fetched twice."),
    )
    return k.render()


DIAGRAMS = {
    "architecture": architecture,
    "reminder-loop": reminder_loop,
}


def main() -> None:
    out = ROOT / "docs" / "assets"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in DIAGRAMS.items():
        for scheme in SCHEMES:
            path = out / f"{name}-{scheme}.svg"
            path.write_text(fn(scheme), encoding="utf-8")
    print(f"{len(DIAGRAMS)} diagrams x {len(SCHEMES)} schemes -> docs/assets/")


if __name__ == "__main__":
    main()
