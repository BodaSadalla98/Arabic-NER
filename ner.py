from genericpath import exists
import pandas as pd
import numpy as np
from helpers.download_model  import download_file_from_google_drive
from transformers import AutoConfig, AutoModelForTokenClassification, AutoTokenizer, BertForTokenClassification
from helpers.helper import en_to_ar
import torch
import os
import gdown
MODEL_NAME = 'aubmindlab/bert-base-arabertv02'

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

file_url ='https://drive.google.com/uc?id=1Ebvc67HJQ5I9M6LfdzAiOVx5iiyVO9LN'
file_id = '1Ebvc67HJQ5I9M6LfdzAiOVx5iiyVO9LN'


parent_folder = DIR_PATH + "/model/ours/"
destination =  parent_folder+ "full_model_v2.pt"
print(destination)


label_list_url = 'https://drive.google.com/uc?id=1th3j28peQf-asgodeaGo-04aIARN0QoL'
label_list_dest = parent_folder+ "label_list.txt"

if not os.path.exists(destination):
    
    os.makedirs(parent_folder, exist_ok=True)
    # download_file_from_google_drive(file_id, destination)
    gdown.download(file_url, destination, quiet=False)
    gdown.download(label_list_url, label_list_dest, quiet=False)
    


TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)




label_list = list(pd.read_csv(f'{DIR_PATH}/model/ours/label_list.txt', header=None, index_col=0).T)
label_map = { v:index for index, v in enumerate(label_list) }
inv_label_map = {i: label for i, label in enumerate(label_list)}


model = torch.load(destination ,map_location='cpu')
model.eval()

def predict_sent(sentences):

    sentences = sentences.split('\n')
    for s in sentences:
        print( 'HERE', s)
    # input_ids  = TOKENIZER.encode(sentences, return_tensors='pt')
    out = TOKENIZER.batch_encode_plus(sentences, return_tensors='pt',padding=True)
    result = ''

    input_ids = out.input_ids
    attention_mask = out.attention_mask

    with torch.no_grad():
        model.to('cpu')
        output = model(input_ids,attention_mask)

    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)


    tokens = [TOKENIZER.convert_ids_to_tokens(x.to('cpu').numpy()) for x in input_ids]

    new_tokens, new_labels = [], []
    for sent_tokens , sent_labels in zip(tokens, label_indices):
        for token, label_idx  in zip(sent_tokens , sent_labels):
            if token.startswith("##"):
                new_tokens[-1] = new_tokens[-1] + token[2:]
            elif token in TOKENIZER.all_special_tokens:
                continue
            else:
                new_labels.append(inv_label_map[label_idx])
                new_tokens.append(token)


    for token, label in zip(new_tokens, new_labels):
        if(label == 'O'):
            continue
        print("{}\t{}".format(label, token))
        s = f"{en_to_ar[label]}     {label}      {token}"
        result = result + s + '\n'
    return result, new_labels, new_tokens



print(predict_sent(" النجم محمد صلاح لاعب المنتخب المصري يعيش في مصر بالتحديد من المنصوره"))