# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from preview import load, render, overhang_report, box_mesh, cut
from wedge import Wedge
O = os.path.join(HERE, "out")
sh = load(os.path.join(O, "_assembly_shell.stl")); ba = load(os.path.join(O, "focus-timer_base.stl"))
cap = load(os.path.join(O, "focus-timer_knob_cap.stl"))
render([sh, ba], os.path.join(O, "preview_assembly.png"), views=((32, 38), (90, 0), (0, 90)),
       titles=["assembled, from front-right", "face (top view)", "side"], colors=[(0.62, 0.45, 0.9), (0.55, 0.78, 0.55)])
# section through the middle (x = 0), PicoHub + boards as grey boxes
import numpy as np
sec_sh = cut(sh, (0, 0, 0), (1, 0, 0)); sec_ba = cut(ba, (0, 0, 0), (1, 0, 0))
render([sec_sh, sec_ba], os.path.join(O, "preview_section.png"), views=((0, 90),), titles=["section x=0 (shell purple, base green)"],
       colors=[(0.62, 0.45, 0.9), (0.55, 0.78, 0.55)], size=9)
render([ba], os.path.join(O, "preview_base.png"), views=((90, 0), (35, 35)), titles=["base top", "base iso"], colors=[(0.55, 0.78, 0.55)])
render([cap], os.path.join(O, "preview_knob_cap.png"), views=((90, 0), (30, 30)), titles=["knob cap top", "knob cap iso"], colors=[(0.9, 0.6, 0.3)])
for n in ("shell", "base", "knob_cap"):
    m = load(os.path.join(O, "focus-timer_%s.stl" % n))
    print(n, "bounds", m.bounds.round(1).tolist(), "watertight", m.is_watertight, "vol %.0f" % m.volume,
          {k: round(v, 1) for k, v in overhang_report(m).items()})
