## Voltzoast

Transform your Windows notifications into physical actions: Automate SwitchBot, Text To Speech with VOICEVOX, and custom sounds.

推しの配信をリアタイしたい層向けの機能として「**推しの配信が始まったら首輪に電撃を流す**」ことができます

### 概要

Windows Toast notifications to SwitchBot, VOICEVOX, and Audio automation hub.

### 事前準備

- **コンセントにつなぐと電流が流れる首輪を用意してください (最重要項目)**

SwitchBot のスマートプラグでコントロールするので、コンセントにつなぐと動作を開始するようになっていることが必要です  
センサー式のスイッチのものはコンセントのオンオフでは動作しないので注意

- YouTube の通知をオンにしてください

https://support.google.com/youtube/answer/3382248?sjid=9891899357558796905-NC

- SwitchBot のハブとスマートプラグを設定しておいてください
  - ハブ (いずれかが必要です)
    - [ハブミニ](https://amzn.to/3MLDAE5)
    - [ハブミニ 木目調](https://amzn.to/3OiW9Qq)
    - [ハブミニ (Matter対応)](https://amzn.to/4axVJgm)
    - ハブ2
    - ハブ3
    - AIハブ
  - スマートプラグ 連動するためのスマートコンセントです
    - [スマートプラグ ミニ](https://amzn.to/464SJqD)
    - [スマートプラグ ミニ (HomeKit対応)](https://amzn.to/4aCJpvC)

- SwitchBot のトークンを取得してください

https://blog.switchbot.jp/announcement/api-v1-1/

- VOICEVOX を使う場合はあらかじめ VOICEVOX Engine を起動しておいてください

配信のタイトルを読み上げたいときに必要です

https://qiita.com/yamanohappa/items/b75d069e3cb0708d8709

### .switchbot

voltzoast.py と同じ場所に配置してください  
これがないと起動しません

```
{
  "token": "xxx-token",
  "secret": "xxx-secret"
}
```

### .config (設定ファイル)

`sample.config` をリネームして voltzoast.py と同じ場所に配置してください

```
{
    "Google Chrome": [
        {"title": "🔴", "body": "こそぎ(心削ぎ)", "volume": 1.3, "device": "電撃", "text": "{from}"},

        {"title": "YouTube", "body": "ライブ配信が始まります", "speaker": 113, "text": "{from}"},
        {"title": "🔴", "body": "ライブ配信中", "speaker": 113, "text": "{title} {from}"},

        {"text": "{from} {title}"}
    ]
}
```

#### 設定できるパラメーター

|||
|-------|-------|
|title  |通知のタイトルに含まれる文字列を指定します|
|body   |通知の本文に含まれる文字列を指定します|
|device |SwitchBot のアプリで設定されているデバイス名を指定します|
|speaker|VOICEVOX の話者 ID を指定します（デフォルトは 3「ずんだもん(ノーマル)」)|
|text   |VOICEVOX で読み上げる文章 `{title}`  `{from}` `{body}` が変数として使えます|
|file   |再生したい .wav ファイルのフルパスを指定します|

### 実行方法

```
git clone https://github.com/sharl/Voltzoast.git
cd Voltzoast
pip install -r requirements.txt
python voltzoast.py
```

### TODO

exe 化
