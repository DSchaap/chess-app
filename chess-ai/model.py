from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import Adam
from keras.utils.data_utils import get_file
import numpy as np


model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(inst_chars[inst]))))
model.add(Dense(len(inst_chars[inst])))
model.add(Activation('softmax'))

optimizer = Adam(lr=0.01)
loss_function = 0
model.compile(loss=, optimizer=optimizer)
model.fit(x, y, batch_size=128, epochs=40)
models[inst] = model
