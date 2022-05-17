#sækir xml-skjöl og tókar, markar og lemmar texta.
#TODO: uppfæra pos og marka með pos_bulk í stað pos_sent

import os
import sys
import tokenizer
import pos
import re
from os.path import join, dirname, isdir, isfile
import json
import logging
import argparse

sys.path.append(join(dirname(__file__), '../nefnir/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../ymislegt/'))
from nefnir import Nefnir
from risamalheild import various

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

    return output.strip()


def text2bulk(sents):
    data = []
    for sent in sents:
        data.append(sent.split(" "))
    return data

def lemmatize(tokens, tags):

    lemmas = {}
    for w, t in zip (tokens, tags):

        try:
            lemma = nefnir.lemmatize(w,t)
            lemmas["{} {}".format(w, t)] = lemma
        except ValueError:
            if line:
                logger.warning('Ignoring line: {}'.format(line))

    return lemmas

def join_token_tag_lemma(tokens_sent, tags_sent, lemmas):

    data = []

    for sent_tokens, sent_tags in zip(tokens_sent, tags_sent):

        sent = []
        for token, tag in zip(sent_tokens, sent_tags):

            sent.append([token, tag, lemmas["{} {}".format(token, tag)]])
        data.append(sent)

    return data

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

def clean_text(text):
    re_end = re.compile(r'(?:(?:°##°|°°°°)[ \n]*)+$')
    re_begin = re.compile(r'^(?:[ \n]*(?:°##°|°°°°))+')
    re_multiple = re.compile(r'((°°°°|°##°)[ \n]+)+')

    text = various.clean_unicode_symbols(text)
    #breyta tab í bil
    text = re.sub(r"\t"," ", text).strip()
    #breyta mörgum stafbilum í eitt
    text = re.sub(r'  +'," ",text)
    #eyða táknum úr upphafi texta
    text = re_begin.sub("", text)
    #eyða táknum úr lok texta
    text = re_end.sub("", text)
    #breyta fjölda tákna í eitt
    text = re_multiple.sub("°°°°\n", text)
    text = text.strip()

    return text

def split2paragraphs(text):
    re_split = re.compile(r'(?:[ \n]*(?:°##°|°°°°) *\n[ \n]*)+')
    splt = re_split.split(text)
    paragraphs = []
    for item in splt:
        splt2 = re.split(r"\n", item.strip())
        for par in splt2:
            par = par.strip()
            if par!="":

                if re.search(r'(?:°##°|°°°°)', item):
                    print(par)
                    print(text_or)
                    print("################")
                    print(text)
                    print("---------------")
                    print(path2file)
                    print()

                    return None
                paragraphs.append(par)


    return paragraphs

def get_tagged_text(path2plain):
    data = None
    with open(path2plain, "r") as f:
        text = f.read()

    text = clean_text(text)
    p = split2paragraphs(text)
    text = "\n".join(p)

    text_tokenized = tokenize(text)
    sentences_tokenized = text_tokenized.split("\n")

    try:
        bulk= text2bulk(sentences_tokenized)
        tags = tagger.tag_bulk(bulk)
        lemmas = lemmatize_bulk(bulk, tags)
        data = join_token_tag_lemma(bulk, tags, lemmas)


    except IndexError:
        print("INdex errr ...")
        print(text_tokenized)
        exit()

    except ValueError:
        print("Bad Value Error ...")
        print(sentences_tokenized)
        exit()

    except RuntimeError:
        print("Setning of löng")
        tags = []
        try:
            for sentence in text_tokenized:
                tags.append(tagger.tag_sent(sentence.split(" ")))
            lemmas = lemmatize_bulk(bulk, tags)
            data = join_token_tag_lemma(bulk, tags, lemmas)
        except RuntimeError:
            print("Setning enn of löng")
            exit()

        except IndexError:
            print("Index error í tagger.tag_sent")
            print(sentence)
            exit()

    return data

def write2file(path2file, data):

    with open(path2file,"w") as f_w:
        for sentence in data:
            for item in sentence:
                f_w.write("\t".join(item)+"\n")
            f_w.write("\n")


path2taggermodel = "/home/starkadur/PycharmProjects/morkun_lemmun/tagger-v2.0.0.pt"
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--input", help="path to plain text")
arg_parser.add_argument("--output", help="path to output files")
args = arg_parser.parse_args()

path2file = args.input
path2output = args.output

# Initialize the tagger
tagger = pos.Tagger(
    model_file=path2taggermodel,
    device="cpu",
)
logging.getLogger("pos").setLevel(logging.ERROR)

# read rules and tagset for Nefnir
with open("/home/starkadur/PycharmProjects/morkun_lemmun/nefnir/gull_rules.json", encoding='utf-8') as f:
    rules = json.load(f)

with open("/home/starkadur/PycharmProjects/morkun_lemmun/nefnir/gull_tagset.json", encoding='utf-8') as f:
    tagset = json.load(f)

#Initialize Nefnir
nefnir = Nefnir(rules, tagset)
logging.getLogger("nefnir").setLevel(logging.ERROR)


#path2file = "/mnt/gagnageymsla/tmp/2021/bb/11/2021_11_ny-slokkvistod-a-isafirdi-unnid-ad-stadarvalsgreiningu.txt"

data = get_tagged_text(path2file)

write2file(path2output, data)
