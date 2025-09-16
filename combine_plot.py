# combine_plot.py
# Dispersion (left) + PDOS (right), research-paper ready, vector output.

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# ---------- styling for papers ----------
mpl.rcParams.update({
    # Keep text as vector text in PDF/EPS/SVG and embed TrueType
    "pdf.fonttype": 42,           # editable text in PDF
    "ps.fonttype": 42,            # editable text in EPS
    "svg.fonttype": "none",       # keep text as text in SVG
    # Fonts and general look
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "STIX Two Text", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.linewidth": 1.0,
    "axes.unicode_minus": False,  # proper minus sign if needed
})

# ---------- inputs & column layout (matches your gnuplot script) ----------
dispfile = "pdisp.dat"   # q in col 4, modes in 5..44 (1-based)
pdosfile = "pdos.dat"    # frequency in col 1, DOS in col 2

qcol_1based       = 4
first_mode_1based = 5
last_mode_1based  = 44   # change if you have fewer/more branches

pfreq_1based = 1
pdos_1based  = 2

# ---------- load data ----------
disp = np.loadtxt(dispfile, comments="#")
pdos = np.loadtxt(pdosfile, comments="#")

# Convert to 0-based indices for NumPy
qcol = qcol_1based - 1
first_mode = first_mode_1based - 1
last_mode  = min(last_mode_1based, disp.shape[1])  # cap if file has fewer cols
mode_slice = slice(first_mode, last_mode)

q = disp[:, qcol]
modes = disp[:, mode_slice]   # shape: (N, n_branches)

freq = pdos[:, pfreq_1based - 1]
dos  = pdos[:, pdos_1based  - 1]

# Frequency limits from dispersion data (so both panels match perfectly)
ymin = np.nanmin(modes)
ymax = np.nanmax(modes)

# ---------- figure layout ----------
fig = plt.figure(figsize=(6.0, 5.0))  # inches (matches your gnuplot size 6x5)
gs = fig.add_gridspec(
    nrows=1, ncols=2,
    width_ratios=[3.6, 1.0],      # left wider than right
    left=0.12, right=0.96, top=0.98, bottom=0.18, wspace=0.18
)

ax_disp = fig.add_subplot(gs[0, 0])
ax_pdos = fig.add_subplot(gs[0, 1], sharey=ax_disp)

# ---------- left: dispersion ----------
# Draw each phonon branch
for i in range(modes.shape[1]):
    ax_disp.plot(q, modes[:, i], lw=0.9, color="black")

ax_disp.set_xlim(0, 2)
ax_disp.set_ylim(ymin, ymax)
ax_disp.set_xlabel("q")
ax_disp.set_ylabel("frequency (THz)")

# Symmetry-point ticks like your gnuplot:
ax_disp.set_xticks([0, 1, 2])
ax_disp.set_xticklabels(["Z", "Γ", "Z"])   # U+2212 minus + Gamma

# Subtle grid on x only (as in your script)
ax_disp.grid(axis="x", linewidth=0.4)

# Polished ticks (both in & out like many journals)
ax_disp.tick_params(which="both", direction="in", top=True, right=True, length=5)
ax_disp.tick_params(which="minor", length=3)
ax_disp.xaxis.set_minor_locator(AutoMinorLocator())
ax_disp.yaxis.set_minor_locator(AutoMinorLocator())

# ---------- right: PDOS (rotated by plotting DOS vs freq) ----------
ax_pdos.plot(dos, freq, lw=1.2, color="black")
ax_pdos.set_ylim(ymin, ymax)
ax_pdos.set_xlim(0, np.nanmax(dos)*1.05)
ax_pdos.set_xlabel("DOS")
# Keep tick marks but hide numbers (frequency labeled at left)
ax_pdos.tick_params(labelleft=False)
ax_pdos.tick_params(which="both", direction="in", top=True, right=True, length=5)
ax_pdos.tick_params(which="minor", length=3)
ax_pdos.yaxis.set_minor_locator(AutoMinorLocator())

# Optional: thin vertical spine between panels (keeps a nice “strip” look)
for ax in (ax_disp, ax_pdos):
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)

# ---------- save vector outputs ----------
for ext in ("pdf", "eps", "svg"):
    fig.savefig(f"combine.{ext}", bbox_inches="tight")

plt.close(fig)
print("Wrote combine.pdf, combine.eps, combine.svg")
