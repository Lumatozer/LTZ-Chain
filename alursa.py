from hashlib import sha256
def randomkeygen(bits=1024):
    from Crypto.PublicKey import RSA
    keypair = RSA.generate(bits)
    d = keypair.d
    e = keypair.e
    n = keypair.n
    return d,e,n,sha256(str(n).encode()).hexdigest()

def signature(hash,d,n):
    bytedhash = int.from_bytes(bytes.fromhex(hash), byteorder='big')
    signature = pow(bytedhash,d,n)
    return signature

def verify(signature,hash,e,n):
    bytedhash = int.from_bytes(bytes.fromhex(hash), byteorder='big')
    hashFromSignature = pow(signature,int(e),int(n))
    if hashFromSignature==bytedhash:
        return True
    else:
        return False

def load():
    try:
        f=open("den.alukeys")
        a=f.read()
        d=int(a.split(",")[0])
        e=int(a.split(",")[1])
        n=int(a.split(",")[2])
        return d,e,n,sha256(str(n).encode()).hexdigest()
    except:
        newkeyd,newkeye,newkeyn,addr=randomkeygen()
        b=open("den.alukeys",'a')
        out=str(str(newkeyd)+","+str(newkeye)+","+str(newkeyn))
        b.write(out)
        return newkeyd,newkeye,newkeyn,addr
