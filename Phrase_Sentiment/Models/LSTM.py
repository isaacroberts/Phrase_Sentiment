import keras

from keras.layers import Dense
from keras.engine.input_layer import Input

import matplotlib.pyplot as plt

class LSTM():

    def __init__(self,input_ct,num_classes,batch_len=16):
        self.batch_length=batch_len

        input=Input(shape=(5,))

        x=Dense(self.batch_length,activation='softmax',input_dim=input_ct)(input)
        m=Dense(self.batch_length,activation='softmax',input_dim=input_ct)(x)
        p=Dense(num_classes ,activation='relu',input_dim=input_ct)(m)

        self.model=keras.models.Model(input,p)

        opt=keras.optimizers.RMSprop(lr=0.02, rho=0.9, epsilon=None, decay=0.0)

        self.model.compile(optimizer=opt,loss='mean_squared_error')


        """
        self.input=keras.engine.input_layer.Input(shape=(4,))
        self.batch_length=batch_len
        self.model=keras.models.Sequential()
        self.model.add(self.input)
        self.model.add(Dense(self.batch_length,
                input_dim=input_ct))
        self.model.add(keras.layers.Activation('tanh'))
        self.model.compile(optimizer='rmsprop',
                            loss='categorical_crossentropy',
                            metrics=['accuracy'])
        """

    def train(self,data,labels,display=True):
        epochs=5

        history=self.model.fit(data,labels,self.batch_length,epochs)

        if display:
            # Plot training & validation loss values
            plt.plot(history.history['loss'])
            plt.title('Model loss')
            plt.ylabel('Loss')
            plt.xlabel('Epoch')
            plt.legend(['Train', 'Test'], loc='upper left')
            plt.ylim(bottom=0)
            plt.show()

    def test(self,data,labels):


        score=self.model.evaluate(data,labels,self.batch_length)
        return score
