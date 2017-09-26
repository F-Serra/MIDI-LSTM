import codecs
import os
import collections
from six.moves import cPickle
import numpy as np


class TextLoader():
    def __init__(self, data_dir, batch_size, seq_length, encoding='utf-8'):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.encoding = encoding

        input_file = os.path.join(data_dir, "messages.npy")
        #vocab_file = os.path.join(data_dir, "vocab.pkl")
        #tensor_file = os.path.join(data_dir, "data.npy")

        self.preprocess(input_file)        
        self.create_batches()
        self.reset_batch_pointer()

    def preprocess(self, input_file):
        data = np.load(input_file)
        counter = collections.Counter(data)
        count_pairs = sorted(counter.items(), key=lambda x: -x[1])
        #print("count pairs", count_pairs)
        self.chars, _ = zip(*count_pairs)
        #print("chars", self.chars)
        self.vocab_size = len(self.chars)
        #print("vocab size", self.vocab_size)
        self.vocab = dict(zip(self.chars, range(len(self.chars))))
        #with open(vocab_file, 'wb') as f:
        #    cPickle.dump(self.chars, f)
        self.tensor = np.array(list(map(self.vocab.get, data)))
        #np.save(tensor_file, self.tensor)    

    def create_batches(self):
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))

        # When the data (tensor) is too small,
        # let's give them a better error message
        if self.num_batches == 0:
            assert False, "Not enough data. Make seq_length and batch_size small."

        self.tensor = self.tensor[:self.num_batches * self.batch_size * self.seq_length]
        xdata = self.tensor
        ydata = np.copy(self.tensor)
        ydata[:-1] = xdata[1:]
        ydata[-1] = xdata[0]
        self.x_batches = np.split(xdata.reshape(self.batch_size, -1),
                                  self.num_batches, 1)
        self.y_batches = np.split(ydata.reshape(self.batch_size, -1),
                                  self.num_batches, 1)

    def next_batch(self):
        x, y = self.x_batches[self.pointer], self.y_batches[self.pointer]
        self.pointer += 1
        return x, y

    def reset_batch_pointer(self):
        self.pointer = 0

#MidiLoader("data", 4, 2)