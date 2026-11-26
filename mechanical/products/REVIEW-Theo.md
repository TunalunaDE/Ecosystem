<!--
SPDX-FileCopyrightText: 2026 noknok (Christopher Houben)
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Mechanical review: Focus Timer + Quiz Buzzers housings (DEV-280)

Theo, 20 Nov 2026. **Computer checks only. Nothing is printed, so nothing here is proven on the bench.**
Checked against the Ecosystem `mechanical/` standards (3D_printed.md, mechanical_PCB.md, housing-profile.md) and the
`mechanical/housing.json` of buzzer, knob, ledbutton, 1.42-display and picohub MOD-0011 (read 20 Nov 2026).

## 1. Numbers in `lib/nk_cad.py` vs the module data

| Item | housing.json | nk_cad | Verdict |
| --- | --- | --- | --- |
| Buzzer, Knob, LED Button: 20x20, holes (2.25,2.25)+(17.75,17.75), clearance_top 3.0 / 6.0 / 4.5, bottom 3.0 | same | same | match |
| Knob shaft hole d7.5 at (10, 10.25) | same | same | match |
| LED Button key 16.4 x 16.2 at (10,10) | same | same | match |
| Buzzer sound port d8.5 at (10,10) | same | same | match |
| Display 40x30, 4 holes, top 1.0 / bottom 3.0, window 37.5 x 18.4 at (19.8,15) | same | same | match (window centre `verified:false`) |
| PicoHub 80x40, top 18.0, bottom 3.5, J1 USB-C at (68, 2.84) | same | same | match |
| PicoHub mounting holes | **8** (4 corners + 4 at x 37.75 / 42.25) | 4 corners | intended: 4 corners hold an 80 x 40 board; the middle four exist for the mezzanine. Fine, say so in the code |
| Display FPC keep-out (x 36-40, y 6-24, both sides) | listed | not modelled | OK: the window is open there and the 4 bosses stay outside (checked by hand: nearest boss edge 0.85 mm from the band); add it to the ghosts later |
| Pico keep-out 51 x 21 at (1.37, 9.46) | listed | used for the ghost | match |
| Face plate thickness | knob/button/display were tuned with a 1.2 mm plate | `TF` = 1.6 | **deviation**, harmless for fit (clearance_top is measured to the inside of the plate) but the Knob shaft sticks out 0.4 mm less and the Display glass sits 0.5 mm below the outer face instead of 0.12 |
| Buzzer / Knob / Button JST positions (W y=15.5, E y=4.5) | listed | not used by the wedge | **used by the puck: the cable windows ignored them, see 3** |

## 2. Findings in the wedge (shell + base)

| # | Finding | Severity | Action |
| --- | --- | --- | --- |
| W1 | **Rubber feet recesses 1.0 mm deep for 1.0 mm feet: the feet would sit flush, not lift the case.** | real | now 0.5 mm deep (foot stands 0.5 mm proud). Same on the puck base. |
| W2 | **Feet recesses overlapped the countersunk screw-head recesses** (front 0.5 mm, back 2.0 mm): a foot would cover a screw hole. | real | feet moved to (+-34, 12) and (+-30, D-11): now 2.3 / 2.8 mm clear. |
| W3 | USB-C slot 13 x 7 mm: fine for a bare plug, too tight for the usual 12-16 mm overmoulds. The 2 mm wall plus a 7 mm gap to the board edge means the overmould must pass through the slot. | real | now 15 x 9 mm, still 0.5 mm clear of the rear screw boss. |
| W4 | Back-wall vent slots stopped at z = 23 mm. Warm air collects under the slanted face (up to 60 mm), so the slots were at the cold end. DEV-146 (hub heat) is open and nothing was measured. | likely | slots now run z 9-45 mm (still 11 mm below the face underside). Open: measure, see 4. |
| W5 | Height envelope: Pico 2 W top (incl. the 18 mm margin) is at z 26.1; the plate underside at the Pico's front edge is at z 35.2, under the Display 28.7. Margin 9 mm / 2.6 mm. | OK | Display margin is thin but covers the real Display + JST at 3.0 mm bottom. Nothing to do; keep `clearance_top` of the Hub at 18. |
| W6 | Display bosses are 1.0 mm below the plate + 0.4 mm into it. With M2.5 x 3 the screw bites **1.4 mm** (about 3 threads) in PLA; geometry allows at most 1.8 mm (0.8 mm skin is kept). | acceptable, weak | Fine for a 5 g board that is never moved. Strips after 2-3 re-assemblies. Fallback: a drop of cyanoacrylate, or `TF` 2.0 + M2.5 x 4 screws (engagement 2.4 mm). Test on the first print before changing. |
| W7 | Display window clearance to the glass is 0.49 mm per side in X but only **0.16 mm in Y**, and the glass offset (19.8, 15) is unmeasured. | risk | Open. Needs calipers on a real Display; if the glass is off by 0.2 mm the window clips it. Fallback: widen the window height to 19.0. |
| W8 | Wall 2.0 mm (standard asks 1.2 mm), standoff wall 1.8 mm, boss-to-boss gap hub standoff / shell boss 0.2 mm (different parts, fine). | OK | none |
| W9 | Print: only walls at 30 degrees, no support. Overhang report (`lib/check_print.py`): shell patches are the text engravings (0.5 mm), the USB slot ceiling (15 x 1.7 mm) and the vent slot ceilings (2 x 1.7 mm). All are short bridges. Base: the feet recesses are 10.4 mm bridges, now 0.5 mm high (2 layers), expect slightly rough undersides. | OK | watch the first print |
| W10 | Pico micro-USB and the Hub host port J2 have **no opening**. The Focus Timer / Quiz console must be opened (4 screws) to reach them. That matches the module notes ("deliberately not given an opening") but costs convenience when developing. | open | Christopher's call: add a closable 9 x 5 mm cover if developers need it. |
| W11 | 3D_printed.md wants tool-free assembly. These housings use 8 M2.5 screws. Deviation is stated in the README; keep. | note | none |

