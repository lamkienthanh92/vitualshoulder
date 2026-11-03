# Data sources

**BodyParts3D**, © The Database Center for Life Science, licensed under Creative Commons Attribution-Share Alike 2.1 Japan (http://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html).
Release 3.0 (20110915), obtained via the STL conversion at github.com/Kevin-Mattheus-Moerman/BodyParts3D.

Structures used (right side): scapula FMA13395, humerus FMA23130, clavicle FMA13322, supraspinatus FMA32544, infraspinatus FMA32547, subscapularis FMA13414, teres minor FMA32553, long head of biceps FMA37686, short head of biceps FMA37684, deltoid parts FMA34680/34682/34684 (merged), teres major FMA32551, coracobrachialis FMA37665, long head of triceps FMA37699.

Modifications: mesh decimation, coordinate change (origin at humeral head centre, x = subject left, y = up, z = anterior), 16-bit quantisation, per-vertex skinning weights for muscles, derived landmarks. These adaptations remain under CC BY-SA 2.1 Japan.

Citation: Mitsuhashi N, Fujieda K, Tamura T, Kawamoto S, Takagi T, Okubo K. BodyParts3D: 3D structure database for anatomical concepts. Nucleic Acids Res. 2009;37:D782-5. doi:10.1093/nar/gkn613

three.js r128 (MIT) is loaded from cdnjs at run time.

## Samples and literature
- `sample/`: landmark files for synthetic CT series built from real scapula and humerus meshes (paired_shoulder_001_F_56, Zenodo 14590062, CC-BY 4.0), as described in `sample/README.md`.
- Numbers and flags cite the papers listed in `docs/EVIDENCE.md`.
