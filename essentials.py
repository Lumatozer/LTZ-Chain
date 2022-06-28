from hashlib import sha256
import traceback
from aludbms import query
import json,alursa,os
from branching import *

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
    path="utxo"+"\\"+key
    return (open(path).read().split(":")[0].replace('"',"").replace("{",""))


def in_any(main_list: list,item):
    for x in main_list:
        if item in x:
            return True
    return False


def array_all_in_one(t_array: list):
    out_arr=[]
    for x in t_array:
        for y in x:
            out_arr.append(y)
    return out_arr


def balance(addr):
    longest_branch=get_longest()
    test_longest_branch=array_all_in_one(longest_branch)
    paesa=0
    import os,json
    path="utxo"
    all_files=os.listdir(path)
    for file in all_files:
        block_id=json.loads(open(f"utxo\\{file}").read())["block"]
        with open(str(f'{path}\\{file}')) as of:
            fileread=of.read()
            inputrec=json.loads(fileread)
            if utxo_person(file)==addr and block_id in test_longest_branch:
                paesa+=inputrec[addr]
    return paesa


def utxos(addr):
    ips=[]
    import os,json
    path="utxo"
    for file in os.listdir(path):
        with open(str(f'{path}\\{file}')) as of:
            fileread=of.read()
            if utxo_person(file)==addr:
                ips.append(sha256(fileread.encode()).hexdigest())
            of.close()
    return ips


def key_hash(a,b):
    return sha256(f"{a}.{b}".encode()).hexdigest()


class tx:
    def __init__(self,to,amount,d,e,n) -> None:
        self.to=to
        self.amount=amount
        self.sign=alursa.signature(sha256((str(address(n))+str(self.to)+str(self.amount)).encode()).hexdigest(),d,n)
        self.n=n
        self.e=e
    def __repr__(self):
        return str({"sign":self.sign,"n":self.n,"e":self.e,"to":self.to,"amount":self.amount})


class lump:
    def __init__(self,txs: list,inputs: list) -> None:
        self.txs=txs
        self.inputs=inputs
        self.hash=sha256(str({"txs":self.txs,"inputs":self.inputs}).encode()).hexdigest()
    def __repr__(self):
        return str({"txs":self.txs,"inputs":self.inputs,"hash":self.hash})


def utxo_value(key):
    key="utxo"+"\\"+key
    return int(open(key).read().split(":")[1].split(",")[0].replace(" ",""))


def verify_lump(check_lump):
    if len(str(check_lump))<=9216:
        pass
    else:
        print("False len")
        return False
    longest_branch=get_longest()
    check_lump=json.loads(double_quote(check_lump))
    if check_lump["hash"]==sha256(str({"txs":check_lump["txs"],"inputs":check_lump["inputs"]}).encode()).hexdigest():
        jlump=json.loads(double_quote(check_lump))
        input_sender=utxo_person(jlump["inputs"][0])
        e=jlump["txs"][0]["e"]
        n=jlump["txs"][0]["n"]
        n_sender=address(n)
        all_txs=len(jlump["txs"])
        crt_txs=0
        tap=0
        spenttap=0
        for x in jlump["inputs"]:
            block_id=json.loads(open(f"utxo\\{x}").read())["block"]
            if in_any(longest_branch,block_id):
                tap+=utxo_value(x)
        for x in jlump['txs']:
            copy_x=x.copy()
            del copy_x["sign"]
            if alursa.verify(x["sign"],sha256((n_sender+str(x["to"])+str(x["amount"])).encode()).hexdigest(),e,n) and n_sender==input_sender:
                spenttap+=x["amount"]
                crt_txs+=1
        if spenttap==tap and crt_txs==all_txs:
            return True
        else:
            print("somewhere in txs")
            return False
    else:
        print("somewhere in hashes")
        return False


def handle_lump_io(check_lump,block):
    check_lump=json.loads(double_quote(check_lump))
    for x in check_lump["inputs"]:
        query.remove("utxo",x)
    for x in check_lump["txs"]:
        query.add("utxo",sha256(double_quote(str({x["to"]:x["amount"],"block":block["hash"],"lump":check_lump["hash"]})).encode()).hexdigest(),double_quote(str({x["to"]:x["amount"],"block":block["hash"],"lump":check_lump["hash"]})))


def handle_block_io(block):
    block=json.loads(block)
    query.add("chain",block["hash"],double_quote(block))
    utxo={block["miner"]:50,"block":block["hash"]}
    query.add("utxo",sha256(double_quote(utxo).encode()).hexdigest(),double_quote(utxo))
    for x in block["txlump"]:
        handle_lump_io(x,block)


