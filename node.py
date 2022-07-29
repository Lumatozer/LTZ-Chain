logovar="""""""""
                   %%%%%.%                   
                %%%% %%%%%%%%%%              
           %%%%%%%%%%%%%%%%%%%%%%%%,         
       %%%%%%%%%%%%%% %#%%%%%%%%%%#%%%%%     
   %%%%%%%%%%%%%%%%% %%%% %%%%%%% %%%%%%%%%%   
 %%%%%%%%%%%%%%%%%% %%%%%%% %%%% %%%%%%%%%%%%% 
  %%%%%%%%%%%%%%%%,%%%%%%%%%%. %%%%%%%%%%%%%%% 
 %% %%%%%%%%%%%%%%%%%%%%%%%%%  %%%%%%%%%%%%%%%   
 %%%% %%%%%%%%% %%%%%%%%%%%%,%%% %%%%%%%%%%%%%   
 %%%%%% %%%%%% %%%%%%%%%%% %%%%%%% %%%%%%%%%%%  
 %%%%%%%% %%% %%%%%%%%%%% %%%%%%%%%#%%%%%%%%%%   
 %%%%%%%%%%  %%%%%%%%%%%%%%%%%%%%%%%% %%%%%%%    
 %%%%%%%%%%/% %%%%%%%% %%%%%%%%%%%%%%%% %%%%,%  
 %%%%%%%%#%%%%% %%%%% %%%%%%%%%%%%%%%%%%%. %%%    
 %%%%%%% %%%%%%%% %#%%%%%%%%%%%%%%%%%%%%%  %%%                                                    
 %%%%%% %%%%%%%%%% .%%%%%%%%%%%%%%%%%%%%%%%% %    
     % %%%%%%%%%% %%%/%%%%%%%%%%%%%%%% %%%                                                        
         %%%%%%.%%%%%%%##%%%%%%%%%%%%          
             / %%%%%%%%%%%,%%%%%%              
                  %%%%%%%%%%                   
                     %%%                       
"""""""""
settings=None
import json

from query2.query2 import get_file_read, givedb
def load_settings():
    global settings
    try:
        with open("bin/settings.json") as fw:
            settings=json.loads(fw.read())
    except:
        raise Exception("No settings.json file found in bin folder!")

load_settings()
relay_msg=settings["msg"]
firstpeer=True
initial_sync=True
verbose=settings["verbose"]
sys_verbose=settings["sys verbose"]
miner_threads=False
coinbase=settings["coinbase"]
print(logovar)
import socket, threading, random,traceback,sys,hash_test
try:
    port=int(sys.argv[1])
except:
    port = random.randint(100,1000)
from essentials import *
difficulty = 4
d,e,n,node_addr = alursa.load()
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',port))
print(f"Your host port is {port}")
server.listen()
allc = {}
used = []
msg_used=[]
in_sync={}
true_lumps=[]
true_contracts=[]
mined_blocks=[]

def push_blocks_to_storage():
    global mined_blocks
    last_handle=json.loads(open(f'chain/{get_file_read("bin/last_handled")}').read())["height"]
    mined_2=mined_blocks.copy()
    top_blocks=get_file_read("bin/top.chain")
    if len(top_blocks.split(","))==1:
        longest_chain=array_all_in_one(get_longest())
        for x in mined_blocks:
            if int(top_blocks.split(",")[0].split("->")[1])-x["height"]>2:
                if x["hash"] in longest_chain and (x["hash"]!=get_file_read("bin/last_handled")):
                    if x["height"]>=last_handle:
                        handle_block_io(x)
                    mined_2.remove(x)
                    print(f"Block {x['hash']} was confirmed.")
                else:
                    mined_2.remove(x)
                    print(f"Block {x['hash']} was found to be an uncle.")
    mined_blocks=mined_2


def remove_overlapping():
    global true_lumps
    cc_tl=true_lumps.copy()
    all_inputs=[]
    for x in true_lumps:
        abort=False
        if abort==False:
            for y in x["inputs"]:
                if abort==False:
                    if y in all_inputs:
                        cc_tl.remove(x)
                        abort=True
                    else:
                        all_inputs.append(y)
                else:
                    continue
        else:
            continue
    true_lumps=cc_tl

