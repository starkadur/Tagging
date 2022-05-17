#bætir við ner-tögum úr nafnaþekkjara í xml-skjölc
from os import listdir
from os.path import isfile, join, exists
from lxml import etree
from lxml.etree import Element as ET
from copy import deepcopy
from NERTag import NERTag
import timeit
from collections import OrderedDict



def contains_token(elem):

     return elem.tag in ['{http://www.tei-c.org/ns/1.0}w','{http://www.tei-c.org/ns/1.0}pc']

def get_tokens(s):
    tokens = []
    for elem in s:

        if contains_token(elem):
            tokens.append(elem.text)
    return tokens

def replace_unk(ner, tokens):

    def get_next_chunc(data, i):

        a = i
        while a < len(data):
            if data[a]=="[":
                break
            a+=1
        return data[i:a]

    replacements = []
    ner_list = []
    ner_new = []
    for n in ner:
        if n[0] not in ["[SEP]","[CLS]"]:
            ner_list.append(n[0])

    ner_str = "".join(ner_list)
    tokens_str = "".join(tokens)
    n = 0
    t = 0
    while n < len(ner_str) and t < len(tokens_str):

        if ner_str[n]!=tokens_str[t]:
            if ner_str[n:n+5]=="[UNK]":
                next_chunk = get_next_chunc(ner_str, n+5)
                if next_chunk.strip()!="":
                    index = tokens_str[t:].find(next_chunk)

                    insert = tokens_str[t:t+index]
                    t+=index-1
                else:
                    insert = tokens_str[t]
                replacements.append(insert)
                n+=4
            else:
                print("hm")
                print(ner_str[n:n+5])
                print(tokens_str)
                print(ner_str)
                exit()
        n+=1
        t+=1
    index = 0
    for i in range(0, len(ner)):
        if ner[i][0]=="[UNK]":
            text = replacements[index]
            index+=1
        else:
            text = ner[i][0]
        ner_new.append([text, ner[i][1]])

    return ner_new

def joinTokens(ner, tokens):

    ner = replace_unk(ner, tokens)

    '''print("######################################")
    print(tokens)
    print()
    print(ner)
    print("---------------------")'''
    ner2 = []

    n = 0
    t = 0
    while t <len(tokens) and n < len(ner):

        if ner[n][0] in ["[SEP]","[CLS]"]:
            n+=1
            continue
        ner_new = None
        if ner[n][0]!=tokens[t]:

            #if ner[n][0] in ["[UNK]"]:
            #    ner_new = replace_unk(tokens[t], ner[n])

            if len(tokens[t])>len(ner[n][0]): #þarf að sameina ner
                n2 = n
                comb = ner[n][0]
                step = 0
                ner_len = 0
                while len(comb)<len(tokens[t]):
                    step+=1
                    #n2+=1
                    comb = "{}{}".format(comb,ner[n+step][0])



                if comb == tokens[t]:
                    ner_new = (comb, ner[n][1])
                    n = n+step

                else:
                    print("VILLA: tókst ekki að laga")
                    print(tokens)
                    print(ner)
                    print(comb)
                    print(tokens[t])
                    exit()
            elif len(tokens[t])>len(ner[n][0]):
                ner2.append([ner[n][0],ner[n][1]])
            else:
                print("HM")
                exit()
        else:
            ner_new = ner[n]


        ner2.append(ner_new)
        t+=1
        n+=1
    if len(ner2) == len(tokens):
        return ner2
    else:
        print("VILLA: ekki sama lengd")
        print(ner2)
        print("------------")
        print(tokens)

        exit()


#setur tóka inn í name-tag
def wrap(type, s, start_index, elems,end_index, index_sub):
    #print("############")
    #print(start_index)
    #print(index_sub)
    index = start_index-index_sub
    #print(index)
    #print(s[index].text)

    name = ET('name', attrib={'type': type})
    s.insert(index, name)
    i = start_index
    j = start_index
    while i <=end_index:
        if contains_token(elems[j]):
            s.remove(elems[j])
            name.append(elems[j])
            i+=1
        j+=1

def update_tagsdecl(root, tags):
    tagsDecl = root.find(".//tei:tagsDecl", ns)
    namespace = tagsDecl.find(".//tei:namespace", ns)

    for tag in tags:

        tagusage = ET("tagUsage")
        tagusage.attrib['occurs'] = str(tags[tag])
        tagusage.attrib['gi'] = tag
        namespace.append(tagusage)

