def get(dbname,query):
    try:
        path=dbname+"\\"+query
        file=open(path)
        return file.read()
    except:
        return False

def add(dbname,id,query):
    import os.path
    pathtofile=dbname+"\\"+str(id)
    file_exists = os.path.exists(pathtofile)
    if file_exists==False:
        with open(pathtofile, 'x') as f:
            f.write((query))
        return True
    else:
        return False

def remove(dbname,id):
    import os
    pathtofile=dbname+"\\"+str(id)
    file_exists = os.path.exists(pathtofile)
    if file_exists==False:
        return False
    else:
        os.remove(pathtofile)
        return True