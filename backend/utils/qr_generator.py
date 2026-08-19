import os
import qrcode
from io import BytesIO
import base64

def generate_qr_code_file(content: str, filename: str) -> str:
    """Generates a QR code image file and returns the relative path URL."""
    output_dir = os.path.join("backend", "static", "qrcodes")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, f"{filename}.png")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#4F46E5", back_color="white")
    img.save(file_path)
    
    return f"/static/qrcodes/{filename}.png"

def generate_qr_code_base64(content: str) -> str:
    """Generates a base64 encoded PNG data URI for direct inline HTML display."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#4F46E5", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
