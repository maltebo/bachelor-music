from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import numpy as np
import warnings
import os
import sys

import time
from keras.callbacks import Callback, TensorBoard
import keras.backend as K


class ModelCheckpointBatches(Callback):
    """Save the model after every batch.

    # Arguments
        filepath: string, path to save the model file.
        monitor: quantity to monitor.
        verbose: verbosity mode, 0 or 1.
        save_best_only: if `save_best_only=True`,
            the latest best model according to
            the quantity monitored will not be overwritten.
        mode: one of {auto, min, max}.
            If `save_best_only=True`, the decision
            to overwrite the current save file is made
            based on either the maximization or the
            minimization of the monitored quantity. For `val_acc`,
            this should be `max`, for `val_loss` this should
            be `min`, etc. In `auto` mode, the direction is
            automatically inferred from the name of the monitored quantity.
        save_weights_only: if True, then only the model's weights will be
            saved (`model.save_weights(filepath)`), else the full model
            is saved (`model.save(filepath)`).
        period: Interval (number of batches) between checkpoints.
    """

    def __init__(self, temp_save_path, monitor='loss', verbose=0,
                 save_best_only=True, save_weights_only=False,
                 mode='auto', period=1000, walltime=0, start_epoch=0):
        super(ModelCheckpointBatches, self).__init__()
        self.monitor = monitor
        self.verbose = verbose
        self.save_best_only = save_best_only
        self.save_weights_only = save_weights_only
        self.period = period
        self.batches_since_last_save = 0

        self.start_time = time.time()
        self.last_time = time.time()
        self.average_time = 0
        self.reached_wall_time = False
        self.walltime = walltime
        self.time_filepath = temp_save_path
        self.start_epoch = start_epoch

        if mode not in ['auto', 'min', 'max']:
            warnings.warn('ModelCheckpoint mode %s is unknown, '
                          'fallback to auto mode.' % (mode),
                          RuntimeWarning)
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = np.less
            self.best = np.Inf
        elif mode == 'max':
            self.monitor_op = np.greater
            self.best = -np.Inf
        else:
            if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
                self.monitor_op = np.greater
                self.best = -np.Inf
            else:
                self.monitor_op = np.less
                self.best = np.Inf

    def on_train_begin(self, logs=None):
        if self.walltime:
            sys.stdout.write("Start training with the following walltime: %d\n" % self.walltime)
        else:
            sys.stdout.write("Start training without specified walltime\n")
        sys.stdout.flush()

    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        self.batches_since_last_save += 1
        if self.batches_since_last_save >= self.period:
            self.batches_since_last_save = 0
            # filepath = self.filepath # .format(epoch=batch + 1, **logs)
            # if self.save_best_only:
            #     current = logs.get(self.monitor)
            #     print("In batch %d: %s is %0.5f" % (batch+1, self.monitor, current), flush=True)
            #     if current is None:
            #         print('Can save best model only with %s available, '
            #               'skipping.' % (self.monitor), flush=True)
            #     else:
            #         if self.monitor_op(current, self.best):
            #             if self.verbose > 0:
            #                 print('\nBatch %05d: %s improved from %0.5f to %0.5f,'
            #                       ' saving model to %s'
            #                       % (batch + 1, self.monitor, self.best,
            #                          current, filepath), flush=True)
            #             self.best = current
            #             if self.save_weights_only:
            #                 self.model.save_weights(filepath, overwrite=True)
            #             else:
            #                 self.model.save(filepath, overwrite=True)
            #         else:
            #             if self.verbose > 0:
            #                 print('\nBatch %05d: %s did not improve from %0.5f' %
            #                       (batch + 1, self.monitor, self.best), flush=True)
            # else:
            #     if self.verbose > 0:
            #         print('\nBatch %05d: saving model to %s' % (batch + 1, filepath), flush=True)
            #     if self.save_weights_only:
            #         self.model.save_weights(filepath, overwrite=True)
            #     else:
            #         self.model.save(filepath, overwrite=True)

            if self.walltime:
                used_time = time.time() - self.last_time
                if self.average_time > 0:
                    self.average_time = (self.average_time + used_time) / 2
                else:
                    self.average_time = used_time
                if ((time.time() - self.start_time) + 5*self.average_time) > self.walltime:
                    self.reached_wall_time = True
                    self.model.stop_training = True
                    self.model.save(self.time_filepath, overwrite=True)
                    print("Wall time is reached, restart model!", flush=True)
                self.last_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        if not 'val_loss' in logs:
            return
        self.start_epoch += 1
        print("Epoch %d:" % self.start_epoch, logs)

    def on_train_end(self, logs=None):
        sys.stdout.write("Training finished!")
        sys.stdout.flush()


