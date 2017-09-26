import tensorflow as tf
from tensorflow.contrib import rnn
from tensorflow.contrib import legacy_seq2seq

import numpy as np


class Model():
    def __init__(self, args, training=True):
        self.args = args
        if not training:
            args.batch_size = 1
            args.seq_length = 1

        if args.model == 'rnn':
            cell_fn = rnn.BasicRNNCell
        elif args.model == 'gru':
            cell_fn = rnn.GRUCell
        elif args.model == 'lstm':
            cell_fn = rnn.BasicLSTMCell
        elif args.model == 'nas':
            cell_fn = rnn.NASCell
        else:
            raise Exception("model type not supported: {}".format(args.model))

        cells = []
        for _ in range(args.num_layers):
            cell = cell_fn(args.rnn_size)
            if training and (args.output_keep_prob < 1.0 or args.input_keep_prob < 1.0):
                cell = rnn.DropoutWrapper(cell,
                                          input_keep_prob=args.input_keep_prob,
                                          output_keep_prob=args.output_keep_prob)
            cells.append(cell)

        self.cell = cell = rnn.MultiRNNCell(cells, state_is_tuple=True)

        self.input_data = tf.placeholder(
            tf.int32, [args.batch_size, args.seq_length])
        self.targets = tf.placeholder(
            tf.int32, [args.batch_size, args.seq_length])
        self.initial_state = cell.zero_state(args.batch_size, tf.float32)

        with tf.variable_scope('rnnlm'):
            softmax_w = tf.get_variable("softmax_w",
                                        [args.rnn_size, args.vocab_size])
            softmax_b = tf.get_variable("softmax_b", [args.vocab_size])

        embedding = tf.get_variable("embedding", [args.vocab_size, args.rnn_size])
        inputs = tf.nn.embedding_lookup(embedding, self.input_data)

        # dropout beta testing: double check which one should affect next line
        if training and args.output_keep_prob:
            inputs = tf.nn.dropout(inputs, args.output_keep_prob)
        #print(inputs)
        inputs = tf.split(inputs, args.seq_length, 1)
        #print(inputs[0])
        #type(inputs)
        inputs = [tf.squeeze(input_, [1]) for input_ in inputs]

        def loop(prev, _):
            prev = tf.matmul(prev, softmax_w) + softmax_b
            prev_symbol = tf.stop_gradient(tf.argmax(prev, 1))
            return tf.nn.embedding_lookup(embedding, prev_symbol)

        #print(inputs)
        #type(inputs)

        outputs, last_state = legacy_seq2seq.rnn_decoder(inputs, self.initial_state, cell, loop_function=loop if not training else None, scope='rnnlm')
        output = tf.reshape(tf.concat(outputs, 1), [-1, args.rnn_size])


        self.logits = tf.matmul(output, softmax_w) + softmax_b
        self.probs = tf.nn.softmax(self.logits)
        loss = legacy_seq2seq.sequence_loss_by_example(
                [self.logits],
                [tf.reshape(self.targets, [-1])],
                [tf.ones([args.batch_size * args.seq_length])])
        self.cost = tf.reduce_sum(loss) / args.batch_size / args.seq_length
        with tf.name_scope('cost'):
            self.cost = tf.reduce_sum(loss) / args.batch_size / args.seq_length
        self.final_state = last_state
        self.lr = tf.Variable(0.0, trainable=False)
        tvars = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(tf.gradients(self.cost, tvars),
                args.grad_clip)
        with tf.name_scope('optimizer'):
            optimizer = tf.train.AdamOptimizer(self.lr)
        self.train_op = optimizer.apply_gradients(zip(grads, tvars))

        # instrument tensorboard
        tf.summary.histogram('logits', self.logits)
        tf.summary.histogram('loss', loss)
        tf.summary.scalar('train_loss', self.cost)

    def sample(self, sess, chars, vocab, num=1000, sampling_type=0, prime=500):
        state = sess.run(self.cell.zero_state(1, tf.float32))

        msg_list = np.load("data/messages.npy")
        r_pos  = np.random.randint(0, len(msg_list)-prime)
        prime_list = msg_list[r_pos:r_pos+prime]

        for char in prime_list[:-1]:
            x = np.zeros((1, 1))
            x[0, 0] = vocab[char]
            feed = {self.input_data: x, self.initial_state: state}
            [state] = sess.run([self.final_state], feed)

        def weighted_pick_c(weights):
            max_w = np.argmax(weights)
            if max_w <128:
                t = np.cumsum(weights)
                s = np.sum(weights)
                return(int(np.searchsorted(t, np.random.rand(1)*s)))
            else:
                return max_w

        def weighted_pick_c_2(weights):
            max_w = np.argmax(weights)
            if max_w <128:
                t = np.cumsum(weights[:128])
                s = np.sum(weights[:128])
                return(int(np.searchsorted(t, np.random.rand(1)*s)))
            else:
                return max_w

        def weighted_pick(weights):
            t = np.cumsum(weights)
            s = np.sum(weights)
            return(int(np.searchsorted(t, np.random.rand(1)*s)))            

        ret = np.zeros(prime+num)
        ret[:prime] = prime_list
        char = prime_list[-1]
        for n in range(num):
            x = np.zeros((1, 1))
            x[0, 0] = vocab[char]
            feed = {self.input_data: x, self.initial_state: state}
            [probs, state] = sess.run([self.probs, self.final_state], feed)
            p = probs[0]

            if sampling_type == 0:
                sample = np.argmax(p)
            elif sampling_type == 1:
                sample = weighted_pick_c(p)
            elif sampling_type == 2: 
                sample = weighted_pick_c_2(p)
            elif sampling_type == 3:            	
                if n%12==0:
                	sample = weighted_pick_c_2(p)
                else:
                	sample = np.argmax(p)
            elif sampling_type == 4: 
                sample = weighted_pick(p)

            pred = chars[sample]
            ret[prime+n] = pred
            char = pred

        ret_wo = ret[prime:]
        return ret, ret_wo
