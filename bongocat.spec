# -*- mode: python ; coding: utf-8 -*-
# bongocat.spec — PyInstaller spec для Bongo Cat AI
# Запуск: pyinstaller bongocat.spec

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Собираем все данные (ассеты, данные)
datas = [
    ('assets',   'assets'),   # иконки, картинки
    ('data',     'data'),     # начальные json-файлы
    ('config.py','.')         # конфиг рядом с exe (перезаписываемый)
]

# Скрытые импорты
hiddenimports = [
    'plyer.platforms.win.notification',
    'plyer.platforms.win',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.scrolledtext',
    'tkinter.ttk',
    'requests',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zetas, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BongoCatAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # без чёрного окна консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico', # иконка exe
    uac_admin=False,        # не требуем прав администратора
    version='version_info.txt',  # метаданные exe
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BongoCatAI',
)