class ModelCheckpoint(Callback):
    """Save the model after every epoch.

    `filepath` can contain named formatting options,
    which will be filled the value of `epoch` and
    keys in `logs` (passed in `on_epoch_end`).

    For example: if `filepath` is `weights.{epoch:02d}-{val_loss:.2f}.hdf5`,
    then the model checkpoints will be saved with the epoch number and
    the validation loss in the filename.

    # Arguments
        filepath: string, path to save the model file.
        monitor: quantity to monitor.
        verbose: verbosity mode, 0 or 1.
        save_best_only: if `save_best_only=True`,
            the latest best model according to
            the quantity monitored will not be overwritten.
        mode: one of {auto, min, max}.
            If `save_best_only=True`, the decision
            to overwrite the current save file is made
            based on either the maximization or the
            minimization of the monitored quantity. For `val_acc`,
            this should be `max`, for `val_loss` this should
            be `min`, etc. In `auto` mode, the direction is
            automatically inferred from the name of the monitored quantity.
        save_weights_only: if True, then only the model's weights will be
            saved (`model.save_weights(filepath)`), else the full model
            is saved (`model.save(filepath)`).
        period: Interval (number of epochs) between checkpoints.
    """

    def __init__(self, filepath, monitor='val_loss', verbose=0,
                 save_best_only=False, save_weights_only=False,
                 mode='auto', period=1):
        super(ModelCheckpoint, self).__init__()
        self.monitor = monitor
        self.verbose = verbose
        self.filepath = filepath
        self.save_best_only = save_best_only
        self.save_weights_only = save_weights_only
        self.period = period
        self.epochs_since_last_save = 0

        if mode not in ['auto', 'min', 'max']:
            warnings.warn('ModelCheckpoint mode %s is unknown, '
                          'fallback to auto mode.' % (mode),
                          RuntimeWarning)
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = np.less
            self.best = np.Inf
        elif mode == 'max':
            self.monitor_op = np.greater
            self.best = -np.Inf
        else:
            if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
                self.monitor_op = np.greater
                self.best = -np.Inf
            else:
                self.monitor_op = np.less
                self.best = np.Inf

    def on_epoch_end(self, epoch, logs=None):
        if not 'val_loss' in logs:
            return
        logs = logs or {}
        self.epochs_since_last_save += 1
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
            try:
                filepath = self.filepath.format(epoch=epoch + 1, **logs)
            except:
                raise KeyError("Why did this happen?")
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    warnings.warn('Can save best model only with %s available, '
                                  'skipping.' % (self.monitor), RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s improved from %0.5f to %0.5f,'
                                  ' saving model to %s'
                                  % (epoch + 1, self.monitor, self.best,
                                     current, filepath), flush=True)
                        self.best = current
                        if self.save_weights_only:
                            self.model.save_weights(filepath, overwrite=True)
                        else:
                            self.model.save(filepath, overwrite=True)
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve from %0.5f' %
                                  (epoch + 1, self.monitor, self.best), flush=True)
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving model to %s' % (epoch + 1, filepath), flush=True)
                if self.save_weights_only:
                    self.model.save_weights(filepath, overwrite=True)
                else:
                    self.model.save(filepath, overwrite=True)


class ReduceLREarlyStopping(Callback):

    def __init__(self, file, factor, patience_lr, min_lr, patience_stop):
        super(ReduceLREarlyStopping, self).__init__()

        self.monitor = 'val_loss'
        if factor >= 1.0:
            raise ValueError('ReduceLROnPlateau '
                             'does not support a factor >= 1.0.')
        self.data = None
        self.file = file
        self.factor = factor
        self.min_lr = min_lr
        self.patience_lr = patience_lr
        self.wait_lr = 0
        self.wait_total = 0
        self.patience_stop = patience_stop
        self.best = 0

    def on_train_begin(self, logs=None):
        self._setup()

    def _setup(self):
        if not os.path.exists(self.file):
            os.makedirs(os.path.split(self.file)[0], exist_ok=True)
            with open(self.file, 'x') as fp:
                fp.write(json.dumps({'lr': float(K.get_value(self.model.optimizer.lr)),
                                     'wait_lr': 0,
                                     'wait_total': 0,
                                     'best': float('inf')}))

        with open(self.file, 'r') as fp:
            self.data = json.loads(fp.read())
            K.set_value(self.model.optimizer.lr, max(self.min_lr, self.data['lr']))
            self.wait_lr = int(self.data['wait_lr'])
            self.wait_total = int(self.data['wait_total'])
            self.best = float(self.data['best'])

    def on_epoch_end(self, epoch, logs=None):

        if 'val_loss' not in logs:
            return

        current = logs.get(self.monitor)

        if current <= self.best:
            self.best = current
            self.wait_total = 0
            self.wait_lr = 0
        else:
            self.wait_total += 1
            self.wait_lr += 1

            if self.wait_total >= self.patience_stop:
                print("Model stopped!", flush=True)
                self.model.stop_training = True
            elif self.wait_lr >= self.patience_lr:
                self.wait_lr = 0
                old_lr = float(K.get_value(self.model.optimizer.lr))
                if old_lr > self.min_lr:
                    new_lr = old_lr * self.factor
                    new_lr = max(new_lr, self.min_lr)
                    K.set_value(self.model.optimizer.lr, new_lr)
                    print("LR changed from %0.5f to %0.5f" % (old_lr, new_lr))

        with open(self.file, 'w') as fp:
            fp.write(json.dumps({'lr': float(K.get_value(self.model.optimizer.lr)),
                                 'wait_lr': self.wait_lr,
                                 'wait_total': self.wait_total,
                                 'best': self.best}))


class TensorBoardWrapper(TensorBoard):
    '''Sets the self.validation_data property for use with TensorBoard callback.'''

    def __init__(self, batch_gen, nb_steps, **kwargs):
        super().__init__(**kwargs)
        self.batch_gen = batch_gen # The generator.
        self.nb_steps = int(nb_steps) # Number of times to call next() on the generator.

    def on_epoch_end(self, epoch, logs=None):
        pitches, lengths, offsets, pitches_out, lengths_out = [], [], [], [], []
        for s in range(self.nb_steps):
            data, label = next(self.batch_gen)
            pitch, length, offset = data
            pitch_o, length_o = label
            for p, l, o, po, lo in zip(pitch, length, offset, pitch_o, length_o):
                pitches.append(p)
                lengths.append(l)
                offsets.append(o)
                pitches_out.append(po)
                lengths_out.append(lo)
        self.validation_data = [np.array(pitches), np.array(lengths), np.array(offsets), np.array(pitches_out), np.array(lengths_out),
                                         np.ones(len(pitches_out)), np.ones(len(lengths_out)), 0.0]
        return super().on_epoch_end(epoch, logs)


