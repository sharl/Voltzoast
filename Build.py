import os
import sys
import subprocess
import shutil
from pathlib import Path


def get_asset_data(filename):
    """Assets フォルダからデータを読み込む"""
    path = Path("Assets") / filename
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def generate_manifest(app_id, version):
    """Assets の情報に基づいてマニフェストファイルを生成する"""
    manifest_path = Path("voltzoast.manifest")
    # Windows の assemblyIdentity version は 'n.n.n.n' 形式である必要があるため補完
    win_version = f"{version}.0" if version.count('.') < 3 else version
    
    content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity 
    version="{win_version}" 
    name="{app_id}" 
    type="win32" 
    processorArchitecture="*"/>
  <description>Voltzoast - Notification Hub</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
    </application>
  </compatibility>
</assembly>
"""
    manifest_path.write_text(content, encoding="utf-8")
    return manifest_path


def build():
    try:
        # 1. Assets から情報を取得
        print("Checking assets...")
        app_name = get_asset_data("app_name.txt")
        app_id_format = get_asset_data("app_id_format.txt")
        app_id = app_id_format.format(app_name)
        version = get_asset_data("version.txt")

        print(f"Target App Name: {app_name}")
        print(f"Target App ID  : {app_id}")
        print(f"Target Version : {version}")
        exit()

        # 2. マニフェスト生成
        print("Generating manifest...")
        manifest_file = generate_manifest(app_id, version)

        # 3. PyInstaller コマンドの構築
        # --add-data の区切り文字は Windows なら ';'
        cmd = [
            "pyinstaller",
            "voltzoast.py",
            "--onefile",
            "--noconsole",
            "--name", "voltzoast",
            "--icon", "Assets/sample.ico",
            "--manifest", str(manifest_file),
            "--add-data", "Assets;Assets",
            "--clean"
        ]

        # 4. 実行
        print("Starting PyInstaller...")
        subprocess.run(cmd, check=True)
        
        print("\n" + "="*30)
        print("BUILD SUCCESSFUL")
        print(f"Version: {version}")
        print(f"Executable: dist/voltzoast.exe")
        print("="*30)

    except Exception as e:
        print(f"\nBUILD FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()
