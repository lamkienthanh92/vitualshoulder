# Sample landmark files

`synthetic_shoulder_CT_right_landmarks_for_virtual_shoulder_3d.json` and the `left` file hold landmark positions (SG, GT, HH, SH, GA, GP, HT) in the patient coordinates of the synthetic CT series `synthetic_shoulder_CT_right.zip` / `_left.zip`
(built from real scapula and humerus meshes of paired_shoulder_001_F_56, Zenodo 14590062, CC-BY 4.0; the CT zips are distributed separately because of their size).
Load the CT zip in the Patient tab, then use "Load reference points (JSON)" to show the pink crosses, and "Fill landmarks from phantom" to place the landmarks.
Landmark positions are derived from the dataset landmarks and mesh geometry (GA and GP at 13 mm either side of the glenoid centre along the glenoid anteroposterior axis; SH 60 mm from HH along the shaft), not from expert annotation.
Expected result for the right CT: graft length 48.4, 47.8, 45.6, 39.7 mm at 0, 10, 30, 60 degrees glenohumeral abduction.

The in-page "Use simulated phantom" button needs no files.
