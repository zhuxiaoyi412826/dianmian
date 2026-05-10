
"""生成自签名SSL证书"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime
import os

# 确保目录存在
os.makedirs('certs', exist_ok=True)

# 生成私钥
private_key = rsa.generate_private_key(
    public_exponent=65537, 
    key_size=4096, 
    backend=default_backend()
)

# 生成证书
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "InterviewAI"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

cert = x509.CertificateBuilder().subject_name(subject)\
    .issuer_name(issuer)\
    .public_key(private_key.public_key())\
    .serial_number(x509.random_serial_number())\
    .not_valid_before(datetime.datetime.utcnow())\
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))\
    .sign(private_key, hashes.SHA256(), default_backend())

# 保存私钥
key_path = os.path.join('certs', 'server.key')
with open(key_path, "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

# 保存证书
cert_path = os.path.join('certs', 'server.crt')
with open(cert_path, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print(f"✅ 证书生成成功！")
print(f"   私钥: {os.path.abspath(key_path)}")
print(f"   证书: {os.path.abspath(cert_path)}")
