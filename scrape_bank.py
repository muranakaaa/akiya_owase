import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# ChromeDriver 自動インストール
chromedriver_autoinstaller.install()

# Chromeオプション設定（必要なら headless 無効化も可）
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ドライバ起動
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# ▼ 対象URLリスト（売買 + 賃貸）
urls = [
    # 売買
    "https://www.ijyu.pref.mie.lg.jp/bank/?transaction=sale&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/2/?transaction=sale&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/3/?transaction=sale&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/4/?transaction=sale&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/5/?transaction=sale&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/6/?transaction=sale&municipality%5B0%5D=municipality-owase&sort_order=default",
    # 賃貸
    "https://www.ijyu.pref.mie.lg.jp/bank/?transaction=rent&municipality%5B%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/2/?transaction=rent&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/3/?transaction=rent&municipality%5B0%5D=municipality-owase&sort_order=default",
    "https://www.ijyu.pref.mie.lg.jp/bank/page/4/?transaction=rent&municipality%5B0%5D=municipality-owase&sort_order=default"
]

all_data = []

for url in urls:
    driver.get(url)
    print(f"アクセス中: {url}")
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/main/div/div[3]/div[3]/div[2]/ol")))
        listings = driver.find_elements(By.XPATH, "/html/body/div/main/div/div[3]/div[3]/div[2]/ol/li")

        for i in range(1, len(listings) + 1):
            row = []

            # ▼ div[1]〜div[4]のうち、dd要素のみ取得
            for j in range(1, 5):
                try:
                    xpath = f"/html/body/div/main/div/div[3]/div[3]/div[2]/ol/li[{i}]/section/div/div[2]/dl/div[{j}]/dd"
                    detail = driver.find_element(By.XPATH, xpath)
                    row.append(detail.text.strip())
                except Exception as e:
                    row.append("取得失敗")
                    print(f"{i}件目の div[{j}] の取得に失敗: {e}")

            # ▼ 詳細リンク（div[3] or div[4] の aタグ）
            try:
                found_link = False
                for div_num in [3, 4]:
                    link_xpath = f"/html/body/div/main/div/div[3]/div[3]/div[2]/ol/li[{i}]/section/div/div[{div_num}]/div/a"
                    link_elements = driver.find_elements(By.XPATH, link_xpath)
                    if link_elements:
                        row.append(link_elements[0].get_attribute("href"))
                        found_link = True
                        break
                if not found_link:
                    row.append("リンクなし")
            except Exception as e:
                row.append("取得失敗")
                print(f"{i}件目のリンク取得で例外: {e}")

            all_data.append(row)

    except Exception as e:
        print(f"{url} のページ処理中にエラー: {e}")

# ▼ CSV保存
csv_file = "akiya_owase.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["住所", "売買希望価格", "賃貸希望価格", "間取り", "詳細リンク"])
    writer.writerows(all_data)

print(f"\n✅ CSVに保存完了 → {csv_file}")
driver.quit()
