#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RMSD (mean ± SEM) desde réplicas — versión CLI

Uso:
python rmsd_mean_sem.py -d ./rmsd
python rmsd_mean_sem.py -d ./rmsd --color blue
python rmsd_mean_sem.py -d ./rmsd --color "0,0.35,0" --alpha 0.2
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
        description="Calcular RMSD mean ± SEM desde réplicas"
    )

    parser.add_argument("-d", "--dir", required=True,
                        help="Directorio con archivos RMSD")

    parser.add_argument("-p", "--pattern", default="rmsd_CA_rep*.dat",
                        help="Patrón de archivos")

    parser.add_argument("--dt", type=float, default=0.1,
                        help="Paso de tiempo en ns")

    parser.add_argument("--no-time", action="store_true",
                        help="No convertir frame a tiempo")

    parser.add_argument("--out", default=None,
                        help="Prefijo de salida")

    parser.add_argument("--color", default="0,0.35,0",
                        help="Color: nombre, HEX o RGB (ej: blue, #1f77b4, 0,0.35,0)")

    parser.add_argument("--alpha", type=float, default=0.25,
                        help="Transparencia banda SEM")

    parser.add_argument("--lw", type=float, default=0.8,
                        help="Grosor línea")

    return parser.parse_args()


# ============================================================
# FUNCIONES
# ============================================================

def parse_color(color_str):
    if "," in color_str:
        return tuple(float(x) for x in color_str.split(","))
    return color_str


def load_xy_file(path):
    path = Path(path)

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
        arr = np.array(rows, dtype=float)

    if arr.ndim == 1:
        y = arr
        x = np.arange(1, len(y) + 1)
        return x, y

    x = arr[:, 0]
    y = arr[:, -1]  # última columna (RMSD)

    return x, y


def frame_to_time_ns(x, dt):
    x = np.asarray(x)
    x = x - np.min(x)
    return x * dt


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()

    workdir = Path(args.dir)
    color = parse_color(args.color)

    files = sorted(glob.glob(str(workdir / args.pattern)))

    if not files:
        raise FileNotFoundError(f"No encontré archivos: {args.pattern}")

    print("Archivos:")
    for f in files:
        print(" -", f)

    xs, ys = [], []

    for f in files:
        x, y = load_xy_file(f)
        xs.append(x)
        ys.append(y)

    n_pts = len(ys[0])

    for i, y in enumerate(ys):
        if len(y) != n_pts:
            raise ValueError(f"Replica {i} tiene distinto largo")

    x = xs[0]

    if not args.no_time:
        x = frame_to_time_ns(x, args.dt)
        xlabel = "Time (ns)"
    else:
        xlabel = "Frame"

    data = np.vstack(ys)

    mean = data.mean(axis=0)
    std = data.std(axis=0, ddof=1)
    sem = std / np.sqrt(data.shape[0])

    prefix = args.out if args.out else "RMSD"

    out_dat = workdir / f"{prefix}_summary_mean_SD_SEM.dat"
    out_png = workdir / f"{prefix}_mean_SEM.png"

    np.savetxt(
        out_dat,
        np.column_stack([x, mean, std, sem]),
        header=f"{xlabel} RMSD_mean RMSD_SD RMSD_SEM"
    )

    print("\nGuardado:", out_dat)

    # =========================
    # PLOT
    # =========================

    plt.figure(figsize=(10, 4.6))

    plt.plot(x, mean, lw=args.lw, color=color, label="Mean")

    plt.fill_between(
        x,
        mean - sem,
        mean + sem,
        color=color,
        alpha=args.alpha,
        label="SEM"
    )

    plt.xlabel(xlabel)
    plt.ylabel(r"RMSD C$\alpha$ (Å)")
    plt.title("RMSD (mean ± SEM)")
    plt.legend()

    plt.tight_layout()
    plt.savefig(out_png, dpi=300)

    print("Figura:", out_png)


if __name__ == "__main__":
    main()
