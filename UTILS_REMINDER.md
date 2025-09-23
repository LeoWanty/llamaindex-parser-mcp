# Reminder for utils scripts and commands

## Console

### Last logs in .log file

*For Windows* :
```bash
Get-Content -Path ".\src\mcp_llamaindex\STATIC\dev_server.log" -Wait -Tail 20 | ForEach-Object { 
    switch -Regex ($_) {
        "ERROR" { Write-Host $_ -ForegroundColor Red }
        "WARN" { Write-Host $_ -ForegroundColor Yellow }
        "INFO" { Write-Host $_ -ForegroundColor Cyan }
        "DEBUG" { Write-Host $_ -ForegroundColor Gray }
        default { Write-Host $_ }
    }
}
```

## Jupyter notebook