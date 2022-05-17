import sys
from os import listdir
from os.path import isfile, join
from lxml import etree
from lxml.etree import Element as ET
from ufal.udpipe import Model, Pipeline, ProcessingError # pylint: disable=no-name-in-module
import re
import os
from collections import OrderedDict

def format_data(data):
    data2 = []

    for sent in data:
        data2.append(" ".join(sent))
    data3 = "\n".join(data2)
    return data3

def txt2none(txt):
    txt = txt.strip()
    if txt == "_":
        return None
    else:
        return txt


def format_ud_data(data):
    data2 = []
    sentences = re.split(r"\n# sent_id = \d+\n", data)
    for sent in sentences[1:]:
        splt = sent.strip().split("\n")
        sent2 = []
        for item in splt:

            splt2 = item.strip().split("\t")

            ud_item = {
                'id' : splt2[0],
                'form' : splt2[1],
                'upos' : txt2none(splt2[3]),
                'xpos' : txt2none(splt2[4]),
                'feats' : txt2none(splt2[5]),
                'head' : txt2none(splt2[6]),
                'deprel' : txt2none(splt2[7]),
                'deps' : txt2none(splt2[8]),
                'misc' : txt2none(splt2[9])
            }
            sent2.append(ud_item)
        data2.append(sent2)
    return data2

def get_tokens(s):
    sentence = []
    for item in s:
        if item.tag in ['{http://www.tei-c.org/ns/1.0}w','{http://www.tei-c.org/ns/1.0}pc']:
            sentence.append(item)

    return sentence

def update_tagsdecl(root, tags):
    tagsDecl = root.find(".//tei:tagsDecl", ns)
    namespace = tagsDecl.find(".//tei:namespace", ns)

    for tag in tags:

        tagusage = ET("tagUsage")
        tagusage.attrib['occurs'] = str(tags[tag])
        tagusage.attrib['gi'] = tag
        namespace.append(tagusage)

path2ana = "/media/starkadur/NewVolume/ParlaMint-IS/ParlaMint-IS.ana"
path2ana2 = "/media/starkadur/NewVolume/ParlaMint-IS/ParlaMint-IS.ana2"
path2taggermodel = "/home/starkadur/PycharmProjects/morkun_lemmun/tagger-v2.0.0.pt"
path2UDmodel = "../is_icepahc.model"

#load UD_model
model = Model.load(path2UDmodel)

if not model:
    sys.stderr.write("Cannot load model from file '%s'\n" % sys.argv[3])
    sys.exit(1)
sys.stderr.write('UD model lodaed\n')

pipeline = Pipeline(model, "horizontal", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
error = ProcessingError()

parser = etree.XMLParser(remove_blank_text=True)
ns = {'tei': "http://www.tei-c.org/ns/1.0"}
files = [f for f in listdir(path2ana) if isfile(join(path2ana, f)) and f.startswith("ParlaMint-IS_")]
for file in files:

    path2file = join(path2ana, file)
    filename_ana2 = join(path2ana2, file)

    if os.path.exists(filename_ana2):
        continue
    print(file)
    tree = etree.parse(path2file, parser)
    root = tree.getroot()
    count_link = 0
    count_linkgrp = 0

    #start_time = time.time()
    #ítra yfir seg og skrá s og w
    data = []
    for s in root.findall(".//tei:s", ns):
        sentence = []
        for item in s:
            if item.tag in ['{http://www.tei-c.org/ns/1.0}w','{http://www.tei-c.org/ns/1.0}pc']:
                sentence.append(item.text)

        data.append(sentence)

    data = format_data(data)
    processed = pipeline.process(data, error)
    sents_ud = format_ud_data(processed)
    sents_xml = root.findall(".//tei:s", ns)
    if len(sents_ud)!=len(sents_xml):
        print(len(sents_ud))
        print(len(sents_xml))
        exit()

    for sent_xml, sent_ud in zip(sents_xml, sents_ud):
        sent_xml_id = sent_xml.attrib['{http://www.w3.org/XML/1998/namespace}id']
        links = []
        tokens_xml = get_tokens(sent_xml)
        for i in range(0, len(tokens_xml)):
            token_ud = sent_ud[i]
            token_xml = tokens_xml[i]


            if token_xml.text != token_ud['form']:
                print("VILLA:")
                print(token_xml.text, token_ud['form'])
            if token_ud['deps'] or token_ud['misc']:
                print(token_ud)

            if token_ud['deprel']:
                head_id = int(token_ud['head'])

                if head_id == 0:
                    head = sent_xml_id
                else:
                    head = tokens_xml[head_id-1].attrib['{http://www.w3.org/XML/1998/namespace}id']

                links.append(["ud-syn:{}".format(token_ud['deprel'].replace(":","_")),
                              head,
                              token_xml.attrib['{http://www.w3.org/XML/1998/namespace}id'],
                              ])

            if token_ud['feats']:
                msd = "UPosTag={}|{}".format(token_ud['upos'], token_ud['feats'])
            else:
                msd = "UPosTag={}".format(token_ud['upos'])
            token_xml.attrib['msd'] = msd

        #búa til linkGrp
        linkGrp = ET("linkGrp")
        linkGrp.attrib['targFunc'] = "head argument"
        linkGrp.attrib['type'] = "UD-SYN"
        sent_xml.append(linkGrp)
        count_linkgrp+=1
        for link in links:

            link_ = ET("link")
            link_.attrib['ana'] = link[0]
            link_.attrib['target'] = "#{} #{}".format(link[1], link[2])

            linkGrp.append(link_)
            count_link+=1

    dict_ = OrderedDict()
    dict_['linkGrp'] = count_linkgrp
    dict_['link'] = count_link
    update_tagsdecl(root, dict_)
    et = etree.ElementTree(root)
    et.write(filename_ana2, pretty_print=True,encoding="UTF-8",xml_declaration=True)
