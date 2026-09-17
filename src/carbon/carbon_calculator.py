import logging
from config import (
    BASE_EMBODIED_CARBON_KG, DEFAULT_REFURB_EFFICIENCY_GAMMA,
    MAX_POH_HOURS, MIN_HEALTH_THRESHOLD_THETA, TARGET_LIFESPAN_EXT_YEARS
)

logger = logging.getLogger("Carbon_Calculator")

def calculate_avoided_carbon(health_data, embodied_base=BASE_EMBODIED_CARBON_KG, refurb_efficiency=DEFAULT_REFURB_EFFICIENCY_GAMMA):
    """
    Calculates Scope 3 Avoided Embodied Carbon (C_saved) and Remaining Service Life (R_life).
    """
    s_accel_norm = health_data["s_accel"] / 100.0
    poh = health_data.get("poh_hours", 14000.0)

    # Remaining Service Life Factor (R_life)
    r_life = max(0.0, 1.0 - (poh / MAX_POH_HOURS))
    extended_years = round(s_accel_norm * TARGET_LIFESPAN_EXT_YEARS, 2)

    if s_accel_norm < MIN_HEALTH_THRESHOLD_THETA:
        c_saved = 0.0
        extended_years = 0.0
        logger.info(f"Health score {s_accel_norm:.2f} below threshold {MIN_HEALTH_THRESHOLD_THETA}. No carbon savings.")
    else:
        # C_saved Calculation
        c_saved = round(embodied_base * s_accel_norm * r_life * refurb_efficiency, 2)
        logger.info(f"C_saved calculated: {embodied_base} * {s_accel_norm:.2f} * {r_life:.2f} * {refurb_efficiency} = {c_saved} kg CO2e")

    return {
        "c_saved_kg_co2e": c_saved,
        "r_life": round(r_life, 2),
        "lifecycle_extension_years": extended_years,
        "embodied_base_kg": embodied_base
    }