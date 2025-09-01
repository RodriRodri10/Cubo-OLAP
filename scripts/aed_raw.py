import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def iqr_outlier_mask(s: pd.Series, k: float = 1.5):
    q1 = s.quantile(0.25); q3 = s.quantile(0.75)
    iqr = q3 - q1; lower = q1 - k*iqr; upper = q3 + k*iqr
    return (s < lower) | (s > upper), lower, upper, iqr

# --- Raíz del repo y carpetas ---
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "eda_raw_output"

def run_eda(input_csv: Path):
    ensure_dir(OUT_DIR)
    print(f" Cargando: {input_csv.resolve()}")
    df = pd.read_csv(
        input_csv, encoding="utf-8-sig",
        parse_dates=["OrderDate"], dayfirst=False, infer_datetime_format=True
    )

    info = {
        "rows": len(df),
        "cols": df.shape[1],
        "duplicated_rows": int(df.duplicated().sum()),
        "missing_total": int(df.isna().sum().sum())
    }
    print("ℹ Info general:", info)

    dtypes = df.dtypes.astype(str).rename("dtype").to_frame()
    missing = df.isna().sum().rename("missing").to_frame()
    missing["missing_pct"] = (missing["missing"] / len(df) * 100).round(2)
    dtypes.join(missing).to_csv(OUT_DIR / "01_column_quality.csv")
    print(" Guardado: 01_column_quality.csv")

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        df[num_cols].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).T.to_csv(OUT_DIR / "02_numeric_describe.csv")
        print(" Guardado: 02_numeric_describe.csv")

    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    topn = 15
    cat_summary = []
    for c in cat_cols:
        vc = df[c].value_counts(dropna=False).head(topn)
        tmp = vc.reset_index(); tmp.columns = [c, "count"]
        tmp["pct"] = (tmp["count"] / len(df) * 100).round(2); tmp["column"] = c
        cat_summary.append(tmp)

        plt.figure(figsize=(10, 4))
        vc.sort_values(ascending=True).plot(kind="barh")
        plt.title(f"Top {topn} - {c}"); plt.tight_layout()
        plt.savefig(OUT_DIR / f"cat_top_{c}.png", dpi=150); plt.close()
    if cat_summary:
        pd.concat(cat_summary, ignore_index=True).to_csv(OUT_DIR / "03_categorical_topN.csv", index=False)
        print(" Guardado: 03_categorical_topN.csv + gráficos")

    for c in num_cols:
        s = df[c].dropna()
        if s.empty: continue
        plt.figure(figsize=(6,4)); s.plot(kind="hist", bins=30)
        plt.title(f"Histograma - {c}"); plt.xlabel(c); plt.ylabel("Frecuencia")
        plt.tight_layout(); plt.savefig(OUT_DIR / f"num_hist_{c}.png", dpi=150); plt.close()

        plt.figure(figsize=(6,2.5)); plt.boxplot(s, vert=False, manage_ticks=True)
        plt.title(f"Boxplot - {c}"); plt.xlabel(c)
        plt.tight_layout(); plt.savefig(OUT_DIR / f"num_box_{c}.png", dpi=150); plt.close()
    if num_cols: print(" Guardados: num_hist_* y num_box_*")

    if len(num_cols) >= 2:
        corr = df[num_cols].corr(numeric_only=True)
        corr.to_csv(OUT_DIR / "04_numeric_correlation.csv")
        plt.figure(figsize=(0.6*len(num_cols)+3, 0.6*len(num_cols)+3))
        plt.imshow(corr, interpolation="nearest"); plt.title("Correlación (numéricas)")
        plt.xticks(range(len(num_cols)), num_cols, rotation=90)
        plt.yticks(range(len(num_cols)), num_cols); plt.colorbar()
        plt.tight_layout(); plt.savefig(OUT_DIR / "num_corr_heatmap.png", dpi=150); plt.close()
        print(" Guardados: 04_numeric_correlation.csv y num_corr_heatmap.png")

    outlier_rows = []
    for c in num_cols:
        s = df[c].dropna()
        if s.empty: continue
        mask, lower, upper, iqr = iqr_outlier_mask(s)
        n_out = int(mask.sum())
        if n_out > 0:
            outlier_rows.append({
                "column": c, "n_outliers": n_out,
                "pct_outliers": round(n_out / len(s) * 100, 2),
                "lower_bound": lower, "upper_bound": upper, "iqr": iqr
            })
    if outlier_rows:
        pd.DataFrame(outlier_rows).to_csv(OUT_DIR / "05_outliers_iqr.csv", index=False)
        print(" Guardado: 05_outliers_iqr.csv")

    md = []
    md.append("# AED - RAW DATA\n")
    md.append(f"- Archivo: `{input_csv.name}`\n")
    md.append(f"- Filas: **{info['rows']}**, Columnas: **{info['cols']}**\n")
    md.append(f"- Filas duplicadas: **{info['duplicated_rows']}**\n")
    md.append(f"- Celdas con nulos: **{info['missing_total']}**\n")
    md.append("\n## Entregables\n")
    md += [f"- 00_quality_overview.csv",
           f"- 01_column_quality.csv",
           f"- 02_numeric_describe.csv",
           f"- 03_categorical_topN.csv",
           f"- 04_numeric_correlation.csv",
           f"- 05_outliers_iqr.csv",
           f"- Gráficas: `cat_top_*.png`, `num_hist_*.png`, `num_box_*.png`, `num_corr_heatmap.png`"]
    (OUT_DIR / "README_AED.md").write_text("\n".join(md), encoding="utf-8")
    print(" Reporte README_AED.md generado")
    print(f" Carpeta de salida: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    default_csv = DATA_DIR / "ventas_raw_10000.csv"
    parser.add_argument("--input", default=str(default_csv), help="Ruta al CSV crudo")
    args = parser.parse_args()
    run_eda(Path(args.input))
