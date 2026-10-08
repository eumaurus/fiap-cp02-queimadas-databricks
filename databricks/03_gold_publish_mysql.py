# Databricks notebook source
# MAGIC %md
# MAGIC # Camada Gold - armazenamento no MySQL (Azure)
# MAGIC Agrega a Silver e publica 3 tabelas no MySQL Flexible Server:
# MAGIC `gold_focos_estado_dia`, `gold_focos_bioma_dia`, `gold_municipios_criticidade`.
# MAGIC
# MAGIC **ANTES DE RODAR:** preencha `MYSQL_HOST`, `MYSQL_USER` e `MYSQL_PASSWORD` na celula de configuracao abaixo.
# MAGIC Faca isso so no notebook DENTRO do Databricks (nunca no GitHub).

# COMMAND ----------

# ===================== CONFIGURACAO (EDITE AQUI) =====================
MYSQL_HOST = "<COLE_AQUI_O_FQDN>"        # ex.: mysql-queimadas-abc123.mysql.database.azure.com
MYSQL_PORT = "3306"
MYSQL_DB = "queimadas"
MYSQL_USER = "queimadasadmin"
MYSQL_PASSWORD = "<COLE_AQUI_A_SENHA>"   # a mesma da secret MYSQL_ADMIN_PASSWORD do GitHub
# =====================================================================

if "<COLE_AQUI" in MYSQL_HOST or "<COLE_AQUI" in MYSQL_PASSWORD:
    raise ValueError("Preencha MYSQL_HOST e MYSQL_PASSWORD na celula de configuracao antes de rodar.")

# COMMAND ----------

from pyspark.sql.functions import count, avg, max as spark_max

df_silver = spark.table("inpe.silver.queimadas_focos")

gold_estado_dia = (
    df_silver.groupBy("data", "estado")
    .agg(
        count("*").alias("qtd_focos"),
        avg("frp").alias("frp_medio"),
        avg("risco_fogo").alias("risco_medio"),
    )
)

gold_bioma_dia = (
    df_silver.groupBy("data", "bioma")
    .agg(
        count("*").alias("qtd_focos"),
        avg("frp").alias("frp_medio"),
    )
)

gold_municipios_criticidade = (
    df_silver.groupBy("estado", "municipio")
    .agg(
        count("*").alias("qtd_focos"),
        avg("frp").alias("frp_medio"),
        avg("risco_fogo").alias("risco_medio"),
        spark_max("frp").alias("frp_max"),
    )
)

# COMMAND ----------

JDBC_URL = (
    f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    "?useSSL=true&requireSSL=true&rewriteBatchedStatements=true"
)

def grava_mysql(df, tabela):
    """Tenta o conector nativo 'mysql' do Databricks; se nao existir no compute, cai para JDBC."""
    try:
        (
            df.write.format("mysql")
            .option("host", MYSQL_HOST).option("port", MYSQL_PORT)
            .option("database", MYSQL_DB).option("dbtable", tabela)
            .option("user", MYSQL_USER).option("password", MYSQL_PASSWORD)
            .option("useSSL", "true").option("requireSSL", "true")
            .mode("overwrite").save()
        )
        return "conector mysql"
    except Exception as e:
        print(f"[{tabela}] conector nativo falhou ({type(e).__name__}); tentando JDBC...")
        (
            df.write.format("jdbc")
            .option("url", JDBC_URL)
            .option("driver", "com.mysql.cj.jdbc.Driver")
            .option("dbtable", tabela)
            .option("user", MYSQL_USER).option("password", MYSQL_PASSWORD)
            .mode("overwrite").save()
        )
        return "jdbc"

for df_out, nome in [
    (gold_estado_dia, "gold_focos_estado_dia"),
    (gold_bioma_dia, "gold_focos_bioma_dia"),
    (gold_municipios_criticidade, "gold_municipios_criticidade"),
]:
    via = grava_mysql(df_out, nome)
    print(f"OK: {nome} gravada no MySQL via {via}")

# COMMAND ----------

# Conferencia: le de volta do MySQL e mostra a contagem de cada tabela
resultado = []
for nome in ["gold_focos_bioma_dia", "gold_focos_estado_dia", "gold_municipios_criticidade"]:
    try:
        n = (
            spark.read.format("jdbc")
            .option("url", JDBC_URL)
            .option("driver", "com.mysql.cj.jdbc.Driver")
            .option("dbtable", nome)
            .option("user", MYSQL_USER).option("password", MYSQL_PASSWORD)
            .load().count()
        )
    except Exception as e:
        n = f"erro ao conferir: {type(e).__name__}"
    resultado.append((nome, str(n)))

display(spark.createDataFrame(resultado, ["tabela", "qtd_registros"]))
