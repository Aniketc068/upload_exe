from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import Name, CertificateBuilder, NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import datetime
import OpenSSL
from cryptography.x509 import SubjectAlternativeName, DNSName
import os

# Define details for the certificate
subject = "CN=Managex (INDIA) Limited"
issuer = "CN=Managex (INDIA) Limited"
valid_from = datetime.datetime.now(datetime.timezone.utc)  # Use UTC aware datetime
valid_until = valid_from + datetime.timedelta(days=365*10)  # 10 years validity
password = "Managex@2024"
domain = "www.managexindia.in"

# Step 1: Generate RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Step 2: Create the certificate
from cryptography.x509 import NameAttribute

subject_name = Name([
    NameAttribute(NameOID.COUNTRY_NAME, "IN"),
    NameAttribute(NameOID.ORGANIZATION_NAME, "Managex (INDIA) Limited"),
    NameAttribute(NameOID.COMMON_NAME, "Managex (INDIA) Limited")
])

issuer_name = subject_name  # Self-signed certificate

builder = CertificateBuilder(
    subject_name=subject_name,
    issuer_name=issuer_name,
    public_key=private_key.public_key(),
    serial_number=1000,
    not_valid_before=valid_from,
    not_valid_after=valid_until
)

# Step 3: Add SAN (Subject Alternative Name) extension
san = SubjectAlternativeName([DNSName(domain)])
builder = builder.add_extension(san, critical=False)

# Sign the certificate with the private key
certificate = builder.sign(
    private_key=private_key,
    algorithm=hashes.SHA256(),
    backend=default_backend()
)

# Step 4: Export the private key (in PEM format) and certificate (in PEM format)
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

certificate_pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)

# Save private key and certificate
with open("Managex_India_PrivateKey.pem", "wb") as f:
    f.write(private_key_pem)

with open("Managex_India_Certificate.pem", "wb") as f:
    f.write(certificate_pem)

print("Private key and certificate in PEM format generated.")

# Step 5: Convert to PFX format using OpenSSL
# Save the PEM certificate and key to a .pfx file
# Run the OpenSSL command inside Python to generate PFX file
import subprocess

pfx_filename = "Managex_India_Certificate.pfx"
command = [
    "openssl", "pkcs12", "-export",
    "-out", pfx_filename,
    "-inkey", "Managex_India_PrivateKey.pem",
    "-in", "Managex_India_Certificate.pem",
    "-password", "pass:{}".format(password)  # Use the password to protect the PFX file
]

# Execute the OpenSSL command to generate PFX
subprocess.run(command)

print("PFX file generated successfully.")
