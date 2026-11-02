"""
Generate sagittal CT contact sheets for preliminary screening.

Purpose:
    Identify candidate scans without obvious spinal instrumentation
    and with potentially relevant vertebral compression deformities.

Limitations:
    Images are sampled around the CT volume centre, not necessarily
    the anatomical spinal midline. Findings require further review.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np


# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------

DATA_DIR = Path("data/processed")

SCANS = {
    "0280": "4537603",
    "0281": "4554026",
    "0286": "4557469",
    "0295": "3058243",
    "0308": "2558438",
    "0309": "2887318",
    "0318": "4526237",
    "0319": "3220605",
    "0338": "4552210",
    "0341": "4453272",
}

# Offsets from the centre of the CT volume, in voxels
OFFSETS = [-20, 0, 20]


# -------------------------------------------------------------
# CREATE CONTACT SHEET
# -------------------------------------------------------------

fig, axes = plt.subplots(
    len(SCANS),
    len(OFFSETS),
    figsize=(12, 30),
)

for row, (patient_id, scan_id) in enumerate(SCANS.items()):

    image_path = (
        DATA_DIR
        / f"patient{patient_id}"
        / f"{scan_id}.nii.gz"
    )

    # Load and standardise the image to RAS orientation
    image = nib.as_closest_canonical(
        nib.load(image_path)
    )

    volume = np.asarray(image.dataobj)
    spacing = image.header.get_zooms()[:3]

    centre = volume.shape[0] // 2

    for col, offset in enumerate(OFFSETS):

        sagittal = volume[centre + offset, :, :]

        ax = axes[row, col]

        ax.imshow(
            sagittal.T,
            cmap="gray",
            origin="lower",
            extent=[
                0,
                sagittal.shape[0] * spacing[1],
                0,
                sagittal.shape[1] * spacing[2],
            ],
            vmin=-200,
            vmax=1000,
            aspect="equal",
        )

        ax.set_title(
            f"Patient {patient_id} | Scan {scan_id} | "
            f"Offset {offset:+d}",
            fontsize=10,
        )

        ax.set_xticks([])
        ax.set_yticks([])

    print(f"Processed patient {patient_id}, scan {scan_id}")


# -------------------------------------------------------------
# SAVE OUTPUT
# -------------------------------------------------------------

output_path = DATA_DIR / "batch01_sagittal_contact_sheet.png"

plt.tight_layout()
plt.savefig(output_path, dpi=140)
plt.close()

print(f"\nContact sheet saved to: {output_path}")
