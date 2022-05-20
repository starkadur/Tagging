#sækir xml-skjöl og tókar, markar og lemmar texta.
#TODO: uppfæra pos og marka með pos_bulk í stað pos_sent
from os import listdir

from lxml import etree
from lxml.etree import Element as ET
import os
import sys
import tokenizer
import re
import pos
from os.path import join, dirname, isdir, isfile
import json
import logging
import time
import argparse
import torch
from copy import deepcopy
from datetime import datetime
from collections import OrderedDict
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

def get_u_text(u):
    data = []
    for seg in u.findall(".//tei:{}".format(seg_name), ns):
        data.append(seg.text)
        seg.text = None

    return " ".join(data)

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

def calculate_indices(texts):

    indices = []
    index = 0
    for text in texts:
        text = text.replace(" ","")

        index+=len(text)
        indices.append(index)
    return indices

def read_tagsdecl(root):
    data = {}
    for tagusage in root.findall(".//tei:tagUsage", ns):

        data[tagusage.attrib['gi']] = int(tagusage.attrib['occurs'])
    return data

def count_tags(root):
    data = {'vocal':0, 'kinesic':0, 'note':0, 'incident':0}

    data['vocal'] = len([x for x in root.findall(".//tei:vocal", ns)])
    data['kinesic'] = len([x for x in root.findall(".//tei:kinesic", ns)])
    data['incident'] = len([x for x in root.findall(".//tei:incident", ns)])
    data['note'] = len([x for x in root.findall(".//tei:note", ns)])

    return data

#færir vocal ... úr s og í seg ef það er í lok setningar.
def arrange(seg):

    for sent in seg.findall("s"):
        items = [x for x in sent]

        if items[-1].tag not in ['w','pc']:

            seg.insert(seg.index(sent)+1,items[-1])

def validate():

    tagusage = read_tagsdecl(root)
    tagusage2 = count_tags(root)
    for tag in tagUsage2:

        if (tagusage2[tag]>0 and tag not in tagusage) or (tag in tagusage and tagusage[tag] != tagusage2[tag]):
            return False

    return True

def txt2none(txt):
    txt = txt.strip()
    if txt == "_":
        return None
    else:
        return txt


def update_tagsdecl(root, tags):
    tagsDecl = root.find(".//tei:tagsDecl", ns)
    namespace = tagsDecl.find(".//tei:namespace", ns)

    for tag in tags:

        tagusage = ET("tagUsage")
        tagusage.attrib['occurs'] = str(tags[tag])
        tagusage.attrib['gi'] = tag
        namespace.append(tagusage)


def add_resp_stmt(data):

    titleStmt = root.find(".//tei:titleStmt", ns)

    resp_stmt = titleStmt.findall(".//tei:respStmt", ns)[-1]
    index = titleStmt.index(resp_stmt)

    for item in data:
        index+=1
        respStmt = ET('respStmt')
        persName = ET('persName')
        persName.text = item['name']
        respStmt.append(persName)
        for lang in item['role']:
            resp = ET("resp")
            resp.text = lang['txt']
            resp.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = lang['lang']
            respStmt.append(resp)
        titleStmt.insert(index, respStmt)


def has_error(rest, next):

    if rest:
        if next[0]!=rest[0]:
            return True
        else:
            return False
    return False

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








    #taka strip af ef um er að ræðpath2textsa texta sem inniheldur innskot eins og vocal, note ...
    text = re.sub(r'  +'," ", text).strip()

    return text

def update_extent(_root, w_cnt):

    extent= _root.find(".//tei:extent", ns)

    for measure in extent.findall(".//tei:measure", ns):

        if measure.attrib['unit'] == "words":

            measure.attrib['quantity'] = str(w_cnt)
            measure.text = "{} words".format(str(w_cnt))

    return _root

def get_files():

    data = []

    tree_ = etree.parse(teiCorpus, parser)
    root_ = tree_.getroot()
    for include in root_.findall("{http://www.w3.org/2001/XInclude}include"):

        data.append(join(args.input,include.attrib['href']))

    return data

