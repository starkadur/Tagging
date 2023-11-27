#les inn eitt skjal þar sem hver lína inniheldur einn bút (oftast ein setning, en stundum fleiri)
#tókar og markar hverja einingu fyrir sig og skráir í skjal þar sem tvö línubil eru á milli búta
# en ein á milli setninga

from os import listdir
import os
import sys
import tokenizer
import re
import pos
from os.path import join, dirname, isdir, isfile
import logging
import time
import argparse
import torch
import json
from copy import deepcopy
from datetime import datetime
sys.path.append(join(dirname(__file__), '../nefnir/'))
from nefnir import Nefnir

def fix_tokenize(text, output):
    tokenize2 = []
    tokenize3 = []
    output_fixed = False
    fixed_tokens = []
    for line in output.split("\n"):
        tokenize2.append(line.split(" "))

    for i in range(0, len(tokenize2)):

        while True:
            fixed = False #set True if something is fixed

            for j in range(0, len(tokenize2[i])):
                token = tokenize2[i][j]

                if text.find(token)<0:

                    if len(token)==2:
                        fixed = True
                        output_fixed = True
                        tokens = list(token)
                        fixed_tokens.append(token)
                        tokenize2[i][j] = tokens[0]
                        j+=1
                        tokenize2[i].insert(j, tokens[1])
                        break
                    else:
                        pass
                        '''"Þarf að laga tóka? ################################"
                        print("text:")
                        print(text)
                        print("output")
                        print(output)
                        print()'''
            if not fixed:
                break

        tokenize2[i] = " ".join(tokenize2[i])
    #sameina setningar er síðari er . og fyrri endar á .
    removes = []

    for i in reversed(range(1, len(tokenize2))):

        if re.match(r'^\.+$', tokenize2[i]) and tokenize2[i-1].endswith("."):
            tokenize2[i-1]+=tokenize2[i]
            removes.append(i)
            output_fixed = True

    for r in removes:
        del tokenize2[r]

    output2 = "\n".join(tokenize2)

    if output_fixed:
        for t in fixed_tokens:
            if t!="?…":
                pass
                '''print("Tókun löguð: ###########################")
                print("Fyrir")
                print(output)
                print("Eftir")
                print(output2)'''

        if output.replace(" ","").replace("\n","")!=output2.replace(" ","").replace("\n",""):
            print("EKKI SAMA")
            print("Fyrir")
            print(output)
            print("Eftir")
            print(output2)
            exit()


    return output2

def tokenize(text):

    output = ""
    for line in text.split("\n"):

        if line.strip()!="":
            token_list = tokenizer.split_into_sentences(line.strip())

            #token_list = FixTokenizer.join_sentences(token_list)
            if token_list is not None:
                for sent in token_list:
                    output+=sent+"\n"

            else:
                return None

    output = fix_tokenize(text, output.strip())
    return output


def lemmatize(tokens, tags):

    lemmas = {}
    for w, t in zip(tokens, tags):
        try:
            lemma = nefnir.lemmatize(w,t)
            lemmas["{} {}".format(w, t)] = lemma
        except ValueError:
            if line:
                logger.warning('Ignoring line: {}'.format(line))

    return lemmas

def lemmatize_bulk(tokens, tags):

    lemmas = {}
    for sent_w, sent_t in zip(tokens, tags):
        for w, t in zip(sent_w, sent_t):

            try:
                lemma = nefnir.lemmatize(w,t)
                lemmas["{} {}".format(w, t)] = lemma
            except ValueError:
                if line:
                    logger.warning('Ignoring line: {}'.format(line))

    return lemmas

def add_lemmas(tokens, tags, lemmas):
    data = []
    for w, t in zip(tokens, tags):
        data.append([w, t, lemmas["{} {}".format(w, t)]])

    return data


def text2bulk(sents):

    data = []
    for sent in sents:
        data.append(sent.split(" "))
    return data

def join_token_tag_lemma(tokens_sent, tags_sent, lemmas):
    data = []
    for sent_tokens, sent_tags in zip(tokens_sent, tags_sent):
        sent = []
        for token, tag in zip(sent_tokens, sent_tags):

            sent.append([token, tag, lemmas["{} {}".format(token, tag)]])
        data.append(sent)

    return data


