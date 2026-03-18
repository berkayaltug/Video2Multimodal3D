import os
import datetime
import json
import os
import platform
import shutil
from pathlib import Path

def collect_system_info(output_path="logs/system_info.json"):
    try:
        import psutil
    except Exception:
        psutil = None

    try:
        import torch
    except Exception:
        torch = None

    # GPU bilgileri
    if torch is not None and torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_gpu_memory = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        used_gpu_memory = round(torch.cuda.memory_allocated(0) / (1024**3), 2)
    else:
        gpu_name = "CUDA not available"
        total_gpu_memory = used_gpu_memory = 0

    # CPU ve RAM bilgileri
    cpu_info = platform.processor()
    ram_total = round(psutil.virtual_memory().total / (1024**3), 2) if psutil is not None else None

    # Disk bilgisi
    disk_root = Path.cwd().anchor or str(Path.cwd())
    disk_usage = shutil.disk_usage(disk_root)
    disk_total = round(disk_usage.total / (1024**3), 2)
    disk_free = round(disk_usage.free / (1024**3), 2)
    disk_used_percent = round(disk_usage.used / disk_usage.total * 100, 2)

    # Python, OS, datetime
    python_version = platform.python_version()
    os_info = f"{platform.system()} {platform.release()}"
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # PyTorch bilgisi
    torch_version = torch.__version__ if torch is not None else "unavailable"
    cuda_version = torch.version.cuda if torch is not None and torch.cuda.is_available() else "N/A"

    system_info = {
        "gpu": gpu_name,
        "gpu_memory_total_gb": total_gpu_memory,
        "gpu_memory_used_gb": used_gpu_memory,
        "cuda_version": cuda_version,
        "pytorch_version": torch_version,
        "cpu": cpu_info,
        "ram_total_gb": ram_total,
        "os": os_info,
        "disk_total_gb": disk_total,
        "disk_free_gb": disk_free,
        "disk_used_percent": disk_used_percent,
        "python_version": python_version,
        "start_time": start_time
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(system_info, f, indent=4)

    print(f"[✓] Sistem bilgisi kaydedildi: {output_path}")
    return system_info
