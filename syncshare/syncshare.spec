# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('templates/*', 'templates'),
        ('static/*', 'static'),
        ('app.py', '.'),
        ('C:\\Users\\qwerty\\Downloads\\ngrok-v3-stable-windows-amd64\\ngrok.exe', '.')

    ],
    hiddenimports=['PyQt6', 'qrcode', 'requests'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SyncShare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SyncShare'
)
