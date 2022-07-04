from query2 import query2
def mer(msg):
    base="\n"+"#"*(len(msg)+4)+"\n"
    return "*Error*" + base + "| " + msg + " |"+ base
def dict_keyval(dict):
    base=str(dict).replace("'","").replace('"',"").split("{")
    return base[1].split(": ")[0],base[1].split(": ")[1].split("}")[0]
def get_longest(opposite=False):
    import os,json
    path="chain"
    mes=[]
    prevs=[]
    tops=[]
    chain=query2.givedb("chain")
    for x in chain:
        a,b=dict_keyval(x)
        mes.append(str(a))
        prevs.append(str(b))
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

def get_building_hash():
    return get_longest()[0][0]

def is_chain_empty():
    import os
    if os.listdir("chain")==[]:
        return True
    return False