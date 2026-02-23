import os
import time
import pandas as pd
import pyperclip
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

SAVE_DIR = "downloaded_images"

def download_image(url):
    if not url or not url.startswith('http'):
        return None
    try:
        file_name = url.split('/')[-1].split('?')[0]
        save_path = os.path.join(SAVE_DIR, file_name)
        
        # User-Agentを送って「ブラウザからのアクセスだよ」と偽装する（拒否対策）
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        
        if response.status_code == 200: # ここを修正
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return file_name
    except Exception as e:
        print(f"画像DL失敗: {url} - {e}")
    return None

def start_process(file_path):
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    options = webdriver.ChromeOptions()
    # 画面が崩れないようにウィンドウサイズを指定
    options.add_argument('--window-size=1280,1024')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    final_output = ""
    img_selectors = [
        "#__next > div > main > section.custom-product-details.detail-page > div > div.product-zone > div.image-slider-wrapper > div.swiper.swiper-initialized.swiper-horizontal.swiper-pointer-events.swiper-free-mode.thumbnails.swiper-thumbs.swiper-backface-hidden > div > div.swiper-slide.swiper-slide-visible.swiper-slide-active > img",
        "#__next > div > main > section.custom-product-details.detail-page > div > div.product-zone > div.image-slider-wrapper > div.swiper.swiper-initialized.swiper-horizontal.swiper-pointer-events.swiper-free-mode.thumbnails.swiper-thumbs.swiper-backface-hidden > div > div.swiper-slide.swiper-slide-visible.swiper-slide-thumb-active > img",
        "#__next > div > main > section.custom-product-details.detail-page > div > div.product-zone > div.image-slider-wrapper > div.swiper.swiper-initialized.swiper-horizontal.swiper-pointer-events.swiper-free-mode.thumbnails.swiper-thumbs.swiper-backface-hidden > div > div:nth-child(4) > img"
    ]

    try:
        # 文字コードを指定してCSV読み込み
        try:
            df = pd.read_csv(file_path, encoding='cp932')
        except:
            df = pd.read_csv(file_path, encoding='utf-8')

        urls = df['url'].tolist()

        for url in urls:
            print(f"アクセス中: {url}")
            driver.get(url)
            
            # 要素が表示されるまで最大10秒待つ（これを入れると安定するよ！）
            wait = WebDriverWait(driver, 10)
            
            try:
                # 商品名の取得待ち
                name_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#__next > div > main > section.custom-product-details.detail-page > div > h2")))
                name = name_el.text.strip()

                desc = driver.find_element(By.CSS_SELECTOR, "#__next > div > main > section.custom-product-details.detail-page > div > div.product-description > div").text.strip()

                downloaded_files = []
                for selector in img_selectors:
                    try:
                        img_el = driver.find_element(By.CSS_SELECTOR, selector)
                        img_url = img_el.get_attribute("src")
                        fname = download_image(img_url)
                        if fname: downloaded_files.append(fname)
                    except:
                        continue

                img_list_str = ", ".join(downloaded_files)
                safe_desc = f'"{desc.replace("\"", "\"\"")}"'
                final_output += f"{name}\t{safe_desc}\t{img_list_str}\n"
                print(f"成功: {name}")

            except Exception as e:
                print(f"エラー発生: {url}")
                final_output += f"ERROR\tERROR\tERROR\n"

        pyperclip.copy(final_output)
        messagebox.showinfo("完了", "データをコピーしました！")

    finally:
        driver.quit()

# （以下、UI部分は以前と同じなので省略）
def select_file():
    path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if path:
        label_path.config(text=path)
        btn_run.config(state=tk.NORMAL, command=lambda: start_process(path))

root = tk.Tk()
root.title("Excelコピペ & 画像DLくん")
root.geometry("400x250")
tk.Label(root, text="商品情報スクレイピング", font=("Arial", 12, "bold")).pack(pady=10)
tk.Button(root, text="CSV選択", command=select_file).pack()
label_path = tk.Label(root, text="未選択", fg="gray")
label_path.pack()
btn_run = tk.Button(root, text="実行", state=tk.DISABLED, bg="orange")
btn_run.pack(pady=20)
root.mainloop()