def xml_unescape(txt):

    txt = txt.replace("%!lt!%","<")
    txt = txt.replace("%!gt!%",">")
    txt = txt.replace("%!amp!%","&")
    txt = txt.replace("%!39!%",'"')
    return txt


def afhreinsa_texta(texti):
    texti = texti.replace("%!11!%"," ")
    return textipath2texts

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--input", help="path to folder containing input files (TEI-files with untagged texts.)")
arg_parser.add_argument("--output", help="path to output files (TEI-files with tagged texts.)")
arg_parser.add_argument("--reverse", type=int, default=0, help="If 1 then the files are iterated in reverse order. Userful if you want to run the script simultaneously.")
arg_parser.add_argument("--teiCorpus", help="path to the file containing teiCorpus.")
arg_parser.add_argument("--configfile", help="Path to config file")
arg_parser.add_argument("--update_extent", default=0, help="Default is 0. Set to 1 if extent (word count) should be updated in original file")
arg_parser.add_argument("--skip_unicode_error", default=0, help="Default is 0. Set to 1 if you want the script to ignore segments with unicode error instaed of aborting the whole wile to do i later.")
arg_parser.add_argument("--skip_cleaning", default=0, help="Default is 0. Set to 1 if you want the script to skip cleaning the text of unicode symbols that the tagger can't handle.")


args = arg_parser.parse_args()

teiCorpus = args.teiCorpus

tmp = teiCorpus.rsplit("/",1)[1].replace(".xml",".txt")
errorlogfile = "errors_{}".format(tmp)


if args.input.find("ParlaMint")>-1 or args.input.find("Parla")>-1:
    seg_name = "seg"
else:
    seg_name = "p"

print(seg_name)
if not args.input.endswith("/"):
    args.input = "{}/".format(args.input)
if not args.output.endswith("/"):
    args.output = "{}/".format(args.output)

if not args.configfile:
    print("Þú verður að senda inn stikann --configfile með slóð á config-skrá.")
    exit()


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

#sækja skjöl
path2tei = args.input
path2tei_ana = args.output

parser = etree.XMLParser(remove_blank_text=True)

#files = get_files()

#files = sorted(files, reverse=(args.reverse==1))

files = ['/media/starkadur/NewVolume/Parlatmp/Parlatmp.xml']
with open(args.configfile) as f:
    config = json.load(f)


# Initialize the tagger
device = torch.device("cpu")  # CPU
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

ns = {'tei': "http://www.tei-c.org/ns/1.0"}

