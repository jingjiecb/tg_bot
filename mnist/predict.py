# coding=utf-8
# author        : claws
# date          : 2021/3/20
# description   : predict
import PIL.ImageOps
from PIL import Image
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from matplotlib import pyplot as plt

class CNN(object):
    def __init__(self):
        # model = models.Sequential()
        # # 1: 第1层卷积，卷积核大小为3*3，32个，28*28为待训练图片的大小
        # model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)))
        # # 2: 池化
        # model.add(layers.MaxPooling2D((2, 2)))
        # # 3: 第2层卷积，卷积核大小为3*3，64个
        # model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        # # 4: 池化
        # model.add(layers.MaxPooling2D((2, 2)))
        # # 5: 第3层卷积，卷积核大小为3*3，64个
        # model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        # # 输出展平
        # model.add(layers.Flatten())
        # # 6: 全连接层 64个神经元
        # model.add(layers.Dense(64, activation='relu'))
        # # 7: 全连接到输出层 10个输出神经元
        # model.add(layers.Dense(10, activation='softmax'))

        model = models.Sequential()
        # 1: 第1层卷积，卷积核大小为3*3，32个，28*28为待训练图片的大小
        model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)))
        # 2: 池化
        model.add(layers.MaxPooling2D((2, 2)))
        # 3: 第2层卷积，卷积核大小为3*3，64个
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        # 4: 池化
        model.add(layers.MaxPooling2D((2, 2)))
        # 5: 第3层卷积，卷积核大小为3*3，64个
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        # 输出展平
        model.add(layers.Flatten())
        # 6: 全连接层 64个神经元
        model.add(layers.Dense(120, activation='relu'))

        model.add(layers.Dense(64, activation='relu'))
        # 7: 全连接到输出层 10个输出神经元
        model.add(layers.Dense(10, activation='softmax'))

        model.summary()

        self.model = model


class PredictService:
    def __init__(self):
        latest = tf.train.latest_checkpoint('./ckpt')
        self.cnn = CNN()
        # 加载训练好的模型，恢复网络权重
        self.cnn.model.load_weights(latest)

    def process_pic(self, pic):
        img = pic.resize((28, 28), Image.ANTIALIAS)
        # img = np.asarray(img)

        # threshold = 100
        # new_pic = []
        # for i in range(28):
        #     for j in range(28):
        #         if img[i][j] > threshold:
        #             new_pic.append(255)
        #         else:
        #             new_pic.append(img[i][j])
        # img = np.asarray(new_pic).reshape(28, 28)

        # plt.subplot(122), plt.imshow(img)
        # plt.show()

        # return Image.fromarray(img)
        return img

    def predict(self, image_path, invert=False):
        # 以黑白方式读取图片
        img = Image.open(image_path).convert('L')

        # 降噪处理（效果不好舍弃不用）
        # img_ = np.asarray(img)
        # cv2.fastNlMeansDenoising(img_, img_, h=10, templateWindowSize=7, searchWindowSize=21)
        # img = Image.fromarray(img_)

        img = self.process_pic(img)

        if invert:
            img = PIL.ImageOps.invert(img)

        img = np.reshape(img, (28, 28, 1)) / 255.
        x = np.array([1 - img])

        # API refer: https://keras.io/models/model/
        y = self.cnn.model.predict(x)

        # 因为x只传入了一张图片，取y[0]即可
        # np.argmax()取得最大值的下标，即代表的数字
        # print(image_path,end='')
        # print('        -> Predict :', np.argmax(y[0]))
        return np.argmax(y[0])


if __name__ == "__main__":
    app = PredictService()
    app.predict('test_images/0.png')
    app.predict('test_images/1.png')
    app.predict('test_images/4.png')
    app.predict('test_images/1.png')
    app.predict('test_images/1-3.png  ')
