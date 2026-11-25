# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import cadquery as cq
from preview import load, render, cut
from nk_cad import to_mesh
import build
O = os.path.join(HERE, "out")
sh = load(os.path.join(O, "_assembly_shell.stl")); ba = load(os.path.join(O, "focus-timer_base.stl"))
meshes, cols = [cut(sh, (0, 0, 0), (1, 0, 0)), cut(ba, (0, 0, 0), (1, 0, 0))], [(0.62, 0.45, 0.9), (0.55, 0.78, 0.55)]
palette = {"hub_low": (0.35, 0.35, 0.4), "hub_pico": (0.8, 0.3, 0.3), "knob": (0.95, 0.75, 0.2), "led_button": (0.95, 0.75, 0.2),
           "buzzer": (0.95, 0.75, 0.2), "display": (0.3, 0.6, 0.9)}
for n, g in build.W.ghosts().items():
    p = os.path.join(os.environ["TEMP"], "g_%s.stl" % n); to_mesh(g, p)
    m = load(p)
    if m.bounds[0][0] < 0 < m.bounds[1][0]:
        m = cut(m, (0, 0, 0), (1, 0, 0))
        meshes.append(m); cols.append(palette.get(n.rsplit("_", 1)[0] if n not in palette else n, (0.6, 0.6, 0.6)))
render(meshes, os.path.join(O, "preview_section.png"), views=((0, -90),), titles=["section x=0: shell purple, base green, PicoHub grey/red, modules yellow/blue"], colors=cols, size=9)
