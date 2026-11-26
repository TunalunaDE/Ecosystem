# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import trimesh
from preview import load, render, overhang_report, box_mesh, cut
import build as B
O = os.path.join(HERE, "out")
con = load(os.path.join(O, "_assembly_console_shell.stl")); cb = load(os.path.join(O, "quiz-buzzers_console_base.stl"))
pb = load(os.path.join(O, "_assembly_puck_body.stl")); pba = load(os.path.join(O, "quiz-buzzers_puck_base.stl"))
render([con, cb], os.path.join(O, "preview_console.png"), views=((32, 38), (90, 0), (30, 160)),
       titles=["console, front-right", "console face", "console back (Qwiic cable exits, vents, USB-C power)"],
       colors=[(0.62, 0.45, 0.9), (0.55, 0.78, 0.55)])
# puck: assembled exterior + section with PCB (yellow) and switch (red) ghosts
pcb = box_mesh(-10, 10, -10, 10, B.BP + B.KEY["cb"], B.PCB_TOP)
sw = box_mesh(-7.95, 7.95, -7.85, 7.85, B.PCB_TOP, B.PCB_TOP + 11.6)
parts = [cut(pb, (0, 0, 0), (1, 0, 0)), cut(pba, (0, 0, 0), (1, 0, 0)), cut(pcb, (0, 0, 0), (1, 0, 0)), cut(sw, (0, 0, 0), (1, 0, 0))]
cols = [(0.62, 0.45, 0.9), (0.55, 0.78, 0.55), (0.95, 0.75, 0.2), (0.85, 0.3, 0.3)]
render(parts, os.path.join(O, "preview_puck_section.png"), views=((0, -90),), titles=["puck section x=0: body purple, base green, PCB yellow, key switch red"], colors=cols, size=8)
render([pb, pba], os.path.join(O, "preview_puck.png"), views=((35, 35), (90, 0)), titles=["puck (body + base)", "puck top"], colors=[(0.62, 0.45, 0.9), (0.55, 0.78, 0.55)])
for n in ("console_shell", "console_base", "puck_body_1", "puck_base"):
    m = load(os.path.join(O, "quiz-buzzers_%s.stl" % n))
    print(n, "bounds", m.bounds.round(1).tolist(), "watertight", m.is_watertight, "vol %.0f" % m.volume, {k: round(v, 1) for k, v in overhang_report(m).items()})
m = load(os.path.join(O, "noknok_fit_coupon.stl")); print("coupon", m.bounds.round(1).tolist(), m.is_watertight)
