import color_text
import sys
import pandas as pd
import numpy as np

import os
import argparse
import time
import random
import utils
import pdb

import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.functional as F
import torch.optim as optim

from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from data import PaddedTensorDataset
from data import TextLoader
from model import LSTMClassifier


def main():

    lets,sylls=color_text.get_syll_df()

    sys.stdout=sys.__stdout__
    print ("Train.py:\n\n")
    print (sylls)

    train(sylls)




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

if __name__=="__main__":
   main()
