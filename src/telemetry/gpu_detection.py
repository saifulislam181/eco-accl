import logging

# Try to import nvidia-ml-py (newer) or pynvml (older, deprecated)
try:
    import nvidia_ml_py as pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    try:
        import pynvml
        PYNVML_AVAILABLE = True
    except ImportError:
        PYNVML_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GPU_Detection")

def detect_gpus():
    """
    Detects physical NVIDIA GPUs via NVML. 
    Falls back gracefully to simulated accelerator mode if NVML fails or 0 devices found.
    """
    if not PYNVML_AVAILABLE:
        logger.warning("NVML module not found. Falling back to Simulated Mode.")
        return _get_simulated_gpu()

    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()

        if device_count == 0:
            logger.warning("No physical GPUs detected by NVML. Falling back to Simulated Mode.")
            return _get_simulated_gpu()

        devices = []
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            devices.append({
                "index": i,
                "name": name,
                "handle": handle,
                "is_simulated": False
            })
        logger.info(f"Successfully detected {len(devices)} physical accelerator(s).")
        return devices

    except Exception as e:
        logger.warning(f"NVML Initialization failed ({e}). Falling back to Simulated Mode.")
        return _get_simulated_gpu()

def _get_simulated_gpu():
    return [{
        "index": 0,
        "name": "Simulated Accelerator (NVIDIA RTX Enterprise Class)",
        "handle": None,
        "is_simulated": True
    }]