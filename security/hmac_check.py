import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

def verify_signature(payload_body, header_signature, secret_token):
    """
    Verifies that the incoming request actually came from GitHub.
    Uses HMAC SHA-256 to sign the payload body with your secret token
    and compares it to the signature provided in the header.
    
    Args:
        payload_body (bytes): The raw body of the POST request.
        header_signature (str): The 'X-Hub-Signature-256' header.
        secret_token (str): Your private webhook secret.
        
    Returns:
        bool: True if authentic, False otherwise.
    """
    if not secret_token:
        logger.error("GITHUB_WEBHOOK_SECRET is not set in environment variables.")
        return False
    
    if not header_signature:
        return False

    # GitHub signature format: "sha256=<hex_digest>"
    try:
        sha_name, signature = header_signature.split('=')
    except ValueError:
        return False
        
    if sha_name != 'sha256':
        return False
    
    # Calculate the HMAC of the payload using the secret
    mac = hmac.new(secret_token.encode(), msg=payload_body, digestmod=hashlib.sha256)
    
    # hmac.compare_digest() is used to prevent timing attacks
    # (a standard string comparison could leak the length of the matching prefix)
    return hmac.compare_digest(mac.hexdigest(), signature)