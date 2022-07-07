from hashlib import sha256
import traceback
from aludbms import query
import json,alursa,os
from branching import *
from query2 import query2

import string
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
string.digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'

def ltz_round(num):
    return round(float(num),4)

def num_encode(n):
    if n < 0:
        return SIGN_CHARACTER + num_encode(-n)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0: break
    return ''.join(reversed(s))

def num_decode(s):
    if s[0] == SIGN_CHARACTER:
        return -num_decode(s[1:])
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n

def dict_keyval(dict):
    key_1=str(dict.keys()).replace("'","").replace('"',"")[11:-2]
    return key_1,dict[key_1]

def make_error(msg):
    base="\n"+"#"*(len(msg)+4)+"\n"
    return "*Error*" + base + "| " + msg + " |"+ base


def make_warning(msg):
    base="\n"+"#"*(len(msg)+4)+"\n"
    return "*Warning*" + base + "| " + msg + " |"+ base


def double_quote(msg):
    return str(msg).replace("'",'"')


def pretty_print(a_dict):
    output="{\n"
    for k, d in a_dict.items():
        output+="   "+str(k) + " : "+ str(d)+",\n"
    output+="}"
    return output


def tohex(msg):
    return (msg.encode()).hex()


def utxo_person(key):
    utxs=query2.givedb("inputs")
    for x in utxs:
        if dict_keyval(x)[0]==key:
            return dict_keyval(dict_keyval(x)[1])[0]


def in_any(main_list: list,item):
    for x in main_list:
        if item in x:
            return True
    return False


def array_all_in_one(t_array: list):
    out_arr=[]
    for x in t_array:
        for y in x:
            if y not in out_arr:
                out_arr.append(y)
    return out_arr


def balance(addr):
    longest_branch=get_longest()
    test_longest_branch=array_all_in_one(longest_branch)
    paesa=0
    inputs=query2.givedb("inputs")
    for x in inputs:
        base=dict_keyval(dict_keyval(x)[1])
        if base[0]==addr:
            paesa+=float(base[1])
    return ltz_round(paesa)


def utxos(addr):
    ips=[]
    longest_branch=get_longest()
    test_longest_branch=array_all_in_one(longest_branch)
    import os,json
    path="utxo"
    inputs=query2.givedb("inputs")
    for x in inputs:
        file=dict_keyval(x)[0]
        if dict_keyval(dict_keyval(x)[1])[0]==addr:
            with open(str(f'{path}\\{file}')) as of:
                block_id=json.loads(double_quote(of.read()))["block"]
                if block_id in test_longest_branch:
                    ips.append(file)
    return ips


def key_hash(a,b):
    return sha256(f"{a}.{b}".encode()).hexdigest()


class tx:
    def __init__(self,to,amount,d,e,n) -> None:
        self.to=to
        self.amount=amount
        self.sign=num_encode(int(alursa.signature(sha256((str(address(n))+str(self.to)+str(self.amount)).encode()).hexdigest(),d,n)))
        self.n=num_encode(n)
        self.e=num_encode(e)
    def __repr__(self):
        return str({"sign":self.sign,"n":self.n,"e":self.e,"to":self.to,"amount":self.amount})


class lump:
    def __init__(self,txs: list,inputs: list,msg="") -> None:
        self.txs=txs
        self.inputs=inputs
        self.msg=msg
        self.hash=sha256(str({"txs":self.txs,"inputs":self.inputs,"msg":self.msg}).encode()).hexdigest()
    def __repr__(self):
        return str({"txs":self.txs,"inputs":self.inputs,"msg":self.msg,"hash":self.hash})


def utxo_value(key):
    return ltz_round(query2.get("inputs",key))


