# -*- coding: utf-8 -*-
import re


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
    for i in range(0, 2359 + 1):
        t = f'{i:04d}'
        hh = t[:2]
        mm = t[2:]
        text = f'まもなく、雪になるでしょう 現在地で{hh}:{mm}に降り始め、28分間続くことが予想されます。'
        repl = dictime(text)
        if '時' in repl:
            print(repl)
