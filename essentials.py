from ast import arg
from hashlib import sha256
import traceback
from aludbms import query
import json,alursa,os,time,datetime
from branching import *
from query2 import query2


import string
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
string.digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'

def is_digit(check_str):
    try:
        float(check_str)
        return True
    except:
        return False

def arr_double_opp(chain: list):
    chain.reverse()
    new_chain=[]
    for x in chain:
        x.reverse()
        new_chain.append(x)
    return new_chain


def ltz_round(num):
    return round(float(num),8)


def unix_time():
    ms = datetime.datetime.now()
    return int(time.mktime(ms.timetuple()))


def padded_hex(hex_str, pads):
    return hex(hex_str)[2:].zfill(pads)


def redefine_target(last,time_taken: int,to_take: int):
    this_int=int(last,16)
    new_factor=this_int/(to_take/time_taken)
    if new_factor>this_int*2:
        return padded_hex(round(this_int*2),13)
    if new_factor<this_int/2:
        return padded_hex(round(this_int/2),13)
    return padded_hex(round(new_factor),13)


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


def utxos(addr,currency="LTZ"):
    if os.path.exists(f"bin/utxos/{currency}/{addr}"):
        pass
    else:
        return []
    ips=[]
    path="utxo"
    longest_branch=get_longest()
    test_longest_branch=array_all_in_one(longest_branch)
    inputs=json.loads(query2.get_file_read(f"bin/utxos/{currency}/{addr}"))["inputs"]
    for x in inputs:
        with open(str(f'{path}/{x}')) as of:
            block_id=json.loads(double_quote(of.read()))["block"]
            if block_id in test_longest_branch:
                ips.append(x)
    return ips


def balance(addr,currency="LTZ"):
    inputs=utxos(addr,currency)
    paesa=0
    for x in inputs:
        with open(str(f'utxo/{x}')) as of:
            j_file=json.loads(double_quote(of.read()))
            paesa+=float(j_file[list(j_file.keys())[0]])
    return ltz_round(paesa)


def key_hash(a,b):
    return sha256(f"{a}.{b}".encode()).hexdigest()

def utxo_value(key):
    with open(str(f'utxo/{key}')) as of:
        j_file=json.loads(double_quote(of.read()))
    return ltz_round(float(j_file[list(j_file.keys())[0]]))

def calculate_gas(check_lump):
    check_lump=json.loads(double_quote(check_lump))
    msg=str(check_lump["msg"])
    if len(msg)==0:
        return 0.0
    return ltz_round(len(msg)/512)


class tx:
    def __init__(self,to,amount) -> None:
        self.to=to
        self.amount=amount
    def __repr__(self):
        return str({"to":self.to,"amount":self.amount})


class lump:
    def __init__(self,txs: list,d,e,n,inputs: list,msg="",currency="LTZ") -> None:
        self.txs=txs
        self.inputs=inputs
        self.msg=msg
        self.currency=currency
        self.n=num_encode(n)
        self.e=num_encode(e)
        self.sign=num_encode(int(alursa.signature(sha256(str({"txs":self.txs,"inputs":self.inputs,"msg":self.msg,"currency":currency}).encode()).hexdigest(),d,n)))
    def __repr__(self):
        return str({"txs":self.txs,"inputs":self.inputs,"msg":self.msg,"currency":self.currency,"e":self.e,"n":self.n,"sign":self.sign})


def smart_contract_verify(msg):
    args=msg.split()
    if len(args)!=0:
        if args[0]=="_cmd_":
            if args[1]=="token":
                if args[2]=="create":
                    if len(args[3])>0 and len(args[3])<7 and args[3]==args[3].upper() and os.path.exists(f"bin/utxos/{args[3]}")==False:
                        if is_digit(args[4]):
                            return True
    return False


