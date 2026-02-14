# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import uuid

import requests


class Switchbot:
    base_url = 'https://api.switch-bot.com'
    charset = 'utf-8'
    token = None
    secret = None
    devices = []

    def __init__(self):
        conf = (os.environ.get('HOME') or '.') + '/.switchbot'
        try:
            with open(conf) as fd:
                j = json.load(fd)
                self.token = j['token']
                self.secret = j['secret']
        except Exception as e:
            raise e

    def make_headers(self):
        nonce = uuid.uuid4()
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(self.token, t, nonce)

        string_to_sign = bytes(string_to_sign, self.charset)
        secret = bytes(self.secret, self.charset)
        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

        return {
            'Content-Type': 'application/json; charset={}'.format(self.charset),
            'Authorization': self.token,
            'sign': str(sign, self.charset),
            't': str(t),
            'nonce': str(nonce),
        }

    def get_device_list(self):
        headers = self.make_headers()
        with requests.get(self.base_url + '/v1.1/devices', headers=headers, timeout=10) as r:
            self.devices = json.loads(str(r.content, 'utf-8')).get('body', {}).get('deviceList', [])
        return self.devices

    def get_device_ID(self, deviceName, isCloud=True):
        for d in self.devices:
            if d.get('deviceName') == deviceName and d.get('enableCloudService') is isCloud:
                return d.get('deviceId')

    def set_device_power(self, deviceID, cmd):
        commands = {
            'on': 'turnOn',
            'off': 'turnOff',
        }
        headers = self.make_headers()
        try:
            command = commands[cmd]
            requests.post(self.base_url + '/v1.1/devices/{}/commands'.format(deviceID),
                          headers=headers,
                          json={
                              'command': command,
                              'parameter': 'default',
                              'commandType': 'command',
                          },
                          timeout=10)
            return 'ok'
        except Exception:
            return 'ng'


if __name__ == '__main__':
    sb = Switchbot()
    sb.get_device_list()
    for device in sb.get_device_list():
        print(device)
    deviceName = '電撃'
    deviceID = sb.get_device_ID(deviceName)
    print(deviceName, deviceID)
    sb.set_device_power(deviceID, 'on')
