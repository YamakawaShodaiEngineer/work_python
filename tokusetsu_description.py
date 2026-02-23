import time
import pandas as pd
import pyperclip
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def start_process(file_path):
    if not file_path:
        messagebox.showwarning("注意", "CSVファイルを選択してね！")
        return

    # ブラウザ起動（少し設定を追加して安定させます）
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # 最終的なテキストを溜める変数
    # Excelで扱いやすい「タブ区切り」の形式で作っていくよ
    final_output = ""

    try:
        df = pd.read_csv(file_path)
        urls = df['url'].tolist()

        for url in urls:
            print(f"取得中: {url}")
            driver.get(url)
            time.sleep(3) # 読み込み待ち（サイトに合わせて調整してね）

            try:
                # 商品名の取得
                name_el = driver.find_element(By.CSS_SELECTOR, "#__next > div > main > section.custom-product-details.detail-page > div > h2")
                product_name = name_el.text.strip()

                # 説明文の取得
                desc_el = driver.find_element(By.CSS_SELECTOR, "#__next > div > main > section.custom-product-details.detail-page > div > div.product-description > div")
                description = desc_el.text.strip()

                # --- Excel対応のフォーマット整形 ---
                # 説明文の中に改行があっても1セルに収めるために " " で囲むよ
                # また、もし説明文の中に " 自体があったらエラーになるのでエスケープ処理しておくね
                safe_description = f'"{description.replace("\"", "\"\"")}"'
                
                # 「商品名[タブ]説明文」という1行を作る
                line = f"{product_name}\t{safe_description}\n"
                final_output += line
                
            except Exception as e:
                print(f"スキップ: {url} (要素が見つかりませんでした)")

        # 最後にまとめてクリップボードにコピー！
        pyperclip.copy(final_output)
        messagebox.showinfo("完了", "Excelに貼り付けられる状態でコピーしたよ！\nExcelを開いてCtrl+V（貼り付け）してみてね。")

    except Exception as e:
        messagebox.showerror("エラー", f"予期せぬエラーが発生したよ:\n{e}")
    finally:
        driver.quit()

# --- UI部分は前回と同じ ---
def select_file():
    file_path = filedialog.askopenfilename(title="CSVファイルを選択", filetypes=[("CSV", "*.csv")])
    if file_path:
        label_path.config(text=f"選択: {file_path}")
        btn_run.config(state=tk.NORMAL, command=lambda: start_process(file_path))

root = tk.Tk()
root.title("Excelコピペくん")
root.geometry("400x200")
tk.Label(root, text="商品情報スクレイピング", font=("Arial", 12, "bold")).pack(pady=10)
btn_select = tk.Button(root, text="CSV選択", command=select_file).pack(pady=5)
label_path = tk.Label(root, text="未選択", fg="gray")
label_path.pack()
btn_run = tk.Button(root, text="実行してクリップボードへ保存", state=tk.DISABLED, bg="lightgreen")
btn_run.pack(pady=20)
root.mainloop()