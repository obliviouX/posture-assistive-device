import ujson as json

x = 27

jsonData = {"num": x}

try:
    with open('savedata.json', 'w') as f:
        json.dump(jsonData, f)
except:
    print("Error. Did not save data")
    