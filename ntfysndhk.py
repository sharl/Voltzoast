# -*- coding: utf-8 -*-
from datetime import datetime as dt, timedelta as td, timezone as tz
import asyncio
import ctypes
import json
import os
import threading
import winsound

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import darkdetect as dd
import winrt.windows.ui.notifications as notifications
import winrt.windows.ui.notifications.management as management

from vvox import vvox
from Switchbot import Switchbot

PreferredAppMode = {
    'Light': 0,
    'Dark': 1,
}
# https://github.com/moses-palmer/pystray/issues/130
ctypes.windll['uxtheme.dll'][135](PreferredAppMode[dd.theme()])

# .config example
# {
#     "Google Chrome": [
#         {"title": "YouTube", "body": "ライブ配信が始まります", "text": "{from}"},
#         {"title": "🔴", "body": "ライブ配信中", "text": "{title} {from}"}
#     ],
#     "スマートフォン連携": [
#         {"title": "X", "file": "C:\\Windows\\Media\\Windows Notify Messaging.wav"},
#
#         {"title": "DQⅩツール","body": "錬金釜",  "text": "{body}"},
#         {"title": "DQⅩツール", "file": "C:\\Windows\\Media\\nc308516m.wav"}
#     ],
#     "Unknown": "C:\\Windows\\Media\\Windows Foreground.wav"
# }
SOUND_CONFIG = {}


def load_config():
    global SOUND_CONFIG

    SOUND_CONFIG = {}
    with open('.config', encoding='utf-8') as fd:
        SOUND_CONFIG = json.load(fd)
        print(json.dumps(SOUND_CONFIG, indent=2, ensure_ascii=False))


TITLE = 'Notification Sound Hook'
sb = Switchbot()
sb.get_device_list()

load_config()
main_loop = None
last_toast_ids = []


def getNow():
    return dt.now(tz(td(hours=+9), 'JST')).strftime('%Y/%m/%d %H:%M:%S')


def get_sound_path(app_name, title, body):
    """ルールに基づいて適切なサウンドパスを返す"""
    if app_name not in SOUND_CONFIG:
        return None

    config = SOUND_CONFIG[app_name]

    # 単純な文字列指定の場合
    if isinstance(config, str):
        return config

    # ルールリスト（dictのリスト）の場合
    # "title":
    # "body":
    #
    # 2026/02/12 21:14:53 Detected: [app_name='Google Chrome']
    # title='🔴 【 #飲酒配信 】おもしろいホラゲだったね！呑み足りなかったぜ【こそぎ/ #心削ぎ #Vtuber】'
    # body='こそぎ(心削ぎ) / kosogi がライブ配信中'
    #
    # Match rule
    # rule_title='🔴'
    # rule_body='ライブ配信中'
    # _title='🔴 【 #飲酒配信 】おもしろいホラゲだったね！呑み足りなかったぜ【こそぎ/ #心削ぎ #Vtuber】'
    # _from='こそぎ(心削ぎ) / kosogi がライブ配信中'
    # _body='こそぎ(心削ぎ) / kosogi がライブ配信中'
    #
    # 2026/02/12 22:11:42 Detected: [app_name='Google Chrome']
    # title='Bôa'
    # body='The guitar has been at the heart of Bôa’s sound for years 🖤 #NationalGuitarDay 🎸'
    #
    # Match rule
    # rule_title=''
    # rule_body=''
    # _title='Bôa'
    # _from='The guitar has been at the heart of Bôa’s sound for years 🖤 #NationalGuitarDay 🎸'
    # _body='The guitar has been at the heart of Bôa’s sound for years 🖤 #NationalGuitarDay 🎸'
    if isinstance(config, dict):
        config = [config]
    if isinstance(config, list):
        for rule in config:
            rule_title = rule.get('title', '')
            is_title = (rule_title == title) or (rule_title in title)
            rule_body = rule.get('body', '')
            is_body = rule_body in body
            result = set([is_title, is_body])
            # print('  rule', rule)
            # print('result', result)
            if result == {True}:
                is_file = rule.get('file')
                is_text = rule.get('text')

                # device power on
                is_device = rule.get('device')
                if is_device:
                    deviceID = sb.get_device_ID(is_device)
                    if deviceID:
                        sb.set_device_power(deviceID, 'on')
                        print(f'{is_device} の電源をONにしました')

                if is_file:
                    print(f'Match rule {rule_title=} {rule_body=}')
                    return is_file
                elif is_text:
                    lines = body.strip().split('\n')
                    _title = title
                    _from = lines[0]
                    _body = body.strip()
                    # insurance
                    if len(lines) > 1:
                        _body = '\n'.join(lines[1:])

                    kvs = dict(locals())
                    new = dict()
                    # title, from, body に絞りたい
                    for k in kvs:
                        if k in ['_title', '_from', '_body']:
                            new[k.removeprefix('_')] = kvs[k]
                    text = is_text.format(**new)
                    print(f'Match rule {rule_title=} {rule_body=} {_title=}\n{_from=}\n{_body=}')
                    print(f'\033[93m{getNow()} [{app_name}] {text}\033[0m')
                    vvox(
                        text,
                        speaker=int(rule.get('speaker', 3)),
                        speed=float(rule.get('speed', 1.2)),
                        volume=float(rule.get('volume', 1.0)),
                    )
                    return None

    return None


