# Databricks notebook source
# MAGIC %md
# MAGIC # Camada Silver - limpeza e qualidade de dados
# MAGIC Le `inpe.bronze.focos_raw`, remove duplicados, corrige acentuacao quebrada, cria colunas derivadas
# MAGIC e grava `inpe.silver.queimadas_focos` (sobrescrevendo, para ser idempotente).

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.functions import col, trim, to_date, year, month, dayofmonth, when, count

df_raw = spark.table("inpe.bronze.focos_raw")

# COMMAND ----------

# Correcao de acentos "quebrados" (UTF-8 lido como Latin-1) que aparecem em alguns CSVs do INPE.
# Se os dados ja vierem corretos, estas trocas simplesmente nao fazem nada.
SUBSTITUICOES = [
    ("Ã\u0083", "Ã"), ("Ãƒ", "Ã"), ("Ã‰", "É"), ("Ã‡", "Ç"), ("Ã“", "Ó"), ("Ãš", "Ú"), ("Ã•", "Õ"),
    ("Ã¡", "á"), ("Ã¢", "â"), ("Ã£", "ã"), ("Ã©", "é"), ("Ãª", "ê"), ("Ã­", "í"),
    ("Ã³", "ó"), ("Ã´", "ô"), ("Ãµ", "õ"), ("Ãº", "ú"), ("Ã§", "ç"),
]

def corrige_texto(c):
    expr = trim(col(c))
    for errado, certo in SUBSTITUICOES:
        expr = F.regexp_replace(expr, F.lit(errado), F.lit(certo))
    return expr

df_silver = (
    df_raw
    .withColumn("id", trim(col("id")))
    .dropDuplicates(["id"])
    .withColumn("estado", corrige_texto("estado"))
    .withColumn("municipio", corrige_texto("municipio"))
    .withColumn("bioma", corrige_texto("bioma"))
    # casos especificos do material da aula
    .withColumn("estado", F.regexp_replace("estado", "^PARÃ$", "PARÁ"))
    .withColumn("municipio", F.regexp_replace("municipio", "^LÃBREA$", "LÁBREA"))
    .withColumn("municipio", F.regexp_replace("municipio", "^PATROCÃNIO$", "PATROCÍNIO"))
    .withColumn("data", to_date(col("data_hora_gmt")))
    .withColumn("ano", year(col("data_hora_gmt")))
    .withColumn("mes", month(col("data_hora_gmt")))
    .withColumn("dia", dayofmonth(col("data_hora_gmt")))
    .withColumn(
        "criticidade",
        when((col("risco_fogo") >= 0.8) & (col("frp") >= 100), "alta")
        .when((col("risco_fogo") >= 0.5) & (col("frp") >= 50), "media")
        .otherwise("baixa"),
    )
    .withColumn(
        "classe_risco",
        when(col("risco_fogo") >= 0.8, "ALTO")
        .when(col("risco_fogo") >= 0.4, "MEDIO")
        .otherwise("BAIXO"),
    )
    .withColumn("data_ref", to_date("data_hora_gmt"))
    .filter(col("lat").isNotNull() & col("lon").isNotNull())
)

# COMMAND ----------

(
    df_silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("inpe.silver.queimadas_focos")
)

# COMMAND ----------

# Relatorio de qualidade (sobre a tabela ja gravada)
df_s = spark.table("inpe.silver.queimadas_focos")
df_quality = df_s.select(
    count("*").alias("total_registros"),
    count(when(col("id").isNull(), 1)).alias("id_nulo"),
    count(when(col("data_hora_gmt").isNull(), 1)).alias("data_nula"),
    count(when((col("lat") < -90) | (col("lat") > 90), 1)).alias("lat_invalida"),
    count(when((col("lon") < -180) | (col("lon") > 180), 1)).alias("lon_invalida"),
    count(when(col("frp") < 0, 1)).alias("frp_invalido"),
)
display(df_quality)
