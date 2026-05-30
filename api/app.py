from fastapi import FastAPI
import psutil
import platform
from datetime import datetime

app = FastAPI()

def get_size(bytes):
    for unit in ["", "K", "M", "G", "T"]:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

@app.get("/status")
def get_status():
    # Собираем данные
    virtual_mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.now() - boot_time).split('.')[0]

    return {
        "system": platform.system(),
        "release": platform.release(),
        "uptime": uptime,
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "cpu_count": psutil.cpu_count(),
        "ram": {
            "used": get_size(virtual_mem.used),
            "total": get_size(virtual_mem.total),
            "percent": virtual_mem.percent
        },
        "disk": {
            "used": get_size(disk.used),
            "total": get_size(disk.total),
            "percent": disk.percent
        }
    }
