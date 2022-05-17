# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 20:19:14 2020

@author: Benedikt
"""

import json
import torch
import numpy as np
import configparser

from keras.preprocessing.sequence import pad_sequences
from transformers import (BertForTokenClassification,
                          BertTokenizer,
                          )

class NERTag:

    def __init__(self):
        self.model, self.tag2name = self.load_model()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased',
                                                  do_lower_case=False)

    def get_tag2idx(self, file_path):
        with open(file_path) as json_file:
            tag2idx = json.load(json_file)
        return tag2idx


    def get_tag2name(self, file_path):
        with open(file_path) as json_file:
            tag2name = json.load(json_file)
        return tag2name


    #def tag_tokenized(self, tokenized_texts):

    #takes one sentence, split it into segments if it is too long, before tagging it. Then joins again.
    def tag_sentence(self, test_query):


        max_len  = 75
        tokenized_texts = []
        temp_token = []

        token_list = self.tokenizer.tokenize(test_query)
        words = []
        word = []
        cnt = 0
        for m,token in enumerate(token_list):
            cnt+=1
            if token.find("##")!=0:
                words.append(word)
                word = []
            word.append(token)
        words.append(word)

        temp_tokens_split = []
        cnt = 0
        temp_token = ['CLS']
        for word in words:
            if len(temp_token)+len(word)>=max_len-1:
                temp_token.append("[SEP]")
                temp_tokens_split.append(temp_token)
                temp_token = ['CLS']

            temp_token+=word
        if len(temp_token)>1:
            temp_token.append("[SEP]")
            temp_tokens_split.append(temp_token)

        cnt = 0
        output = []
        out = []
        for temp_token in temp_tokens_split:

            tokenized_texts.append(temp_token)

            input_ids = pad_sequences([self.tokenizer.convert_tokens_to_ids(txt) for txt in tokenized_texts],
                                      maxlen=max_len, dtype="long", value=0.0,
                                      truncating="post", padding="post")

            attention_masks = [[int(i>0) for i in ii] for ii in input_ids]
            segment_ids = [[0] * len(input_id) for input_id in input_ids]

            input_ids = torch.tensor(input_ids).to(torch.int64).to(self.device)
            attention_masks = torch.tensor(attention_masks).to(torch.int64).to(self.device)
            segment_ids = torch.tensor(segment_ids).to(torch.int64).to(self.device)

            #self.model.eval();

            with torch.no_grad():
                    outputs = self.model(input_ids, token_type_ids=None, attention_mask=None)
                    logits = outputs[0]

            predict_results = logits.detach().cpu().numpy()

            from scipy.special import softmax

            result_arrays_soft = softmax(predict_results[0])

            result_array = result_arrays_soft

            result_list = np.argmax(result_array,axis=-1)

            test = [x[0:2] != '##' for x in temp_token]
            test = np.where(test)

            temp_string = ' '.join(temp_token).replace(' ##', '')
            temp_string_list = temp_string.split(' ')


            for i,j in zip(range(len(temp_string_list)), test[0]):
                if i == 0 or i == len(temp_string_list)-1:
                    pass
                else:
                    out.append((temp_string_list[i], self.tag2name[str(result_list[j])]))

        return out


    def load_model(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        SAVED_MODEL_PATH = config['PATHS']['model_default_load']
        TAG2IDX_PATH = config['PATHS']['tag2idx']
        TAG2NAME_PATH = config['PATHS']['tag2name']

        tag2idx = self.get_tag2idx(TAG2IDX_PATH)
        tag2name = self.get_tag2name(TAG2NAME_PATH)
        model = BertForTokenClassification.from_pretrained('bert-base-multilingual-cased',
                                                           num_labels=len(tag2idx))


        model.load_state_dict(torch.load(SAVED_MODEL_PATH,map_location=torch.device('cpu')))

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        return model, tag2name
