# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""Quiz Buzzers housings: one console (desk wedge: PicoHub + Display + Buzzer) and four team pucks
(one LED Button each). Print the pucks in four colours.

    python quiz-buzzers/build.py       # writes quiz-buzzers/out/*.step, *.stl

Console = the same Wedge generator as the Focus Timer, with a different face layout and a Qwiic cable
exit in the back wall. Puck = body (tube + deck with the key opening) + base (PCB standoffs, 3 screws).
The pucks are chained with Qwiic cables: console -> puck 1 -> puck 2 -> puck 3 -> puck 4.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import cadquery as cq
from wedge import Wedge
from nk_cad import cyl, box, to_desk, to_mesh, volume, MODULES, PCB_T, M25_PILOT, M25_CLEAR, M25_HEAD
from coupon import coupon

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---------------- console -------------------------------------------------------------------
ROW = 6.0
LAYOUT = [("buzzer", -10, ROW), ("display", -20, ROW + 24)]
# the S-edge Qwiic ports J5 (10.0, 3.2) and J6 (20.6, 3.2) of the PicoHub face the back wall
W = Wedge(LAYOUT, D=69.0, hub_y0=20.0, vent_x=(-14, -6, 2, 10), jst_ports=((10.0, 3.2), (20.6, 3.2)))


def engrave(text, x, y, size, depth=0.5):
    t = (cq.Workplane("XY").workplane(offset=-depth).center(x, y)
         .text(text, size, depth + 0.5, halign="center", valign="center", combine=False))
    return to_desk(t, W.TH, W.HF)


def console_shell():
    sh = W.shell()
    sh = sh.cut(engrave("sound", -0, 2.6, 3.2))
    sh = sh.cut(engrave("quiz buzzers", 0, 66.0, 5.0))
    sh = sh.cut(engrave("noknok", 0, 72.2, 3.4))
    return sh


# ---------------- puck ----------------------------------------------------------------------
R, WALL, BP = 32.0, 1.6, 3.0
KEY = MODULES["led_button"]
PCB_TOP = BP + KEY["cb"] + PCB_T                       # 7.6
DECK_IN = PCB_TOP + KEY["ct"]                          # inner face of the deck (clearance_top 4.5) = 12.1
DECK_T = 2.0
H = DECK_IN + DECK_T                                    # 14.1
BOSS_R = 24.0
BOSS_ANG = (90, 210, 330)


def puck_body(number):
    body = cyl(0, 0, 0, H, 2 * R)
    body = body.faces(">Z").edges().chamfer(1.2)
    body = body.faces("<Z").edges().chamfer(0.6)
    body = body.cut(cyl(0, 0, -1, DECK_IN, 2 * (R - WALL)))                    # cavity, open at the bottom
    kx, ky, kw, kh = KEY["feature"][1], KEY["feature"][2], KEY["feature"][3], KEY["feature"][4]
    ox, oy = -10.0, -10.0                                                       # PCB centred on the puck
    body = body.cut(box(ox + kx - kw / 2, ox + kx + kw / 2, oy + ky - kh / 2, oy + ky + kh / 2, DECK_IN - 1, H + 1))
    for a in BOSS_ANG:                                                          # screw bosses for the base
        x, y = BOSS_R * math.cos(math.radians(a)), BOSS_R * math.sin(math.radians(a))
        boss = cyl(x, y, BP, DECK_IN + 0.4, 6.4).cut(cyl(x, y, BP - 0.1, BP + 9.0, M25_PILOT))
        body = body.union(boss)
    # Qwiic cable windows: the JST sockets sit at payload (3.1, 15.5) W and (16.9, 4.5) E -> puck y = +5.5 (W) and -5.5 (E).
    # 9 mm wide, centred on the socket; cut well into the cavity so no sliver of the curved wall is left at the window edges.
    for sx, yc in ((-1, 5.5), (1, -5.5)):
        x0, x1 = (-(R + 1), -(R - WALL - 4)) if sx < 0 else ((R - WALL - 4), R + 1)
        body = body.cut(box(x0, x1, yc - 4.5, yc + 4.5, BP, BP + 5.5))
    body = body.cut(cq.Workplane("XY").workplane(offset=H - 0.5).center(0, -22).text(str(number), 9.0, 1.0, combine=False,
                                                                                  halign="center", valign="center"))
    return body


