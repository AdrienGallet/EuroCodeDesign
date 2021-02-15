# Steel design script overview
This document highlights how a universal steel design script based on EC3 rules will be developed.

# Limitations
* Design limitations
 ** British National Annexes are used/applied
* Sections considered: UKBs and UKCs only
* Class 4 sections are not accounted for
* Only uniform members are considered (no tapered sections)
* No allowance is made for openings (fastener holes do not exceed 0.05b, where b is the width of the flange or the height of the web, see EN 1993-1-5 2.3(1))
* No stiffeners are designed for
* All plates and panels are assuemed rectangular
* Impact of connection design is not accounted for

# Areas of conservatism
* Section classes
  * Possible section enhancements according to EN 1993-1-1 5.5.2 are not accounted for.
  * Cross-sections are classified based on their compression only behaviour (increase in section class due to bending is ignored)
* Shear and bending/axial combinations
  * Reduced yield strength is applied to the entire section, not just the shear area (see EN 1993-1-1 6.2.8, 6.2.9)
  * Shear area is taken as the simplified web or flange area without accounting for the radius of the rolled sections (see EN 1993-1-1 6.2.6)

# General design approach
1. Specify the section and member properties
 * Section name (from selection available)
 * Member length

2. Specify a combination of cross-sectional forces
 * N<sub>t,Ed</sub> (Axial tension), N<sub>c,Ed</sub> (Axial compression), V<sub>z,Ed</sub> (Major axis shear), V<sub>y,Ed</sub> (Minor axis shear),  M<sub>y,Ed</sub> (Major axis bending), M<sub>z,Ed</sub> (Minor axis bending),  T<sub>Ed</sub> (Torsion)