## 3. Findings in the pucks

| # | Finding | Severity | Action |
| --- | --- | --- | --- |
| P1 | **Cable windows were in the wrong place.** The JST sockets sit at puck y = +5.5 (W) and -5.5 (E) (housing.json: W y 15.5, E y 4.5, PCB centred). The windows were centred on y = 0 and 9 mm wide (y -4.5..+4.5), so half of the plug (about 2.5 to 8.5) hit the wall. They also left a 0.4-0.7 mm membrane of curved wall at the window edges. | real | windows now centred on the sockets (W +5.5, E -5.5; 180 degree symmetric so the puck works either way round) and cut well into the cavity. New build check: a 7 x 3.4 mm plug + cable on each socket collides 0.00 / 0.05 mm3 with the body. |
| P2 | Feet 0.5 mm deep (see W1). No overlap with screw heads (22.6 mm apart). | fixed | -- |
| P3 | The deck is 2 mm, the PCB is held at two diagonal corners; slap loads go through the switch, PCB and the standoffs to the base, not through the deck. | OK | check by hand on the first print (hit it hard 20 times) |
| P4 | Key opening 16.4 x 16.2, deck inner face 4.5 above the PCB: copied from the print-tuned LED Button profile. | OK | coupon row 3 confirms |

## 4. Heat (DEV-146, not solved here)

Inlet: 6 base slots (240 mm2). Outlet: 6 back slots (now 2 x 33 mm each, 400 mm2) plus whatever the USB slot leaves. This is a guess at convection, not a measurement. Acceptance test (Bob / bench): Pico 2 W + hub running the Focus Timer for 1 h in a 22 C room, thermocouple or IR gun on the buck inductor and the inside of the shell back wall; PLA softens at about 55 C. If it fails: bigger slots first, then PETG.

## 5. The knob cap (rebuilt on paper, 20 Nov; not printed)

Alps EC11E datasheet (Christopher): body 4.5, bushing d7 to 11.5, shaft d6 to 24.5 above the PCB, flat (4.5 across) on the last 10 mm. The old cap had a flat bottom and a round bore, so it would have rested on the bushing (3.9 mm proud of the face), left a gap, and slipped on the flat. It also touched the LED Button key (D30: -1.2 mm). New cap: d25, counterbore for the bushing, round bore d6.2 (coupon), D bore 6.2 x 4.7, 0.6 mm above the face, height 18.8. Gap to the key 1.3 mm (computed in `build.py`). Datasheet heights assume the encoder sits flat on the PCB.

## 6. What changed (all rebuilt, checks re-run)

- `lib/wedge.py`: USB-C slot 15 x 9, vent slots z 9-45, feet 0.5 deep at new positions.
- `quiz-buzzers/build.py`: puck cable windows centred on the sockets, feet 0.5 deep, plug collision check added.
- `lib/check_print.py` (new): watertight + overhang report for every STL (`python lib/check_print.py`).
- Rebuilt STEP / STL / previews. Results: all parts valid single solids, watertight; ghost collision check: none; puck plug check: 0.00 / 0.05 mm3.

## 7. Still open (needs a print or a measurement)

Tolerances (pilot, key opening, shaft bore), knob cap bushing / shaft heights, Display glass offset, screw bite of the Display bosses, heat, the real USB-C plug through the slot, JST cable bend in the 3 mm gap, PLA creep of the d30 cap on a press fit.

## 8. Decisions for Christopher / Tom (proposals)

