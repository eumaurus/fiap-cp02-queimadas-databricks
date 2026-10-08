-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Setup (rodar UMA vez) - catalogo, schemas e volume
-- MAGIC Cria o catalogo `inpe`, os schemas `bronze`, `silver`, `gold` e o volume `inpe.bronze.arquivo`.
-- MAGIC O caminho do volume fica: `/Volumes/inpe/bronze/arquivo/`

-- COMMAND ----------

CREATE CATALOG IF NOT EXISTS inpe;

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS inpe.bronze;
CREATE SCHEMA IF NOT EXISTS inpe.silver;
CREATE SCHEMA IF NOT EXISTS inpe.gold;

-- COMMAND ----------

CREATE VOLUME IF NOT EXISTS inpe.bronze.arquivo;

-- COMMAND ----------

-- Conferencia: deve listar bronze, silver, gold (+ default/information_schema)
SHOW SCHEMAS IN inpe;

-- COMMAND ----------

-- Conferencia: deve listar o volume 'arquivo'
SHOW VOLUMES IN inpe.bronze;
