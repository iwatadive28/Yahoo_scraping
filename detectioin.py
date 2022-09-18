#!/usr/bin/env python
# -*- coding: utf-8 -*
import sys
import cv2 # OpenCV のインポート
import os
from datetime import datetime
import numpy as np

cascade     = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('cascades/haarcascade_eye.xml')

video_source = 0

# モザイク処理の関数。やってることは、取得した画像を拡大した後、もとのサイズに縮小する
# 参考：https://note.nkmk.me/python-opencv-mosaic/
def mosaic(src, ratio=0.1):
    small = cv2.resize(src, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST) # おっきくしてから…
    return  cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST) # 元のサイズに戻す。

# モザイクの範囲を指定する関数
def mosaic_area(src, x, y, width, height, ratio=0.1):
    dst = src.copy()
    dst[y:y + height, x:x + width] = mosaic(dst[y:y + height, x:x + width], ratio)
    return dst

# 顔の検出
def face_detect(frame,show_face=[], face_size=[180,180]):
    # そのままの大きさだと処理速度がきついのでリサイズ
    # frame = cv2.resize(frame, (int(frame.shape[1] * 0.7), int(frame.shape[0] * 0.7)))

    # 処理速度を高めるために画像をグレースケールに変換したものを用意
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 顔検出 detecctMultiScale()は検出器のルール(cascade)に従って検出した結果をfacerectに返す関数
    facerect = cascade.detectMultiScale(
        gray,
        scaleFactor=1.11,
        minNeighbors=3,
        minSize=(20, 20)
    )

    # import pdb; pdb.set_trace()
    if len(facerect) != 0:
        # Resize 顔より少し広い範囲を指定
        mag = 1
        # facerect
        for i_det in range(facerect.shape[0]):
            facerect[i_det, 0] = int(facerect[i_det, 0] - facerect[i_det, 2] * (mag-1)*0.5)
            facerect[i_det, 1] = int(facerect[i_det, 1] - facerect[i_det, 3] * (mag-1)*0.5)
            facerect[i_det, 2] = int(facerect[i_det, 2] * mag)
            facerect[i_det, 3] = int(facerect[i_det, 3] * mag)

        for i_fc in range(facerect.shape[0]):
            x, y, w, h = facerect[i_fc]
            # 顔の部分
            face = frame[y: y + h, x: x + w]
            # くり抜いた顔の部分
            face_resize = cv2.resize(face, (int(face_size[0]), int(face_size[1])))
            face_resize = face_resize[np.newaxis,:,:,:]

            if i_fc == 0:
                show_face = face_resize
            else:
                show_face = np.concatenate([show_face,face_resize],0)

            # cv2.imshow('face', show_face_gray)  # imshow()で見たい画像を表示する
            # 顔検出した部分に枠を描画
            '''
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (255, 255, 255),
                thickness=2
            )
            '''
    return (frame,show_face,facerect)

def save_image(save_path,face):
    # 画像を保存
    cv2.imwrite(save_path, face)
    # print(save_path + "is clip and saved!")
    return

def save_faceImage(save_dir):
    while (True):
        if cv2.waitKey(1) == 27:
            break

        # カメラを起動
        camera = cv2.VideoCapture(video_source)
        face   = []

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        # 顔の検出
        _, img = camera.read()
        img, face = face_detect(img, face)

        # 画像の保存
        if face != []:
            # ディレクトリの作成
            if not os.path.exists(save_dir):
                os.mkdir(os.path.join(save_dir))

            image_fname = datetime.now().strftime("%Y-%m-%d-%H%M%S") + '.jpg'
            save_path   = save_dir + '/' + image_fname
            save_image(save_path,face)