1. **Where the housings live.** Recommendation: a new `Ecosystem/mechanical/products/` folder with scripts + STL only (about 2 MB), STEP files attached to GitHub releases (about 20 MB of the 25 MB). Keeps the repo light; STEP is only needed by Fusion users.
2. **Manifest `3d_files`.** Recommendation: list of `{part, file, qty, orientation, notes}` per product, pointing at the STL in the repo; the app shows the print list. Needs Sue to agree on the schema.
3. **Generator vs configurator vs Fusion.** The Housing Configurator (JSCAD) makes boxes for flat module grids. The wedge (tilted face, cap, pucks) is quicker as CadQuery. Recommendation: keep CadQuery as the product-housing generator, export STEP for Fusion; do not port to JSCAD now.
4. **Reuse for Metronome, Stopwatch, Dice Roller, Morse Tapper.** Yes: the `Wedge` class takes a layout list (module, x, y); the hub, base, bosses, slots are shared. New product = about 10 lines. Morse Tapper needs a bigger key opening (new coupon row).

## 9. Update (20 Nov, after Christopher's input)

- Openings (knob plate hole 7.5, key 16.4 x 16.2, display window 37.5 x 18.4) already equal the housing configurator's print-proven values: no change.
- PCB mounting holes checked in the KiCad files of buzzer, knob, ledbutton, display and PicoHub MOD-0011: **all use the noknok M2.5 footprint, drill 2.5 mm** (display 4x, PicoHub 12x incl. 4 under the Pico). The `notes` in the buzzer and knob `housing.json` still say "M2 / 2.2 mm holes": stale, worth a fix in those repos.
- One screw, one pilot size for every boss in the housings (`M25_PILOT`). The fit coupon is cut down to two rows (knob cap bore 6.1-6.5, pilot 2.0-2.4), 50 x 28 x 3 mm, about 5 minutes.

## 10. Coupon result (Christopher, 20 Nov 2026)

- Shaft bore: 6.1 too tight, **6.2 fits**, 6.3 too loose. The shaft is round with a D-flat (cap rebuilt accordingly).
- M2.5 pilot, steel screw: only **2.4** takes it and it holds (2.0-2.3 do not). `M25_PILOT` = 2.4 everywhere; all parts rebuilt, collision checks none. Next print candidates: the Focus Timer base/shell with the knob cap (watch the cap bore and the 0.6 mm gap).

## 11. Screw harmonisation (Christopher, 20 Nov 2026)

Two screw lengths for the whole product line: **M2.5 x 6** (Knob, LED Button, Buzzer, PicoHub, base-to-shell, puck) and **M2.5 x 4** (Display only). Before: 3, 5, 6 and 8 mm. One length is not possible: the Display boss sits at most 3.0 mm under the outer face (glass flush with the window), which allows a 4 mm screw at the very most. To make that work the face plate went from 1.6 to **2.0 mm** and the pilot stops 0.6 mm under the outer face (was 0.8). Bite: Display 2.4 mm (was 1.4), Buzzer 4.4 mm, base screws 4.6 mm (countersink included). Side effects: key and shaft stand about 0.4 mm less proud than with a 1.6 mm plate (about 0.8 less than the 1.2 mm configurator prints); the Display glass sits 0.9 mm below the outer face. The knob cap is generated from the plate thickness; the cap being test-printed is from the 1.6 mm version and is still valid for the bore and gap test (the final cap is 0.4 mm shorter). All parts rebuilt, collision checks none. 0.6 mm of skin over a screw tip is only 3 layers: check on the first shell that no screw tip shows or bulges the face.

## 12. Walls 1.6 mm (Christopher, 20 Nov 2026)

Shell and puck walls 2.0 / 2.4 -> **1.6 mm** (4 perimeters); face plate stays 2.0 mm. Shell volume 39.2 -> 34.8 cm3 (-11 %), puck body 11.9 -> 10.1 cm3 (-15 %). Base screw posts keep their 0.2 mm overlap with the wall and move with it; the rear posts now clear the hub standoffs by 0.6 mm (was 0.2). Rebuilt: all parts valid, watertight, ghost collisions none, puck plug check 0.00 / 0.00 mm3. Not proven: stiffness of the 60 mm tall back wall in 1.6 mm PLA (press on it after printing; if it flexes, go back to 2.0 on the back wall only).

## 13. Knob cap printed (Christopher, 24 Nov 2026)

D25 cap printed: **fits the Knob perfectly** (bores 6.2 / D-flat / counterbore / gap proven). Too big, so the outer diameter is now **13 mm** (-48 %), 12 flutes, same bores and height 18.4. Wall around the counterbore about 1.8 mm. The D13 cap is not printed yet; gap to the LED key is 7 mm.

## 14. D13 cap printed (Christopher, 25 Nov 2026)

D13 knob cap printed: fits perfectly. Cap design is closed (bore 6.2, D-flat, counterbore, gap 0.6, D13 x 18.4). Next prints: Focus Timer base, puck body, puck base.
