import re
with open("blends.txt","r") as f:
    lines = [line.strip("\n") for line in f.readlines() if line.strip("\n") != "None"]
    for line in lines:
        if re.match("^\[.+?\]$", line) is None:
            print(line) 
