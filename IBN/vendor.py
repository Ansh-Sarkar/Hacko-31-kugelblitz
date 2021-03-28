# importing the required libraries
import random
import string
import pytezos.encoding as pe
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from Crypto.PublicKey import RSA

# function for creation a random transaction ID of 64 characters
def create_transaction_id(size = 64):
    x = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])
    return x

# for debug : used in terminal as def for create_transactio_id
def d(size = 64):
    x = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])
    return x

# decodes the public_key from the various layers of encoding 
def public_key_decoder(x):
    b_form = bytes(x,'utf-8')
    pem_public = pe.base58.b58decode(b_form)
    public_key = serialization.load_pem_public_key(
        pem_public,
        backend = default_backend()
    )
    return public_key
    
# used to generate the sha hash of a string
def sha256_hash_string_encoding_based(x):
    message = bytes(x,'utf-8')
    encoded = hashlib.sha256(message)
    return encoded.hexdigest()

# for debug : used as terminal def for function -> sha256_hash_string_encoding_based
def yoyo(x):
    message = bytes(x,'utf-8')
    encoded = hashlib.sha256(message)
    return encoded.hexdigest()

# auxiliary / extra function for implementation of RSA key generation using the PyCryptoDome Library    
def pycrypto_rsa(size = 2048):
    keyPair = RSA.generate(bits = size)
    print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
    print(f"Private key: (n={hex(keyPair.n)}, d={hex(keyPair.d)})")
    
# just a small debug test , prints to the terminal
print(public_key_decoder('8A4MdxHGkuBnV4CY4W3ZgmMTiZkQHi1PdxG4yov65odytYFXkttWy8qojEp5rhNWn9ae3QWigZsfmSVojU62dFbUDR98p74VUdmVA5ZNvtF4LcvjuSSSndGK4nbZrQmJALDH6ZVNS87ZPHeE1yvVcdcwQDfwFwP5RVhsaFcRD5xdwKv5vsE1CNJSZ4S62V1qGN255vKJWUuWbHGy5TbvhBGaBWMDTxKf9GT2rGghyAtx4KEAiS1AvDAN59JAf11EVSeBP6spqusqXAPcVAjrt2vyeYrKEoRJAeHe4EpsjyfS8u7gLnw9XHFAzzWDGywEdwgiQyBRUjbcPJG8rZkuTDbQd36wxo4VMbCKNvTsSppDZWjpJHFo55CayoGRQudXLzoWxGbZyRXQjZ8MnNKQuKcsqgRVWmETDX96ozjNQbuLXcP7u2RToQb6Zih6wbjQz3TQBg5rqswjY2btVCnmxvNdks3o2qMWY9kNurK2AdPQLR7FiwaNiEW52MVFLXNCTCVe8q8ySiinh7mLAdrXKtv6yLe8L3w3JCU3qFtBztvjcXACRHH4njAwesL4TUSS2edLxznXWh6QX5JxMQrRAZjP5C2EzvfN4L5fTgnm'))