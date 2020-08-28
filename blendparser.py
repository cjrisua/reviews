import re, json
import numpy as np 

def Sort_Tuple(tup):
    return(sorted(tup, key = lambda x: x[0])) 

varietal_blend = []
with open("blends.txt","r") as f:
    lines = [line.strip("\n") for line in f.readlines() if line.strip("\n") != "None"]
    for line in lines:
        match = re.match("^([A-Za-z]+)@(\[.+?\]$)", line) 
        if match is not None:
            blendname = Sort_Tuple(eval(match.groups()[1]))
            varietal_blend.append((match.groups()[0], blendname))
single=[]
blends=[]
for vb in varietal_blend:
    grp = [g[0] for g in vb[1]]
    if len(grp) == 1:
        single.append(str(grp[0]).title())
    else:
        blends.append(vb)

for b in blends:
 print(f"{b[0]}@{b[1]}")