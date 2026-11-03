# Pilot in silico sensitivity study: muscle loading and SCR (not for publication)

Purpose: test the workflow and see which inputs matter, using the length demand curves of the shoulder app as input. This is a deliberately simple, literature-calibrated model, not a musculoskeletal simulation and not a prediction for a patient.

## Model
Excess superior translation of the humeral head relative to the intact shoulder:
`du(theta) = [ Fc0*(1 - fc) - Fg(theta) + (Fd - 40) * sd(theta) ] / K`
- `K = 40 N / 0.9 mm = 44 N/mm`: deltoid 40 -> 80 N raised the head by 0.9 mm in torn shoulders (Singh 2019).
- `Fc0 = 3.4 mm * K = 151 N`: effective shear equivalent of the supraspinatus tear; the tear raised translation from 3.0 to 6.4 mm (Mihata 2012).
- `fc` in [-0.5, 0.5]: residual cuff compensation (>0) or further cuff deficit (<0) relative to the torn state.
- `Fd` in [20, 120] N: deltoid load; `sd(theta) = max(0.15, cos theta)`: share of deltoid force that shears the head upward.
- `Fg(theta) = max(0, T0 + k * (L(theta) - L(fix)))`: graft force, a tension-only spring driven by the graft path length from the app (`curves.json`); `T0` in [0, 40] N initial tension.
- `k`: fascia lata calibrated to restore the intact level at 0 degrees when fixed at 10 degrees (Mihata 2017); dermal allograft to restore half; LHBT techniques have no measurement, uniform prior 10-40 N/mm.

## Findings of the pilot
1. At 30 degrees the excess translation is driven mostly by cuff function (standardised coefficient about -0.86) and deltoid load (+0.49); graft stiffness and initial tension matter little (|coefficient| <= 0.23). Partly by construction of the calibration.
2. The graft only acts below its fixation angle in this model (tension-only spring on an inextensible path), so at 60 degrees no technique changes the translation. Cadaver data report restoration at 60 degrees (Mihata 2017), so the model is missing a mechanism (graft stretch, bridging or interposition by thickness, capsule coupling).
3. Peak graft forces are unrealistic (about 150 to 1400 N) because the model's length change is steeper than the cadaver value (slope -0.39 vs -0.25 mm/deg) and the spring is linear. A constitutive law for the graft is needed.
4. Fixation at larger angles makes the graft hold the head below the intact position at 0 degrees (negative values): a possible over-tension signal whose size is not reliable.

## Needed before a real study
Graft stiffness and laxity measured or taken from papers, a model that includes graft thickness and capsule, calibration against Mihata 2016/2017, Singh 2019, Croom 2019 and the group's own cadaver data, and a musculoskeletal model (for example OpenSim) with the app geometry exported.
