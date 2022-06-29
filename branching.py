def mer(msg):
    base="\n"+"#"*(len(msg)+4)+"\n"
    return "*Error*" + base + "| " + msg + " |"+ base
def get_longest(opposite=False):
    print("| Calculating Longest Branch... |")
    import os,json
    path="chain"
    mes=[]
    prevs=[]
    tops=[]
    all_list_path=os.listdir(path)
    for file in all_list_path:
        filepath=path+"\\"+file
        with open(filepath) as fileio:
            filedata=fileio.read()
            jsonfd=json.loads(filedata)
            mes.append(jsonfd["hash"])
            prevs.append(jsonfd["prev"])
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
            if prevs[mes.index(rnow)]!=0:
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
        print("| Longest Branch Calculated |")
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
        print("| Longest Branch Calculated |")
        return out_branch

def get_building_hash():
    return get_longest()[0][0]

def is_chain_empty():
    import os
    if os.listdir("chain")==[]:
        return True
    return False