#athugar hvort name hafi verið skotið inn á röngum stað
def validate_order(root):

    for seg in list(root.findall(".//tei:seg", ns)):

        for s in list(seg.findall(".//tei:s", ns)):
            s_id = s.attrib['{http://www.w3.org/XML/1998/namespace}id']
            curr_nr = 0
            for elem in s.iter():
                if elem.tag in ["{http://www.tei-c.org/ns/1.0}w","{http://www.tei-c.org/ns/1.0}pc"]:

                    nr = int(elem.attrib["{http://www.w3.org/XML/1998/namespace}id"].replace(s_id+".",""))
                    if nr != curr_nr+1:
                        print("VILLA:")
                        print("S ID: {}".format(s_id))
                        print("elem id: {} != {}".format(curr_nr, nr))

                    curr_nr = nr


map_name = {
    'Person' : "PER",
    'Location' : "LOC",
    'Organization' : "ORG",
    'Miscellaneous' : 'MISC'
}
#initiate NERTag
nerTag = NERTag()
unk = set()
parser = etree.XMLParser(remove_blank_text=True)
ns = {'tei': "http://www.tei-c.org/ns/1.0"}

path2tei_folder = "/media/starkadur/NewVolume/ParlaMint-IS/ParlaMint-IS.ana2/"
path2ner_folder = "/media/starkadur/NewVolume/ParlaMint-IS/ParlaMint-IS.ana_ner"
teiFile = "ParlaMint-IS.ana.xml"
extra_name_type = set()
files= [f for f in listdir(path2tei_folder) if isfile(join(path2tei_folder, f)) and f!=teiFile]

files = sorted(files, reverse=False)


for file in files:



    name_cnt = 0
    start_file = timeit.default_timer()
    path2file = join(path2tei_folder, file)
    #path2file = "/media/starkadur/NewVolume/ParlaMint-IS/prufa/ParlaMint-IS_2015-01-20-53.ana.xml"
    path2file_ner = join(path2ner_folder, file)
    if exists(path2file_ner):
        continue
    print(file)

    #opna xml-skjal og setja í rót
    tree = etree.parse(path2file, parser)
    root = tree.getroot()


    for seg in list(root.findall(".//tei:seg", ns)):

        for s in list(seg.findall(".//tei:s", ns)):
            inserts = {} #heldur utan um ner-tög : index (start) = index_ends, type
            name = None
            tokens = get_tokens(s)

            #print(" ".join(tokens))
            #print("Length: "+str(len(tokens)))
            #print("--------------------------")
            #start = timeit.default_timer()


            #get NER tags
            output = nerTag.tag_sentence(" ".join(tokens))
            output = joinTokens(output, tokens)
            elems = s.getchildren()

            j = 0
            i = 0
            insert_start = None
            for elem_ind in range(0, len(elems)):


                if contains_token(elems[elem_ind]):

                    if output[i][1][0] not in ["O","X","["]: #sleppa öllu öðru en I eða B
                        if output[i][1][0] not in ["I","B"]: #ætti aðeins að byrja á I- eða B-
                            print("HA?")
                            print(output[i][1])
                            print(output)
                            print(tokens)
                            exit()

                        #Nýtt ner (insert_start er None eða type er önnur)
                        if (not insert_start and insert_start!=0) or (insert_start in inserts and output[i][1][2:]!=inserts[insert_start]['type']): #

                            inserts[elem_ind] = {'ends':elem_ind, 'type':output[i][1][2:]}
                            insert_start = elem_ind
                            if output[i][1][0]=="I" and output[i][1][2:] == "Person":
                                '''print("############ Ekkert B")
                                print(output)
                                print([output[i]])
                                print()'''
                                pass

                        if output[i][1][0]=="I":
                            inserts[insert_start]['ends']=elem_ind

                    else:
                        insert_start = None

                    if name:
                        name.append(s)
                    i+=1 # next token



            i = 0
            j = 0
            name = None
            elems = list(s)
            index_subtract = 0
            while j < len(elems):

                if contains_token(elems[j]):

                    if j in inserts:
                        ends = inserts[j]['ends']
                        if inserts[j]['type'] in map_name:
                            type = map_name[inserts[j]['type']]

                            wrap(type,s, j, elems, ends,index_subtract)
                            index_subtract+=ends-j
                            name_cnt+=1
                        else:
                            if inserts[j]['type'] not in extra_name_type:
                                extra_name_type.add(inserts[j]['type'])
                                print("### Auka í NER:")
                                print(extra_name_type)
                                print()

                    i+=1
                j+=1


            #stop = timeit.default_timer()
            #print('Time: ', stop - start)
            #print()

    validate_order(root)
    dict_ = OrderedDict()
    dict_['name'] = name_cnt
    update_tagsdecl(root, dict_)

    et = etree.ElementTree(root)
    print(path2file_ner)
    stop = timeit.default_timer()
    print('Time total: ', stop - start_file)
    et.write(path2file_ner, pretty_print=True,encoding="UTF-8",xml_declaration=True)
