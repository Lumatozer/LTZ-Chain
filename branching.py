import json,time
from query2 import query2
def mer(msg):
    base="\n"+"#"*(len(msg)+4)+"\n"
    return "*Error*" + base + "| " + msg + " |"+ base
def dict_keyval(dict):
    base=str(dict).replace("'","").replace('"',"").split("{")
    return base[1].split(": ")[0],base[1].split(": ")[1].split("}")[0]
def get_longest(opposite=False,manual=False):
    if not manual:
        while True:
            with open("bin/top.chain") as fw:
                fr=fw.read()
            if fr!="":
                break
            else:
                time.sleep(0.1)
                continue
        bls=fr.split(",")
        hashes=[]
        heights=[]
        for x in bls:
            hashes.append(x.split("->")[0])
            heights.append(x.split("->")[1])
        top_block=hashes[heights.index(max(heights))]
        mes=[]
        prevs=[]
        tops=[]
        chain=query2.givedb("chain")
        for x in chain:
            a,b=dict_keyval(x)
            mes.append(str(a))
            prevs.append(str(b))
        del chain
        branch=[]
        current=top_block
        while True:
            last=prevs[mes.index(current)]
            if last==0 or last=="0":
                branch.append([current,last])
                break
            else:
                branch.append([current,last])
                current=last
                continue
        return branch
    else:
        mes=[]
        prevs=[]
        tops=[]
        chain=query2.givedb("chain")
        for x in chain:
            a,b=dict_keyval(x)
            mes.append(str(a))
            prevs.append(str(b))
        del chain
        for x in mes:
            if x in prevs:
                pass
            else:
                tops.append(x)
        def findlast(current):
            for x in mes:
                if x==current:
                    return x
        branches=[]
        for x in tops:
            rnow=x
            branch=[]
            branch.append([rnow,prevs[mes.index(rnow)]])
            while True:
                if prevs[mes.index(rnow)]!=0 and prevs[mes.index(rnow)]!=str(0):
                    crtlast=findlast(prevs[mes.index(rnow)])
                    branch.append([crtlast,prevs[mes.index(crtlast)]])
                    rnow=crtlast
                else:
                    break
            branches.append(branch)
        brlens=[]
        if opposite==False:
            for x in branches:
                brlens.append(len(x))
            try:
                longest_list = max(brlens)
            except:
                print(mer("Error no blockchain genesis found! / Empty Chain!"))
                exit()
            return branches[brlens.index(longest_list)]
        if opposite==True:
            for x in branches:
                brlens.append(len(x))
            try:
                longest_list = max(brlens)
            except:
                print(mer("Error no blockchain genesis found! / Empty Chain!"))
                exit()
            out_branch=[] 
            for x in branches[brlens.index(longest_list)][::-1]: 
                out_branch.append(x[::-1]) 
            return out_branch

def get_building_hash(manual=False):
    if manual:
        return get_longest(manual=True)[0][0]
    else:
        while True:
            with open("bin/top.chain") as fw:
                fr=fw.read()
            if fr!="":
                break
            else:
                time.sleep(0.1)
                continue
        bls=fr.split(",")
        hashes=[]
        heights=[]
        for x in bls:
            hashes.append(x.split("->")[0])
            heights.append(x.split("->")[1])
        return hashes[heights.index(max(heights))]

def is_chain_empty():
    import os
    if os.listdir("chain")==[]:
        return True
    return False

def branch_save(block):
    while True:
        with open("bin/top.chain") as fw:
            last_height=int(fw.read().split(",")[0].split("->")[1])
        if last_height!="":
            break
        else:
            time.sleep(0.1)
            continue
    block=json.loads(str(block).replace("'",'"'))
    if block["height"]>last_height:
        b_hash=block["hash"]
        b_height=block["height"]
        with open("bin/top.chain","w+") as fw:
            fw.write(f"{b_hash}->{b_height}")
            fw.close()
    elif block["height"]==last_height:
        b_hash=block["hash"]
        b_height=block["height"]
        with open("bin/top.chain","a") as fw:
            fw.write(f",{b_hash}->{b_height}")
            fw.close()