unfinished = []
cnt = 0
cnt_fatal_errors = 0
print("FJÖLDI: {}".format(len(files)))
for path2file in files:

    #print(path2file)


    cnt+=1
    if cnt%1000==0:
        print(cnt)
    fatal_error = False

    file = path2file.rsplit("/",1)[1]

    filename_ana = path2file.replace(args.input, args.output)

    if filename_ana == path2file:
        print("slóð á .ana er sama og á TEI")
        print(path2file)
        print(filename_ana)
        exit()


    filename_ana = filename_ana.replace(".xml",".ana.xml")
    #print(filename_ana)

    splt = filename_ana.rsplit("/",1)
    if not os.path.exists(splt[0]):
        os.makedirs(splt[0])


    #if os.path.exists(filename_ana):
    #    continue

    #if filename_ana != '/media/starkadur/NewVolume/risamalheild2020/samfelagsmidlar/TEI/IGC-Social-21.10.ana/Twitter/2008/IGC-Social3_2008_04.ana.xml':
    #    continue
    print(filename_ana)
    #else:
    #    unfinished.append(filename_ana)
    #continue

    #print(path2file)
    count_s = 0
    count_w = 0
    count_pc = 0


    tagUsage2 = {'note':0,'vocal':0, 'incident':0, 'kinesic':0}

    #opna xml-skjal og setja í rót

    tree = etree.parse(path2file, parser)
    root_tei = tree.getroot()
    root = deepcopy(root_tei)

    #breyta xml:id í rót
    root.attrib['{http://www.w3.org/XML/1998/namespace}id'] = root.attrib['{http://www.w3.org/XML/1998/namespace}id']+".ana"
    #breyta titli
    title_found = False
    re_title = re.compile(r'\[IGC-\S+[^\] ]\]')
    for title in root.findall(".//tei:title", ns):

        m = re_title.search(title.text)
        if m:
            tmp = m.group()
            tmp2 = tmp.replace("]",".ana]")
            title.text = title.text.replace(tmp, tmp2)
            title_found = True
    if not title_found:
        print("Titill fannst ekki")
        exit()

    #bæta við verkefnum (respStmt)
    add_resp_stmt(config['respStmt'])

    #ítra yfir seg og skrá s og w
    #for u in root.findall(".//tei:u", ns):
    #    #ítra yfir <seg>
    text = root.find(".//tei:text", ns)

    segs = text.findall(".//tei:{}".format(seg_name), ns)

    cnt_seg = len(segs)
    start_time = time.perf_counter()

    print("fjöldi seg: {}".format(cnt_seg))
    for seg in segs:

        #cnt_seg-=1
        #print(cnt_seg)
        #if fatal_error:
        #    break
        try:
            seg_id = seg.attrib['{http://www.w3.org/XML/1998/namespace}id']

        except KeyError:
            print("KEY ERROR")
            print(seg)
            print(seg.attrib)
            fatal_error = True
            break

        texti = seg.text


        #í tilfelli Twtitter þarf að sækja hluta setningar og varpa xml-stöfum
        '''if 'source' in seg.attrib:

            source = seg.attrib['source']
            substr_indices = source.split("-")[1].split(",")
            substr_indices[0] = int(substr_indices[0])
            substr_indices[1] = int(substr_indices[1])
            texti = xml_unescape(texti)
            texti = afhreinsa_texta(texti)
            texti = texti[substr_indices[0]:substr_indices[1]]'''



        texts = []
        elems = []
        try:
            texts.append(texti.strip())
        except AttributeError:
            print("AttributeError")
            print(seg_id)
            fatal_error = True

            continue

        #finna öll elem í seg (vocal, incident ...) og bæta texta við texts
        for elem in seg:

            elems.append([elem, elem.tail])
            if elem.tail:
                texts.append(elem.tail.strip())
                elem.tail = None

            seg.remove(elem)

        if not args.skip_cleaning:

            for i in range(0, len(texts)):
                texts[i] = clean_text(texts[i])

        #finna index þar sem mörk texta eru (og því pláss fyrir elems)
        tags_insert_indices = calculate_indices(texts)

        #sameina allan texta og tóka
        text = " ".join(texts)+" "
        #TODO: gera þetta áður en fyrstu tei-skjöl eru búin til

        text_tokenized = tokenize(text)

        seg.text = None

        try:
            sentences_tokenized = text_tokenized.split("\n")
            bulk= text2bulk(sentences_tokenized)
            tags = tagger.tag_bulk(bulk)
        except IndexError:
            print("INdex errr ...")
            print(sentences_tokenized)

            if not args.skip_unicode_error:
                fatal_error = True
            continue

        except ValueError:
            print("Bad Value Error ...")
            print(sentences_tokenized)
            fatal_error = True
            continue
        except RuntimeError:
            print("Setning of löng")
            tags = []
            try:
                for sentence in sentences_tokenized:
                    tags.append(tagger.tag_sent(sentence.split(" ")))
            except RuntimeError:
                print("Setning enn of löng")
                fatal_error = True
                continue
            except IndexError:
                print("Index error í tagger.tag_sent")
                print(sentence)
                fatal_error = True
                continue


        lemmas = lemmatize_bulk(bulk, tags)

        data = join_token_tag_lemma(bulk, tags, lemmas)

        text_len = 0
        elem_index = 0
        elem_index2 = 0

        s_nr = 1
        text_index = 0
        #ítra yfir hverja setningu (eftir tókun)
        for sent in data:

            s = ET('s')
            s_id = "{}.{}".format(seg_id, s_nr)

            s.attrib['{http://www.w3.org/XML/1998/namespace}id'] = s_id
            item_nr = 1
            #ítra yfir hvert tóka setningar
            for item in sent:
                print(item)

                right_join=True
                token_len = len(item[0])
                text_index+=token_len
                while text_index< len(text) and text[text_index]==" ":
                    right_join = False
                    text_index+=1

                item_id = "{}.{}.{}".format(seg_id, s_nr, item_nr)

                text_len+=len(item[0])
                if item[1][0] == "p":
                    w = ET('pc')
                    count_pc+=1
                else:
                    w = ET('w')
                    count_w+=1
                    w.attrib['lemma'] = item[2]

                w.attrib['{http://www.w3.org/XML/1998/namespace}id'] = item_id
                w.text = item[0]
                w.attrib['pos'] = item[1]
                if right_join:
                    w.attrib['join'] = "right"


                s.append(w)

                #bæta við elem (vocal, incident ...) ef staðsetning er rétt
                if len(elems)>0 and elem_index < len(tags_insert_indices):


                    #komið að skilum texta sem þýðir að tag (vocal,...) ætti að koma inn.
                    if tags_insert_indices[elem_index] == text_len:

                        while elem_index2<len(elems):

                            try:
                                if len(elems)>elem_index2:

                                    s.append(elems[elem_index2][0])

                                    if has_error(elems[elem_index2][1], text[text_index:] ):
                                        print("ERROR#####################")
                                        print(elems[elem_index2][1])
                                        print(text[text_index:])

                                    elem_index2+=1
                            except IndexError:
                                print("INDEX ERROR")
                                print(tags_insert_indices)
                                print(elem_index2)
                                print(len(elems))
                                print(text_len)
                                print(texts)
                                print(etree.tostring(s, pretty_print = True))
                                exit()

                            #stoppa ef elem hafði texta á eftir (tail)

                            if elem_index2>=len(elems):
                                break


                            if elems[elem_index2-1][1]:
                                break

                        elem_index+=1

                item_nr+=1
            seg.append(s)
            count_s+=1

            s_nr+=1

        if len(elems)>0 and (elem_index2 != len(elems) and elem_index2 != len(elems)+1):
            print("VILLA:ekki búið að setja öll tög inn")
            print(elem_index,len(elems))
            print(texts)
            print("ELEMS")
            for elem in elems:
                print(elem)
            fatal_error = True




        seg = arrange(seg)

    end_time = time.perf_counter()
    time_total = end_time- start_time
    per_seg = time_total/float(cnt_seg)
    print(f"Tók {time_total:0.2f} sekúndur, {per_seg:0.4} per segment")

    if fatal_error:
        print("Skjal ekki skráð")
        print(path2file)
        cnt_fatal_errors+=1
        unfinished.append(path2file)
        continue

    dict_ = OrderedDict()
    dict_['s'] = count_s
    dict_['w'] = count_w
    dict_['pc'] = count_pc
    update_tagsdecl(root, dict_)

    if not validate():
        print("VILLA - ath tög")
    #update extent
    if args.update_extent==1:
        root_tei = update_extent(root_tei,count_w)
        root = update_extent(root,count_w)

    et = etree.ElementTree(root)

    et.write(filename_ana, pretty_print=True,encoding="UTF-8",xml_declaration=True)

    if args.update_extent==1:
        et = etree.ElementTree(root_tei)
        et.write(path2file, pretty_print=True,encoding="UTF-8",xml_declaration=True)


exit()
print("FATAL ERRORS: {}".format(cnt_fatal_errors))
print("################################################")
if len(unfinished)>0:

    with open(errorlogfile, "w") as f:
        for item in unfinished:
            print(item)
            f.write("{}\n".format(item))

#print(len(unfinished))