def verify_lump(check_lump,total_longest,verbose=False):
    if len(str(check_lump))<=1536 and len(str(json.loads(double_quote(check_lump))["msg"]))<=512:
        pass
    else:
        if verbose:
            print("Lump length longer than 2 kilobytes (try sending money in smaller portions)")
        return False
    check_lump=json.loads(double_quote(check_lump))
    if len(check_lump["msg"].split())>3 and check_lump["msg"].split()[0]=="_cmd_":
        if os.path.exists(f"bin/utxos/{check_lump['msg'].split()[3]}"):
            return False
    gas=calculate_gas(check_lump)
    minimum=0.1
    if alursa.verify(num_decode(check_lump["sign"]),sha256(str({"txs":check_lump["txs"],"inputs":check_lump["inputs"],"msg":check_lump["msg"],"currency":check_lump["currency"]}).encode()).hexdigest(),num_decode(check_lump["e"]),num_decode(check_lump["n"])):
        jlump=json.loads(double_quote(check_lump))
        all_txs=len(jlump["txs"])
        crt_txs=0
        tap=0
        going_tap=0
        spenttap=0
        curr=check_lump["currency"]
        for x in jlump["inputs"]:
            utxo_lump=json.loads(open(f"utxo/{x}").read())
            if utxo_lump["block"] in total_longest:
                if utxo_lump["currency"]==curr:
                    tap+=ltz_round(utxo_value(x))
                else:
                    print(utxo_lump["currency"],curr)
        for x in jlump['txs']:
            if ltz_round(x["amount"])==0.0:
                return False
            if x['to']==address(num_decode(jlump["n"])):
                spenttap+=ltz_round(x["amount"])
            else:
                spenttap+=ltz_round(x["amount"])
                going_tap+=ltz_round(x["amount"])
            crt_txs+=1
        if ltz_round(gas)>0:
            if ltz_round(going_tap)<ltz_round(minimum):
                if verbose:
                    print("Not enough Gas.")
                return False
        if ltz_round(spenttap)==ltz_round(tap) and crt_txs==all_txs:
            return True
        else:
            if verbose:
                print("TX's of this lump are not valid",crt_txs,all_txs)
                print(spenttap,tap)
            return False
    else:
        if verbose:
            print("Hash Mis-Match")
        return False


def handle_lump_io(check_lump,block_hash):
    check_lump=json.loads(double_quote(check_lump))
    gas=calculate_gas(check_lump)
    lump_hash=sha256(str({"txs":check_lump["txs"],"inputs":check_lump["inputs"],"msg":check_lump["msg"]}).encode()).hexdigest()
    for x in check_lump["txs"]:
        gassed_amount=ltz_round(ltz_round((100-gas)/100)*ltz_round(x["amount"]))
        if x["to"]==address(num_decode(check_lump["n"])):
            utxo_name=sha256(double_quote(str({x["to"]:x["amount"],"currency":check_lump["currency"],"block":block_hash,"lump":lump_hash})).encode()).hexdigest()
            query2.utxo_add(x["to"],utxo_name,currency=check_lump["currency"])
            query.add("utxo",utxo_name,double_quote(str({x["to"]:ltz_round(x["amount"]),"currency":check_lump["currency"],"block":block_hash,"lump":lump_hash})))
        else:
            gassed_name=(sha256(double_quote(str({x["to"]:ltz_round(gassed_amount),"currency":check_lump["currency"],"block":block_hash,"lump":lump_hash})).encode()).hexdigest())
            (query2.utxo_add(addr=x["to"],utxo=gassed_name,currency=check_lump["currency"]))
            query.add("utxo",gassed_name,double_quote(str({x["to"]:ltz_round(gassed_amount),"currency":check_lump["currency"],"block":block_hash,"lump":lump_hash})))
    for x in check_lump["inputs"]:
        (query.remove("utxo",x))
        query2.utxo_remove(address(num_decode(check_lump["n"])),x,currency=check_lump["currency"])
    if check_lump["msg"]!="":
        (query2.contract_append({lump_hash:check_lump["msg"]}))
        if smart_contract_verify(check_lump["msg"]):
            args=check_lump["msg"].split()
            curr=args[3].upper()
            utxo_name=(sha256(double_quote(str({address(num_decode(check_lump["n"])):float(args[4]),"currency":curr,"block":block_hash,"lump":lump_hash})).encode()).hexdigest())
            query.add("utxo",utxo_name,double_quote({address(num_decode(check_lump["n"])):float(args[4]),"currency":curr,"block":block_hash,"lump":lump_hash}))
            query2.utxo_add(address(num_decode(check_lump["n"])),utxo_name,currency=curr)


def handle_block_io(block):
    branch_save(block)
    reward=1
    block=json.loads(double_quote(block))
    query.add("chain",block["hash"],double_quote(block))
    query2.append("chain",block["hash"],block["prev"])
    utxo={block["miner"]:reward,"currency":"LTZ","block":block["hash"]}
    query.add("utxo",sha256(double_quote(utxo).encode()).hexdigest(),double_quote(utxo))
    query2.utxo_add(block["miner"],sha256(double_quote(utxo).encode()).hexdigest(),currency="LTZ")
    query2.custom_append("timestamps",block["timestamp"])
    bhash=block["hash"]
    for x in block["txlump"]:
        handle_lump_io(x,bhash)


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


