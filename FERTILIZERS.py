import json 
import pandas as pd 

with open("data/FERTILIZERS.json", "r") as f:
    data = json.load(f)['daten']

FERTILZER_VALUES = pd.DataFrame(data)[['duengemittel','einheit' , 'Nges pro Einheit' , 'Npfluer pro Einheit']].set_index("duengemittel").to_dict(orient ='index')

print(FERTILZER_VALUES)