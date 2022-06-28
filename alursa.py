from hashlib import sha256
import random
def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b
def findModInverse(a, m):
    if gcd(a, m) != 1:
        return None
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3 
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m
first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
					31, 37, 41, 43, 47, 53, 59, 61, 67,
					71, 73, 79, 83, 89, 97, 101, 103,
					107, 109, 113, 127, 131, 137, 139,
					149, 151, 157, 163, 167, 173, 179,
					181, 191, 193, 197, 199, 211, 223,
					227, 229, 233, 239, 241, 251, 257,
					263, 269, 271, 277, 281, 283, 293,
					307, 311, 313, 317, 331, 337, 347, 349]
def nBitRandom(n):
	return random.randrange(2**(n-1)+1, 2**n - 1)
def getLowLevelPrime(n):
	while True:
		pc = nBitRandom(n)
		for divisor in first_primes_list:
			if pc % divisor == 0 and divisor**2 <= pc:
				break
		else: return pc
def isMillerRabinPassed(mrc):
	maxDivisionsByTwo = 0
	ec = mrc-1
	while ec % 2 == 0:
		ec >>= 1
		maxDivisionsByTwo += 1
	assert(2**maxDivisionsByTwo * ec == mrc-1)
	def trialComposite(round_tester):
		if pow(round_tester, ec, mrc) == 1:
			return False
		for i in range(maxDivisionsByTwo):
			if pow(round_tester, 2**i * ec, mrc) == mrc-1:
				return False
		return True
	numberOfRabinTrials = 20
	for i in range(numberOfRabinTrials):
		round_tester = random.randrange(2, mrc)
		if trialComposite(round_tester):
			return False
	return True
def generate_primes():
	while True:
		n = 1024
		prime_candidate = getLowLevelPrime(n)
		if not isMillerRabinPassed(prime_candidate):
			continue
		else:
			return prime_candidate

def make_kp():
    p=generate_primes()
    q=generate_primes()
    n=p*q
    while True:
        e = random.randrange(2 ** (1024 - 1), 2 ** (1024))
        if gcd(e, (p - 1) * (q - 1)) == 1:
            break
    d=findModInverse(e, (p - 1) * (q - 1))
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
        print("Generating 1024-bit KeyPair for you.\nPlease be patient...")
        newkeyd,newkeye,newkeyn,addr=make_kp()
        print("KeyPair Generated!")
        b=open("den.alukeys",'a')
        out=str(str(newkeyd)+","+str(newkeye)+","+str(newkeyn))
        b.write(out)
        return newkeyd,newkeye,newkeyn,addr