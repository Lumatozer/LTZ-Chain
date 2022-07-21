import json,time
def get_file_read(name):
    while True:
        with open(name) as fw:
            fr=fw.read()
            if fr!="":
                break
            else:
                time.sleep(0.1)
    return fr

def dict_keyval(dict):
    key_1=str(dict.keys()).replace("'","").replace('"',"")[11:-2]
    return key_1,dict[key_1]
def get(dbname,key):
    dbname="bin/"+dbname+".aludb"
    fr=get_file_read(dbname)
    db_file=json.loads(str(fr))
    for x in db_file:
        if (((dict_keyval(x)[0]).replace('"',"")).replace("'",""))==key:
            return dict_keyval(dict_keyval(x)[1])[1]

def key_exists(dbname,key):
    dbname="bin/"+dbname+".aludb"
    file=get_file_read(dbname)
    for x in file:
        if str(x).replace("'",'"').split('{')[1].split(":")[0].replace('"',"")==key:
            return True
    return False

def append(dbname,key,val):
    if not key_exists(dbname,key):
        dbname="bin/"+dbname+".aludb"
        file=get_file_read(dbname)
        file.append({key:val})
        with open(dbname,'w+') as fw:
            fw.write(str(file).replace("'",'"'))
            return True
    elif key_exists(dbname,key):
        dbname="bin/"+dbname+".aludb"
        file=get_file_read(dbname)
        for x in file:
            if str(x).replace("'",'"').split('{')[1].split(":")[0].replace('"',"")==key:
                file[file.index(x)]={key:val}
                with open(dbname,'w+') as fw:
                    fw.write(str(file).replace("'",'"'))
                return True

def custom_append(dbname,val):
    dbname="bin/"+dbname+".aludb"
    file=get_file_read(dbname)
    file.append(val)
    with open(dbname,'w+') as fw:
        fw.write(str(file))
        return True

def givedb(dbname):
    dbname="bin/"+dbname+".aludb"
    file=json.loads(get_file_read(dbname).replace("'",'"'))
    return file

def remove(dbname,key):
    if key_exists(dbname,key):
        dbname="bin/"+dbname+".aludb"
        file=json.loads(get_file_read(dbname).replace("'",'"'))
        for x in file:
            if str(x).replace("'",'"').split('{')[1].split(":")[0].replace('"',"")==key:
                file.remove(json.loads(str(x).replace("'",'"')))
                open(dbname,"w+").write(json.dumps(file))
                return True