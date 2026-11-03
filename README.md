# Virtual Shoulder 3D

Interactive 3D viewer and planning aid for the right shoulder, built as a sibling of the virtual knee 3D app. Single static HTML file, no build step.


## Tabs (current release 0.20; table written for v0.8, see the version sections below)
| Tab | Content |
|---|---|
| **Teaching** | Lesions (full-thickness tear of supraspinatus / infraspinatus / subscapularis, superior migration of the head), procedure (LHBT in situ, fascia lata, human dermal allograft) with evidence cards, arm motion (elevation, plane, rotation, scapulohumeral rhythm), LHBT path length curve. |
| **Display** | Brightness slider for the 3D model, layers (bones, rotator cuff, deltoid, teres major, coracobrachialis, biceps short head, triceps long head, LHBT), transparency, callout labels, colour or grey print style. |
| **Planning** | Live dashboard (sliders for technique, fixation angle, thickness, anchors, head elevation and arm position update the 3D graft, key outputs, a length-change chart, a fixation-angle trade-off chart, editable goals, a what-if panel with published values and a table of literature benchmarks; best-anchor search) plus graft type (LHBT in situ, Chinese way, biceps loop, Box two-bundle, Snake, fascia lata, dermal allograft), width, thickness, fixation angle; anchor positions with an isometry map on the bone surface (click a dot to choose); graft length vs glenohumeral abduction and tension/slack table; comparison with Mihata 2016; side-by-side plan comparison, decision-support variables (fixation-angle matrix, sensitivity to rotation and to head elevation, optional clinical profile: Goutallier, Hamada, LHB tear %); flags; printable / saveable plan. |
| **Patient** | Open DICOM (folder, files or zip; uncompressed and JPEG Lossless), MPR views, landmark picking (SG, GT, HH, SH, GA, GP, optional AC, HT), SCR simulation on the images, image-reliability label, display presets (natural / soft tissue / bone / full range) with trilinear interpolation, a 3D view of the patient's landmarks, graft, the three image planes (MRI or CT slices placed in space, with adjustable positions and opacity), template scapula and humerus fitted to the landmarks (similarity transform; template shape, not patient bone) and optional STL bones (left shoulder mirrored), and an STL-only mode: load the scapula and humerus STL of one case (e.g. `single_shoulder_001_M_56_L_Humerus.stl` + `..._Scapula.stl`) and the app places the landmarks automatically and runs the SCR simulation; click on the bone to move a landmark; with a STL pair the app also reports the bone-to-bone clearance between the humeral head and the scapular roof at the scan pose and across 0–120° abduction. "Run all cases" processes every complete STL pair and saves a CSV table (head radius, glenoid size, template fit error, graft length at 0/10/30/60°, slope); edited landmarks can be exported against the automatic ones (distance per landmark) for validation. |
| **Notes** | Method, limitations, licence, references behind the numbers and flags. |

## Flags (see `docs/EVIDENCE.md`)
Each flag states whether its number comes from the literature or is an app assumption. App assumptions (not validated): 3 mm gap to the best anchor in the grid, 10 mm spare length for LHBT fixation.

## Run / publish
Open `index.html` in a browser (needs internet once for three.js and JSZip from cdnjs). Images and models are read locally and are never uploaded.

- **GitHub Pages:** push these files, Settings → Pages → branch `main`, folder `/ (root)` (`.nojekyll` is included).
- **Netlify:** drag the folder onto app.netlify.com/drop, or connect the GitHub repository (no build command; publish directory `.`, set in `netlify.toml`).
- **Zenodo:** in zenodo.org → GitHub, switch the repository on, then create a GitHub release (tag `v0.20.0`). Zenodo reads `CITATION.cff`, archives the release and gives a DOI; add that DOI to `CITATION.cff` (`doi:`) and to the article.

## Limitations
One male anatomical model, not patient-specific. No collision, capsule, ligament, labrum or humeral-head translation beyond the manual "head up" setting. Scapular motion is an approximation (rotation about the AC point). Tendon and graft lengths are geometric estimates; the humeral anchor default is the footprint centroid, not the medial footprint edge where anchors are usually placed. Cadaver numbers in the evidence cards are time-zero, static-load results. JPEG baseline, JPEG 2000 and RLE DICOM are not read (JPEG Lossless is); bones are not segmented automatically from CT (use 3D Slicer or Mimics and load STL). Automatic STL landmarks are estimates: the greater-tuberosity point comes from registering the template humerus (median fit error about 1 mm on four test cases) and must be checked by eye. Not a medical device.

## Licence
- Code (viewer logic and `scripts/`): MIT, see `LICENSE`.
- Mesh data embedded in `index.html` is derived from BodyParts3D and stays under **CC BY-SA 2.1 Japan**; see `DATA_SOURCES.md`.

## Citation
See `CITATION.cff` (the Zenodo DOI of each release is added there). Please also cite Mitsuhashi et al. 2009 (BodyParts3D).

## Rebuilding
`scripts/01_head_sphere.py` → `02_glenoid.py` → `03_build_data.py` (needs BodyParts3D STL files, numpy, scipy, trimesh, fast-simplification) → `04_assemble.py` (rebuilds `index.html` from `app_template.html`; `data.json` and `blob.b64` are included so step 4 alone reproduces the shipped file).

## Cadaver data
`index.html` contains the constant `CAD` (summary statistics) and `CAD.rows` (one row per shoulder; n = 10 shoulders, 5 cadavers) with the width and thickness of the long head of the biceps tendon and the thickness of the superior capsule. These measurements are reported in the accompanying article; cite it when using them. If you fork this repository for another cohort, replace both (search for `const CAD=` and `CAD.rows=`).

## Research analyses (Planning tab)
- Tendon dimensions of the own cadaver series against the selected technique: per-shoulder table, count below 5 mm with exact (Clopper-Pearson) 95% interval, exact right-left Spearman and Wilcoxon p-values, hatched figure, CSV.
- Variation of the graft path across the CT shoulders loaded in the Patient tab: table, hatched figure, CSV.

## Interface (v0.19)
Sections fold (tap a heading); long explanations sit behind ⓘ icons; the surgical plan is a card (technique chips, status chips, key tiles, graft path chart, bundle bars, check chips, steps, full text on demand); icons on the 3D view open the plan, the tension chart, layer switches and a panel to show or hide sections, show explanations or reset. Choices are kept in the browser (localStorage) when available.

## Windows and tools (v0.20)
Icons on the right of the 3D view open movable windows (surgical plan, graft tension chart, controls, layers, muscles, customise); several can be open at once, each can be dragged by its title bar, resized, made transparent (step button), minimised or closed, and its position is remembered. Icons on the left: labels, fit, play the abduction, see through the bone, isometry map mode, save a picture. A slider at the bottom of the view sets the arm elevation (template) or the simulated abduction (patient), with play and pause.