def get_target():
    timestamps=query2.givedb("timestamps")
    if len(timestamps)<90:
        return open("bin/target").read()
    else:
        taken=timestamps[len(timestamps)-1]-timestamps[0]
        new_target=redefine_target(open("bin/target").read(),int(taken),3600)
        print(f"New network target is {new_target}")
        open("bin/target","w+").write(new_target)
        open("bin/timestamps.aludb","w+").write("[]")
        return open("bin/target").read()

def mine(trans,pkey,coinbase: str):
    print(arrow_msg_gen("Miner Thread","Mining Started!"))
    target=get_target()
    trans["coinbase"]=coinbase
    trans["miner"]=pkey
    base={"checksum":sha256(double_quote(trans).encode()).hexdigest(),"nonce":0}
    while sha256(double_quote(base).encode()).hexdigest()>target:
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


def generate_inputs(n,topay,utxs,currency="LTZ"):
    addr=address(n)
    if balance(addr,currency)>=ltz_round(topay):
        allowed_inputs=utxs
        input_balances=[]
        for x in allowed_inputs:
            y=utxo_value(x)
            input_balances.append(y)
        cc_ib=input_balances.copy()
        input_balances.sort()
        input_balances.reverse()
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
                    break
                else:
                    in_val+=x
                    using_now.append(allowed_inputs[cc_ib.index(x)])
            return using_now
        else:
            return inputs_to_use
    else:
        return False


def workout_lump(topay,whom,d,e,n,msg="",currency="LTZ"):
    addr=address(n)
    utxs=utxos(addr,currency)
    if utxs==[]:
        return False
    inputs=generate_inputs(n,ltz_round(topay),utxs,currency=currency)
    if inputs==False:
        return False
    tap=0
    for x in inputs:
        tap+=ltz_round(utxo_value(x))
    if ltz_round(tap)-ltz_round(topay)==0:
        return lump([tx(whom,ltz_round(topay))],d,e,n,inputs,msg,currency=currency)
    else:
        a=tx(whom,ltz_round(topay))
        b=tx(addr,(ltz_round(tap)-ltz_round(topay)))
        return lump([a,b],d,e,n,inputs,msg,currency=currency)


def tx_base(tx_lump=[],is_genesis=False):
    if is_genesis:
        return {"height":1,"prev":0,"contracts":[],"timestamp":unix_time(),"txlump":tx_lump}
    bhash=get_building_hash()
    return {"height":json.loads(double_quote(open("chain/"+bhash).read()))["height"]+1,"prev":bhash,"contracts":[],"timestamp":unix_time(),"txlump":tx_lump}


def verify_block(block):
    target=get_target()
    if len(str(block))<=10485760:
        pass
    else:
        return False
    block=json.loads(double_quote(block))
    if len(block["coinbase"])<=128 and len(block["miner"])<=64:
        pass
    else:
        return False
    if str(get_building_hash())=="0":
        last_prev=0
    else:
        last_prev=json.loads(double_quote(open("chain/"+get_building_hash()).read()))["prev"]
    if last_prev==0:
        pass
    elif block["height"]>=json.loads(double_quote(open("chain/"+last_prev).read()))["height"]:
        pass
    else:
        return False
    if check_all_lumps(block):
        if block["prev"]!=0:
            if os.path.exists(f'chain/{block["prev"]}'):
                cc_block=block.copy()
                block_hash=cc_block["hash"]
                del cc_block["hash"]
                nonce=cc_block["nonce"]
                del cc_block["nonce"]
                base={"checksum":sha256(double_quote(cc_block).encode()).hexdigest(),"nonce":nonce}
                if sha256(double_quote(base).encode()).hexdigest()==block_hash and block_hash<=target and block["height"]-1==json.loads(double_quote(open("chain/"+block["prev"]).read()))["height"]:
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
            if sha256(double_quote(base).encode()).hexdigest()==block_hash and block_hash<=target and block["height"]-1==0:
                return True   
    return False

def msg_check(msg,uids):
    try:
        if sha256(msg.encode()).hexdigest()[0:4]=="0000" and msg.split("uid=")[1] not in uids and len(msg.split(" nonce=")[0])<=128 and len(msg.split(" nonce=")[0])>0:
            return True
        else:
            return False
    except:
        return False