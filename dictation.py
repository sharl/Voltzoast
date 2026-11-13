# -*- coding: utf-8 -*-
from datetime import datetime as dt
import re


def dicdate(text: str) -> str:
    date_pattern = re.compile(r'(\d{1,2}/\d{1,2})')
    matches = re.findall(date_pattern, text)
    if matches:
        for pat in matches:
            yy = dt.now().year
            leap = (yy % 4 == 0 and (yy % 100 != 0 or yy % 400 == 0))

            mm, dd = [int(mmdd) for mmdd in pat.split('/')]
            if (mm in (4, 6, 9, 11) and dd > 30) or (mm == 2 and dd > (28 + leap)):
                continue
            if dd == 0 or dd > 31:
                continue
            repl = f'{mm}月{dd}日'
            text = text.replace(pat, repl)

    return text


def dictime(text: str) -> str:
    time_pattern = re.compile(r'(\d{1,2}:\d{1,2})')
    matches = re.findall(time_pattern, text)
    if matches:
        for pat in matches:
            hh, mm = pat.split(':')
            if int(hh) > 23 or int(mm) > 59:
                continue

            if hh.startswith('0'):
                hh = hh.removeprefix('0')
            if mm.startswith('0'):
                mm = mm.removeprefix('0')
            repl = f'{hh}時{mm}分'

            text = text.replace(pat, repl)
            if '時0分' in text:
                text = text.replace('0分', '')

    return text


if __name__ == '__main__':
    # test dicdate
    for i in range(101, 1231 + 1):
        mm = i // 100
        dd = i % 100
        text = f'今日は{mm}/{dd}です'
        repl = dicdate(text)
        if '月' in repl and '日' in repl:
            print(repl)

    # test dictime
    for i in range(0, 2359 + 1):
        t = f'{i:04d}'
        hh = t[:2]
        mm = t[2:]
        text = f'まもなく、雪になるでしょう 現在地で{hh}:{mm}に降り始め、28分間続くことが予想されます。'
        repl = dictime(text)
        if '時' in repl:
            print(repl)