def check_all_lumps(trans):
    lumps=len(trans["txlump"])
    crt_lumps=0
    for x in trans["txlump"]:
        if verify_lump(x):
            crt_lumps+=1
    if crt_lumps==lumps:
        return True
    else:
        return False


def arrow_msg_gen(title,msg):
    return title + " -> {\n " + msg + "\n}"


def mine_msg(msg):
    nonce=0
    while sha256(f"{msg} nonce={nonce}".encode()).hexdigest()[0:5]!="00000":
        nonce+=1
    return f"{msg} nonce={nonce}"


def check_msg(msg):
    if len(msg)<=128:
        pass
    else:
        return False
    if sha256(str(msg).encode()).hexdigest()[0:5]=="00000":
        return True
    else:
        return False


def mine(trans,pkey,coinbase: str):
    print(arrow_msg_gen("Miner Thread","Mining Started!"))
    trans["coinbase"]=coinbase
    trans["miner"]=pkey
    hashed_trans=sha256(double_quote(trans).encode()).hexdigest()
    trans["nonce"]=0
    new_base={"hash":hashed_trans,"nonce":0}
    if trans["txlump"]!=[] or trans["txlump"]!="":
        if check_all_lumps(trans):
            while sha256(double_quote(new_base).encode()).hexdigest()[0:6]!="000000":
                new_base["nonce"]+=1
            hash=sha256(double_quote(new_base).encode()).hexdigest()
            trans["hash"]=hash
            trans["nonce"]=new_base["nonce"]
            return trans
    else:
        while sha256(double_quote(new_base).encode()).hexdigest()[0:6]!="000000":
            new_base["nonce"]+=1
        hash=sha256(double_quote(new_base).encode()).hexdigest()
        trans["hash"]=hash
        trans["nonce"]=new_base["nonce"]
        return trans


def address(n):
    return sha256(str(n).encode()).hexdigest()


def msg_gen(data,uid,type):
    ddata=data.decode()
    out={"data":double_quote(ddata),"uid":str(uid),"type":type}
    return double_quote(out)


def uidgen():
	import string
	import random
	characters = list(string.ascii_letters + string.digits)
	length = 25
	random.shuffle(characters)
	password = []
	for i in range(length):
		password.append(random.choice(characters))
	random.shuffle(password)
	return "".join(password)


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
    if balance(addr)>=topay:
        allowed_inputs=utxos(addr)
        input_balances=[]
        for x in allowed_inputs:
            y=utxo_value(x)
            input_balances.append(y)
        cc_ib=input_balances.copy()
        input_balances.sort()
        inputs_to_use=[]
        for x in input_balances:
            if x>=topay:
                inputs_to_use.append(allowed_inputs[cc_ib.index(x)])
                break
        if inputs_to_use==[]:
            in_val=0
            using_now=[]
            for x in input_balances:
                if in_val>=topay:
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


def workout_lump(topay,whom,d,e,n):
    addr=address(n)
    if utxos(addr)==[]:
        return False
    inputs=generate_inputs(n,topay)
    if inputs==False:
        return False
    tap=0
    for x in inputs:
        tap+=utxo_value(x)
    if tap-topay==0:
        return lump([tx(whom,topay,d,e,n)],inputs)
    else:
        a=tx(whom,topay,d,e,n)
        b=tx(addr,(tap-topay),d,e,n)
        return lump([a,b],inputs)


def tx_base(tx_lump=[],is_genesis=False):
    from branching import get_building_hash
    if is_genesis:
        return {"txlump":tx_lump,"prev":0}
    else:
        return {"txlump":tx_lump,"prev":get_building_hash()}


def verify_block(block):
    block=double_quote(block)
    if len(str(block))<=102400:
        pass
    else:
        return False
    block=json.loads(block)
    if len(block["coinbase"])<=128:
        pass
    else:
        return False
    if check_all_lumps(block):
        if block["prev"]!=0:
            if os.path.exists(f'chain\\{block["prev"]}'):
                cc_block=block.copy()
                mined_hash=cc_block["hash"]
                del cc_block["hash"]
                del cc_block["nonce"]
                block_hash=sha256(double_quote(cc_block).encode()).hexdigest()
                if sha256(double_quote({"hash":block_hash,"nonce":block["nonce"]}).encode()).hexdigest()==mined_hash and mined_hash[0:6]=="000000":
                    return True
            else:
                return False
        else:
            cc_block=block.copy()
            mined_hash=cc_block["hash"]
            del cc_block["hash"]
            del cc_block["nonce"]
            block_hash=sha256(double_quote(cc_block).encode()).hexdigest()
            if sha256(double_quote({"hash":block_hash,"nonce":block["nonce"]}).encode()).hexdigest()==mined_hash and mined_hash[0:6]=="000000":
                return True   
    return False