def not_common_lists(list1, list2):
    for x in list1:
        for y in list2:
            if x == y:
                return False
    return True

def not_in_truelumps(lump):
    for x in true_lumps:
        if not_common_lists(json.loads(double_quote(x))["inputs"],json.loads(double_quote(lump))["inputs"]):
            pass
        else:
            return False
    return True

def relay(raw_msg):
    global allc
    cc_allc=allc.copy()
    for client in cc_allc:
        try:
            if client not in in_sync:
                client.send(str(len(raw_msg)).encode())
                client.send(raw_msg)
        except:
            print("Disconnected")
            del cc_allc[client]
    allc=cc_allc

def is_set(text):
    try:
        text=double_quote(text)
        json.loads(text)
        if "set" in str(type(json.loads(text))) or "dict" in str(type(json.loads(text))):
            return True
        else:
            return False
    except:
        return False

def msgen(data,uid,type):
    try:
        if is_set(data)==False:
            return {"data":double_quote(data),"uid":str(uid),"type":type}
        elif is_set(data):
            return {"data":json.loads(double_quote(data)),"uid":str(uid),"type":type}
    except:
        return False

def broadcast(raw_msg,type="msg",append=False):
    global allc
    global used
    cc_allc=allc.copy()
    uid=uidgen()
    msg=double_quote(msgen(raw_msg,uid,type))
    if append==True:
        used.append(uid)
    for client in allc:
        try:
            if client not in in_sync:
                client.send(str(len(msg.encode())).encode())
                client.send(msg.encode())
        except:
            print("Disconnected")
            del cc_allc[client]
    allc=cc_allc

