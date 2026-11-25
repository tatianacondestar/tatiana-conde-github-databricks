# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # S11 — IPD: 3 Predicciones a Futuro con Genie Agents (AI)
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
# MAGIC
# MAGIC Tabla: `ggrrr.s11_ipd.deportistas_s3`
# MAGIC Archivo fuente: `ipd_deportistas_real.csv`
# MAGIC
# MAGIC > **Nota:** Las predicciones a futuro NO son consultas SQL directas.
# MAGIC > Se generan a partir de tendencias y patrones en la data histórica (2019-2024),
# MAGIC > utilizando Python + Pandas + análisis estadístico sobre los datos de Databricks.
# MAGIC > Las capturas de evidencia del Genie Agent se adjuntan en el documento del entregable.

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG ggrrr;
# MAGIC USE SCHEMA s11_ipd;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## PREDICCIÓN 1 — Federaciones con mayor probabilidad de éxito en 2025
# MAGIC
# MAGIC **Pregunta a Genie Agent:**
# MAGIC *"Basándote en los resultados históricos 2019-2024, ¿qué federaciones tienen mayor tendencia de mejora y podrían obtener más medallas en 2025?"*
# MAGIC
# MAGIC **Descripción:**
# MAGIC Se analiza la evolución del puesto promedio por federación año a año.
# MAGIC Una federación con tendencia de puesto promedio **decreciente** (mejora) indica mayor probabilidad de éxito.
# MAGIC Se calcula la **pendiente de regresión lineal** del puesto promedio para proyectar 2025.

# COMMAND ----------

import pandas as pd
import numpy as np
from pyspark.sql import functions as F

# Cargar datos desde la tabla Delta
df_spark = spark.table("ggrrr.s11_ipd.deportistas_s3")
df = df_spark.toPandas()

# Puesto promedio por federación y año
tendencia = (
    df.groupby(["federacion", "anio"])["puesto"]
    .mean()
    .reset_index()
    .rename(columns={"puesto": "puesto_promedio"})
)

# Calcular pendiente por federación (regresión lineal simple)
resultados = []
for fed, grupo in tendencia.groupby("federacion"):
    if len(grupo) >= 3:  # mínimo 3 años de datos
        x = grupo["anio"].values
        y = grupo["puesto_promedio"].values
        pendiente = np.polyfit(x, y, 1)[0]  # pendiente negativa = mejora
        puesto_2025 = np.polyfit(x, y, 1)[0] * 2025 + np.polyfit(x, y, 1)[1]
        total_eventos = df[df["federacion"] == fed].shape[0]
        resultados.append({
            "federacion": fed,
            "pendiente": round(pendiente, 4),
            "puesto_estimado_2025": round(puesto_2025, 2),
            "total_eventos_historicos": total_eventos,
            "tendencia": "MEJORA ↑" if pendiente < 0 else "DECAE ↓"
        })

df_pred1 = pd.DataFrame(resultados).sort_values("pendiente")
print("=== PREDICCIÓN 1: Federaciones con mayor probabilidad de éxito en 2025 ===")
print(df_pred1.to_string(index=False))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado:
# MAGIC Las federaciones con **pendiente negativa** (ej. -0.15 a -0.40) son las que tienen
# MAGIC mayor probabilidad de conseguir mejores puestos en 2025.
# MAGIC
# MAGIC **Ejemplo de interpretación:**
# MAGIC - Federación Peruana de Atletismo: pendiente -0.28 → estimado puesto 2.1 en 2025 → **candidata a medalla de oro**
# MAGIC - Federación Peruana de Natación: pendiente -0.15 → mejora moderada → **candidata a podio**
# MAGIC
# MAGIC > 📸 *Adjuntar captura del Genie Agent con esta predicción en el entregable*

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## PREDICCIÓN 2 — Tendencia de inversión PAD 2025-2026
# MAGIC
# MAGIC **Pregunta a Genie Agent:**
# MAGIC *"¿Cómo ha evolucionado la inversión del PAD (apoyo económico) por año? ¿Cuánto se estima que será la inversión en 2025 y 2026?"*
# MAGIC
# MAGIC **Descripción:**
# MAGIC Se analiza el **monto PAD total por año** de 2019 a 2024.
# MAGIC Usando regresión lineal se proyecta la inversión esperada para 2025 y 2026.
# MAGIC Esto permite estimar el presupuesto necesario para mantener o mejorar resultados.

# COMMAND ----------

# Inversión PAD total por año
inversion_anual = (
    df.groupby("anio")["monto_pad"]
    .sum()
    .reset_index()
    .rename(columns={"monto_pad": "inversion_total"})
    .sort_values("anio")
)

print("=== Inversión PAD histórica por año ===")
print(inversion_anual.to_string(index=False))

# Regresión lineal para proyectar 2025 y 2026
x = inversion_anual["anio"].values
y = inversion_anual["inversion_total"].values
coef = np.polyfit(x, y, 1)

inversion_2025 = coef[0] * 2025 + coef[1]
inversion_2026 = coef[0] * 2026 + coef[1]

print(f"\n=== PREDICCIÓN 2: Estimación de inversión PAD ===")
print(f"Inversión estimada 2025: S/ {inversion_2025:,.2f}")
print(f"Inversión estimada 2026: S/ {inversion_2026:,.2f}")
print(f"Incremento anual proyectado: S/ {coef[0]:,.2f} por año")

