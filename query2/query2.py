import json,time,os
def get_file_read(name):
    while True:
        with open(name) as fw:
            fr=fw.read()
            if fr!="":
                return fr
            else:
                time.sleep(0.1)

def dict_keyval(dict):
    key_1=str(dict.keys()).replace("'","").replace('"',"")[11:-2]
    return key_1,dict[key_1]
def get(dbname,key):
    dbname="bin/"+dbname+".aludb"
    fr=get_file_read(dbname)
    db_file=json.loads(str(fr).replace("'",'"'))
    for x in db_file:
        if (((dict_keyval(x)[0]).replace('"',"")).replace("'",""))==key:
            return dict_keyval(dict_keyval(x)[1])[1]

def key_exists(dbname,key):
    dbname="bin/"+dbname+".aludb"
    file=json.loads(get_file_read(dbname).replace("'",'"'))
    for x in file:
        if dict_keyval(x)[0]==key:
            return True
    return False

def append(dbname,key,val):
    if not key_exists(dbname,key):
        dbname="bin/"+dbname+".aludb"
        file=json.loads(get_file_read(dbname).replace("'",'"'))
        file.append({key:val})
        with open(dbname,'w+') as fw:
            fw.write(str(file).replace("'",'"'))
            return True
    elif key_exists(dbname,key):
        dbname="bin/"+dbname+".aludb"
        file=json.loads(get_file_read(dbname).replace("'",'"'))
        for x in file:
            if dict_keyval(x)[0]==key:
                file[file.index(x)]={key:val}
                with open(dbname,'w+') as fw:
                    fw.write(str(file).replace("'",'"'))
                return True

def custom_append(dbname,val):
    dbname="bin/"+dbname+".aludb"
    file=json.loads(get_file_read(dbname).replace("'",'"'))
    file.append(val)
    with open(dbname,'w+') as fw:
        fw.write(str(file))
        return True

def contract_append(val):
    dbname="bin/contracts.aludb"
    with open(dbname,'a') as fw:
        fw.write(str(val).replace("'",'"')+",")
        return True

def givedb(dbname):
    dbname="bin/"+dbname+".aludb"
    f=get_file_read(dbname)
    if f[0]=="~":
        f=f[1:]
        f=f[:-1]
        f="["+f+"]"
        file=json.loads(f.replace("'",'"'))
    else:
        file=json.loads(f.replace("'",'"'))
    return file

def remove(dbname,key):
    if key_exists(dbname,key):
        dbname="bin/"+dbname+".aludb"
        file=json.loads(get_file_read(dbname).replace("'",'"'))
        for x in file:
            if dict_keyval(x)[0]==key:
                file.remove(json.loads(str(x).replace("'",'"')))
                open(dbname,"w+").write(json.dumps(file))
                return True

def utxo_add(addr,utxo,currency="LTZ"):
    if os.path.exists(f"bin/utxos/{currency}/{addr}"):
        fr=json.loads(get_file_read(f"bin/utxos/{currency}/{addr}"))
        pass
    else:
        if os.path.exists(f"bin/utxos/{currency}"):
            open(f"bin/utxos/{currency}/{addr}","a").close()
        else:
            os.mkdir(f"bin/utxos/{currency}")
            open(f"bin/utxos/{currency}/{addr}","a").close()
        fr={"inputs":[]}
    fr["inputs"].append(utxo)
    with open(f"bin/utxos/{currency}/{addr}","w+") as fw:
        fw.write(str(fr).replace("'",'"'))

def utxo_remove(addr,utxo,currency="LTZ"):
    fr=json.loads(get_file_read(f"bin/utxos/{currency}/{addr}"))
    fr["inputs"].remove(utxo)
    with open(f"bin/utxos/{currency}/{addr}","w+") as fw:
        fw.write(str(fr).replace("'",'"'))