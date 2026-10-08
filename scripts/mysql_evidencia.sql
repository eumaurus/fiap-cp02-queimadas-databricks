-- Rode no Azure Cloud Shell (Bash):
--   mysql -h <FQDN_DO_MYSQL> -u queimadasadmin -p queimadas
-- (se pedir SSL:  mysql -h <FQDN> -u queimadasadmin -p --ssl-mode=REQUIRED queimadas
--  ou, no cliente MariaDB do Cloud Shell:  --ssl )

SELECT 'RM 562503 - checkpoint 02 - Cloud Solutions' AS aluno, NOW() AS data_hora;

SHOW TABLES;

SELECT COUNT(*) FROM gold_focos_bioma_dia;
SELECT COUNT(*) FROM gold_focos_estado_dia;
SELECT COUNT(*) FROM gold_municipios_criticidade;