def client_handeler(client):
    cc=client
    global allc,verbose,true_lumps,used,initial_sync,mined_blocks,sys_verbose
    while True:
        try:
            to_relay=True
            msg_len=client.recv(1024).decode()
            if msg_gen=="":
                print("disconnected")
                break
            else:
                try:
                    torecv=int(msg_len)
                    if torecv>11485760:
                        continue
                except:
                    continue
            received_msg=client.recv(torecv).decode()
            
            if received_msg=="":
                print("disconnected")
                break
            
            try:
                json.loads(received_msg)["data"]
                json.loads(received_msg)["type"]
                json.loads(received_msg)["uid"]
            except:
                if sys_verbose:
                    print("Error : Invalid Message")
                    print(received_msg)
                continue
            if  msg_filter(received_msg,"uid") not in used:
                used.append(msg_filter(received_msg,"uid"))
                data=msg_filter(received_msg, "data")
                if msg_filter(received_msg, "type")=="msg":
                    if msg_check(data,msg_used):
                        if verbose==True:
                            msg_used.append(data.split("uid=")[1])
                            print(data.split(" nonce=")[0])
                            relay(received_msg.encode())
                        else:
                            relay(received_msg.encode())
                        
                elif msg_filter(received_msg, "type")=="lump":
                    try:
                        if verify_lump(data,array_all_in_one(get_longest())) and json.loads(double_quote(data)) not in true_lumps and not_in_truelumps(data):
                            relay(received_msg.encode())
                            true_lumps.append(data)
                            if sys_verbose:
                                print("TX received")
                        elif sys_verbose:
                            print("An invalid lump was broadcasted.")
                    except:
                        if sys_verbose:
                            traceback.print_exc()
                            print("Error verifying lump")
                
                elif msg_filter(received_msg, "type")=="block":
                    relay(received_msg.encode())
                    try:
                        if verify_block(double_quote(data)):
                            for x in json.loads(double_quote(data))["txlump"]:
                                if x in true_lumps:
                                    true_lumps.remove(x)
                            block_json=json.loads(double_quote(data))
                            print(f"Block: hash: {block_json['hash']} height: {block_json['height']} TX's: {len(block_json['txlump'])} miner: {block_json['miner']} nonce: {block_json['nonce']} coinbase: {block_json['coinbase']}")
                            
                            mined_blocks.append(block_json)
                            push_blocks_to_storage()

                            branch_save(block_json)
                            query2.append("chain",block_json["hash"],block_json["prev"])
                            query.add("chain",block_json["hash"],double_quote(block_json))
                        else:
                            if sys_verbose:
                                print("False Block was broadcasted.")
                    except:
                        if sys_verbose:
                            traceback.print_exc()
                        print("False Block/Already Added")
                
                elif msg_filter(received_msg, "type")=="sync_req":
                    from time import sleep
                    print(arrow_msg_gen("Sync Thread"," A client requested sync\n Sending data"))
                    in_sync[client]=client
                    longest_branch=get_longest()
                    longest_branch=arr_double_opp(longest_branch)
                    uid=uidgen()
                    msg=double_quote(msgen("sync",uid,"sending_sync"))
                    client.send(str(len(msg.encode())).encode())
                    client.send(msg.encode())
                    start_sending=False
                    for x in longest_branch:
                        if start_sending:
                            sleep(0.1)
                            with open(f"chain/{x[1]}") as uwu:
                                client.send(json.dumps(json.loads(uwu.read())).encode())
                        else:
                            if str(x[0])==str(data):
                                start_sending=True
                                sleep(0.1)
                                with open(f"chain/{x[1]}") as uwu:
                                    client.send(json.dumps(json.loads(uwu.read())).encode())
                    sleep(0.3)
                    client.send("sync_end".encode())
                    print(arrow_msg_gen("Sync Thread"," Sync complete"))
                    del in_sync[client]
                
                elif msg_filter(received_msg, "type")=="sending_sync":
                    bls=0
                    last=open("bin/last_handled").read()
                    mined_chain=array_all_in_one(get_longest())
                    print(arrow_msg_gen("Sync Thread"," Syncing Initialized!"))
                    while True:
                        uwu=client.recv(11485760).decode()
                        if uwu=="":
                            print("Disconnected while Syncing")
                            break
                        elif uwu=="sync_end":
                            if bls==0:
                                print(arrow_msg_gen("Sync Thread"," Sync Up-to-Date"))
                            else:
                                print(arrow_msg_gen("Sync Thread"," Syncing complete"))
                            if initial_sync:
                                initial_sync=False
                                uid=uidgen()
                                if is_chain_empty():
                                    lb=0
                                else:
                                    lb=get_building_hash()
                                print(make_warning("Resyncing once more to verify sync!"))
                                msg=double_quote(msgen(lb,uid,"sync_req"))
                                client.send(str(len(msg.encode())).encode())
                                client.send(msg.encode())
                            break
                        elif is_set(uwu)==False:
                            print("Syncer node sending inavlid json. Stopping Sync")
                            break
                        elif is_set(uwu):
                            uwu=json.loads(uwu)
                            try:
                                if verify_block(uwu) and uwu["prev"]==last:
                                    last=uwu["hash"]
                                    print(f"Block {bls} Received!")
                                    branch_save(uwu)
                                    if uwu["hash"] not in mined_chain:
                                        query2.append("chain",uwu["hash"],uwu["prev"])
                                        query.add("chain",uwu["hash"],double_quote(uwu))
                                    handle_block_io(uwu)
                                    bls+=1
                                else:
                                    if sys_verbose:
                                        print(uwu,last)
                                    print("Invalid block received!")
                                    if uwu["prev"]!=last:
                                        print("Syncer node sending invalid block series! Immediately Stopping Sync.")
                                    break
                            except:
                                if sys_verbose:
                                    traceback.print_exc()
                                print("Error occured during sync. Stopping sync.")
                else:
                    if sys_verbose:
                        print(received_msg)
                    if verbose:
                        print("Non-Forwardable Message Received!")
        
        except:
            if sys_verbose:
                traceback.print_exc()
            print("Disconnected")
            try:
                del allc[cc]
            except:
                del allc[client]
            client.close()
            break


