# main.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('games', 'games'),
        ('assets', 'assets'),
        ('core', 'core'),
        ('3-foil.ico', '.'),
        ('3-foil-w.png', '.'),
        ('3-stripes-w.png', '.'),
        ('bata-3.jpg', '.'),
    ],
    hiddenimports=[
        '_cffi_backend',
        'cffi',
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'games.tic_tac_toe',
        'games.memory_game',
        'games.balloon_pop',
        'games.fruit_ninja_game',
        'games.object_catcher_game',
        'games.base_game',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='3-foil.ico',
)