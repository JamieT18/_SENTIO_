"""
Admin API endpoints for Sentio backend integration
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import os
import datetime

router = APIRouter()

ADMIN_TOKEN = os.environ.get('SENTIO_ADMIN_TOKEN', 'admin-token')

def verify_admin_token(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail='Invalid admin token')

def log_admin_action(token, action, details=None):
    with open('/var/log/sentio_admin_audit.log', 'a') as f:
        f.write(f"{datetime.datetime.now().isoformat()} | token={token} | action={action} | details={details}\n")

@router.post("/admin/run-tests")
def run_performance_tests(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'run-tests')
    # Simulate running pytest and returning results
    result = subprocess.run(["pytest", "sentio/tests/", "--maxfail=5", "--disable-warnings", "--tb=short"], capture_output=True, text=True)
    return JSONResponse({
        "passed": result.returncode == 0,
        "output": result.stdout,
        "errors": result.stderr,
        "exit_code": result.returncode
    })

@router.post("/admin/restart")
def restart_backend(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'restart')
    # Simulate restart (in production, use supervisor/systemd)
    os.system("touch /tmp/sentio_restart_requested")
    return {"status": "Restart requested"}

@router.post("/admin/auto-fix")
def run_auto_fixes(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'auto-fix')
    # Simulate running a fix script
    result = subprocess.run(["python", "tools/validate_code.py"], capture_output=True, text=True)
    return JSONResponse({
        "output": result.stdout,
        "errors": result.stderr,
        "exit_code": result.returncode
    })

@router.get("/admin/logs")
def get_logs(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'get-logs')
    # Simulate fetching logs
    try:
        with open("/var/log/sentio.log") as f:
            logs = f.readlines()[-20:]
    except Exception:
        logs = ["Log file not found or unreadable."]
    return {"logs": logs}

@router.get("/admin/audit-logs")
def get_audit_logs(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'get-audit-logs')
    try:
        with open('/var/log/sentio_admin_audit.log') as f:
            logs = f.readlines()[-50:]
    except Exception:
        logs = ["Audit log file not found or unreadable."]
    return {"audit_logs": logs}

@router.get("/admin/config")
def get_config_endpoint(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'get-config')
    from sentio.core.config import config_manager
    return {"config": config_manager._config}

@router.post("/admin/config")
def update_config_endpoint(payload: dict, x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'update-config', details=str(payload))
    from sentio.core.config import config_manager
    # Validate and update config
    for k, v in payload.items():
        config_manager.set(k, v)
    config_manager.reload()
    return {"status": "Config updated", "config": config_manager._config}

@router.post("/admin/deploy/blue-green")
def blue_green_deploy(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'blue-green-deploy')
    # Simulate blue/green deployment
    result = os.system("bash deploy/blue_green.sh")
    return {"status": "Blue/green deployment triggered", "result": result}

@router.post("/admin/deploy/rollback")
def rollback_deploy(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'rollback-deploy')
    # Simulate rollback
    return {"status": "Rollback triggered"}

@router.post("/admin/backup")
def trigger_backup(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'trigger-backup')
    # Simulate backup
    return {"status": "Backup started"}

@router.post("/admin/restore")
def trigger_restore(x_admin_token: str = Depends(verify_admin_token)):
    log_admin_action(x_admin_token, 'trigger-restore')
    # Simulate restore
    return {"status": "Restore started"}
