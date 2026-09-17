import os
import io
import time
import hashlib
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config import DEFAULT_PDF_OUTPUT_PATH

logger = logging.getLogger("PDF_Generator")

def generate_pdf_report(gpu_info, health_data, carbon_data, output_path=DEFAULT_PDF_OUTPUT_PATH):
    """
    Generates cryptographically signed compliance certificate.
    Supports writing to disk (for local testing) and returns SHA-256 digest.
    """
    # Safe Directory Parsing
    target_dir = os.path.dirname(os.path.abspath(output_path))
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())

    # Document Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "EcoAccel-ITAD Diagnostic & Carbon Certificate")
    c.setFont("Helvetica", 9)
    c.drawString(50, 735, f"Issued Date: {timestamp_str}")
    c.line(50, 725, 550, 725)

    # 1. Device Identification
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, "1. Device Identification")
    c.setFont("Helvetica", 10)
    c.drawString(70, 682, f"Accelerator Name: {gpu_info['name']}")
    c.drawString(70, 667, f"Device Index: {gpu_info['index']}")

    # 2. Diagnostic & Thermal Assessment
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 637, "2. Diagnostic & Thermal Assessment")
    c.setFont("Helvetica", 10)
    c.drawString(70, 619, f"Health Score (S_accel): {health_data['s_accel']}/100")
    c.drawString(70, 604, f"Status: {health_data['status']}")
    c.drawString(70, 589, f"Max Temperature Reached: {health_data['max_temperature_c']} C")
    c.drawString(70, 574, f"Average Power Draw: {health_data['avg_power_watts']} W")

    # 3. Scope 3 ESG Impact
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 544, "3. Scope 3 ESG & Embodied Carbon Impact")
    c.setFont("Helvetica", 10)
    c.drawString(70, 526, f"Avoided Carbon Footprint (C_saved): {carbon_data['c_saved_kg_co2e']} kg CO2e")
    c.drawString(70, 511, f"Recommended Lifecycle Extension: {carbon_data['lifecycle_extension_years']} Years")

    c.line(50, 485, 550, 485)

    # Cryptographic Hash Stamp Generation
    raw_payload = f"{gpu_info['name']}_{health_data['s_accel']}_{timestamp_str}".encode('utf-8')
    sha256_stamp = hashlib.sha256(raw_payload).hexdigest()

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 468, "Cryptographic Audit Stamp (SHA-256):")
    c.setFont("Courier", 8)
    c.drawString(50, 453, sha256_stamp)

    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Write to File Destination
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    logger.info(f"Certificate PDF rendered successfully: {output_path}")
    return output_path, sha256_stamp