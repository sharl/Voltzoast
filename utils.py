# -*- coding: utf-8 -*-
from pathlib import Path
import ctypes
import os
import sys

from win32com.client import Dispatch
from win32com.propsys import propsys, pscon
from win32com.shell import shellcon
import pythoncom
import winshell


def resource_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath('.'), path)


def setup_program(APP_NAME, APP_ID):
    """スタートメニューにAUMID付きショートカットを作成する"""

    # 自分のプロセスに AUMID をセット
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    # スタートメニューのパス
    shortcut_path = Path(winshell.programs()) / f"{APP_NAME}.lnk"
    target_exe = sys.executable

    # すでに存在していても、AUMIDを更新するために再作成
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = target_exe
    shortcut.WorkingDirectory = os.path.dirname(target_exe)
    shortcut.save()

    # ショートカットのプロパティに AUMID (System.AppUserModel.ID) を書き込む
    # これが WinRT の add_notification_changed を通す鍵
    try:
        storage_mode = shellcon.STGM_READWRITE
    except AttributeError:
        storage_mode = 2
    store = propsys.SHGetPropertyStoreFromParsingName(str(shortcut_path), None, storage_mode)
    pk = pscon.PKEY_AppUserModel_ID

    val = propsys.PROPVARIANTType(APP_ID, pythoncom.VT_LPWSTR)
    store.SetValue(pk, val)
    store.Commit()
    print(f"Shortcut created and AUMID registered: {shortcut_path}")