def base_mineempty():
    tx=tx_base([])
    block=mine(tx,node_addr,coinbase)
    if get_building_hash()==block["prev"]:
        print(arrow_msg_gen("Miner Thread","Block Mined Successfully!"))
        broadcast(double_quote(block),"block")
    else:
        print(arrow_msg_gen("Miner Thread","Block Mined late."))


def send():
    global relay_msg,firstpeer,sys_verbose,true_lumps,coinbase,used,allc,verbose,miner_threads
    while True:
        try:
            raw_msg=input("Node >> ")

            if 1==0:
                pass
            
            elif raw_msg=="add":
                print("~~-Add-New-Peer-~~")
                sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    sc.connect((input("I.P. : ").replace(" ",""),int(input("PORT : ").replace(" ",""))))
                except:
                    print(f"ERROR : Unable to connect to given ip::port combination.")
                    continue
                allc[sc]=sc
                t1=threading.Thread(target=client_handeler,args=(sc,))
                t1.start()
                print("Peer added to list!")
                if firstpeer==True:
                    firstpeer==False
                    sync_client=list(allc.keys())[0]
                    uid=uidgen()
                    if is_chain_empty():
                        lb=0
                    else:
                        lb=open("bin/last_handled").read()
                    msg=double_quote(msgen(lb,uid,"sync_req"))
                    sync_client.send(str(len(msg.encode())).encode())
                    sync_client.send(msg.encode())
            
            elif raw_msg=="default peer":
                sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    sc.connect(("telebit.cloud",58562))
                except:
                    print(f"ERROR : Unable to connect to default peer.")
                    continue
                allc[sc]=sc
                t1=threading.Thread(target=client_handeler,args=(sc,))
                t1.start()
                print("Peer added to list!")
                if firstpeer==True:
                    firstpeer==False
                    sync_client=list(allc.keys())[0]
                    uid=uidgen()
                    if is_chain_empty():
                        lb=0
                    else:
                        lb=open("bin/last_handled").read()
                    msg=double_quote(msgen(lb,uid,"sync_req"))
                    sync_client.send(str(len(msg.encode())).encode())
                    sync_client.send(msg.encode())
            
            elif raw_msg=="sync":
                sync_client=list(allc.keys())[0]
                uid=uidgen()
                if is_chain_empty():
                    lb=0
                else:
                    lb=open("bin/last_handled").read()
                msg=double_quote(msgen(lb,uid,"sync_req"))
                sync_client.send(str(len(msg.encode())).encode())
                sync_client.send(msg.encode())
            
            elif raw_msg=="coinbase":
                coinbase=input("Set custom coinbase value : ")
            
            elif raw_msg=="mem pool":
                print(f"{len(true_lumps)} TX's in mempool")
                total_size=0
                for x in true_lumps:
                    total_size+=len(str(x))
                print(f"Size of Pool : {(total_size/1024)} Kb")

            elif raw_msg=="network target" or raw_msg=="target":
                print(get_target())
            
            elif raw_msg=="nfts":
                if os.path.exists(f"bin/NFT/{node_addr}"):
                    print("-----------------------------------NFT's-----------------------------------")
                    for x in json.loads(get_file_read(f"bin/NFT/{node_addr}"))["inputs"]:
                        print(f" # : {x}")
                    print("-"*75)
                else:
                    print("You currently don't own any NFT's")
            
            
            elif raw_msg=="sys verbose":
                if sys_verbose==False:
                    print("Sys-Verbose Enabled")
                    sys_verbose=True
                elif sys_verbose:
                    print("Sys-Verbose Disabled")
                    sys_verbose=False
            
            elif raw_msg=="messaging":
                if relay_msg==False:
                    print("Messaging Enabled")
                    relay_msg=True
                elif relay_msg:
                    print("Messaging Disabled")
                    relay_msg=False
            
            elif raw_msg=="save settings":
                with open("bin/settings.json","w+") as fw:
                    fw.write(json.dumps({"verbose":verbose,"sys verbose":sys_verbose,"msg":relay_msg,"coinbase":coinbase}))
                print("Changes saved!")

            elif raw_msg=="hashrate":
                hash_test.rate_check()

            elif raw_msg=="verbose":
                if verbose==False:
                    print("Verbose Enabled")
                    verbose=True
                elif verbose:
                    print("Verbose Disabled")
                    verbose=False
            
            elif raw_msg=="tx":
                send_to=input("Receiver : ").replace(" ","")
                amount=input("Amount (number) : ").replace(" ","")
                curr=input("Currency ( LTZ default ) : ").upper()
                if curr=="":
                    curr="LTZ"
                try:
                    float(amount)
                except:
                    print("Invalid Amount")
                    continue
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n,currency=curr)
                if tx_lump_result==False:
                    print("Invalid Lump Details!")
                elif verify_lump(tx_lump_result,array_all_in_one(get_longest()),verbose=True)==False:
                    print("Lump verification Failed")
                else:
                    broadcast(tx_lump_result,type="lump")
                    print("Broadcasted")
            
            elif raw_msg=="contract":
                send_to=input("Contract Incentive Receiver : ").replace(" ","")
                amount=input("Amount : ").replace(" ","")
                contract=input("Contract (len < 512 chars) : ")
                try:
                    float(amount)
                except:
                    print("Invalid Amount")
                    continue
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n,msg=contract)
                if tx_lump_result==False:
                    print("Invalid Lump Details!")
                elif verify_lump(tx_lump_result,array_all_in_one(get_longest()),verbose=True)==False:
                    print("Lump verification Failed")
                else:
                    tx_lump_result=json.loads(double_quote(tx_lump_result))
                    print(f'Contract hash : {sha256(str({"txs":tx_lump_result["txs"],"inputs":tx_lump_result["inputs"],"msg":tx_lump_result["msg"]}).encode()).hexdigest()}')
                    print("Broadcasted")
                    broadcast(tx_lump_result,type="lump")
            
            elif raw_msg=="create token":
                send_to=input("Contract Incentive Receiver : ").replace(" ","")
                amount=0.1
                token_name=input("Input ticker/name/symbol for your token : ")
                if len(token_name)<1 or len(token_name)>6:
                    print("Invalid name provided for creation of the token.")
                    continue
                total_supply=input("Enter the total supply for your token : ")
                contract=f"_cmd_ token create {token_name} {float(total_supply)}"
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n,msg=contract)
                if tx_lump_result==False:
                    print("Invalid Lump Details!")
                elif verify_lump(tx_lump_result,array_all_in_one(get_longest()),verbose=True)==False:
                    print("Lump verification Failed")
                else:
                    tx_lump_result=json.loads(double_quote(tx_lump_result))
                    print(f'Contract hash : {sha256(str({"txs":tx_lump_result["txs"],"inputs":tx_lump_result["inputs"],"msg":tx_lump_result["msg"]}).encode()).hexdigest()}')
                    print("Broadcasted")
                    broadcast(tx_lump_result,type="lump")
            
            elif raw_msg=="send nft":
                send_to=input("NFT Receiver : ").replace(" ","")
                amount=0.1
                nft_hash=input("Input the hash for your NFT : ")
                if os.path.exists(f"nfts/{nft_hash}") and json.loads(get_file_read(f"nfts/{nft_hash}"))["owner"]==node_addr:
                    pass
                else:
                    print("Invalid NFT Provided")
                    continue
                contract=f"_cmd_ nft send {nft_hash} {send_to}"
                if cmd_contract_verify(contract,node_addr):
                    pass
                else:
                    print("Error while verifying contract")
                    continue
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n,msg=contract)
                if tx_lump_result==False:
                    print("Invalid Lump Details!")
                elif verify_lump(tx_lump_result,array_all_in_one(get_longest()),verbose=True)==False:
                    print("Lump verification Failed")
                else:
                    tx_lump_result=json.loads(double_quote(tx_lump_result))
                    print(f'Contract hash : {sha256(str({"txs":tx_lump_result["txs"],"inputs":tx_lump_result["inputs"],"msg":tx_lump_result["msg"]}).encode()).hexdigest()}')
                    print("Broadcasted")
                    broadcast(tx_lump_result,type="lump")
            
            elif raw_msg=="mint nft":
                send_to=input("Contract Incentive Receiver : ").replace(" ","")
                amount=0.1
                nft_url=input("Input the URL for your NFT : ")
                contract=f"_cmd_ nft mint {nft_url}"
                if cmd_contract_verify(contract,node_addr):
                    pass
                else:
                    print("Error while verifying contract")
                    continue
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n,msg=contract)
                if tx_lump_result==False:
                    print("Invalid Lump Details!")
                elif verify_lump(tx_lump_result,array_all_in_one(get_longest()),verbose=True)==False:
                    print("Lump verification Failed")
                else:
                    tx_lump_result=json.loads(double_quote(tx_lump_result))
                    print(f'Contract hash : {sha256(str({"txs":tx_lump_result["txs"],"inputs":tx_lump_result["inputs"],"msg":tx_lump_result["msg"]}).encode()).hexdigest()}')
                    print(f"NFT Hash : {sha256(nft_url.encode()).hexdigest()}")
                    print("Broadcasted")
                    broadcast(tx_lump_result,type="lump")

            elif raw_msg=="balance" or raw_msg=="bal":
                curr=input("Currency ( LTZ default ) : ").upper()
                if curr=="":
                    curr="LTZ"
                print(f"Blockchain ->  Address : {node_addr}\n Balance : {balance(node_addr,currency=curr)} {curr}")

            elif raw_msg=="see bal" or raw_msg=="see balance":
                check_addr=input("Enter Address : ").replace(" ","")
                curr=input("Currency ( LTZ default ) : ").upper()
                if curr=="":
                    curr="LTZ"
                print(f"Blockchain{' -> {'}\n Address : {check_addr}\n Balance : {balance(check_addr,currency=curr)} {curr}"+"\n}")
            
            elif raw_msg=="mine":
                miner_threads=True
                print("Initiaing mining of empty blocks...")

            elif raw_msg=="kill miner thread":
                miner_threads=False
                print("Kill scheduled")
            
            elif raw_msg=="address" or raw_msg=="addr":
                print(node_addr)
            
            elif raw_msg=="utxos":
                action=input("Enter address (empty for self): ").replace(" ","")
                if action=="":
                    print(json.dumps(utxos(node_addr),indent=3))
                else:
                    print(json.dumps(utxos(action),indent=3))
            
            elif raw_msg=="top block":
                print(get_building_hash())
            
            elif raw_msg=="longest branch":
                print(json.dumps(get_longest(),indent=3))
            
            elif raw_msg=="view contract":
                contract_name=input("Enter contract address : ").replace(" ","")
                contracts=givedb("contracts")
                found=False
                for x in contracts:
                    key_val=dict_keyval(x)
                    if key_val[0]==contract_name:
                        found=True
                        print(f'--- Contract Data ---\n{key_val[1]}')
                if found==False:
                    print("Could not find the given contract")
            
            else:
                if relay_msg:
                    mined_msg=msg_mine(raw_msg)
                    broadcast(mined_msg,append=True)
        except:
            if sys_verbose:
                traceback.print_exc()


def loop_mine_thread():
    import time
    while True:
        time.sleep(0.25)
        if len(true_lumps)!=0:
            cc_truelumps=true_lumps.copy()
            if len(cc_truelumps)>=6485:
                tx=tx_base(cc_truelumps[:6485])
                del cc_truelumps[:6485]
            else:
                tx=tx_base(cc_truelumps)
                cc_truelumps=[]
            block=mine(tx,node_addr,coinbase)
            if get_building_hash()==block["prev"]:
                print(arrow_msg_gen("Miner Thread","Block Mined Successfully!"))
                broadcast(double_quote(block),"block")
            else:
                print(arrow_msg_gen("Miner Thread","Block Mined late."))
        elif miner_threads:
            try:
                base_mineempty()
            except:
                if sys_verbose:
                    print(traceback.print_exc())


t2=threading.Thread(target=send)
t2.start()
t3=threading.Thread(target=loop_mine_thread).start()

while True:
    client,addr=server.accept()
    print("Peer connected!")
    allc[client]=client
    t1=threading.Thread(target=client_handeler,args=(client,))
    t1.start()