# Simple-Challonge-Ticker
Very simple program that pushes Challonge matches to text file for an OBS ticker.

Created for Python 2.7. You'll have to install pychallonge and dateutil as they are dependencies. If you're only interested in running the program, you can just grab the compiled .exe of the ticker for Windows.

This program hooks a Challonge bracket and publishes a given recently completed or upcoming match to a text file.

It has both normal and subdomain support. For subdomains, simply enter the subdomain first followed by a dash (-), then the tournament name.

For example: "moal-MoaL41MeleeSingles" would pull from http://moal.challonge.com/MoaL41MeleeSingles

You can vary how many upcoming or completed matches you'd like to publish to the text file. You then hook the text file to an OBS ticker object, and you're all set to go.

Hope you enjoy, this was a really simple fast project for something that can be really unique for your competitive stream.

## Browser Source Dashboard (新增)

此專案新增一個可供 OBS Browser Source 使用的響應式透明看板，包含簡單的後端 API（`/api/tournament`）與前端靜態頁面。

### 快速開始（開發）

1. 建立 Python 3 虛擬環境並安裝相依：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. 啟動後端（預設 port 5000）：

```bash
python ticker_server.py
```

3. 開啟前端看板或在 OBS 中加入 Browser Source：

- 使用模擬資料（開發）： http://localhost:5000/static/dashboard.html
- 指定 Challonge 公開 URL（需 URL encode）： http://localhost:5000/static/dashboard.html?url=https%3A%2F%2Fchallonge.com%2Fyourtournament

OBS 設定：將 Browser Source 指向上方 URL，建議寬高例如 `1920x200`，並在 OBS 中啟用透明背景或在 CSS 設為透明。

### 新增檔案

- [ticker_server.py](ticker_server.py) - Flask 後端，提供 `/api/tournament` 與靜態檔案
- [static/dashboard.html](static/dashboard.html) - 前端看板（透明、響應式）
- [static/style.css](static/style.css) - 樣式
- [static/app.js](static/app.js) - 前端輪詢 API 與更新 DOM
- [requirements.txt](requirements.txt) - 相依套件

### 備註

- 預設抓取間隔：15 秒，可在程式或 URL 參數中調整。
- 主色採用 Challonge 橘色 `#f48024`。
- 目前 HTML 解析以 heuristics 為主；若你的賽事頁面使用不同 DOM 結構，我可以為特定頁面補強解析規則。

