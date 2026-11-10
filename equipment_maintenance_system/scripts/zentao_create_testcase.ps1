[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string]$Data,
    [Parameter(Mandatory = $true)] [int]$Product,
    [Parameter(Mandatory = $true)] [string]$Title
)

[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$OutputEncoding = [Text.UTF8Encoding]::new($false)

$zentao = "C:\Users\zhumi\AppData\Local\Programs\nodejs\node_global\zentao.cmd"
if (-not (Test-Path $zentao)) { $zentao = (Get-Command zentao -ErrorAction Stop).Source }

$arguments = @(
    "--format=json",
    "--machine-readable",
    "testcase",
    "create",
    "--productID=$Product",
    "--title=$Title",
    "--data=$Data"
)
$output = & $zentao @arguments 2>&1
$exitCode = $LASTEXITCODE
$output | ForEach-Object { $_.ToString() }
if ($exitCode -ne 0) { exit $exitCode }