def verify_lump(check_lump,total_longest,verbose=False):
    if len(str(check_lump))<=3072 and len(str(json.loads(double_quote(check_lump))["msg"]))<=512:
        pass
    else:
        if verbose:
            print("Lump length longer than 2.5 kilobytes (try sending money in smaller parts).")
        return False
    check_lump=json.loads(double_quote(check_lump))
    if check_lump["hash"]==sha256(str({"txs":check_lump["txs"],"inputs":check_lump["inputs"],"msg":check_lump["msg"]}).encode()).hexdigest():
        jlump=json.loads(double_quote(check_lump))
        input_sender=utxo_person(jlump["inputs"][0])
        e=int(num_decode(jlump["txs"][0]["e"]))
        n=int(num_decode(jlump["txs"][0]["n"]))
        n_sender=address(n)
        all_txs=len(jlump["txs"])
        crt_txs=0
        tap=0
        spenttap=0.0
        for x in jlump["inputs"]:
            block_id=json.loads(open(f"utxo\\{x}").read())["block"]
            if block_id in total_longest:
                tap+=ltz_round(utxo_value(x))
        for x in jlump['txs']:
            if alursa.verify(int(num_decode(x["sign"])),sha256((n_sender+str(x["to"])+str(x["amount"])).encode()).hexdigest(),e,n) and n_sender==input_sender and ltz_round(x["amount"])>0.0:
                spenttap+=ltz_round(x["amount"])
                crt_txs+=1
        if ltz_round(spenttap)==ltz_round(tap) and crt_txs==all_txs:
            return True
        else:
            if verbose:
                print("TX's of this lump are not valid")
            return False
    else:
        if verbose:
            print("Hash Mis-Match")
        return False


def calculate_gas(check_lump,amount):
    check_lump=json.loads(double_quote(check_lump))
    msg=str(check_lump["msg"])
    if len(msg)==0:
        return 0.0
    if amount>=0.01:
        return ltz_round(len(msg)/512)
    else:
        return 0.99


def handle_lump_io(check_lump,block):
    check_lump=json.loads(double_quote(check_lump))
    gas=calculate_gas(check_lump)
    for x in check_lump["inputs"]:
        query.remove("utxo",x)
        query2.remove("inputs",x)
    for x in check_lump["txs"]:
        gassed_amount=ltz_round(ltz_round((100-gas)/100)*ltz_round(x["amount"]))
        query2.append("inputs",sha256(double_quote(str({x["to"]:gassed_amount,"block":block["hash"],"lump":check_lump["hash"]})).encode()).hexdigest(),{x["to"]:gassed_amount})
        query.add("utxo",sha256(double_quote(str({x["to"]:gassed_amount,"block":block["hash"],"lump":check_lump["hash"]})).encode()).hexdigest(),double_quote(str({x["to"]:gassed_amount,"block":block["hash"],"lump":check_lump["hash"]})))


def handle_block_io(block):
    reward=0.1
    block=json.loads(double_quote(block))
    query.add("chain",block["hash"],double_quote(block))
    query2.append("chain",block["hash"],block["prev"])
    utxo={block["miner"]:reward,"block":block["hash"]}
    query.add("utxo",sha256(double_quote(utxo).encode()).hexdigest(),double_quote(utxo))
    query2.append("inputs",sha256(double_quote(utxo).encode()).hexdigest(),{block["miner"]:reward})
    for x in block["txlump"]:
        handle_lump_io(x,block)


def check_all_lumps(trans):
    trans=json.loads(double_quote(trans))
    if len(trans["txlump"])==0:
        return True
    longest_chain=array_all_in_one(get_longest())
    lumps=len(trans["txlump"])
    crt_lumps=0
    for x in trans["txlump"]:
        if verify_lump(x,longest_chain):
            crt_lumps+=1
    if crt_lumps==lumps:
        return True
    else:
        return False


def arrow_msg_gen(title,msg):
    return title + " -> {\n " + msg + "\n}"


def uidgen():
	import string
	import random
	characters = list(string.ascii_letters + string.digits)
	length = 20
	random.shuffle(characters)
	password = []
	for i in range(length):
		password.append(random.choice(characters))
	random.shuffle(password)
	return "".join(password)


def msg_mine(msg):
    nonce=0
    uid=uidgen()
    while sha256(f"{msg} nonce={nonce} uid={uid}".encode()).hexdigest()[0:4]!="0000":
        nonce+=1
    return f"{msg} nonce={nonce} uid={uid}"


