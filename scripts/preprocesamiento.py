# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path

# Raíz del repo = carpeta padre de /scripts
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

INPUT_FILE = DATA_DIR / "ventas_raw_10000.csv"
OUTPUT_FILE = DATA_DIR / "ventas_limpias_10000.csv"

def normalize_text(x):
    if pd.isna(x):
        return x
    return str(x).strip().title()

def main():
    print(" Cargando datos desde:", INPUT_FILE.resolve())
    raw = pd.read_csv(INPUT_FILE, encoding="utf-8-sig", parse_dates=["OrderDate"])

    df = raw.copy()
    # Normalizar textos
    df["Product"] = df["Product"].apply(normalize_text)
    df["Region"] = df["Region"].apply(normalize_text)

    # Validar regiones
    valid_regions = {"Norte", "Sur", "Este", "Oeste"}
    df["Region"] = df["Region"].where(df["Region"].isin(valid_regions))

    # Imputar descuentos nulos
    df["DiscountRate"] = df["DiscountRate"].fillna(0.0)

    # Quitar nulos críticos
    before_na = len(df)
    df = df.dropna(subset=["Product", "Region", "OrderDate"])
    after_na = len(df)

    # Quitar duplicados
    before_dups = len(df)
    df = df.drop_duplicates()
    after_dups = len(df)

    # Winsorización al p99
    p99 = int(np.percentile(df["Units"], 99))
    df.loc[df["Units"] > p99, "Units"] = p99

    # Métricas derivadas
    df["SalesAmount"] = (df["Units"] * df["UnitPrice"] * (1 - df["DiscountRate"])).round(2)
    df["CostAmount"] = (df["Units"] * df["UnitCost"]).round(2)
    df["Profit"] = (df["SalesAmount"] - df["CostAmount"]).round(2)

    # Campos de tiempo
    od = pd.to_datetime(df["OrderDate"])
    df["Date"] = od.dt.date
    df["Year"] = od.dt.year
    df["MonthNumber"] = od.dt.month
    month_names = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
                   7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    df["MonthName"] = df["MonthNumber"].map(month_names)
    df["Quarter"] = "Q" + ((df["MonthNumber"] - 1)//3 + 1).astype(str)
    df["DateKey"] = od.dt.strftime("%Y%m%d").astype(int)

    # Claves surrogate
    prod_keys = {p:i for i,p in enumerate(sorted(df["Product"].dropna().unique()), start=1)}
    reg_keys = {r:i for i,r in enumerate(sorted(df["Region"].dropna().unique()), start=10)}
    df["ProductKey"] = df["Product"].map(prod_keys)
    df["RegionKey"] = df["Region"].map(reg_keys)

    # Reordenar columnas
    cols = [
        "OrderID","Date","DateKey","Year","MonthNumber","MonthName","Quarter",
        "Category","ProductKey","Product","RegionKey","Region",
        "Units","UnitPrice","UnitCost","DiscountRate",
        "SalesAmount","CostAmount","Profit"
    ]
    df = df[cols].sort_values(["Year","MonthNumber"]).reset_index(drop=True)

    print(f" Filas antes nulos: {before_na} → después: {after_na}")
    print(f" Filas antes duplicados: {before_dups} → después: {after_dups}")
    print(" Percentil 99 de Units:", p99)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(" Dataset limpio guardado en:", OUTPUT_FILE.resolve())

if __name__ == "__main__":
    main()
