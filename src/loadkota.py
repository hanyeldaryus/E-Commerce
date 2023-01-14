import json

datakota = []
raw = {}
def loadAll(dir):
    global raw
    global datakota
    with open(dir) as json_file:
        raw = json.load(json_file)
        datakota = raw['rajaongkir']['results']
 
def isInitialized():
    if len(datakota) == 0:
        print("Data not initialized, initialize with loadAll()")
        return False
    return True
    

def getAll():
    isInitialized()
    return datakota

def search(id):
    isInitialized()
    id = str(id)
    for i in datakota:
        if i['city_id'] == id:
            return i
    return None

def searchByName(name):
    name = name.lower()
    isInitialized()
    for i in datakota:
        if i['city_name'].lower() == name:
            return i
    return None


# demo
if __name__ == "__main__":
    loadAll("data/kota.json")
    #print(datakota)
    print(searchByName("Pati"))