# -*- coding: utf-8 -*-
import asyncio
import binascii
import ctypes
import io
import os
import threading
import winsound

from PIL import Image
from pystray import Icon, Menu, MenuItem
import darkdetect as dd
import winrt.windows.ui.notifications as notifications
import winrt.windows.ui.notifications.management as management

PreferredAppMode = {
    'Light': 0,
    'Dark': 1,
}
# https://github.com/moses-palmer/pystray/issues/130
ctypes.windll['uxtheme.dll'][135](PreferredAppMode[dd.theme()])

SOUND_CONFIG = {
    'スマートフォン連携': {
        'YouTube': r'C:\Windows\Media\Windows Foreground.wav',
        'X': r'C:\Windows\Media\Windows Notify Messaging.wav',
    },
}
main_loop = None
last_toast_ids = [-1]


def play_app_sound(app_name, title=None):
    """winsoundを使用してWAVを再生"""
    sound_path = None
    if app_name in SOUND_CONFIG:
        if isinstance(SOUND_CONFIG[app_name], dict):
            if title in SOUND_CONFIG[app_name]:
                sound_path = SOUND_CONFIG[app_name][title]
        elif isinstance(SOUND_CONFIG[app_name], str):
            sound_path = SOUND_CONFIG[app_name]
    try:
        # SND_FILENAME: パス指定, SND_ASYNC: 非同期再生（即座に制御を戻す）
        print(f'{sound_path=}')
        if isinstance(sound_path, str):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f'再生エラー: {e}')


def run_asyncio_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_notification_listener())


async def fetch_contents(listener):
    global last_toast_ids

    print(f'>>> {last_toast_ids=}')
    try:
        # トースト通知のリストを取得
        toasts = list(await listener.get_notifications_async(notifications.NotificationKinds.TOAST))
        if not toasts:
            print('通知リストは空です。')
            return

        toast_ids = [toasts[i].id for i in range(len(toasts))]
        print(f'{toast_ids=}')

        # 最新の通知を取得
        latest = toasts[-1]
        latest_id = latest.id
        print(f'{latest_id=}')

        if last_toast_ids and latest_id not in last_toast_ids:
            # アプリ名
            app_name = latest.app_info.display_info.display_name

            # 通知からテキストの抽出
            title = 'No Title'
            body = ''

            binding = latest.notification.visual.get_binding('ToastGeneric')
            if binding:
                # テキスト要素（<text>タグ）をすべて取得 0..2 まで
                elements = list(binding.get_text_elements())
                for i, elem in enumerate(elements):
                    print(f'elements[{i}]: {elem.text}')

                # 0番目がタイトル、1番目以降が本文
                if len(elements) > 0:
                    title = elements[0].text
                if len(elements) > 1:
                    body = '\n'.join([elements[i].text for i in range(1, len(elements[1:]) + 1)])

            lines = [
                f'通知検知: {app_name}',
                f'タイトル: {title}',
                f'本　　文:\n{body}',
            ]
            for line in lines:
                print(line)

            # 音を鳴らす
            play_app_sound(app_name, title=title, body=body)

        # 通知のリストを保存
        del last_toast_ids
        last_toast_ids = toast_ids

        print(f'<<< {last_toast_ids=}')

    except Exception as e:
        # 0x8000000B (E_BOUNDS) を含むエラーのハンドリング
        print(f'取得エラー (スキップします): {e}')


def notification_handler(sender, _):
    if main_loop:
        asyncio.run_coroutine_threadsafe(fetch_contents(sender), main_loop)


async def start_notification_listener():
    global main_loop
    main_loop = asyncio.get_running_loop()

    listener = management.UserNotificationListener.current
    status = await listener.request_access_async()

    if status == management.UserNotificationListenerAccessStatus.ALLOWED:
        listener.add_notification_changed(notification_handler)
        while True:
            await asyncio.sleep(1)
    else:
        print('通知へのアクセスが許可されていません。設定を確認してください。')


class taskTray:
    def __init__(self):
        image = Image.open(io.BytesIO(binascii.unhexlify(ICON.replace('\n', '').strip())))
        menu = Menu(
            MenuItem('Open notification setting', self.open_setting, default=True),
            MenuItem('Exit', self.stopApp),
        )
        self.app = Icon(name='PYTHON.win32.test', title='test', icon=image, menu=menu)

    def open_setting(self):
        os.system('start ms-settings:notifications')

    def stopApp(self):
        self.app.stop()

    def runApp(self):
        threading.Thread(target=run_asyncio_thread, daemon=True).start()
        self.app.run()


ICON = """
89504e470d0a1a0a0000000d4948445200000010000000100803000000282d0f530000000467414d410000b18f0bfc6105000000206348524d00007a
26000080840000fa00000080e8000075300000ea6000003a98000017709cba513c000001d7504c54450000000101010f0d0b00010103080a00020300
00000000000000001334451131410000000000001f54701b4b630000001e536f1b4a63000000081820256486225d7b08161d0000000000000b1e2824
6384235f7f08182000000000000000000008141a1c4b63276b8e2565871c4c650611160000000000002625238c8d89215b7907151d0000000000000f
212b979a970a1d260000000000002156721c4c66000000000000215a791d506b000000215b790000001f55711b4c650000000000000a1d2625668723
6080091a23000000010304050f14091c26235e7e236080091a23050f140001010001020002030002030002030001020102033ba1d63b9fd43ca3d83e
a7de3ba0d598c6da48ade13ca6de3da6de3da6dd3ea9e1399ccfd9e5e476c0e447abdf50b0e13ca6dd43a9df3da7df3a9fd392c8e16fbce345aadf7d
b6d192b2bf5ab3e05db4df93b2bf77b6d43ba1d741aae15bb6e4a4acab6f67619fd0e5a4d1e36e655faab7b854b3e33ea8e03eaae2439fd37d6d8b94
a8b891a9b067b9e26bbbe191a8b093a6b87c698842a0d53ba3d9479ed29b2f409a4a5c6f9ec34c91c24d91c2729bbf9c405099314145a0d43286b257
81ab983649933a4e933c5094394d96394d5384b03185b12d61812f5e7dffffffd3f96a210000005374524e530000000000001e1a199c93154ffaf645
fbf80669fcf95f043e73e8e36c37030259e4fdfed84e01076ae5e15f050c77ed640962efe95270fdfa5efd61eee7510b74ece761080762a2eee59d59
0b6f8786886305f4f0d3c000000001624b47449c71bcc2270000000774494d4507e8090e08280661217c2a000000d74944415418d363608000367606
14c0c1c9c58d22c0c3cbc78f2a2020882220242c222a268ee04a484a058748cbc8ca81b98cf20a8a4aa16161e1ca2aaa6a8c0c0c4cea1a9a119151d1
3151b1715ada3acc0cba7afaf1098949c9c94929a9695206860c46c6e9199959d939b979f929a90526a60c66e685c945c525a565e51595c95516960c
6656d535b575f50d8d4dcd2dadb140016b9bb6f68eceaeee9edebefe09c1b6760cf60e8e13274d9e3275eab4e933663a39bb30b0b8bab97bcc9a0d04
b33cbdbcc599812e63f6f1f5f3078280c0205606060074d237e8377bca260000002574455874646174653a63726561746500323032342d30392d3133
5432333a34303a30362b30393a3030d2b5b6cf0000002574455874646174653a6d6f6469667900323032342d30392d31335432333a34303a30362b30
393a3030a3e80e730000000049454e44ae426082
"""

if __name__ == '__main__':
    taskTray().runApp()
