# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""Fit coupon: print this first (about 5 minutes) and try the REAL parts before printing a housing.

  Row 1  shaft holes d6.1 ... d6.5      (EC11 knob shaft: pick the hole for the knob cap bore)
  Row 2  M2.5 pilot holes d2.0 ... d2.4 (self-tapping screw: the one that bites without cracking)
(Key openings and the knob plate hole are NOT tested: 16.4 x 16.2 and 7.5 are print-proven in the housing configurator.)
The size of each hole is engraved next to it."""
import cadquery as cq
from nk_cad import box, cyl

T = 3.0
PITCH = 10.0
X0 = 6.0


def label(x, y, txt, size=3.0):
    return (cq.Workplane("XY").workplane(offset=T - 0.5).center(x, y)
            .text(txt, size, 1.0, combine=False, halign="center", valign="center"))


def coupon():
    base = box(0, 5 * PITCH, 0, 28, 0, T)
    rows = (21.5, 8.5)
    for i, d in enumerate((6.1, 6.2, 6.3, 6.4, 6.5)):
        x = X0 + i * PITCH
        base = base.cut(cyl(x, rows[0], -1, T + 1, d)).cut(label(x, rows[0] - 6.7, "%.1f" % d, 2.4))
    for i, d in enumerate((2.0, 2.1, 2.2, 2.3, 2.4)):
        x = X0 + i * PITCH
        base = base.cut(cyl(x, rows[1], 0.6, T + 1, d)).cut(label(x, rows[1] - 6.0, "%.1f" % d, 2.4))   # blind, like the real bosses
    return base
