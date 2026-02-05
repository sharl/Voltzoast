# -*- coding: utf-8 -*-
import asyncio
import json
import os
import threading
import winsound

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import winrt.windows.ui.notifications as notifications
import winrt.windows.ui.notifications.management as management


# .config example
# {
#     "スマートフォン連携": [
#         {"target": "title", "match": "YouTube", "file": "C:\\Windows\\Media\\Windows Foreground.wav"},
#         {"target": "title", "match": "X", "file": "C:\\Windows\\Media\\Windows Notify Messaging.wav"}
#     ],
#     "Notifications Visualizer": "C:\\Windows\\Media\\notify.wav"
# }
def load_config():
    with open('.config', encoding='utf-8') as fd:
        j = json.load(fd)
        print(json.dumps(j, indent=2, ensure_ascii=False))
        return j


TITLE = 'Notification Sound Hook'
SOUND_CONFIG = load_config()
main_loop = None
last_toast_ids = []


def get_sound_path(app_name, title, body):
    """ルールに基づいて適切なサウンドパスを返す"""
    if app_name not in SOUND_CONFIG:
        return None

    config = SOUND_CONFIG[app_name]

    # 単純な文字列指定の場合
    if isinstance(config, str):
        return config

    # ルールリスト（dictのリスト）の場合
    if isinstance(config, list):
        for rule in config:
            target_val = title if rule.get('target') == 'title' else body
            if rule.get('match') in target_val:
                return rule.get('file')

    return None


def play_app_sound(app_name, title="", body=""):
    sound_path = get_sound_path(app_name, title, body)
    if not sound_path:
        return

    try:
        print(f'Playing: {sound_path}')
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
        latest = toasts[-1]

        # 初回起動時は音を鳴らさずIDリストの更新のみ行う
        if not last_toast_ids:
            last_toast_ids = current_ids
            return

        if latest.id not in last_toast_ids:
            app_name = latest.app_info.display_info.display_name
            title = ""
            body = ""

            binding = latest.notification.visual.get_binding('ToastGeneric')
            if binding:
                elements = list(binding.get_text_elements())
                # スマートフォン連携等の構造に合わせた抽出
                if len(elements) > 0:
                    title = elements[0].text or ""
                if len(elements) > 1:
                    # 2枚目以降のテキストを結合
                    body = "\n".join([e.text for e in elements[1:] if e.text])

            print(f'Detected: [{app_name}] {title} / {body[:30]}...')
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
        MenuItem('Open Settings', open_setting),
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
