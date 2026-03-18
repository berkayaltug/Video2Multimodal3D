# monitor.py
import os
import time
import psutil
import json
import datetime

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

def get_gpu_memory():
    if not NVML_AVAILABLE:
        return None, None
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # GPU 0
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        used = mem_info.used / 1024 / 1024  # MB
        total = mem_info.total / 1024 / 1024
        return used, total
    except:
        return None, None

def monitor_usage(func, *args, frame_id=None, module_name="unnamed", output_dir="logs/module_stats", **kwargs):
    process = psutil.Process(os.getpid())
    ram_before = process.memory_info().rss / 1024 / 1024
    gpu_before, _ = get_gpu_memory()

    start_time = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start_time

    ram_after = process.memory_info().rss / 1024 / 1024
    gpu_after, gpu_total = get_gpu_memory()

    ram_used = round(ram_after - ram_before, 2)
    gpu_used = None
    if gpu_before is not None and gpu_after is not None:
        gpu_used = round(gpu_after - gpu_before, 2)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usage = {
        "frame_id": frame_id,
        "module": module_name,
        "timestamp": timestamp,
        "duration_sec": round(duration, 2),
        "ram_used_mb": ram_used,
        "gpu_used_mb": gpu_used,
        "gpu_freed": gpu_used is not None and gpu_used < 0,
        "ram_before_mb": round(ram_before, 2),
        "ram_after_mb": round(ram_after, 2),
        "gpu_before_mb": round(gpu_before, 2) if gpu_before else None,
        "gpu_after_mb": round(gpu_after, 2) if gpu_after else None,
        "gpu_total_mb": round(gpu_total, 2) if gpu_total else None
    }
    
    # Klasörü oluştur ve JSON olarak kaydet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{frame_id}_{module_name}.json")
    with open(output_path, "w") as f:
        json.dump(usage, f, indent=4)

    print(f"\033[94m[•]\033[0m {module_name} @ {frame_id} → Sistem kullanımı kaydedildi.")
    return result, usage
