import sys
sys.path.append('./')
from services import Gru4rec, evaluation
from constant import data_key
import _pickle as cPickle
import os
import tensorflow as tf

import pandas as pd
import argparse


def main(args):
    local_data_dir = args.local_data_dir
    model_dir = args.model_dir
    train_file_name = args.train_file_name
    batch_size = args.batch_size

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # reading data locally
    data = pd.read_csv(local_data_dir.format(train_file_name), sep=',')
    data.dropna(inplace = True)
    data[data_key.ITEM_KEY] = pd.to_numeric(data[data_key.ITEM_KEY])
    test = data[data[data_key.TIME_KEY] >= (max(data[data_key.TIME_KEY]) - 86400)]
    data = data[data[data_key.TIME_KEY]<(max(data[data_key.TIME_KEY])-86400)]

    gru = Gru4rec.Gru4rec(is_straining=True,
                          session_key=data_key.SESSION_KEY,
                          item_key=data_key.ITEM_KEY,
                          time_key=data_key.TIME_KEY,
                          batch_size=20,
                          embedding=50,
                          initializer=tf.random_normal_initializer(stddev=0.1),
                          hidden_act='tanh',
                          final_act='elu-0.5',
                          loss="bpr",
                          grad_cap=0,
                          layers=[50],
                          rnn_size=50,
                          n_epochs=5,
                          dropout_p_hidden=0,
                          learning_rate=0.1,
                          checkpoint_dir=model_dir)

    gru_config = cPickle.load(open(model_dir+"/gru4rec_config", "rb"))
    for cut_off in [10, 20]:
        res = evaluation.evaluation_gru4rec(test_data=test, train_data=data, items=None, cut_off=cut_off, is_items_vs_all=True, is_out_of_time=False,
                        session_key=data_key.SESSION_KEY, item_key=data_key.ITEM_KEY, time_key=data_key.TIME_KEY,
                        gru=gru, gru_config=gru_config, batch_size=int(batch_size))

        print('Recall@{}: {}'.format(cut_off, res[0]))

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('local_data_dir', type=str, help='Data directory', default="./gru/data/{}")
    parser.add_argument('model_dir', type=str, help='Model checkpoint directory', default="./gru/checkpoints/")
    parser.add_argument("train_file_name", type=str, help="train data file name", default="sample_data.csv")
    parser.add_argument("batch_size", type=int, help="Batch size", default="400")
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))