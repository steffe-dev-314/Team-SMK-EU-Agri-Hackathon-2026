import json 
import pandas as pd 

with open("data/NRW_CROPS.json", "r") as f:
    NRW_CROPS = json.load(f)

kulturen = [
    crop for crop in NRW_CROPS
    if not NRW_CROPS[crop]["Zwischenfrucht"]
]

zwischenfruechte = [
    crop for crop in NRW_CROPS
    if NRW_CROPS[crop]["Zwischenfrucht"]
]

N_BEDARF = {crop : NRW_CROPS[crop]['Stickstoffbedarf der Kultur'] for crop in NRW_CROPS}

ERTRAEGE = {crop : NRW_CROPS[crop]['Ertrag der Kultur'] for crop in NRW_CROPS}