def clean_text(text):

    text = text.replace(u"\uF0B7"," ")
    text = text.replace(u"\u202a","")
    text = text.replace(u"\u202c","")
    text = text.replace(u"\u200e","")
    text = text.replace(u"\uFFFD","")
    text = text.replace(u"\uF04A","")
    text = text.replace(u"\u200D","")
    text = text.replace(u"\u007F","")
    text = text.replace(u"\u008D","")
    text = text.replace(u"\u0081","")
    text = text.replace(u"\u009C","")
    text = text.replace(u"\u200F","")
    text = text.replace(u"\u009A","")
    text = text.replace(u"\u009D","")
    text = text.replace(u"\u008A","")
    text = text.replace(u"\u007F","")
    text = text.replace(u"\u008F","")
    text = text.replace(u"\u200C","")
    text = text.replace(u"\u009C","")
    text = text.replace(u"\uF038","")
    text = text.replace(u"\uF0DA","")
    text = text.replace(u"\uF09F","")
    text = text.replace(u"\uF04B","")
    text = text.replace(u"\uF0D8","")

    text = text.replace(u"\uf03e","")
    text = text.replace(u"\uf02e","")
    text = text.replace(u"\uf02d","")

    text = text.replace(u"\uf071","")
    text = text.replace(u"\uf06e","")
    text = text.replace(u"\uf0ad","")
    text = text.replace(u"\uf04c","")
    text = text.replace(u"\x86","")
    text = text.replace(u"\uf0fc","")
    text = text.replace(u"\uf076","")
    text = text.replace(u"\uf0b0","")
    text = text.replace(u"\uf0f0","")
    text = text.replace(u"\uf0b3","")
    text = text.replace(u"\uf062","")
    text = text.replace(u"\uf061","")
    text = text.replace(u"\uf0a6","")
    text = text.replace(u"\uf0e0","")
    text = text.replace(u"\u202e","")
    text = text.replace(u"\U000f6b73","")
    text = text.replace(u"\uf06c","")
    text = text.replace(u"\u202b","")
    text = text.replace(u"\uf0df","")
    text = text.replace(u"\uf8ff","")
    text = text.replace(u"\u202d","")
    text = text.replace(u"\x9b","")
    text = text.replace(u"\uf0ba","")
    text = text.replace(u"\uf070","")
    text = text.replace(u"\uf0a2","")
    text = text.replace(u"\ue09a","")
    text = text.replace(u"\uf0d6","")
    text = text.replace(u"\ue078","")
    text = text.replace(u"\ue074","")
    text = text.replace(u"\ue072","")
    text = text.replace(u"\ue034","")

    text = text.replace(u"\ue079","")
    text = text.replace(u"\x8e","Ž")
    text = text.replace(u"\x99", "") #TM
    text = text.replace(u"\x88", "^")
    text = text.replace(u"\x9e", "ž")
    text = text.replace(u"\u206e", "")
    text = text.replace(u"\u0FE335", "")
    text = text.replace(u"\u000e0067", "")
    text = text.replace(u"\u000e0062", "")
    text = text.replace(u"\u000e0073", "")
    text = text.replace(u"\u000e0063", "")
    text = text.replace(u"\u000e0074", "")
    text = text.replace(u"\uf0de", "")
    text = text.replace(u"\u000e007f", "")
    text = text.replace(u"\uf078", "")
    text = text.replace(u"\uf02c", "")
    text = text.replace(u"\uf06f", "")
    text = text.replace(u"\uf035", "")
    text = text.replace(u"\uf06f", "")
    text = text.replace(u"\uf02c", "")
    text = text.replace(u"\uf024", "")
    text = text.replace(u"\uf078", "")
    text = text.replace(u"\uf050", "")
    text = text.replace(u"\ue74d", "")
    text = text.replace(u"\uf020", "")
    text = text.replace(u"\uf0ff", "")
    text = text.replace(u"\x83", "")
    text = text.replace(u"\uea0b", "")
    text = text.replace(u"\uf095", "")
    text = text.replace(u"\uf04d", "")
    text = text.replace(u"\uf08e", "")    
    text = text.replace(u"\x96", "")
    text = text.replace(u"\x89", "‰")
    text = text.replace(u"\x84", "")
    text = text.replace(u"\x97", "")
    text = text.replace(u"\x93", "")
    text = text.replace(u"\ue415", "")
    text = text.replace(u"\uefa0","")
    text = text.replace(u"\uf21c","")
    text = text.replace(u"\ue7d3","")
    text = text.replace(u"\ue18f","")
    text = text.replace(u"\ue7d3","")
    text = text.replace(u"\uefff","")
    text = text.replace(u"\uf207","")
    text = text.replace(u"\ue499","")
    text = text.replace(u"\ueeff","")
    text = text.replace(u"\ue023","")
    text = text.replace(u"\x94", '”')
    text = text.replace(u"\x95", '')
    text = text.replace(u"\x92", '’')


    #taka strip af ef um er að ræðpath2textsa texta sem inniheldur innskot eins og vocal, note ...
    text = re.sub(r'  +'," ", text).strip()

    return text



arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--input", default=None, help="path to file containing text - one sentence per line")
arg_parser.add_argument("--output", default=None, help="path to output file")
arg_parser.add_argument("--skip_cleaning", default=0, help="Default is 0. Set to 1 if you want the script to skip cleaning the text of unicode symbols that the tagger can't handle.")
args = arg_parser.parse_args()

path2input = args.input
path2output = args.output


#hægt að senda inn 1 sem fyrstu stiku og þá er ítrað yfir möppur í öfugri röð. Má nota ef það á að keyra skriftuna
#tvisvar sinnum til að flýta fyrir

resp_stmt = [
    {
        'name':"Starkaður Barkarson",
        'role':[
            {'txt':"Málfræðimörkun", 'lang':'is'},
            {'txt':"Linguistic annotation", 'lang':'en'},
        ]
    }
]

# Initialize the tagger
device = torch.device("cuda")  # CPU
tagger: pos.Tagger = torch.hub.load(
    repo_or_dir="cadia-lvl/POS",
    model="tag_large", # This specifies which model to use. Set to 'tag_large' for large model.
    device=device,
    force_reload=False,
    force_download=False,
)
#tagger = pos.Tagger(
#    model_file=path2taggermodel,
#    device="cpu",
#)

logging.getLogger("pos").setLevel(logging.ERROR)

# read rules and tagset for Nefnir
with open("../nefnir/gull_rules.json", encoding='utf-8') as f:
    rules = json.load(f)

with open("../nefnir/gull_tagset.json", encoding='utf-8') as f:
    tagset = json.load(f)

#Initialize Nefnir
nefnir = Nefnir(rules, tagset)
logging.getLogger("nefnir").setLevel(logging.ERROR)

#opna textaskjal og varpa í fylki    
with open(path2input, "r") as f:
   linur = f.readlines()

#opnar skjal
with open(path2output, "w") as f:
   #ítra yfir hverja línu 
   for texti in linur:
      #clean text
      if args.skip_cleaning==0:
         texti = clean_text(texti)

      #tóka texta - skiltar textastreng þar sem hver setning er aðgreind með líunubili
      text_tokenized = tokenize(texti)
      #skipta tóðuðum texta upp í fylki - einn setning í línu
      sents = text_tokenized.split("\n")
      #sníða tókaðan texta þannig að henti markara
      bulk= text2bulk(sents)
      #marka tókaðan texta
      tags = tagger.tag_bulk(bulk)
      #lemma texta
      lemmas = lemmatize_bulk(bulk, tags)
      #sameina texta, mörk og lemmur í eitt margvídd fylki: setning -> tókar -> orðmynd|mark|lemma
      data = join_token_tag_lemma(bulk, tags, lemmas)

      for sent in data:
         for token in sent:
            f.write("{}\t{}\t{}\n".format(token[0], token[1], token[2]))
         f.write("\n")
      f.write("\n")
     