def play_app_sound(app_name, title='', body=''):
    sound_path = get_sound_path(app_name, title, body)
    if not sound_path:
        return

    try:
        print(f'\033[93m{getNow()} [{app_name}] {title=} {body=} {sound_path}\033[0m')
        winsound.PlaySound(
            sound_path,
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )
    except Exception as e:
        print(f'Play sound error: {e}')


async def fetch_contents(listener):
    global last_toast_ids

    try:
        toasts_raw = await listener.get_notifications_async(
            notifications.NotificationKinds.TOAST
        )
        toasts = list(toasts_raw)
        if not toasts:
            return

        current_ids = [t.id for t in toasts]
        print(f'{last_toast_ids=}')
        print(f'   {current_ids=}')
        if not current_ids:
            print('toast history cleared')
            last_toast_ids = current_ids
            return

        latest = toasts[-1]
        if latest.id not in last_toast_ids:
            app_name = 'Unknown'
            title = ""
            body = ""

            # AppInfo not implemented in some cases
            try:
                if latest.app_info and latest.app_info.display_info:
                    app_name = latest.app_info.display_info.display_name
            except Exception:
                pass

            binding = latest.notification.visual.get_binding('ToastGeneric')
            if binding:
                elements = list(binding.get_text_elements())
                # スマートフォン連携等の構造に合わせた抽出
                if len(elements) > 0:
                    title = elements[0].text or ''
                if len(elements) > 1:
                    # 2枚目以降のテキストを結合
                    body = '\n'.join([e.text for e in elements[1:] if e.text])

            print(f'{getNow()} Detected: [{app_name=}] {title=} {body=}')

            play_app_sound(app_name, title, body)

        last_toast_ids = current_ids

    except Exception as e:
        print(f'Retrieving error: {e}')


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
        print('Access denied.')


def setup():
    image = Image.new('RGB', (64, 64), (45, 45, 45))
    dc = ImageDraw.Draw(image)
    dc.ellipse([2, 2, 62, 62], fill=(0, 255, 150))

    def open_setting(_, __):
        os.system('start ms-settings:notifications')

    def on_quit(icon, _):
        icon.stop()

    menu = Menu(
        MenuItem('Open Notification Settings', open_setting, default=True),
        MenuItem('reload config', load_config),
        MenuItem('Exit', on_quit)
    )
    return Icon(
        'NotificationSoundHook',
        icon=image,
        title=TITLE,
        menu=menu
    )


def run_asyncio_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_notification_listener())


if __name__ == "__main__":
    threading.Thread(target=run_asyncio_thread, daemon=True).start()
    setup().run()
