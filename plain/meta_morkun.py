
from os import listdir
from os.path import isfile, join

path2markad = "/media/starkadur/NewVolume/tmp/output"

files = [f for f in listdir(path2markad) if isfile(join(path2markad, f))]
total_cnt = 0
total_correct = 0
for file in files:
    print(file)
    with open(join(path2markad,file),"r") as f:
        lines = f.readlines()

    cnt = 0
    cnt_correct = 0
    for line in lines:
        line = line.strip()
        if line=="":
            continue
        cnt+=1
        splt = line.split("\t")
        if splt[1]==splt[2]:
            cnt_correct+=1

    total_cnt+=cnt
    total_correct+=cnt_correct
    print(cnt, (float(cnt_correct)/cnt)*100)

print(total_cnt, total_correct)
print(total_cnt, (float(total_correct)/total_cnt)*100)
