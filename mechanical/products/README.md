<!--
SPDX-FileCopyrightText: 2026 noknok (Christopher Houben)
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# noknok product housings

Printable housings for finished noknok products, generated with CadQuery (Python). Scripts are the CAD source: they are
parametric (wedge angle, face layout, wall, base plate, bosses are arguments). Print-ready **STL** files are in the repo
(`*/out/`); **STEP** files for Fusion 360 / other CAD are attached to the GitHub release
[`products-housings-2026-11`](https://github.com/buildwithnoknok/Ecosystem/releases/tag/products-housings-2026-11) (not committed: about 11 MB).
Made first by the exploration account (20 Nov 2026), reviewed and merged by Theo (DEV-280).

| Product | Housing | Parts to print |
| --- | --- | --- |
| Focus Timer (poc `focus-timer-v1`) | desk wedge, 30 degree face: PicoHub flat inside, Display, Knob, LED Button, Buzzer on the face | [focus-timer/](focus-timer/README.md): shell, base, knob cap |
| Quiz Buzzers (poc `quiz-buzzers-v1`) | one console (same wedge: Display + Buzzer) and four team pucks (one LED Button each) | [quiz-buzzers/](quiz-buzzers/README.md): console shell + base, 4 puck bodies, puck base x4 |

The same wedge generator (`lib/wedge.py`) serves every product with a Display and a row of controls (Metronome, Stopwatch,
Dice Roller, Morse Tapper): a new face layout is about 10 lines (`Wedge` class), not a new design.

## Status: what is print-proven and what is NOT (read this first)

| Part | Status |
| --- | --- |
| **Knob cap** (D13 x 18.4, bore 6.2, D-flat, counterbore, 0.6 mm gap) | **PRINTED and fits the Knob perfectly** (Christopher, 25 Nov 2026). Design closed. |
| **Fit coupon** (`quiz-buzzers/out/noknok_fit_coupon.stl`) | **PRINTED 20 Nov 2026.** Result: shaft bore 6.2 fits (6.1 too tight, 6.3 too loose); M2.5 steel self-tapping pilot **2.4** is the only size that holds (2.0-2.3 do not). `M25_PILOT = 2.4` everywhere. |
| Focus Timer **shell** (wedge) and **base** | **NOT printed.** Geometry checked by computer only (valid solid, watertight, no ghost-board collisions, overhangs). |
| Quiz **console** shell + base | **NOT printed** (same generator as the Focus Timer). |
| Quiz **pucks** (body x4, base) | **NOT printed.** Cable windows were re-centred on the JST sockets after review; checked by a plug collision test, not on a real cable. |
| Heat (DEV-146) | **NOT measured.** The vents are a guess at convection; PLA softens at about 55 C. |
| USB-C power plug through the back slot (15 x 9 mm) | **NOT tried** with a real cable / overmould. |
| Display glass offset (window 37.5 x 18.4 at 19.8, 15) | **NOT measured** (`verified: false` in the Display `housing.json`); only 0.16 mm clearance in Y. |
| Display boss screw bite (M2.5 x 4, 2.4 mm engagement), 0.6 mm skin over screw tips | **NOT tested** on a print. |
| Stiffness of the 60 mm back wall at 1.6 mm | **NOT tested** (fallback: 2.0 mm on the back wall only). |
| Qwiic cable bend in the 3 mm gap; PicoHub/Pico micro-USB access | **NOT checked** (no opening; the case must be opened to reach them). |
| Puck: deck slap loads (hit it 20 times), key opening 16.4 x 16.2 | **NOT tested** (key opening equals the print-proven configurator value). |

Do not describe any housing as "fit-tested" except the knob cap and the coupon.

### Next prints (for Christopher, in this order)

1. **Focus Timer base** (about 1 h). Check: PicoHub sits on the 4 standoffs, rubber feet recesses, countersinks take M2.5 x 6.
2. **Puck body + puck base**, one set (small, fast). Check: LED Button fits (key through 16.4 x 16.2), both cable windows line up with the JST sockets, 3 base screws bite, feet.
3. **Focus Timer shell** (largest, 92 x 89 x 52 mm, face down, no supports): all modules, Display window against a real Display, screw tips not showing on the face, back wall stiffness, USB-C slot with the real power plug.
4. Then **console shell + base** (same wedge, quick check only), and finally four more pucks.
5. Heat: Focus Timer running 1 h with Pico 2 W + hub at 22 C, thermometer on the hub buck inductor and the inside of the back wall (DEV-146).
6. Record each result in a new section of the Ecosystem changelog / `focus-timer/README.md` and fix the numbers in `lib/nk_cad.py` / `focus-timer/build.py` where a print disagrees.

Optional later: Metronome, Stopwatch, Dice Roller, Morse Tapper (new face layout list; Morse Tapper needs a bigger key opening, so a new coupon row).

## Printing (Bambu Lab X1 Carbon)

- PLA, 0.4 mm nozzle, 0.2 mm layers (ecosystem standard, [3D_printed.md](../3D_printed.md)). 4 to 5 wall loops (shell walls are 1.6 mm), infill 15 %. **No supports** when printed in the pose of the STL.
- STL files are already in PRINT POSE: shell face down (every wall leans 30 degrees, never more than 47 degrees from vertical), puck body deck down, bases and cap as they are. Import and print; do not rotate.
- Small bridges to expect: USB-C slot in the back wall (15 mm), feet recesses under the bases (10.4 mm circle, 0.5 mm up), puck cable windows. All short; watch the first print.

## Fasteners and parts (per Focus Timer; the Quiz console is the same without Knob / LED Button)

| What | Count | Note |
| --- | --- | --- |
| **M2.5 x 6 mm** self-tapping (steel; nylon not tested) | 2 Knob, 2 LED Button, 2 Buzzer, 4 PicoHub, 4 base | into printed pilot holes (d2.4); base screws sit in a countersink from below |
| **M2.5 x 4 mm** self-tapping | 4 Display | the only other length: the Display boss is shallow |
| rubber feet d10 x 1 mm, self-adhesive | 4 | 0.5 mm deep recesses (feet stand 0.5 mm proud) |
| Qwiic / JST-SH 4-pin cables | 4 (chain) | 100 mm; JST sockets are on the BOTTOM side of every module |

Quiz pucks: per puck 2x M2.5 x 6 (PCB), 3x M2.5 x 6 (base), 3 feet, 1 cable.

Deviation from `3D_printed.md` (tool-free assembly): these housings need a small screwdriver. Deliberate: a re-openable, repairable product fits noknok better than a snap case that breaks on the third opening.

## Rebuild / change

```
pip install cadquery trimesh numpy matplotlib networkx scipy rtree mapbox_earcut shapely   # Python 3.12
python focus-timer/build.py      # parts + STEP + STL in focus-timer/out
python quiz-buzzers/build.py     # console, 4 pucks, fit coupon
python lib/check_print.py        # watertight + overhang report for every STL
```

`*.step` is git-ignored here; rebuilding creates it locally. Module dimensions come from each module's `mechanical/housing.json`
(read 20 Nov 2026); if a module changes, rebuild. The full mechanical review (what was checked and what changed) is kept in
[REVIEW-Theo.md](REVIEW-Theo.md).

## Licence

Scripts: MIT. STL, STEP, previews and documents: CC BY-SA 4.0. See the [licence overview](../../README.md).
