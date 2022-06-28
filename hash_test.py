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
test=b'{"hash":c791eabd1c48cd429a3f230662735dd97dfee2fdcce66c20d937191958c36239,"nonce":99999999'
while time()<=end:
    sha256(test)
    hashes+=1
print(arrow_msg_gen("Mining Test",f"Your hashrate was {(hashes/test_time)/1000000} million hashes per second!"))