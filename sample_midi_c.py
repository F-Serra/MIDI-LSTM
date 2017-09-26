from __future__ import print_function
import tensorflow as tf

import argparse
import os
from six.moves import cPickle

from model_midi_c import Model
from utils_midi_c import TextLoader
import numpy2midi
#from six import text_type


def main():
    parser = argparse.ArgumentParser(
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--save_dir', type=str, default='save',
                        help='model directory to store checkpointed models')
    parser.add_argument('-n', type=int, default=12000,
                        help='number of notes to sample')
    parser.add_argument('-prime', type=int, default=2030,
                        help='number of prime notes')
    parser.add_argument('--sample', type=int, default=0,
                        help='0 to use max at each timestep, 1 to sample at '
                             'each timestep, 2 to sample on spaces')

    args = parser.parse_args()
    sample(args)


def sample(args):
    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    #with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
    #    chars, vocab = cPickle.load(f)
    data_loader = TextLoader(saved_args.data_dir, saved_args.batch_size, saved_args.seq_length)
    saved_args.vocab_size = data_loader.vocab_size
    model = Model(saved_args, training=False)
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            ret, ret_wo = model.sample(sess, data_loader.chars, data_loader.vocab, args.n, args.sample, args.prime)
            numpy2midi.convert_c(ret,"song-")
            numpy2midi.convert_c(ret_wo,"song-wo-")

if __name__ == '__main__':
    main()
