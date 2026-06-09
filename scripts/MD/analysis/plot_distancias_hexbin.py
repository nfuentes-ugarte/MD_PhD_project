#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HEXBIN + histogramas marginales para distancias cpptraj.

Entrada esperada:
Archivo combinado con columnas, por ejemplo:
col1 = dist1
col2 = dist2
col3 = HMP

Ejemplo:
python3 scripts/plot_distancias_hexbin.py \
  --input distancias/distancias_combinadas.dat \
  --xcol 1 \
  --ycol 2 \
  --xlabel "d Q44 - HMP-P (Å)" \
  --ylabel "d HMP-P - ATP (Å)" \
  --output distancias/dist1_vs_dist2_hexbin_frames.png
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
from PIL import Image
import matplotlib.font_manager as fm


# ======================================================
# ARGUMENTOS
# ======================================================

parser = argparse.ArgumentParser()

parser.add_argument("--input", required=True, help="Archivo combinado de distancias")
parser.add_argument("--xcol", type=int, default=1, help="Columna para eje X, empezando en 1")
parser.add_argument("--ycol", type=int, default=2, help="Columna para eje Y, empezando en 1")
parser.add_argument("--xlabel", default="Distancia X (Å)")
parser.add_argument("--ylabel", default="Distancia Y (Å)")
parser.add_argument("--output", default="hexbin_distancias.png")

args = parser.parse_args()

INPUT_FILE = Path(args.input)
OUT_PNG = Path(args.output)

XCOL = args.xcol - 1
YCOL = args.ycol - 1

XLABEL = args.xlabel
YLABEL = args.ylabel


# ======================================================
# FUENTE
# ======================================================

def set_arial():
    fonts = [f.name for f in fm.fontManager.ttflist]

    if "Arial" in fonts:
        plt.rcParams["font.family"] = "Arial"
    else:
        plt.rcParams["font.family"] = "DejaVu Sans"

    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42


set_arial()


# ======================================================
# CONFIG FIGURA
# ======================================================

FIGSIZE = (8.4, 8.0)
DPI = 600

BIN_WIDTH = 0.2

HEX_GRIDSIZE = 100
HEX_CMAP = "viridis"
HEX_MINCNT = 1

W_GAP = 0.14
W_CBAR = 0.08
WSPACE = 0.12
HSPACE = 0.05

ADJ_LEFT = 0.11
ADJ_RIGHT = 0.84
ADJ_BOTTOM = 0.14
ADJ_TOP = 0.96

SPINE_W = 2.0
TICK_W = 1.6
TICK_L = 6

FS_MAIN = 24
FS_HIST = 18
FS_CBAR = 18
FS_TICK = 18

EXPORT_PAD_INCHES = 0.12
TMP_EXPORT = "_tmp_export.png"


# ======================================================
# UMBRALES
# ======================================================

DRAW_THRESHOLDS = True
THR_X = 3.5
THR_Y = 4.5

DRAW_THR_ON_HISTS = True

THR_COLOR = "black"
THR_LS = (0, (6, 4))
THR_LW = 2.2
THR_ALPHA = 0.9


# ======================================================
# EXPORT ROBUSTO
# ======================================================

def save_fixed_png(fig, out_png, figsize, dpi, pad_inches=0.12, tmp_png="_tmp_export.png"):
    target_w = int(round(figsize[0] * dpi))
    target_h = int(round(figsize[1] * dpi))

    fig.savefig(
        tmp_png,
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=pad_inches
    )

    im = Image.open(tmp_png).convert("RGBA")
    iw, ih = im.size

    scale = min(target_w / iw, target_h / ih, 1.0)

    if scale < 1.0:
        new_size = (int(iw * scale), int(ih * scale))
        im = im.resize(new_size, resample=Image.Resampling.LANCZOS)
        iw, ih = im.size

    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    ox = (target_w - iw) // 2
    oy = (target_h - ih) // 2
    canvas.alpha_composite(im, (ox, oy))
    canvas.save(out_png)

    try:
        Path(tmp_png).unlink(missing_ok=True)
    except Exception:
        pass


# ======================================================
# HELPERS
# ======================================================

def style(ax):
    ax.set_facecolor("none")

    for s in ax.spines.values():
        s.set_linewidth(SPINE_W)
        s.set_color("black")

    ax.tick_params(
        width=TICK_W,
        length=TICK_L,
        labelsize=FS_TICK,
        colors="black"
    )


def make_bins(v):
    lo = np.floor(v.min() / BIN_WIDTH) * BIN_WIDTH
    hi = np.ceil(v.max() / BIN_WIDTH) * BIN_WIDTH
    return np.arange(lo, hi + BIN_WIDTH, BIN_WIDTH)


def build_fig(w_hist):
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor="none")

    gs = GridSpec(
        4, 6,
        figure=fig,
        width_ratios=[1, 1, 1, w_hist, W_GAP, W_CBAR],
        wspace=WSPACE,
        hspace=HSPACE
    )

    ax_top = fig.add_subplot(gs[0, 0:3])
    ax_main = fig.add_subplot(gs[1:4, 0:3])
    ax_right = fig.add_subplot(gs[1:4, 3])
    ax_gap = fig.add_subplot(gs[1:4, 4])
    ax_cbar = fig.add_subplot(gs[1:4, 5])

    ax_gap.axis("off")

    for ax in (ax_top, ax_main, ax_right, ax_cbar):
        style(ax)

    return fig, ax_top, ax_main, ax_right, ax_cbar


def measure(fig, ax_top, ax_right):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    return (
        ax_top.get_window_extent(r).height,
        ax_right.get_window_extent(r).width
    )


# ======================================================
# CARGA DE DATOS
# ======================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"No existe el archivo: {INPUT_FILE}")

