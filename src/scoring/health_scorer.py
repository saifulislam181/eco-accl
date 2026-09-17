import math
import logging
from config import (
    WEIGHT_VEC, WEIGHT_FREQ, WEIGHT_TEMP, WEIGHT_COMP,
    ECC_UNCORRECTABLE_THRESHOLD, CRITICAL_TEMP_THRESHOLD_C, ALPHA_THERMAL_DECAY
)

logger = logging.getLogger("Health_Scorer")

def calculate_health_score(baseline_telemetry, stress_samples, poh_hours=14000.0):
    """
    Computes Composite Accelerator Health Index (S_accel) using multi-factor linear formulation.
    When running in CPU-only mode (simulated telemetry), H_c is set to 1.0.
    """
    temps = [s["temperature_c"] for s in stress_samples]
    powers = [s["power_watts"] for s in stress_samples]

    max_temp = max(temps) if temps else baseline_telemetry["temperature_c"]
    avg_power = sum(powers) / len(powers) if powers else baseline_telemetry["power_watts"]
    ecc_errors = baseline_telemetry.get("ecc_uncorrectable", 0)

    # 1. Memory / ECC Integrity (H_v)
    H_v = max(0.0, 1.0 - (ecc_errors / ECC_UNCORRECTABLE_THRESHOLD))

    # 2. Boost Frequency Retention (H_f) - FIXED!
    max_boost = baseline_telemetry.get("max_boost_clock_mhz", 1770)
    # স্ট্রেস টেস্টের সময় সর্বোচ্চ ক্লক খুঁজুন
    observed_boosts = [s.get("boost_clock_mhz", 0) for s in stress_samples]
    max_observed_boost = max(observed_boosts) if observed_boosts else 0
    H_f = min(1.0, max_observed_boost / max_boost) if max_boost > 0 else 1.0

    # 3. Thermal History Degradation (H_t)
    overtemp_duration = sum(0.05 for t in temps if t > CRITICAL_TEMP_THRESHOLD_C)
    H_t = math.exp(-ALPHA_THERMAL_DECAY * (overtemp_duration / max(1.0, poh_hours)))

    # 4. Compute Yield Throughput (H_c)
    is_simulated = any(s.get("is_simulated", False) for s in stress_samples)
    if is_simulated:
        H_c = 1.0
        logger.info("Simulated mode detected. H_c set to 1.0 (neutral).")
    else:
        H_c = 1.0  # placeholder if real measurement later

    # Composite Score (S_accel)
    S_accel = round((WEIGHT_VEC * H_v + WEIGHT_FREQ * H_f + WEIGHT_TEMP * H_t + WEIGHT_COMP * H_c) * 100.0, 2)

    if S_accel >= 90.0:
        status = "EXCELLENT"
    elif S_accel >= 75.0:
        status = "GOOD"
    elif S_accel >= 55.0:
        status = "MAINTENANCE REQUIRED"
    else:
        status = "RECYCLE"

    logger.info(f"Calculated S_accel Breakdown: {{'H_v (ECC)': {H_v}, 'H_f (Boost)': {H_f}, 'H_t (Thermal)': {H_t}, 'H_c (Compute)': {H_c}}} -> Final Score: {S_accel}")

    return {
        "s_accel": S_accel,
        "status": status,
        "max_temperature_c": round(max_temp, 2),
        "avg_power_watts": round(avg_power, 2),
        "ecc_uncorrectable": ecc_errors,
        "poh_hours": poh_hours,
        "factors": {"H_v": H_v, "H_f": H_f, "H_t": H_t, "H_c": H_c}
    }