if coef[0] > 0:
    print("✅ Tendencia CRECIENTE: el IPD está incrementando su inversión — señal positiva")
else:
    print("⚠️ Tendencia DECRECIENTE: el presupuesto PAD está bajando — riesgo de menor rendimiento")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado:
# MAGIC Si la tendencia es creciente, se proyecta que para **2025 la inversión PAD supere el máximo histórico**.
# MAGIC Esto correlaciona con más deportistas apoyados y potencialmente mejores resultados
# MAGIC en competencias internacionales.
# MAGIC
# MAGIC **Implicancia:** Una mayor inversión PAD históricamente se asocia a mejores puestos
# MAGIC (correlación negativa entre monto_pad alto y puesto alto).
# MAGIC
# MAGIC > 📸 *Adjuntar captura del Genie Agent con esta predicción en el entregable*

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## PREDICCIÓN 3 — Departamentos con mayor riesgo de perder representación
# MAGIC
# MAGIC **Pregunta a Genie Agent:**
# MAGIC *"¿Qué departamentos han disminuido su participación en eventos internacionales en los últimos años? ¿Cuáles corren riesgo de desaparecer del deporte internacional peruano en 2025?"*
# MAGIC
# MAGIC **Descripción:**
# MAGIC Se analiza la **evolución de participaciones por departamento** año a año.
# MAGIC Departamentos con tendencia decreciente en número de deportistas representados
# MAGIC tienen mayor riesgo de **perder presencia internacional**.
# MAGIC Esto es clave para que el IPD redistribuya recursos y apoyo.

# COMMAND ----------

# Participaciones por departamento y año
participacion_dept = (
    df.groupby(["departamento", "anio"])
    .size()
    .reset_index(name="participaciones")
)

# Calcular tendencia por departamento
riesgo = []
for dept, grupo in participacion_dept.groupby("departamento"):
    if len(grupo) >= 3:
        x = grupo["anio"].values
        y = grupo["participaciones"].values
        pendiente = np.polyfit(x, y, 1)[0]
        participaciones_2025 = np.polyfit(x, y, 1)[0] * 2025 + np.polyfit(x, y, 1)[1]
        total_hist = df[df["departamento"] == dept].shape[0]
        riesgo.append({
            "departamento": dept,
            "pendiente": round(pendiente, 3),
            "participaciones_estimadas_2025": max(0, round(participaciones_2025, 1)),
            "total_historico": total_hist,
            "riesgo": "🔴 ALTO" if pendiente < -0.3 else ("🟡 MEDIO" if pendiente < 0 else "🟢 BAJO")
        })

df_pred3 = pd.DataFrame(riesgo).sort_values("pendiente")

print("=== PREDICCIÓN 3: Riesgo de pérdida de representación por departamento ===")
print(df_pred3.to_string(index=False))

alto_riesgo = df_pred3[df_pred3["riesgo"] == "🔴 ALTO"]
print(f"\n⚠️ Departamentos en RIESGO ALTO ({len(alto_riesgo)}):")
for _, row in alto_riesgo.iterrows():
    print(f"  → {row['departamento']}: estimado {row['participaciones_estimadas_2025']} participaciones en 2025")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado:
# MAGIC Departamentos periféricos como **Puno, Madre de Dios, Tumbes** o similares
# MAGIC podrían mostrar tendencia decreciente en participaciones internacionales.
# MAGIC
# MAGIC **Recomendación para el IPD:**
# MAGIC - Priorizar apoyo PAD en departamentos con riesgo alto
# MAGIC - Crear programas de captación de talentos en regiones subrepresentadas
# MAGIC - Revisar si la reducción de apoyo económico coincide con la baja de participaciones
# MAGIC
# MAGIC > 📸 *Adjuntar captura del Genie Agent con esta predicción en el entregable*

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Resumen — 3 Predicciones a Futuro
# MAGIC
# MAGIC | # | Predicción | Método | Horizonte |
# MAGIC |---|---|---|---|
# MAGIC | 1 | **Federaciones con mayor éxito en 2025** | Regresión lineal sobre puesto promedio | 2025 |
# MAGIC | 2 | **Tendencia de inversión PAD 2025-2026** | Regresión lineal sobre monto total anual | 2025-2026 |
# MAGIC | 3 | **Departamentos en riesgo de perder representación** | Regresión lineal sobre participaciones anuales | 2025 |
# MAGIC
# MAGIC ### Pregunta Genie Agent que genera cada predicción:
# MAGIC - **P1:** *"¿Qué federaciones tienen mejor tendencia de resultados y podrían ganar más en 2025?"*
# MAGIC - **P2:** *"¿Cómo va a crecer la inversión PAD del IPD en los próximos años?"*
# MAGIC - **P3:** *"¿Qué departamentos están perdiendo deportistas en competencias internacionales?"*
# MAGIC
# MAGIC > **Importante:** Estas predicciones se basan en tendencias históricas lineales.
# MAGIC > El rendimiento real puede variar por factores externos (pandemias, cambios de entrenadores,
# MAGIC > lesiones, presupuesto gubernamental, etc.)