from Morkun import Morkun
from os import listdir
from os.path import isfile, join


path2output = "data/output.txt"

morkun = Morkun("plain")

path2set = "/media/starkadur/NewVolume/tmp/eval_set"
path2output = "/media/starkadur/NewVolume/tmp/output/"

files = [f for f in listdir(path2set) if isfile(join(path2set, f))]
for file in files:
    print(file)
    with open(join(path2set,file),"r") as f:
        texti = f.read()

    data = morkun.tag(texti)
    morkun.write_to_file2(data, texti, join(path2output, file))
