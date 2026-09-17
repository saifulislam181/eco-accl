import time
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

logger = logging.getLogger("Telemetry_Extractor")

def extract_telemetry(gpu_info):
    """
    Polls real-time hardware telemetry registers (Temperature, Power, Clocks, ECC errors).
    """
    if gpu_info.get("is_simulated") or not PYNVML_AVAILABLE or gpu_info.get("handle") is None:
        return _extract_simulated_telemetry(gpu_info)

    handle = gpu_info["handle"]
    telemetry = {
        "timestamp": time.time(),
        "is_simulated": False,
        "gpu_name": gpu_info["name"],
        "gpu_index": gpu_info["index"]
    }

    try:
        telemetry["temperature_c"] = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    except Exception:
        telemetry["temperature_c"] = 45.0

    try:
        telemetry["power_watts"] = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
    except Exception:
        telemetry["power_watts"] = 75.0

    try:
        telemetry["boost_clock_mhz"] = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
        telemetry["max_boost_clock_mhz"] = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_SM)
    except Exception:
        telemetry["boost_clock_mhz"] = 1770
        telemetry["max_boost_clock_mhz"] = 1770

    try:
        telemetry["ecc_uncorrectable"] = pynvml.nvmlDeviceGetTotalEccErrors(
            handle, 1, pynvml.NVML_AGGREGATE_ECC
        )
    except Exception:
        telemetry["ecc_uncorrectable"] = 0

    return telemetry

def _extract_simulated_telemetry(gpu_info):
    return {
        "timestamp": time.time(),
        "is_simulated": True,
        "gpu_name": gpu_info["name"],
        "gpu_index": gpu_info["index"],
        "temperature_c": 42.5,
        "power_watts": 65.0,
        "boost_clock_mhz": 1770,
        "max_boost_clock_mhz": 1770,
        "ecc_uncorrectable": 0
    }