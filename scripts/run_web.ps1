$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

.venv\Scripts\uvicorn.exe app.web.app_factory:create_web_app --factory --host 127.0.0.1 --port 8000 --reload
