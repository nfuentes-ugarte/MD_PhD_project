#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RMSF (mean ± SEM) desde réplicas — versión CLI

Uso:
python rmsf_mean_sem.py -d ./rmsf
python rmsf_mean_sem.py -d ./rmsf --color "#1f77b4"
python rmsf_mean_sem.py -d ./rmsf --color "0,0.35,0" --alpha 0.2 --out APO
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import glob
import argparse


# ============================================================
# ARGUMENTOS CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcular RMSF mean ± SEM desde réplicas"
    )

    parser.add_argument("-d", "--dir", required=True,
                        help="Directorio con archivos RMSF")

    parser.add_argument("-p", "--pattern", default="rmsf_prot_rep*.dat",
                        help="Patrón de archivos")

    parser.add_argument("--out", default=None,
                        help="Prefijo de salida")

    parser.add_argument("--color", default="0,0.35,0",
                        help="Color: nombre, HEX o RGB. Ej: blue, #1f77b4, 0,0.35,0")

    parser.add_argument("--alpha", type=float, default=0.25,
                        help="Transparencia de la banda SEM")

    parser.add_argument("--lw", type=float, default=0.8,
                        help="Grosor de línea")

    parser.add_argument("--rmsf-col", type=int, default=None,
                        help="Columna 0-based para RMSF. Default: última columna")

    return parser.parse_args()


# ============================================================
# FUNCIONES
# ============================================================

def parse_color(color_str):
    color_str = color_str.strip()

    if "," in color_str:
        color = tuple(float(x.strip()) for x in color_str.split(","))
        if len(color) != 3:
            raise ValueError("Color RGB inválido. Usa formato: 0,0.35,0")
        return color

    return color_str


def load_rmsf_file(path, rmsf_col=None):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")

    try:
        arr = np.loadtxt(path, comments="#")
    except Exception:
        rows = []
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue

                try:
                    rows.append([float(p) for p in s.split()])
                except ValueError:
                    continue

        if not rows:
            raise ValueError(f"No pude leer datos numéricos desde: {path}")

        arr = np.array(rows, dtype=float)

    if arr.ndim == 1:
        y = arr.astype(float)
        x = np.arange(1, len(y) + 1)
        return x, y

    ncols = arr.shape[1]

    use_col = ncols - 1 if rmsf_col is None else int(rmsf_col)

    if use_col < 0 or use_col >= ncols:
        raise ValueError(
            f"RMSF_COL inválida ({use_col}). {path.name} tiene {ncols} columnas."
        )

    y = arr[:, use_col].astype(float)

    x0 = arr[:, 0]

    if np.all(np.isfinite(x0)) and np.allclose(x0, np.round(x0), atol=1e-6):
        x = x0.astype(int)
    else:
        x = np.arange(1, len(y) + 1)

    return x, y


def style_axes(ax):
    for spine in ax.spines.values():
        spine.set_linewidth(1.8)

    ax.tick_params(
        axis="both",
        which="both",
        width=1.6,
        length=6,
        labelsize=12
    )


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()

    workdir = Path(args.dir).resolve()
    color = parse_color(args.color)

    if not workdir.exists():
        raise FileNotFoundError(f"No existe el directorio: {workdir}")

    files = sorted(glob.glob(str(workdir / args.pattern)))

    if not files:
        raise FileNotFoundError(
            f"No encontré archivos con patrón: {workdir / args.pattern}"
        )

    print("Directorio:", workdir)
    print("\nArchivos detectados:")

    for f in files:
        print(" -", f)

    xs = []
    ys = []

    for f in files:
        x, y = load_rmsf_file(f, rmsf_col=args.rmsf_col)
        xs.append(x)
        ys.append(y)

    n_res = len(ys[0])

    for i, y in enumerate(ys, start=1):
        if len(y) != n_res:
            raise ValueError(
                f"Longitudes distintas: réplica {i} tiene {len(y)} residuos, "
                f"pero la primera tiene {n_res}"
            )

    resid = xs[0]

    rmsf = np.vstack(ys)

    mean = rmsf.mean(axis=0)

    if rmsf.shape[0] > 1:
        std = rmsf.std(axis=0, ddof=1)
        sem = std / np.sqrt(rmsf.shape[0])
    else:
        std = np.zeros_like(mean)
        sem = np.zeros_like(mean)

    prefix = args.out if args.out else "RMSF"

    out_dat = workdir / f"{prefix}_summary_mean_SD_SEM.dat"
    out_png = workdir / f"{prefix}_mean_SEM.png"

    np.savetxt(
        out_dat,
        np.column_stack([resid, mean, std, sem]),
        fmt=["%6d", "%12.6f", "%12.6f", "%12.6f"],
        header="ResID  RMSF_mean(Å)  RMSF_SD(Å)  RMSF_SEM(Å)"
    )

    print("\nResumen guardado en:")
    print(out_dat)

    plt.figure(figsize=(10, 4.6))
    ax = plt.gca()

    ax.plot(
        resid,
        mean,
        lw=args.lw,
        color=color,
        label="RMSF mean"
    )

    ax.fill_between(
        resid,
        mean - sem,
        mean + sem,
        color=color,
        alpha=args.alpha,
        label="± SEM"
    )

    ax.set_xlabel("Residue", fontsize=12)
    ax.set_ylabel("RMSF (Å)", fontsize=12)
    ax.set_title("RMSF (mean ± SEM)", fontsize=13)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=12)

    plt.tight_layout()
    plt.savefig(out_png, dpi=300)

    print("Figura guardada en:")
    print(out_png)


if __name__ == "__main__":
    main()