data = np.loadtxt(INPUT_FILE)

if data.ndim == 1:
    raise ValueError("El archivo debe tener al menos dos columnas.")

if XCOL >= data.shape[1] or YCOL >= data.shape[1]:
    raise ValueError(
        f"El archivo tiene {data.shape[1]} columnas, "
        f"pero pediste xcol={args.xcol}, ycol={args.ycol}"
    )

x = data[:, XCOL]
y = data[:, YCOL]

mask = np.isfinite(x) & np.isfinite(y)
x = x[mask]
y = y[mask]

n = min(len(x), len(y))
x = x[:n]
y = y[:n]

if n == 0:
    raise ValueError("No hay datos válidos para graficar.")

bx = make_bins(x)
by = make_bins(y)


# ======================================================
# AUTOAJUSTE HISTOGRAMA LATERAL
# ======================================================

lo, hi = 0.15, 2.00
best = None

for _ in range(30):
    mid = 0.5 * (lo + hi)

    fig_tmp, at, am, ar, ac = build_fig(mid)
    ht, wr = measure(fig_tmp, at, ar)
    diff = wr - ht

    best = (mid, diff)
    plt.close(fig_tmp)

    if abs(diff) < 1.0:
        break

    if diff < 0:
        lo = mid
    else:
        hi = mid

w_hist = best[0]


# ======================================================
# FIGURA FINAL
# ======================================================

fig, ax_top, ax_main, ax_right, ax_cbar = build_fig(w_hist)

hb = ax_main.hexbin(
    x,
    y,
    gridsize=HEX_GRIDSIZE,
    cmap=HEX_CMAP,
    mincnt=HEX_MINCNT,
    linewidths=0,
    bins=None
)

if DRAW_THRESHOLDS:
    ax_main.axvline(
        THR_X,
        color=THR_COLOR,
        linestyle=THR_LS,
        linewidth=THR_LW,
        alpha=THR_ALPHA
    )

    ax_main.axhline(
        THR_Y,
        color=THR_COLOR,
        linestyle=THR_LS,
        linewidth=THR_LW,
        alpha=THR_ALPHA
    )


# ======================================================
# COLORBAR
# ======================================================

cbar = plt.colorbar(hb, cax=ax_cbar)

cbar.ax.tick_params(
    labelsize=FS_TICK,
    width=TICK_W,
    length=TICK_L,
    pad=4
)

cbar.set_label(
    "Frames",
    fontsize=FS_CBAR,
    labelpad=10,
    color="black"
)

cbar.ax.yaxis.set_label_position("right")
cbar.ax.yaxis.tick_right()


# ======================================================
# HISTOGRAMA X
# ======================================================

wx = np.ones_like(x) * 100.0 / n

ax_top.hist(
    x,
    bins=bx,
    weights=wx,
    color="green",
    edgecolor="black",
    lw=1.4
)

counts_x, _ = np.histogram(x, bins=bx)
cent_x = 0.5 * (bx[:-1] + bx[1:])

ax_top.plot(
    cent_x,
    counts_x * 100.0 / n,
    linestyle="--",
    lw=2.2,
    color="green"
)

ax_top.set_ylabel(
    "Frequency (%)",
    fontsize=FS_HIST,
    labelpad=8,
    color="black"
)

ax_top.tick_params(labelbottom=False)

if DRAW_THRESHOLDS and DRAW_THR_ON_HISTS:
    ax_top.axvline(
        THR_X,
        color=THR_COLOR,
        linestyle=THR_LS,
        linewidth=THR_LW,
        alpha=THR_ALPHA
    )


# ======================================================
# HISTOGRAMA Y
# ======================================================

wy = np.ones_like(y) * 100.0 / n

ax_right.hist(
    y,
    bins=by,
    weights=wy,
    orientation="horizontal",
    color="yellow",
    edgecolor="black",
    lw=1.4
)

counts_y, _ = np.histogram(y, bins=by)
cent_y = 0.5 * (by[:-1] + by[1:])

ax_right.plot(
    counts_y * 100.0 / n,
    cent_y,
    linestyle="--",
    lw=2.2,
    color="yellow"
)

ax_right.set_xlabel(
    "Frequency (%)",
    fontsize=FS_HIST,
    labelpad=10,
    color="black"
)

ax_right.tick_params(labelleft=False)

if DRAW_THRESHOLDS and DRAW_THR_ON_HISTS:
    ax_right.axhline(
        THR_Y,
        color=THR_COLOR,
        linestyle=THR_LS,
        linewidth=THR_LW,
        alpha=THR_ALPHA
    )


# ======================================================
# LABELS
# ======================================================

ax_main.set_xlabel(
    XLABEL,
    fontsize=FS_MAIN,
    labelpad=12,
    color="black"
)

ax_main.set_ylabel(
    YLABEL,
    fontsize=FS_MAIN,
    labelpad=12,
    color="black"
)

ax_top.set_xlim(ax_main.get_xlim())
ax_right.set_ylim(ax_main.get_ylim())

fig.subplots_adjust(
    left=ADJ_LEFT,
    right=ADJ_RIGHT,
    bottom=ADJ_BOTTOM,
    top=ADJ_TOP
)

OUT_PNG.parent.mkdir(parents=True, exist_ok=True)

save_fixed_png(
    fig,
    OUT_PNG,
    FIGSIZE,
    DPI,
    pad_inches=EXPORT_PAD_INCHES,
    tmp_png=TMP_EXPORT
)

print(f"Guardado: {OUT_PNG}")
print(f"Frames analizados: {n}")
print(f"Columna X usada: {args.xcol}")
print(f"Columna Y usada: {args.ycol}")

plt.close(fig)
