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

from alursa import make_kp
def load_settings():
    global settings
    try:
        with open("settings.json") as fw:
            settings=json.loads(fw.read())
    except:
        raise Exception("No settings.json file found!")

load_settings()
relay_msg=settings["msg"]
firstpeer=True
initial_sync=True
verbose=settings["verbose"]
sys_verbose=settings["sys verbose"]
print(logovar)
import socket, threading, random,traceback,sys,hash_test
try:
    port=int(sys.argv[1])
except:
    port = random.randint(100,1000)
from essentials import *
difficulty = 4
d,e,n,node_addr = alursa.load()
coinbase="LTZ is the best!"
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
                    if torecv>1048576:
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
                            print(f"Block: hash: {block_json['hash']} miner: {block_json['miner']} coinbase: {block_json['coinbase']}")
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
                                sleep(0.2)
                                with open(f"chain\\{x[1]}") as uwu:
                                    client.send((uwu.read()).encode())
                    sleep(0.3)
                    client.send("sync_end".encode())
                    print(arrow_msg_gen("Sync Thread"," Sync complete"))
                    del in_sync[client]
                
                elif msg_filter(received_msg, "type")=="sending_sync":
                    bls=0
                    print(arrow_msg_gen("Sync Thread"," Syncing Initialized!"))
                    while True:
                        uwu=client.recv(1048576).decode()
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
                                if verify_block(uwu):
                                    print("Block Received!")
                                    handle_block_io(uwu)
                                    bls+=1
                                else:
                                    print(uwu)
                                    print("invalid block received")
                                    print("Syncer node sending inavlid blocks. Stopping Sync")
                                    break
                            except:
                                if sys_verbose:
                                    traceback.print_exc()
                                print("Error during sync. Stopping sync.")
                else:
                    print(received_msg)
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

def loop_mine():
    while True:
        base_mineempty()

def thread_loop_mine():
    threading.Thread(target=loop_mine).start()

def send():
    global relay_msg,firstpeer,sys_verbose,true_lumps,coinbase,used,allc,verbose
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
                    sync_client=next(iter(allc))
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
                    sc.connect(("department-bucks.at.playit.gg",60622))
                except:
                    print(f"ERROR : Unable to connect to default peer.")
                    continue
                allc[sc]=sc
                t1=threading.Thread(target=client_handeler,args=(sc,))
                t1.start()
                print("Peer added to list!")
                if firstpeer==True:
                    firstpeer==False
                    sync_client=next(iter(allc))
                    uid=uidgen()
                    if is_chain_empty():
                        lb=0
                    else:
                        lb=get_building_hash()
                    msg=double_quote(msgen(lb,uid,"sync_req"))
                    sync_client.send(str(len(msg.encode())).encode())
                    sync_client.send(msg.encode())
            
            elif raw_msg=="sync":
                sync_client=next(iter(allc))
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
                with open("settings.json","w+") as fw:
                    fw.write(json.dumps({"verbose":verbose,"sys verbose":sys_verbose,"msg":relay_msg}))

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
            
            elif raw_msg=="mine empty":
                threading.Thread(target=base_mineempty).start()
            
            elif raw_msg=="mine loop":
                thread_loop_mine()
            
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
    global true_lumps
    import time
    while True:
        time.sleep(0.1)
        if len(true_lumps)!=0:
            remove_overlapping()
            cc_truelumps=true_lumps.copy()
            if len(cc_truelumps)>=6144:
                tx=tx_base(cc_truelumps[0:6144])
                del cc_truelumps[:6144]
            else:
                tx=tx_base(cc_truelumps)
                cc_truelumps=[]
            block=mine(tx,node_addr,coinbase)
            if get_building_hash()==block["prev"]:
                print(arrow_msg_gen("Miner Thread","Block Mined Successfully!"))
                broadcast(double_quote(block),"block")
            else:
                print(arrow_msg_gen("Miner Thread","Block Mined late."))


t2=threading.Thread(target=send)
t2.start()
t3=threading.Thread(target=loop_mine_thread).start()

while True:
    client,addr=server.accept()
    print("Peer connected!")
    allc[client]=client
    t1=threading.Thread(target=client_handeler,args=(client,))
    t1.start()