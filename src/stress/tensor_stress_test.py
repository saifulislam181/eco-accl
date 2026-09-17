import time
import logging
import numpy as np
from src.telemetry.telemetry_extractor import extract_telemetry
from config import DEFAULT_STRESS_DURATION_SEC, DEFAULT_MATRIX_SIZE

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger("Tensor_Stress")

def run_tensor_stress_test(gpu_info, duration_sec=DEFAULT_STRESS_DURATION_SEC, matrix_size=DEFAULT_MATRIX_SIZE):
    """
    Executes a transient GEMM stress workload to measure compute yield and dynamic thermals.
    When CUDA is not available, uses simulated telemetry to represent GPU load behavior.
    """
    start_time = time.time()
    telemetry_samples = []
    
    logger.info(f"Starting NDTSH Stress Test on {gpu_info['name']} for {duration_sec}s...")

    # Check if CUDA is available and GPU is real
    use_cuda = TORCH_AVAILABLE and torch.cuda.is_available() and (not gpu_info.get("is_simulated"))

    if use_cuda:
        device = torch.device(f"cuda:{gpu_info['index']}")
        try:
            total_mem_gb = torch.cuda.get_device_properties(device).total_memory / (1024 ** 3)
            if total_mem_gb < 4.0:
                matrix_size = 2048
            elif total_mem_gb < 8.0:
                matrix_size = 4096

            logger.info(f"Allocating GEMM matrices of size {matrix_size}x{matrix_size} on CUDA...")
            a = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
            b = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
        except Exception as e:
            logger.warning(f"CUDA memory allocation warning ({e}). Lowering matrix size to 1024.")
            matrix_size = 1024
            try:
                a = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
                b = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
            except:
                use_cuda = False
                logger.warning("CUDA allocation failed. Falling back to CPU simulation.")

    if not use_cuda:
        logger.info("CUDA not available. Running CPU fallback with simulated GPU telemetry.")
    
    ops_completed = 0
    while time.time() - start_time < duration_sec:
        if use_cuda:
            for _ in range(5):
                _ = torch.matmul(a, b)
                ops_completed += 1
            torch.cuda.synchronize()
        else:
            # CPU fallback: just do some work to simulate load
            a_cpu = np.random.randn(1024, 1024).astype(np.float32)
            b_cpu = np.random.randn(1024, 1024).astype(np.float32)
            _ = np.matmul(a_cpu, b_cpu)
            ops_completed += 1

        sample = extract_telemetry(gpu_info)
        
        # If we're running in CPU mode but GPU is real, simulate the load effect
        if not use_cuda:
            sample = extract_telemetry(gpu_info)
            sample["is_simulated"] = True
            elapsed = time.time() - start_time
            sample["temperature_c"] = min(80.0, 42.5 + (elapsed * 15.0))
            sample["power_watts"] = min(220.0, 65.0 + (elapsed * 70.0))
            # বাড়তি: বুট ক্লকও সিমুলেট করুন (210 MHz → 1770 MHz)
            sample["boost_clock_mhz"] = int(min(1770, 210 + (elapsed * 500)))

        telemetry_samples.append(sample)
        time.sleep(0.05)

    elapsed_total = time.time() - start_time
    logger.info(f"NDTSH completed. Executed {ops_completed} GEMM ops in {elapsed_total:.3f}s across {len(telemetry_samples)} samples.")
    return telemetry_samples