
#  Exploración y Preprocesamiento de Datos

## 1. Análisis Exploratorio (AED) del Dataset RAW

A partir de la **primera exploración** (`ventas_raw_10000.csv`) obtuvimos lo siguiente:

- Filas: 10066
- Columnas: 9
- Filas duplicadas: 65
- Celdas con valores nulos: 100

### Calidad por columna
Se detectaron nulos en:
- `Product`: ~0.25% de los registros
- `Region`: ~0.25% de los registros
- `DiscountRate`: ~0.5% de los registros

### Outliers
- En la columna **Units** se detectaron valores extremos superiores a 500, claramente outliers.
- En `UnitPrice` y `UnitCost` también se observaron valores muy alejados del rango intercuartílico.

### Conclusión AED
El dataset crudo contiene **duplicados, nulos, inconsistencias de texto y outliers**.  
Con esta información se definió la estrategia de **preprocesamiento**.

---

## 2. Configuración del Código de Preprocesamiento

A partir de lo identificado en el AED, el script de limpieza (`preprocesamiento.py`) aplica las siguientes transformaciones:

1. **Limpieza de datos**
   - Elimina nulos en columnas críticas (`Product`, `Region`, `OrderDate`).
   - Imputa valores faltantes en `DiscountRate` con 0.0 (sin descuento).
   - Elimina filas duplicadas.

2. **Normalización**
   - Quita espacios y estandariza mayúsculas/minúsculas (`Product`, `Region`).
   - Valida que `Region` pertenezca a: Norte, Sur, Este, Oeste.

3. **Tratamiento de outliers**
   - Winsoriza `Units` al percentil 99 para controlar pedidos atípicamente grandes.

4. **Transformaciones y métricas derivadas**
   - `SalesAmount` = Units × UnitPrice × (1 − DiscountRate).
   - `CostAmount` = Units × UnitCost.
   - `Profit` = SalesAmount − CostAmount.

5. **Enriquecimiento temporal**
   - Extrae `Year`, `MonthNumber`, `MonthName`, `Quarter` y `DateKey` de `OrderDate`.

6. **Claves surrogate**
   - `ProductKey` y `RegionKey` generados para separar dimensiones.

7. **Exportación**
   - Se guarda `ventas_limpias_10000.csv`, con columnas organizadas en orden lógico para construir un **esquema estrella** en Power BI.

---

## 3. Resultado Final

- Filas limpias finales: 9951
- Columnas en el dataset limpio: 18
- El dataset ahora está **listo para análisis en Power BI**, donde se construirá el esquema estrella y VertiPaq generará el cubo OLAP tabular.

---

## 4. Conclusión General

La práctica demuestra cómo:
1. Con un **AED inicial** se identifican problemas de calidad.
2. A partir de esos hallazgos, se configura un **pipeline de preprocesamiento** en Python.
3. El dataset resultante se convierte en la **base del esquema estrella** que Power BI transforma en un **cubo OLAP tabular** mediante VertiPaq.