# Databricks notebook source
# MAGIC %md
# MAGIC # Camada Bronze - ingestao "raw"
# MAGIC Le **todos os CSVs** que estao no volume `/Volumes/inpe/bronze/arquivo/` e grava `inpe.bronze.focos_raw`.
# MAGIC Tambem registra uma linha de auditoria por arquivo em `inpe.bronze.auditoria_ingestao`.
# MAGIC
# MAGIC Por que ler a pasta inteira (e nao so o arquivo novo)? O gatilho *file arrival* nao informa qual arquivo chegou.
# MAGIC Reprocessar a pasta toda e sempre sobrescrever as tabelas torna o pipeline **idempotente**: a cada execucao
# MAGIC o resultado reflete exatamente os arquivos que estao no volume, sem duplicar dados.

# COMMAND ----------

from pyspark.sql import functions as F

VOLUME_PATH = "/Volumes/inpe/bronze/arquivo/"

dbutils.widgets.text("input_path", VOLUME_PATH)
input_path = dbutils.widgets.get("input_path").strip() or VOLUME_PATH

# Falha cedo e com mensagem clara se nao houver CSV no volume
arquivos = [f.path for f in dbutils.fs.ls(input_path) if f.name.lower().endswith(".csv")] if input_path.endswith("/") else [input_path]
if not arquivos:
    raise ValueError(f"Nenhum arquivo .csv encontrado em {input_path}")
print(f"{len(arquivos)} arquivo(s) CSV encontrado(s):")
for a in arquivos:
    print(" -", a)

# COMMAND ----------

# Leitura: tudo como string primeiro (robusto a variacoes de cabecalho/formato entre os meses do INPE)
df_in = (
    spark.read
    .option("header", True)
    .option("encoding", "UTF-8")
    .option("pathGlobFilter", "*.csv")
    .csv(input_path)
)

# Padroniza nomes de coluna (minusculo, sem espacos)
df_in = df_in.toDF(*[c.strip().lower().replace(" ", "_") for c in df_in.columns])
print("Colunas encontradas no CSV:", df_in.columns)

esperadas = [
    "id", "lat", "lon", "data_hora_gmt", "satelite", "municipio", "estado", "pais",
    "municipio_id", "estado_id", "pais_id", "numero_dias_sem_chuva",
    "precipitacao", "risco_fogo", "bioma", "frp",
]
# Colunas que nao vieram no arquivo entram como nulas (evita quebrar o job)
for c in esperadas:
    if c not in df_in.columns:
        df_in = df_in.withColumn(c, F.lit(None).cast("string"))

# Se o CSV nao trouxer 'id', gera um id deterministico a partir do proprio registro
df_in = df_in.withColumn(
    "id",
    F.coalesce(
        F.nullif(F.trim(F.col("id")), F.lit("")),
        F.sha2(F.concat_ws("|", "lat", "lon", "data_hora_gmt", "satelite"), 256),
    ),
)

# COMMAND ----------

def num(c, tipo):
    # try_cast devolve NULL em vez de estourar erro (a Serverless usa ANSI mode)
    return F.expr(f"try_cast(trim(`{c}`) as {tipo})").alias(c)

df_bronze = df_in.select(
    F.col("id"),
    num("lat", "double"),
    num("lon", "double"),
    F.expr(
        "coalesce(try_to_timestamp(trim(data_hora_gmt), 'yyyy-MM-dd HH:mm:ss'), try_to_timestamp(trim(data_hora_gmt)))"
    ).alias("data_hora_gmt"),
    F.col("satelite"),
    F.col("municipio"),
    F.col("estado"),
    F.col("pais"),
    num("municipio_id", "bigint"),
    num("estado_id", "bigint"),
    num("pais_id", "bigint"),
    num("numero_dias_sem_chuva", "bigint"),
    num("precipitacao", "double"),
    num("risco_fogo", "double"),
    F.col("bioma"),
    num("frp", "double"),
    F.col("_metadata.file_name").alias("arquivo_origem"),
    F.current_timestamp().alias("data_ingestao"),
)

# COMMAND ----------

(
    df_bronze.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("inpe.bronze.focos_raw")
)

# COMMAND ----------

# Auditoria: uma linha por arquivo, a cada execucao
df_saved = spark.table("inpe.bronze.focos_raw")
auditoria = (
    df_saved.groupBy("arquivo_origem")
    .agg(F.count("*").alias("qtd_registros"))
    .withColumn("caminho_volume", F.lit(input_path))
    .withColumn("data_processamento", F.current_timestamp())
    .withColumn("status", F.lit("sucesso"))
)
auditoria.write.mode("append").option("mergeSchema", "true").saveAsTable("inpe.bronze.auditoria_ingestao")

display(auditoria)
print("Total de registros na Bronze:", df_saved.count())
df_saved.printSchema()
