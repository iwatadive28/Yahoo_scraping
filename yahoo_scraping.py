# -*- coding: utf-8 -*-
# 必要なライブラリのインポート
import os
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By

# 顔認識のためのライブラリ
import io
import numpy as np
from PIL import Image
import cv2
from detectioin import face_detect, save_image

CHROMEDRIVER = "./chromedriver.exe" # WebDriverのパスを設定

# 複数の顔画像のダウンロードを行う関数
def download_faceimgs(img_urls, save_dir, max_img=20):
    cnt_face = 0
    for i, url in enumerate(img_urls):
        file_name = f"{i}.png"  # 画像ファイル名
        save_img_path = os.path.join(save_dir, file_name)  # 保存パス

        r = requests.get(url, stream=True)
        if r.status_code == 200:
            # Binary -> np.asarray
            img_base = np.asarray(Image.open(io.BytesIO(r.content)))
            img_base = cv2.cvtColor(img_base, cv2.COLOR_RGBA2BGR)

            # Face Detection
            img_det, img_face, facerect = face_detect(img_base)

            if len(img_face) != 0: # 顔検出したらカウントアップして保存
                cnt_face = cnt_face + 1
                img_face = np.squeeze(img_face[0][:][:][:])
                cv2.imwrite(save_img_path, img_face)
                # cv2.imshow('face', img_face)  # imshow()で見たい画像を表示する

        if (cnt_face + 1) % 10 == 0 or (cnt_face + 1) == len(img_urls):
            print(f"{cnt_face + 1} / {len(img_urls)} done")
        if cnt_face >= max_img:
            return()

def yahoo_scraping(word, max_img=20, save_dir='./downloads/'):
    # ディレクトリが存在しなければ作成する
    os.makedirs(save_dir,exist_ok=True)

    # Webdriverの設定
    options = Options()
    options.add_argument('--headless')  # UI無しで操作する
    chrome_service = fs.Service(executable_path=CHROMEDRIVER)
    driver = webdriver.Chrome(service=chrome_service,options=options)

    # yahoo画像へアクセス
    url = "https://search.yahoo.co.jp/image/search?p={}"
    driver.get(url.format(word))  # 指定したURLへアクセス

    urls = []  # 画像URLを格納するリスト

    # 止まるまでスクロールする
    while True:
        prev_html = driver.page_source  # スクロール前のソースコード
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 最下部までスクロール
        sleep(1.0)  # 1秒待機
        current_html = driver.page_source  # スクロール後のソースコード

        # スクロールの前後で変化が無ければループを抜ける
        if prev_html != current_html:
            prev_html = current_html
        else:
            # 「もっと見る」ボタンがあればクリック
            try:
                button = driver.find_element_by_class_name("sw-Button")
                button.click()
            except:
                break

    # 画像タグをすべて取得
    # elements = driver.find_elements_by_tag_name("img") # Selenium 3系
    elements = driver.find_elements(By.TAG_NAME, "img") # Selenium 4系

    # すべての画像URLを抜き出す
    for elem in elements:
        url = elem.get_attribute("src")
        if url not in urls:
            urls.append(url)  # urlをリストに追加する

    driver.close()  # driverをクローズする
    download_faceimgs(urls, save_dir, max_img)  # 顔画像をダウンロードする

if __name__ == '__main__':
    word     = ['JOY','ハリー杉山','ウエンツ瑛士','ユージ','ラウール']
    dir_name = ['Joy','Harry','Uentsu','Yuji','Raul']
    # word     = ['岩本照'  ,'深澤辰哉'  ,'渡辺翔太' ,'向井康二','阿部亮平','目黒蓮', '宮舘涼太'  ,'佐久間大介','ラウール']
    # dir_name = ['Iwamoto','Fukazawa','Watanabe','Mukai' ,'Abe'    ,'Meguro','Miyadate','Sakuma'  ,'Raul']
    max_img = 100
    for i in range(word.__len__()):
        keyword = word[i]
        save_dir = './downloads/' + dir_name[i]
        print('keyword  = ' + keyword)
        print('save_dir = ' + save_dir)
        yahoo_scraping(keyword,max_img,save_dir)
