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

sys.path.append(os.path.join(os.path.dirname(__file__), '../../ymislegt/'))
from risamalheild import various

class Morkun:

    def __init__(self, input_type):

        self.input_type = input_type
        path2taggermodel = "/home/starkadur/PycharmProjects/morkun_lemmun/tagger-v2.0.0.pt"

        # Initialize the tagger
        self.tagger = pos.Tagger(
            model_file=path2taggermodel,
            device="cpu",
        )

        logging.getLogger("pos").setLevel(logging.ERROR)


    def clean_text(self, text):
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

    def split2paragraphs(self, text):
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

    def tokenize(self, text):

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

    def text2bulk(self, sents):
        data = []
        for sent in sents:
            data.append(sent.split(" "))
        return data

    def tag_text(self, sentences_tokenized):
        data = None

        try:
            bulk= self.text2bulk(sentences_tokenized)
            tags = self.tagger.tag_bulk(bulk)
            data = self.join_token_tag(bulk, tags)


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
                data = self.join_token_tag(bulk, tags)
            except RuntimeError:
                print("Setning enn of löng")
                exit()

            except IndexError:
                print("Index error í tagger.tag_sent")
                print(sentence)
                exit()

        return data

    def join_token_tag(self, tokens_sent, tags_sent):

        data = []

        for sent_tokens, sent_tags in zip(tokens_sent, tags_sent):

            sent = []
            for token, tag in zip(sent_tokens, sent_tags):

                sent.append([token, tag])
            data.append(sent)

        return data

    def plain2sents(self, text):

        sentences_tokenized = []
        sentences = re.split(r'\n\n+',text)
        for sent in sentences:
            sent2 = []
            for item in sent.split("\n"):

                sent2.append(item.split("\t")[0].strip())
            sentences_tokenized.append(" ".join(sent2))

        return sentences_tokenized

    def tag(self, text):

        text = text.strip()

        if self.input_type == "normal":
            text = self.clean_text(text)
            p = self.split2paragraphs(text)

            text = "\n".join(p)

            text_tokenized = self.tokenize(text)
            sentences_tokenized = text_tokenized.split("\n")

        elif self.input_type == "plain":
            sentences_tokenized = self.plain2sents(text)


        tagged_text = self.tag_text(sentences_tokenized)
        return tagged_text

    def write_to_file(self, data, path2file):

        with open(path2file,"w") as f_w:
            for sentence in data:
                for item in sentence:
                    f_w.write("\t".join(item)+"\n")
                f_w.write("\n")

    def text2dataFormat(self, text):

        data = []
        sentences = re.split(r'\n\n+',text)
        for sent in sentences:
            sent2 = []
            for item in sent.split("\n"):

                sent2.append(item.split("\t"))

            data.append(sent2)

        return data

    def join_data_and_text(self, data, text):

        data_joined = []
        data_text = self.text2dataFormat(text)
        if len(data_text) != len(data):
            print("VILLA 1")
            exit()
        for sent1, sent2 in zip(data_text, data):
            sent = []
            if len(sent1) != len(sent2):
                print("VILLA 2")
                exit()
            for item1, item2 in zip(sent1, sent2):
                sent.append([item1[0], item1[1], item2[1]])
            data_joined.append(sent)

        return data_joined

    #tekur sem stika ...
    #  data: listi setninga sem eru listi lína sem eru listi með tóka og marki
    #  text: upprunalegi texti sem var sendur til mörkunar (plain form)
    #  path2file: slóð á output-skjal
    def write_to_file2(self, data, text, path2file):

        data = self.join_data_and_text(data, text.strip())

        with open(path2file,"w") as f_w:
            for sentence in data:
                for item in sentence:
                    f_w.write("\t".join(item)+"\n")
                f_w.write("\n")
