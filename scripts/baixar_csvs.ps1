# Baixa 3 CSVs mensais do INPE (Windows PowerShell). Salva em .\csv_inpe
# Escolhi meses de 2026 que sao pequenos (5 a 7 MB cada) para o upload ser rapido.
# Qualquer mes da listagem serve: https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/
$base  = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil"
$meses = @("202602", "202603", "202604")

New-Item -ItemType Directory -Force -Path .\csv_inpe | Out-Null
foreach ($m in $meses) {
    $arq = "focos_mensal_br_$m.csv"
    Write-Host "Baixando $arq ..."
    Invoke-WebRequest -Uri "$base/$arq" -OutFile ".\csv_inpe\$arq"
}
Get-ChildItem .\csv_inpe | Select-Object Name, @{n="MB";e={[math]::Round($_.Length/1MB,2)}}
