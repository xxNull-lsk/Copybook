# -*- mode: python -*-
import sys
sys.setrecursionlimit(5000)

block_cipher = None


a = Analysis(['../main.py',
			  '../PinYin.py',
			  '../HanZi.py'],
             pathex=['../'],
             binaries=[('/home/allan/work/PinYin/fonts', 'fonts'), ('../app.ico', '.')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
if False:
    exe = EXE(pyz,
              a.scripts,
              [],
              exclude_binaries=True,
              name='Copybook',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              console=False)
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=False,
                   upx=True,
                   name='Copybook')
else:
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='Copybook',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              runtime_tmpdir=None,
              console=False , icon='../app.ico')