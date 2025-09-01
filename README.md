README – Minería de Datos (Power BI + Python) 

1) DESCRIPCIÓN RÁPIDA
  * Dataset sintético (10k filas) con ruido realista.
  * EDA y preprocesamiento en Python.
  * CSV limpio listo para Power BI.
  * Modelo estrella + OLAP tabular (VertiPaq).
- Dominio simulado: ventas minoristas (Teléfono, Cómputo, Tablet) durante 2023 y 2024 en regiones Norte/Sur/Este/Oeste.

2) ESTRUCTURA MÍNIMA
MineriaDatos/
  data/
    ventas_raw_10000.csv
    ventas_limpias_10000.csv
  scripts/
    aed_raw.py
    preprocesamiento.py
  README.md  (opcional, esta versión en .txt)

3) SETUP
- Recomendado (conda):
    conda env create -f env/mineria_olap.yml
    conda activate mineria_olap

4) USO RÁPIDO
- AED (genera CSVs y gráficas de calidad en eda_raw_output/):
    python scripts/aed_raw.py --input data/ventas_raw_10000.csv

- Preprocesamiento → CSV limpio:
    python scripts/preprocesamiento.py
  Salida: data/ventas_limpias_10000.csv

5) POWER BI (MODELO ESTRELLA BÁSICO)
- Importar data/ventas_limpias_10000.csv como FactSales.
- Crear dimensiones por referencia (quitar duplicados por clave):
    DimDate   = DateKey, Date, Year, Quarter, MonthNumber, MonthName
    DimProduct= ProductKey, Product, Category
    DimRegion = RegionKey, Region
- Relaciones 1:* (filtro Único) desde cada dimensión hacia FactSales.
- Marcar DimDate como "tabla de fechas" y ordenar MonthName por MonthNumber.

6) DAX MÍNIMO
  Total Sales   = SUM ( FactSales[SalesAmount] )
  Total Profit  = SUM ( FactSales[Profit] )
  Profit Margin % = DIVIDE ( [Total Profit], [Total Sales] )

7) DATASET Y RUIDO
- Qué simula: ventas diarias con variación de unidades, descuentos y márgenes por producto/categoría/región.
- Ruido incluido (para practicar calidad de datos):
  * ±2% gaussiano en precios/costos; outliers en Units (se atenúan con winsor p99).
  * 2% regiones inválidas y 1% textos con espacios extra.
  * Nulos en DiscountRate (~5%) y nulos críticos en Product/OrderDate (~1%).
  * 0.5% filas duplicadas.
- El preprocesamiento normaliza, valida regiones, imputa DiscountRate, elimina nulos críticos/duplicados, winsoriza Units, calcula métricas y genera claves/tiempo.

8) RESULTADOS ESPERADOS
- Dataset limpio ≈ 9,951 filas × 19 columnas.
- Visuales mínimos: tarjetas (ventas/utilidad/margen), matriz (Región × Categoría/Producto), línea temporal.