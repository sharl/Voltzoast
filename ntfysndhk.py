# -*- coding: utf-8 -*-
import asyncio
import os
import threading
import winsound

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import winrt.windows.ui.notifications as notifications
import winrt.windows.ui.notifications.management as management

TITLE = 'Notification Sound Hook'
SOUND_CONFIG = {
    # app_name: dict
    'スマートフォン連携': {
        # title:  filename
        'YouTube': r'C:\Windows\Media\Windows Foreground.wav',
        'X': r'C:\Windows\Media\Windows Notify Messaging.wav',
    },
    # app_name: filename
    'Notifications Visualizer': r'C:\Windows\Media\notify.wav',
}
main_loop = None
last_toast_ids = [-1]


def play_app_sound(app_name, title=None, body=None):
    sound_path = None
    if app_name in SOUND_CONFIG:
        if isinstance(SOUND_CONFIG[app_name], dict):
            if title in SOUND_CONFIG[app_name]:
                sound_path = SOUND_CONFIG[app_name][title]
        elif isinstance(SOUND_CONFIG[app_name], str):
            sound_path = SOUND_CONFIG[app_name]
    try:
        print(f'{sound_path=}')
        if isinstance(sound_path, str):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f'play sound rror: {e}')


def run_asyncio_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_notification_listener())


async def fetch_contents(listener):
    global last_toast_ids

    print(f'>>> {last_toast_ids=}')
    try:
        # get toast notifications list
        toasts = list(await listener.get_notifications_async(notifications.NotificationKinds.TOAST))
        if not toasts:
            print('toast notifications are empty.')
            return

        toast_ids = [toasts[i].id for i in range(len(toasts))]
        print(f'{toast_ids=}')

        # get latest toast ID
        latest = toasts[-1]
        latest_id = latest.id
        print(f'{latest_id=}')

        # FIXME: wrong function at fitst time
        if last_toast_ids and latest_id not in last_toast_ids:
            # get application name
            app_name = latest.app_info.display_info.display_name

            # get information from toast
            title = 'No Title'
            body = ''

            binding = latest.notification.visual.get_binding('ToastGeneric')
            if binding:
                # examples:
                # extract only <text>, no attributions
                #
                # <visual>
                #   <binding template="ToastGeneric">
                #     <text>YouTube</text>
                #     <text>打首獄門同好会 -GOKUMON-</text>
                #     <text>打首獄門同好会「10獄放送局」第67回</text>
                #   </binding>
                # </visual>
                # 0: Phone App
                # 1: channel name
                # 2: title
                #
                # <visual>
                #   <binding template="ToastGeneric">
                #     <text>X</text>
                #     <text>青木亞一人🎯アシュラシンドロームとTsukisamu Mutton Network(TMN)</text>
                #     <text>会長ありがとうございました</text>
                #   </binding>
                # </visual>
                # 0: Phone App
                # 1: from
                # 2: body

                # construct title, body
                elements = list(binding.get_text_elements())
                if len(elements) > 0:
                    # Phone App
                    title = elements[0].text
                if len(elements) > 1:
                    body = '\n'.join([elements[i].text for i in range(1, len(elements[1:]) + 1)])

            lines = [
                f'app_name: {app_name}',
                f'title   : {title}',
                f'body    :\n{body}',
            ]
            for line in lines:
                print(line)

            play_app_sound(app_name, title=title, body=body)

        # save toast list
        del last_toast_ids
        last_toast_ids = toast_ids

        print(f'<<< {last_toast_ids=}')

    except Exception as e:
        # error handling includes 0x8000000B (E_BOUNDS)
        print(f'(Skip) Error when retrieving information: {e}')


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
        print('Notification access is not allowed, please check your settings.')


def setup():
    image = Image.new('RGB', (64, 64), (45, 45, 45))
    dc = ImageDraw.Draw(image)
    dc.ellipse([2, 2, 62, 62], fill=(0, 255, 150))

    def open_setting(self):
        os.system('start ms-settings:notifications')

    def on_quit(icon):
        icon.stop()

    menu = Menu(
        MenuItem('Open notification setting', open_setting, default=True),
        MenuItem('Exit', on_quit),
    )
    return Icon(name='PYTHON.win32.NotificationSoundHook', icon=image, title=TITLE, menu=menu)


if __name__ == "__main__":
    threading.Thread(target=run_asyncio_thread, daemon=True).start()
    setup().run()
