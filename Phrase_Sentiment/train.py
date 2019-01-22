import os
import sys
import argparse
import time
import random
import math

import pandas as pd
import numpy as np
import keras

import color_text
from Models.LSTM import LSTM

def main(maxlines=-1):

    lets,sylls=color_text.get_sylls(max=maxlines)

    sys.stdout=sys.__stdout__
    print ("\n\nTrain.py:)
    print (sylls)

    sylls.to_csv("syllables.csv",index=True,encoding='utf-8')

    wordIx=sylls.columns.get_loc(color_text.DICT)
    scoreIx=sylls.columns.get_loc('Score')
    lenIx=sylls.columns.get_loc('Len')
    rdIx=sylls.columns.get_loc('Rd')
    spIx=sylls.columns.get_loc('Sp')
    vwIx=sylls.columns.get_loc('Vw')
    obIx=sylls.columns.get_loc('Ob')
    endIx=sylls.columns.get_loc('IsEnd')

    batch_len=16

    extra=sylls.shape[0]%batch_len
    #sylls=sylls.append(np.zeros((extra,sylls.shape[1])))

    batches=math.ceil(sylls.shape[0]/batch_len)
    print (batch_len,extra,sylls.shape,batches)


    score_resolution=20
    input_ct=sylls.shape[1]-2
    lstm=LSTM(input_ct,score_resolution,batch_len)

    data=sylls.values[:,lenIx:endIx]


    #Labels = int (score * 100)
    labels=np.array(sylls.values[:,scoreIx]*score_resolution/5.,dtype=int)
    labels[labels>=score_resolution]=score_resolution-1
    #One-hot encode
    labels = keras.utils.to_categorical(labels,num_classes=score_resolution)

    print (data.shape)
    print (labels.shape)



    trainAmt=int(data.shape[0]*.9)
    if data.shape[0]-trainAmt > 10000:
        trainAmt=data.shape[0]-10000
    print ("train amt=",trainAmt)


    lstm.train(data[:trainAmt],labels[:trainAmt],display=True)

    score=lstm.test(data[trainAmt:],labels[trainAmt:])

    print ("\n\n\n ----------- Final Score = ",score,'--------------')

    #lstm.train(sylls.)

'''
def train(sylls,hidden_dim=32,batch_size=32,num_epochs=5,char_dim=128,alpha=.01,weight_decay=1e-4,seed=0):

	random.seed(seed)

    """
    data_loader = TextLoader(args.data_dir)

	train_data = data_loader.train_data
	dev_data = data_loader.dev_data
	test_data = data_loader.test_data

	char_vocab = data_loader.token2id
	tag_vocab = data_loader.tag2id
	char_vocab_size = len(char_vocab)
    """

	print('Training samples:', len(train_data))
	print('Valid samples:', len(dev_data))
	print('Test samples:', len(test_data))

	print(char_vocab)
	print(tag_vocab)

	model = LSTMClassifier(char_vocab_size, char_dim, hidden_dim, len(tag_vocab))
	optimizer = optim.SGD(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

	model = train_model(model, optimizer, train_data, dev_data, char_vocab, tag_vocab, args.batch_size, args.num_epochs)

	evaluate_test_set(model, test_data, char_vocab, tag_vocab)



def apply(model, criterion, batch, targets, lengths):
    pred = model(torch.autograd.Variable(batch), lengths.cpu().numpy())
    loss = criterion(pred, torch.autograd.Variable(targets))
    return pred, loss


def train_model(model, optimizer, train, dev, x_to_ix, y_to_ix, batch_size, max_epochs):
    criterion = nn.NLLLoss(size_average=False)
    for epoch in range(max_epochs):
        print('Epoch:', epoch)
        y_true = list()
        y_pred = list()
        total_loss = 0
        for batch, targets, lengths, raw_data in utils.create_dataset(train, x_to_ix, y_to_ix, batch_size=batch_size):
            batch, targets, lengths = utils.sort_batch(batch, targets, lengths)
            model.zero_grad()
            pred, loss = apply(model, criterion, batch, targets, lengths)
            loss.backward()
            optimizer.step()

            pred_idx = torch.max(pred, 1)[1]
            y_true += list(targets.int())
            y_pred += list(pred_idx.data.int())
            total_loss += loss
        acc = accuracy_score(y_true, y_pred)
        val_loss, val_acc = evaluate_validation_set(model, dev, x_to_ix, y_to_ix, criterion)
        print("Train loss: {} - acc: {} \nValidation loss: {} - acc: {}".format(list(total_loss.data.float())[0]/len(train), acc,
                                                                                val_loss, val_acc))
    return model


def evaluate_validation_set(model, devset, x_to_ix, y_to_ix, criterion):
    y_true = list()
    y_pred = list()
    total_loss = 0
    for batch, targets, lengths, raw_data in utils.create_dataset(devset, x_to_ix, y_to_ix, batch_size=1):
        batch, targets, lengths = utils.sort_batch(batch, targets, lengths)
        pred, loss = apply(model, criterion, batch, targets, lengths)
        pred_idx = torch.max(pred, 1)[1]
        y_true += list(targets.int())
        y_pred += list(pred_idx.data.int())
        total_loss += loss
    acc = accuracy_score(y_true, y_pred)
    return list(total_loss.data.float())[0]/len(devset), acc


def evaluate_test_set(model, test, x_to_ix, y_to_ix):
    y_true = list()
    y_pred = list()

    for batch, targets, lengths, raw_data in utils.create_dataset(test, x_to_ix, y_to_ix, batch_size=1):
        batch, targets, lengths = utils.sort_batch(batch, targets, lengths)

        pred = model(torch.autograd.Variable(batch), lengths.cpu().numpy())
        pred_idx = torch.max(pred, 1)[1]
        y_true += list(targets.int())
        y_pred += list(pred_idx.data.int())

    print(len(y_true), len(y_pred))
    print(classification_report(y_true, y_pred))
    print(confusion_matrix(y_true, y_pred))
'''
if __name__=="__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("max", type=int,default=-1,help="Amount of words to analyze.",nargs="?")
    #parser.add_argument("--run",default=False,action='store_true', help="Whether to run model")

    args = parser.parse_args()

    main(args.max)