def puck_base():
    c = 0.25
    b = cyl(0, 0, 0, BP, 2 * (R - WALL - c))
    for a in BOSS_ANG:
        x, y = BOSS_R * math.cos(math.radians(a)), BOSS_R * math.sin(math.radians(a))
        b = b.cut(cyl(x, y, -1, BP + 1, M25_CLEAR))
        b = b.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y).circle(M25_HEAD / 2)
                  .workplane(offset=1.62).circle(M25_CLEAR / 2).loft())
    ox, oy = -10.0, -10.0
    for (hx, hy) in KEY["holes"]:                                               # PCB standoffs, blind pilot holes
        x, y = ox + hx, oy + hy
        st = cyl(x, y, BP - 0.1, BP + KEY["cb"], 5.8).cut(cyl(x, y, BP - 1.8, BP + KEY["cb"] + 0.1, M25_PILOT))
        b = b.union(st)
    for a in (30, 150, 270):                                                    # feet recesses
        x, y = 21 * math.cos(math.radians(a)), 21 * math.sin(math.radians(a))
        b = b.cut(cyl(x, y, -0.1, 0.5, 10.4))      # 0.5 deep: a 1 mm foot stands 0.5 mm proud
    return b


def main():
    parts = {}
    sh, ba = console_shell(), W.base()
    g = W.ghosts()
    bad = [(n, pn, volume(p.intersect(gh))) for n, gh in g.items() for pn, p in (("shell", sh), ("base", ba)) if volume(p.intersect(gh)) > 1.0]
    print("console collisions >1 mm3:", bad if bad else "none")
    parts["console_shell"], parts["console_base"] = sh, ba
    parts["puck_body_1"], parts["puck_base"] = puck_body(1), puck_base()
    for n in (2, 3, 4):
        parts["puck_body_%d" % n] = puck_body(n)
    parts["fit_coupon"] = coupon()
    # cable check: a JST-SH plug (7 wide, 3.4 high) plus 12 mm of cable sticking straight out of each socket must not touch the body
    for sx, yc in ((-1, 5.5), (1, -5.5)):
        x0, x1 = (-(R + 12), -(R - WALL - 8)) if sx < 0 else ((R - WALL - 8), R + 12)
        plug = box(x0, x1, yc - 3.5, yc + 3.5, BP + 0.3, BP + 3.7)
        v = volume(parts["puck_body_1"].intersect(plug))
        print("puck cable plug %s: collision %.2f mm3" % ("W" if sx < 0 else "E", v))
    for name, part in parts.items():
        print("%-14s valid=%s solids=%d volume=%.0f mm3" % (name, part.val().isValid(), len(part.solids().vals()), volume(part)))
        cq.exporters.export(part, os.path.join(OUT, "quiz-buzzers_%s.step" % name))
    # puck body prints upside down (deck on the bed); console shell face down like the focus timer
    for n in (1, 2, 3, 4):
        pb = parts["puck_body_%d" % n].rotate((0, 0, 0), (1, 0, 0), 180)
        bb = pb.val().BoundingBox()
        to_mesh(pb.translate((0, 0, -bb.zmin)), os.path.join(OUT, "quiz-buzzers_puck_body_%d.stl" % n))
    to_mesh(parts["puck_base"], os.path.join(OUT, "quiz-buzzers_puck_base.stl"))
    shp = sh.rotate((0, 0, 0), (1, 0, 0), -W.TH).rotate((0, 0, 0), (0, 1, 0), 180)
    bb = shp.val().BoundingBox()
    to_mesh(shp.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin)), os.path.join(OUT, "quiz-buzzers_console_shell.stl"))
    to_mesh(ba, os.path.join(OUT, "quiz-buzzers_console_base.stl"))
    to_mesh(parts["fit_coupon"], os.path.join(OUT, "noknok_fit_coupon.stl"))
    to_mesh(sh, os.path.join(OUT, "_assembly_console_shell.stl"))
    to_mesh(parts["puck_body_1"], os.path.join(OUT, "_assembly_puck_body.stl"))
    return parts


if __name__ == "__main__":
    main()
