import secrets
import sys

def polynomial_eval(coeffs, x, prime):
    result = 0
    for coeff in reversed(coeffs):
        result = (result * x + coeff) % prime
    return result

def generate_shares(secret_int, num_shares, threshold, prime):
    coeffs = [secret_int] + [secrets.randbelow(prime) for _ in range(threshold - 1)]
    shares = []
    for i in range(1, num_shares + 1):
        y = polynomial_eval(coeffs, i, prime)
        shares.append((i, y))
    return shares

if __name__ == "__main__":
    # 256-bit prime for cryptographic modulus
    PRIME = 2**256 - 189
    
    # Generate random 256-bit root decryption key
    secret_key = secrets.randbits(256)
    print(f"ROOT_SECRET_INT: {secret_key}")
    
    # Threshold 3-of-5 split across administrative trustees
    shares = generate_shares(secret_key, num_shares=5, threshold=3, prime=PRIME)
    
    print("DISTRIBUTED TRUSTEE SHARDS:")
    for idx, share in shares:
        print(f"Custodian_{idx}: {share}")