def mine(trans,pkey,coinbase: str):
    print(arrow_msg_gen("Miner Thread","Mining Started!"))
    if trans["txlump"]!=[] or trans["txlump"]!="":
        if check_all_lumps(trans):
            trans["coinbase"]=coinbase
            trans["miner"]=pkey
            base={"checksum":sha256(double_quote(trans).encode()).hexdigest(),"nonce":0}
            while sha256(double_quote(base).encode()).hexdigest()[0:5]!="00000":
                base["nonce"]+=1    
            trans["hash"]=sha256(double_quote(base).encode()).hexdigest()
            trans["nonce"]=base["nonce"]
            return trans
        else:
            return False
    else:
        trans["coinbase"]=coinbase
        trans["miner"]=pkey
        base={"checksum":sha256(double_quote(trans).encode()).hexdigest(),"nonce":0}
        while sha256(double_quote(base).encode()).hexdigest()[0:5]!="00000":
            base["nonce"]+=1    
        trans["hash"]=sha256(double_quote(base).encode()).hexdigest()
        trans["nonce"]=base["nonce"]
        return trans


def address(n):
    return sha256(sha256(str(n).encode()).hexdigest().encode()).hexdigest()


def msg_gen(data,uid,type):
    ddata=data.decode()
    out={"data":double_quote(ddata),"uid":str(uid),"type":type}
    return double_quote(out)


def msg_filter(msg,query):
    try:
        message=json.loads(msg)
    except Exception as e:
        print(e)
        return False
    try:
        return message[query]
    except:
        return False


def generate_inputs(n,topay):
    addr=address(n)
    if balance(addr)>=ltz_round(topay):
        allowed_inputs=utxos(addr)
        input_balances=[]
        for x in allowed_inputs:
            y=utxo_value(x)
            input_balances.append(y)
        cc_ib=input_balances.copy()
        input_balances.sort()
        inputs_to_use=[]
        for x in input_balances:
            if x>=ltz_round(topay):
                inputs_to_use.append(allowed_inputs[cc_ib.index(x)])
                break
        if inputs_to_use==[]:
            in_val=0
            using_now=[]
            for x in input_balances:
                if in_val>=ltz_round(topay):
                    print(using_now)
                    break
                else:
                    in_val+=x
                    using_now.append(allowed_inputs[cc_ib.index(x)])
            return using_now
        else:
            return inputs_to_use
    else:
        return False


def workout_lump(topay,whom,d,e,n,msg=""):
    addr=address(n)
    if utxos(addr)==[]:
        return False
    inputs=generate_inputs(n,ltz_round(topay))
    if inputs==False:
        return False
    tap=0
    for x in inputs:
        tap+=ltz_round(utxo_value(x))
    if ltz_round(tap)-ltz_round(topay)==0:
        return lump([tx(whom,ltz_round(topay),d,e,n)],inputs,msg)
    else:
        a=tx(whom,ltz_round(topay),d,e,n)
        b=tx(addr,(ltz_round(tap)-ltz_round(topay)),d,e,n)
        return lump([a,b],inputs,msg)


def tx_base(tx_lump=[]):
    return {"txlump":tx_lump,"prev":get_building_hash(),"contracts":[],"others":[]}


def verify_block(block):
    if len(str(block))<=1048576:
        pass
    else:
        return False
    block=json.loads(double_quote(block))
    if len(block["coinbase"])<=128 and len(block["miner"])<=64:
        pass
    else:
        return False
    if check_all_lumps(block):
        if block["prev"]!=0:
            if os.path.exists(f'chain\\{block["prev"]}'):
                cc_block=block.copy()
                block_hash=cc_block["hash"]
                del cc_block["hash"]
                nonce=cc_block["nonce"]
                del cc_block["nonce"]
                base={"checksum":sha256(double_quote(cc_block).encode()).hexdigest(),"nonce":nonce}
                if sha256(double_quote(base).encode()).hexdigest()==block_hash and block_hash[0:5]=="00000":
                    return True
            else:
                return False
        else:
            cc_block=block.copy()
            block_hash=cc_block["hash"]
            del cc_block["hash"]
            nonce=cc_block["nonce"]
            del cc_block["nonce"]
            base={"checksum":sha256(double_quote(cc_block).encode()).hexdigest(),"nonce":nonce}
            if sha256(double_quote(base).encode()).hexdigest()==block_hash and block_hash[0:5]=="00000":
                return True   
    return False

def msg_check(msg,uids):
    try:
        if sha256(msg.encode()).hexdigest()[0:4]=="0000" and msg.split("uid=")[1] not in uids and len(msg.split(" nonce=")[0])<=128:
            return True
        else:
            return False
    except:
        return False