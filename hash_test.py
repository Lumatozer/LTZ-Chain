from hashlib import sha256
from time import time

def arrow_msg_gen(title,msg):
    return title + " -> {\n " + msg + "\n}"

def make_warning(msg):
    base="\n"+"#"*(len(msg)+4)+"\n"
    return "*Warning*" + base + "| " + msg + " |"+ base

test_time=10
hashes=0
print(make_warning(f"Test Started. Please wait for {test_time} seconds before the test results are shown."))
end=time()+test_time
test='{"checksum":"edbadfbc0339425e3bc08a76c55901b188621c67ca332e65b7b44063f022a467","nonce":9999999'
while time()<=end:
    sha256(test.encode()).hexdigest()
    hashes+=1
print(arrow_msg_gen("Mining Test",f"Your hashrate was {(hashes/test_time)/1000}k hashes per second!"))