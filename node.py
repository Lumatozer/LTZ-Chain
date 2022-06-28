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

firstpeer=True
initial_sync=True
coinbase="Block Mined"
allc = {}
used = []
in_sync={}
true_lumps=[]


print(logovar)


from ast import arg
import socket, threading, random,traceback,sys,time
from essentials import *


try:
    port=int(sys.argv[1])
except:
    port = random.randint(100,1000)


d,e,n,node_addr = alursa.load()


server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',port))
print(arrow_msg_gen("BlockChain",f" Your host port is {port}"))
server.listen()


def relay(raw_msg):
    global allc
    cc_allc=allc.copy()
    for client in cc_allc:
        try:
            if client not in in_sync:
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
                client.send(msg.encode())
        except:
            print("Disconnected")
            del cc_allc[client]
    allc=cc_allc


def client_handeler(client):
    cc=client
    global allc
    global true_lumps
    global used
    global initial_sync
    while True:
        try:
            received_msg=client.recv(1024000).decode()
            if received_msg=="":
                print("disconnected")
                break
            try:
                json.loads(received_msg)
                msg_filter(received_msg,"type")
                msg_filter(received_msg,"data")
            except:
                print("Error : Invalid Message")
                print(received_msg)
                continue
            if  msg_filter(received_msg,"uid") not in used:
                used.append(msg_filter(received_msg,"uid"))
                data=msg_filter(received_msg, "data")
                if msg_filter(received_msg, "type")=="msg":
                    print(data)
                    relay(received_msg.encode())
                elif msg_filter(received_msg, "type")=="lump":
                    if verify_lump(data):
                        true_lumps.append(data)
                        relay(received_msg.encode())    
                    else:
                        print("Invalid lump broadcasted")    
                elif msg_filter(received_msg, "type")=="block":
                    relay(received_msg.encode())
                    try:
                        if verify_block(double_quote(data)):
                            print("True Block")
                            handle_block_io(double_quote(data))
                        else:
                            print("False Block")
                    except:
                        traceback.print_exc()
                        print("False Block/Already Added")
                elif msg_filter(received_msg, "type")=="sync_req":
                    from time import sleep
                    print(arrow_msg_gen("Sync Thread"," A client requested sync\n Sending data"))
                    in_sync[client]=client
                    longest_branch=get_longest(opposite=True)
                    uid=uidgen()
                    msg=double_quote(msgen("sync",uid,"sending_sync"))
                    client.send(msg.encode())
                    start_sending=False
                    for x in longest_branch:
                        if start_sending:
                            sleep(0.1)
                            client.send((open(f"chain\\{x[0]}").read()).encode())
                        else:
                            if str(x[0])==str(data):
                                start_sending=True
                                sleep(0.1)
                                client.send((open(f"chain\\{x[1]}").read()).encode())
                    sleep(0.3)
                    client.send("sync_end".encode())
                    print(arrow_msg_gen("Sync Thread"," Sync complete"))
                    del in_sync[client]
                elif msg_filter(received_msg, "type")=="sending_sync":
                    print(arrow_msg_gen("Sync Thread"," Syncing Initialized!"))
                    while True:
                        uwu=client.recv(1024000).decode()
                        if uwu=="":
                            print("Disconnected while Syncing")
                            break
                        elif uwu=="sync_end":
                            print(arrow_msg_gen("Sync Thread"," Sync complete"))
                            if initial_sync:
                                initial_sync=False
                                uid=uidgen()
                                if is_chain_empty():
                                    lb=0
                                else:
                                    lb=get_building_hash()
                                msg=double_quote(msgen(lb,uid,"sync_req"))
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
                                else:
                                    print(uwu)
                                    print("invalid block received")
                                    print("Syncer node sending inavlid blocks. Stopping Sync")
                                    break
                            except:
                                traceback.print_exc()
                                print("Error during sync. Stopping sync.")
                else:
                    print(received_msg)
                    print("Non-Forwardable Message Received!")
        except:
            traceback.print_exc()
            print("Disconnected")
            try:
                del allc[cc]
            except:
                del allc[client]
            client.close()
            break


def mine_empty():
    tx=tx_base([])
    start=time.time()
    block=mine(tx,node_addr,coinbase)
    if get_building_hash()==block["prev"]:
        print(arrow_msg_gen("Miner Thread",f"Block Mined Successfully!\n Time Taken : {time.time()-start}"))
        broadcast(double_quote(block),"block")
        print(f"Mined Block Validity : {verify_block(double_quote(block))}")
    else:
        print(arrow_msg_gen("Miner Thread","Block Mined late."))


def loop_mine():
    try:
        while True:
            mine_empty()
    except KeyboardInterrupt:
        pass 


def send():
    global allc
    global used
    global coinbase
    global true_lumps
    global firstpeer
    while True:
        raw_msg=input("Node >> ")
        if 1==0:
            pass
        elif raw_msg=="add":
            print("~~-Add-New-Peer-~~")
            sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                sc.connect((input("I.P. : "),int(input("PORT : "))))
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
                sync_client.send(msg.encode())
        elif raw_msg=="default peer":
            sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                sc.connect(("department-bucks.at.playit.gg",60622))
            except:
                traceback.print_exc()
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
                sync_client.send(msg.encode())
        elif raw_msg=="sync":
            sync_client=next(iter(allc))
            uid=uidgen()
            if is_chain_empty():
                lb=0
            else:
                lb=get_building_hash()
            msg=double_quote(msgen(lb,uid,"sync_req"))
            sync_client.send(msg.encode())
        elif raw_msg=="coinbase":
            coinbase=input("Set custom coinbase value : ")
        elif raw_msg=="tx":
            send_to=input("Receiver : ")
            amount=input("Amount (int) : ")
            try:
                int(amount)
            except:
                print("Invalid Amount")
                continue
            tx_lump_result=workout_lump(int(amount),send_to,d,e,n)
            if tx_lump_result==False:
                print("Invalid Lump!")
            elif verify_lump(tx_lump_result)==False:
                print("Lump verification Failed")
            else:
                print(tx_lump_result)
                broadcast(tx_lump_result,type="lump")
                print("Broadcasted")
        elif raw_msg=="balance" or raw_msg=="bal":
            print(f"Blockchain{' -> {'}\n Address : {node_addr}\n Balance : {balance(node_addr)} LTZ"+"\n}")
        elif raw_msg=="mine loop":
            threading.Thread(target=loop_mine).start()
        elif raw_msg=="address" or raw_msg=="addr":
            print(node_addr)
        else:
            broadcast(raw_msg,append=True)

def loop_mine_thread():
    global true_lumps
    while True:
        if len(true_lumps)!=0:
            if len(true_lumps)>=5:
                tx=tx_base(true_lumps[0:5])
                del true_lumps[:5]
            if len(true_lumps)>=7:
                tx=tx_base(true_lumps[0:7])
                del true_lumps[:7]
            elif len(true_lumps)<5:
                tx=tx_base(true_lumps)
                true_lumps=[]
            start=time.time()
            block=mine(tx,node_addr,coinbase)
            if get_building_hash()==block["prev"]:
                print(arrow_msg_gen("Miner Thread",f"Block Mined Successfully!\n Time Taken : {time.time()-start}"))
                broadcast(double_quote(block),"block")
            else:
                print(arrow_msg_gen("Miner Thread","Block Mined late."))


t2=threading.Thread(target=send)
t2.start()
t3=threading.Thread(target=loop_mine_thread).start()


while True:
    client,addr=server.accept()
    print("Got Peer")
    allc[client]=client
    t1=threading.Thread(target=client_handeler,args=(client,))
    t1.start()