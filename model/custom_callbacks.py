from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import warnings
import os

import time
from keras.callbacks import Callback


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

    def __init__(self, filepath, monitor='val_loss', verbose=0,
                 save_best_only=True, save_weights_only=False,
                 mode='auto', period=1000, walltime=0, last_epoch=0):
        super(ModelCheckpointBatches, self).__init__()
        self.monitor = monitor
        self.verbose = verbose
        self.filepath = filepath
        self.save_best_only = save_best_only
        self.save_weights_only = save_weights_only
        self.period = period
        self.batches_since_last_save = 0

        self.start_time = time.time()
        self.last_time = time.time()
        self.average_time = 0
        self.reached_wall_time = False
        self.walltime = walltime
        self.time_filepath = os.path.join(os.path.split(filepath)[0], "weights_saved_wall_time.hdf5")
        self.last_epoch = last_epoch

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

    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        self.batches_since_last_save += 1
        if self.batches_since_last_save >= self.period:
            self.batches_since_last_save = 0
            filepath = self.filepath.format(epoch=batch + 1, **logs)
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    warnings.warn('Can save best model only with %s available, '
                                  'skipping.' % (self.monitor), RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print('\nBatch %05d: %s improved from %0.5f to %0.5f,'
                                  ' saving model to %s'
                                  % (batch + 1, self.monitor, self.best,
                                     current, filepath))
                        self.best = current
                        if self.save_weights_only:
                            self.model.save_weights(filepath, overwrite=True)
                        else:
                            self.model.save(filepath, overwrite=True)
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve from %0.5f' %
                                  (batch + 1, self.monitor, self.best))
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving model to %s' % (batch + 1, filepath))
                if self.save_weights_only:
                    self.model.save_weights(filepath, overwrite=True)
                else:
                    self.model.save(filepath, overwrite=True)

            if self.walltime:
                used_time = time.time() - self.last_time
                if self.average_time > 0:
                    self.average_time = (self.average_time * 7 + used_time) / 8
                else:
                    self.average_time = used_time
                if (time.time() - self.start_time + 10*self.average_time) > self.walltime:
                    self.reached_wall_time = True
                    self.model.stop_training = True
                    self.model.save(self.time_filepath, overwrite=True)

                self.last_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        self.last_epoch += 1
