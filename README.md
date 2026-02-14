## Voltzoast

Transform your Windows notifications into physical actions: Automate SwitchBot, Text To Speech with VOICEVOX, and custom sounds.

推しの配信をリアタイしたい層向けの機能として「**推しの配信が始まったら首輪に電撃を流す**」ことができます

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

アプリと同じ場所に配置してください  
これがないと起動しません

```
{
  "token": "xxx-token",
  "secret": "xxx-secret"
}
```

### .config

アプリと同じ場所に配置してください  

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

詳細はあとで

- title
- body
- speaker
- volume
- speed
- file
- text
  - title
  - from
  - body
