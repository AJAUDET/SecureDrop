# Author : AJ Audet  
# Purpose : generate a public/private key pair and store them in a json string in a .txt file

import sys
import json
from Crypto.PublicKey import RSA

# need to encrypt the keys, unsecured storing as plaintext for both public and private keys
def generateKeys(pub, priv):
    priv_key = RSA.generate(2048)
    pub_key = priv_key.public_key()
    
    try: 
        with open(pub, 'x') as pubF:
            data = {"Public key": pub_key.exportKey().decode("utf-8")}
            print(json.dumps(data, separators=(',', ':')), file=pubF)
    except:
        with open(pub, 'a+') as pubF:
                data = {"Public key": pub_key.export_key().decode("utf-8")}
                print(json.dumps(data, separators=(',', ':')), file=pubF)
    try:
        with open(priv, 'x') as privF:
            data = {"Private Key": priv_key.export_key().decode("utf-8")}
            print(json.dumps(data, separators=(',', ':')), file=privF)
    except:
        with open(priv, 'a+') as privF:
            data = {"Private Key": priv_key.export_key().decode("utf-8")}
            print(json.dumps(data, separators=(',', ':')), file=privF)

if __name__ == '__main__':
    if (len(sys.argv) != 4):
        print(f"Usage:")
        print(f"\tpython3 keygen.py --generate <outfile_pubKey> <outfile_privFile>")
        sys.exit(1)

    mode = sys.argv[1]
    pubFile = sys.argv[2]
    privFile = sys.argv[3]
    
    if mode == '--generate':
        generateKeys(pubFile, privFile)
    else:
        print(f"Improper Usage")