#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rg (mean ± SEM) desde réplicas — versión CLI

Uso:
python rg_mean_sem.py -d ./rg
python rg_mean_sem.py -d ./rg --color "0,0.35,0"
python rg_mean_sem.py -d ./rg --color "#1f77b4" --alpha 0.2
python rg_mean_sem.py -d ./rg --out APO
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
        description="Calcular Rg mean ± SEM desde réplicas"
    )

    parser.add_argument(
        "-d", "--dir",
        required=True,
        help="Directorio donde están los archivos .dat"
    )

    parser.add_argument(
        "-p", "--pattern",
        default="radgyr_rep*.dat",
        help="Patrón de archivos dentro del directorio"
    )

    parser.add_argument(
        "--dt",
        type=float,
        default=0.1,
        help="Paso de tiempo en ns por frame"
    )

    parser.add_argument(
        "--no-time",
        action="store_true",
        help="No convertir frame a tiempo"
    )

    parser.add_argument(
        "--out",
        default=None,
        help="Prefijo de salida"
    )

    parser.add_argument(
        "--color",
        default="0,0.35,0",
        help="Color de línea/banda: nombre, HEX o RGB normalizado. Ej: blue, #1f77b4, 0,0.35,0"
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=0.25,
        help="Transparencia de la banda SEM"
    )

    parser.add_argument(
        "--lw",
        type=float,
        default=0.8,
        help="Grosor de línea del promedio"
    )

    return parser.parse_args()


# ============================================================
# FUNCIONES
# ============================================================

def parse_color(color_str):
    """
    Acepta:
    - nombres matplotlib: blue, red, black
    - HEX: #1f77b4
    - RGB normalizado: 0,0.35,0
    """
    color_str = color_str.strip()

    if "," in color_str:
        try:
            color = tuple(float(x.strip()) for x in color_str.split(","))
            if len(color) != 3:
                raise ValueError
            return color
        except ValueError:
            raise ValueError(
                "Color RGB inválido. Usa formato tipo: 0,0.35,0"
            )

    return color_str


def load_xy_file(path, y_col=1):
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
        x = np.arange(1, len(y) + 1, dtype=float)
        return x, y

    ncols = arr.shape[1]

    if y_col < 0 or y_col >= ncols:
        raise ValueError(
            f"Y_COL={y_col} inválida. {path.name} tiene {ncols} columnas."
        )

    y = arr[:, y_col].astype(float)

    if ncols >= 2:
        x = arr[:, 0].astype(float)
    else:
        x = np.arange(1, len(y) + 1, dtype=float)

    return x, y


def frame_to_time_ns(x, dt):
    x = np.asarray(x, dtype=float)
    x = x - np.nanmin(x)
    return x * dt


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
        x, y = load_xy_file(f, y_col=1)
        xs.append(x)
        ys.append(y)

    n_pts = len(ys[0])

    for i, y in enumerate(ys, start=1):
        if len(y) != n_pts:
            raise ValueError(
                f"Longitudes distintas: réplica {i} tiene {len(y)} puntos, "
                f"pero la primera tiene {n_pts}"
            )

    x = xs[0]

    if not args.no_time:
        x = frame_to_time_ns(x, args.dt)
        x_label = "Time (ns)"
    else:
        x_label = "Frame"

    data = np.vstack(ys)

    mean = data.mean(axis=0)

    if data.shape[0] > 1:
        std = data.std(axis=0, ddof=1)
        sem = std / np.sqrt(data.shape[0])
    else:
        std = np.zeros_like(mean)
        sem = np.zeros_like(mean)

    prefix = args.out if args.out else "Rg"

    out_dat = workdir / f"{prefix}_summary_mean_SD_SEM.dat"
    out_png = workdir / f"{prefix}_mean_SEM.png"

    np.savetxt(
        out_dat,
        np.column_stack([x, mean, std, sem]),
        fmt=["%12.6f", "%12.6f", "%12.6f", "%12.6f"],
        header=f"{x_label}  Rg_mean(Å)  Rg_SD(Å)  Rg_SEM(Å)"
    )

    print("\nResumen guardado en:")
    print(out_dat)

    plt.figure(figsize=(10, 4.6))
    ax = plt.gca()

    ax.plot(
        x,
        mean,
        lw=args.lw,
        color=color,
        label="Rg mean"
    )

    ax.fill_between(
        x,
        mean - sem,
        mean + sem,
        color=color,
        alpha=args.alpha,
        label="± SEM"
    )

    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel("Rg (Å)", fontsize=12)
    ax.set_title("Rg (mean ± SEM)", fontsize=13)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=12)

    plt.tight_layout()
    plt.savefig(out_png, dpi=300)

    print("Figura guardada en:")
    print(out_png)


if __name__ == "__main__":
    main()
