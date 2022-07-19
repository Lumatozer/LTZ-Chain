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
    global allc,verbose,true_lumps,used,initial_sync
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
                            true_lumps.append(data)
                            relay(received_msg.encode())
                        elif verbose:
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
                            print(f"Block: hash: {block_json['hash']} height: {block_json['height']} miner: {block_json['miner']} nonce: {block_json['nonce']} coinbase: {block_json['coinbase']}")
                            handle_block_io(double_quote(data))
                        else:
                            print("False Block")
                    except:
                        if sys_verbose:
                            traceback.print_exc()
                        print("False Block/Already Added")
                
                elif msg_filter(received_msg, "type")=="sync_req":
                    from time import sleep
                    print(arrow_msg_gen("Sync Thread"," A client requested sync\n Sending data"))
                    in_sync[client]=client
                    longest_branch=get_longest(opposite=True)
                    uid=uidgen()
                    msg=double_quote(msgen("sync",uid,"sending_sync"))
                    client.send(str(len(msg.encode())).encode())
                    client.send(msg.encode())
                    start_sending=False
                    for x in longest_branch:
                        if start_sending:
                            sleep(0.1)
                            with open(f"chain\\{x[0]}") as uwu:
                                client.send((uwu.read()).encode())
                        else:
                            if str(x[0])==str(data):
                                start_sending=True
                                sleep(0.1)
                                with open(f"chain\\{x[1]}") as uwu:
                                    client.send((uwu.read()).encode())
                    sleep(0.3)
                    client.send("sync_end".encode())
                    print(arrow_msg_gen("Sync Thread"," Sync complete"))
                    del in_sync[client]
                
                elif msg_filter(received_msg, "type")=="sending_sync":
                    bls=0
                    last=get_building_hash()
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
                                    print("Block "+bls+" Received!")
                                    handle_block_io(uwu)
                                    bls+=1
                                    last=uwu["hash"]
                                else:
                                    if sys_verbose:
                                        print(uwu)
                                    print("Invalid block received!")
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
                        lb=get_building_hash()
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
                        lb=get_building_hash()
                    msg=double_quote(msgen(lb,uid,"sync_req"))
                    sync_client.send(str(len(msg.encode())).encode())
                    sync_client.send(msg.encode())
            
            elif raw_msg=="sync":
                sync_client=list(allc.keys())[0]
                uid=uidgen()
                if is_chain_empty():
                    lb=0
                else:
                    lb=get_building_hash()
                msg=double_quote(msgen(lb,uid,"sync_req"))
                sync_client.send(str(len(msg.encode())).encode())
                sync_client.send(msg.encode())
            
            elif raw_msg=="coinbase":
                coinbase=input("Set custom coinbase value : ")

            elif raw_msg=="network target" or raw_msg=="target":
                print(get_target())
            
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
                try:
                    float(amount)
                except:
                    print("Invalid Amount")
                    continue
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n)
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
                tx_lump_result=workout_lump(ltz_round(amount),send_to,d,e,n,contract)
                if tx_lump_result==False:
                    print("Invalid Lump Details!")
                elif verify_lump(tx_lump_result,array_all_in_one(get_longest()),verbose=True)==False:
                    print("Lump verification Failed")
                else:
                    broadcast(tx_lump_result,type="lump")
                    print("Broadcasted")
            
            elif raw_msg=="balance" or raw_msg=="bal":
                print(f"Blockchain ->  Address : {node_addr}\n Balance : {balance(node_addr)} LTZ")

            elif raw_msg=="see bal" or raw_msg=="see balance":
                check_addr=input("Enter Address : ").replace(" ","")
                print(f"Blockchain{' -> {'}\n Address : {check_addr}\n Balance : {balance(check_addr)} LTZ"+"\n}")
            
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
            
            else:
                if relay_msg:
                    mined_msg=msg_mine(raw_msg)
                    broadcast(mined_msg,append=True)
        except:
            if sys_verbose:
                traceback.print_exc()

def loop_mine_thread():
    global true_lumps,miner_threads
    import time
    while True:
        time.sleep(0.25)
        if len(true_lumps)!=0:
            remove_overlapping()
            cc_truelumps=true_lumps.copy()
            if len(cc_truelumps)>=6485:
                tx=tx_base(cc_truelumps[0:6485])
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
                continue


t2=threading.Thread(target=send)
t2.start()
t3=threading.Thread(target=loop_mine_thread).start()

while True:
    client,addr=server.accept()
    print("Peer connected!")
    allc[client]=client
    t1=threading.Thread(target=client_handeler,args=(client,))
    t1.start()