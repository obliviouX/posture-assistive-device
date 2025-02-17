import ujson as json

try:
    with open('savedata.json', 'r') as f:
        data = json.load(f)
        y = data["num"]
        print(y)
except:
    print("Variable not found.")
    y = 56
    
jsonData = {"num": y}
            