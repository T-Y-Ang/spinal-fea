# Spinal FEA — Literature References

This bibliography records publications consulted during
development and validation of the L1–L2 finite element model.

The notes describe their relevance to our modelling decisions.
They do not imply that our model has reproduced or validated
the published results.

## 1. Ibarz et al. (2013)

**Title:** Development and Kinematic Verification of a
Finite Element Model for the Lumbar Spine:
Application to Disc Degeneration

**Journal:** The Scientific World Journal

**DOI:** https://doi.org/10.1155/2013/705185

**Full text:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3591128/

### Relevance

- Vertebrae and intervertebral discs were meshed separately.
- Geometric congruency at vertebra–disc interfaces was considered
  important for avoiding artificial stress concentrations.
- Abaqus tie constraints were used to connect the structures.
- Mesh refinement was investigated.

**Application to our project:**
Supports investigating interface geometry and tie-constraint
formulation rather than increasing tolerance without assessing
its mechanical consequences.

**Limitation:**
The paper does not establish an appropriate numerical tie
tolerance for our CalculiX model.

## 2. Warren et al. (2020)

**Title:** Development and Validation of a Computationally
Efficient Finite Element Model of the Human Lumbar Spine:
Application to Disc Degeneration

**Journal:** International Journal of Spine Surgery

**DOI:** https://doi.org/10.14444/7066

**Full text:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7478021/

### Relevance

- Investigates computationally efficient lumbar modelling.
- Demonstrates the value of simplified modelling approaches.
- Emphasises comparison of predicted mechanical behaviour
  against reference models or validation data.

**Application to our project:**
Supports the use of an initial simplified L1–L2 model before
progressing to more anatomically complex simulations.

**Limitation:**
This reference is not being used to justify a specific
tie-tolerance value or interface-repair algorithm.

## 3. Wiczenbach et al. (2023)

**Title:** Development and Validation of Lumbar Spine
Finite Element Model

**Journal:** PeerJ

**DOI:** https://doi.org/10.7717/peerj.15805

**Full text:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10424670/

### Relevance

- Describes a more detailed representation of spinal tissues.
- Uses shared-node connectivity for selected structures.
- Incorporates contact formulations for selected interfaces.
- Evaluates mechanical behaviour under multiple loading modes.

**Application to our project:**
Illustrates that interface formulations should reflect
the mechanical relationships between the modelled structures.

**Limitation:**
Its contact formulations should not be transferred directly
to our simplified bonded vertebra–disc interfaces without
considering the differences in model construction.

## 4. Schmidt et al. (2007)

**Title:** Application of a Calibration Method Provides
More Realistic Results for a Finite Element Model of a
Lumbar Spinal Segment

**Journal:** Clinical Biomechanics

**DOI:** https://doi.org/10.1016/j.clinbiomech.2006.11.008

**PubMed:** https://pubmed.ncbi.nlm.nih.gov/17204355/

### Relevance

- Examines calibration of lumbar finite element models.
- Highlights the importance of experimental comparison.
- Demonstrates that apparently acceptable baseline predictions
  do not guarantee reliable predictions under altered conditions.

**Application to our project:**
Supports validating the model's mechanical response rather
than adjusting numerical parameters merely to obtain
plausible stiffness values.

**Limitation:**
Does not provide a direct solution to the specific
CalculiX tie-constraint problem identified in our model.

## Literature-informed modelling decision

The current priority is to investigate the geometry and
connectivity of the vertebra–disc interfaces.

Potential approaches include:

1. Correcting the existing interface geometry while retaining
   appropriate tie constraints.
2. Constructing conforming meshes with shared interface nodes.
3. Comparing the mechanical response of repaired models
   against the existing simulations.

Further increases in tie tolerance alone are not considered
a sufficient validation strategy.

These decisions are provisional and subject to additional
numerical testing and literature review.
