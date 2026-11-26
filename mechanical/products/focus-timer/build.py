# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""Focus Timer housing: a desk wedge (30 degree face) for PicoHub + Knob + LED Button + Buzzer + Display.

    python focus-timer/build.py            # writes focus-timer/out/*.step, *.stl and previews

Needs: pip install cadquery trimesh numpy matplotlib   (tested with cadquery 2.8, Python 3.12)
Parts: shell (print face down), base (print flat), knob_cap (print upright).
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import cadquery as cq
from wedge import Wedge
from nk_cad import cyl, box, to_desk, to_mesh, volume, MODULES

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

ROW = 6.0                       # front margin: modules start 6 mm behind the front edge of the face
LAYOUT = [("knob", -32, ROW), ("led_button", -10, ROW), ("buzzer", 12, ROW), ("display", -20, ROW + 24)]
W = Wedge(LAYOUT, D=69.0, hub_y0=20.0)


def engrave(w, text, x, y, size, depth=0.5):
    """Cut text into the outer face; local face frame (x right, y up the slope), reads from outside."""
    t = (cq.Workplane("XY").workplane(offset=-depth).center(x, y)
         .text(text, size, depth + 0.5, halign="center", valign="center", combine=False))
    return to_desk(t, W.TH, W.HF)


def build_shell():
    sh = W.shell()
    labels = [("time", -22, 2.6), ("start", 0, 2.6), ("beep", 22, 2.6)]
    for (t, x, y) in labels:
        sh = sh.cut(engrave(sh, t, x, y, 3.2))
    sh = sh.cut(engrave(sh, "focus timer", 0, 66.0, 5.0))
    sh = sh.cut(engrave(sh, "noknok", 0, 72.2, 3.4))
    return sh


# Alps EC11E vertical encoder (datasheet, 20 Nov 2026), heights above the PCB top: body 4.5, bushing d7 up to 11.5,
# shaft d6 to 24.5, the last 10 mm of the shaft have a flat (4.5 mm across flat to opposite side).
ENC = dict(bushing_top=11.5, flat_start=14.5, shaft_end=24.5, bushing_d=7.0, shaft_d=6.0, flat_w=4.5)
BORE = 6.2                      # fit coupon: 6.1 too tight, 6.2 fits, 6.3 loose (printed hole, round part of the shaft)


def knob_cap(D=13.0, bore=BORE, gap=0.6, flutes=12):
    """Printable cap for the EC11 D-shaft. From the bottom up: counterbore over the bushing, round bore over the
    round part of the shaft, D-shaped bore (same 0.2 mm allowance as the round fit) over the flat part, closed roof.
    The cap floats `gap` above the face. D 13 (the printed D 25 fitted perfectly but was too big, Christopher 24 Nov); the old D 30 touched the LED key."""
    face_top = MODULES["knob"]["ct"] + W.TF                       # outer face height above the knob PCB (7.6)
    cb = ENC["bushing_top"] - face_top - gap + 0.5                # counterbore depth (bushing sticks out 3.9, 0.5 clearance)
    round_end = ENC["flat_start"] - face_top - gap                # round bore up to where the flat starts
    top = ENC["shaft_end"] - face_top - gap + 0.5                 # D bore up to here (0.5 above the shaft end)
    H = top + 2.0
    body = cyl(0, 0, 0, H, D).faces(">Z").edges().fillet(1.6)
    for i in range(flutes):                                       # grip scallops
        a = 2 * math.pi * i / flutes
        body = body.cut(cyl((D / 2 + 0.3) * math.cos(a), (D / 2 + 0.3) * math.sin(a), -0.1, H + 0.1, 2.4))
    body = body.cut(cyl(0, 0, -0.1, cb, ENC["bushing_d"] + 0.6))
    body = body.cut(cyl(0, 0, cb - 0.01, round_end, bore))
    flat_y = bore / 2 - (ENC["flat_w"] + (bore - ENC["shaft_d"]))  # flat position: same 0.2 allowance as the round part
    dbore = cyl(0, 0, round_end - 0.01, top, bore).intersect(box(-bore, bore, flat_y, bore, round_end - 1, top + 1))
    body = body.cut(dbore)
    body = body.cut(box(1.0, D / 2 + 1, -0.7, 0.7, H - 0.6, H + 0.1))   # pointer groove, rim to the middle
    return body


def cap_vs_key_gap(cap_d):
    """Distance in the face plane between the knob cap circle and the LED Button key opening (negative = collision)."""
    kx, ky = LAYOUT[0][1] + MODULES["knob"]["feature"][1], LAYOUT[0][2] + MODULES["knob"]["feature"][2]
    bx, by = LAYOUT[1][1] + 10.0, LAYOUT[1][2] + 10.0
    dx = max(abs(kx - bx) - 16.4 / 2, 0); dy = max(abs(ky - by) - 16.2 / 2, 0)
    return math.hypot(dx, dy) - cap_d / 2


def main():
    shell, base, cap = build_shell(), W.base(), knob_cap()
    # collision check against the ghost boards
    g = W.ghosts()
    bad = []
    for n, gh in g.items():
        for pn, p in (("shell", shell), ("base", base)):
            v = volume(p.intersect(gh))
            if v > 1.0:
                bad.append((n, pn, v))
    print("collisions >1 mm3:", bad if bad else "none")
    print("knob cap to LED key opening: %.1f mm gap, cap height %.1f mm" % (cap_vs_key_gap(13.0), cap.val().BoundingBox().zlen))
    for name, part in (("shell", shell), ("base", base), ("knob_cap", cap)):
        print("%-9s valid=%s solids=%d volume=%.0f mm3" % (name, part.val().isValid(), len(part.solids().vals()), volume(part)))
        cq.exporters.export(part, os.path.join(OUT, "focus-timer_%s.step" % name))
    # STL in PRINT pose
    shell_print = shell.rotate((0, 0, 0), (1, 0, 0), -W.TH).translate((0, 0, 0))     # face normal -> +Z
    shell_print = shell_print.rotate((0, 0, 0), (0, 1, 0), 180)                       # face down on the bed
    bb = shell_print.val().BoundingBox()
    shell_print = shell_print.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    to_mesh(shell_print, os.path.join(OUT, "focus-timer_shell.stl"))
    to_mesh(base, os.path.join(OUT, "focus-timer_base.stl"))
    to_mesh(cap, os.path.join(OUT, "focus-timer_knob_cap.stl"))
    # assembly (desk pose) for the picture
    to_mesh(shell, os.path.join(OUT, "_assembly_shell.stl"))
    return shell, base, cap


if __name__ == "__main__":
    main()
