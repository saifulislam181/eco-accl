import sys
import logging
from src.telemetry.gpu_detection import detect_gpus
from src.telemetry.telemetry_extractor import extract_telemetry
from src.stress.tensor_stress_test import run_tensor_stress_test
from src.scoring.health_scorer import calculate_health_score
from src.carbon.carbon_calculator import calculate_avoided_carbon
from src.reporting.pdf_generator import generate_pdf_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Main_Pipeline")

def run_ecoaccel_pipeline():
    logger.info("=== EcoAccel-ITAD Diagnostic & Carbon Accounting Engine ===")

    try:
        # Step 1: Hardware Detection
        gpus = detect_gpus()
        if not gpus:
            logger.error("No active hardware or simulated target available. Exiting.")
            sys.exit(1)

        target_gpu = gpus[0]
        logger.info(f"[1/5] Target Accelerator: {target_gpu['name']} (Index: {target_gpu['index']})")

        # Step 2: Baseline Telemetry Extraction
        baseline = extract_telemetry(target_gpu)
        logger.info(f"[2/5] Baseline Temp: {baseline['temperature_c']} C | Power: {baseline['power_watts']} W")

        # Step 3: Non-Destructive Tensor Stress Harness (NDTSH)
        stress_samples = run_tensor_stress_test(target_gpu, duration_sec=1.80)
        logger.info(f"[3/5] Stress test complete. Total telemetry samples collected: {len(stress_samples)}")

        # Step 4: Health Scoring & Carbon Calculation
        health_metrics = calculate_health_score(baseline, stress_samples, poh_hours=14000.0)
        carbon_metrics = calculate_avoided_carbon(health_metrics)
        logger.info(f"[4/5] Score S_accel: {health_metrics['s_accel']} | Avoided Carbon: {carbon_metrics['c_saved_kg_co2e']} kg CO2e")

        # Step 5: Certificate PDF Generation
        pdf_path, digest = generate_pdf_report(target_gpu, health_metrics, carbon_metrics)
        logger.info(f"[5/5] Audit Certificate successfully generated at: {pdf_path}")
        logger.info(f"Audit Digest (SHA-256): {digest}")

    except Exception as e:
        logger.critical(f"Unhandled exception during pipeline execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_ecoaccel_pipeline()