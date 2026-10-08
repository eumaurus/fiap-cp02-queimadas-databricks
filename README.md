# Checkpoint 02 - Cloud Solutions & Scalable Infrastructure (FIAP)

Pipeline Medallion no Databricks (Bronze -> Silver -> Gold) com dados de queimadas do INPE,
publicando a camada Gold em um MySQL Flexible Server na Azure (provisionado com Terraform + GitHub Actions).

```
.github/workflows/terraform-apply.yml   workflow que cria o MySQL (manual: Run workflow)
infra/                                  Terraform (RG + MySQL Flexible Server + banco + firewall)
databricks/00_setup_catalog_volume.sql  cria catalogo inpe, schemas e volume 'arquivo'
databricks/01_bronze_csv_ingest.py      Bronze: CSVs do volume -> inpe.bronze.focos_raw (+ auditoria)
databricks/02_silver_standardize_quality.py  Silver: limpeza -> inpe.silver.queimadas_focos
databricks/03_gold_publish_mysql.py     Gold: 3 tabelas agregadas -> MySQL
databricks/job_queimadasINPE.json       definicao do job (opcional, via CLI/API)
scripts/                                download dos CSVs e comandos de evidencia
```

Secrets do GitHub: `AZURE_CREDENTIALS`, `MYSQL_ADMIN_PASSWORD`.
Base: https://github.com/rksakai/QueimadasINPE-Databricks (adaptado).
