# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# myBIZcon PC Desktop Client - PyInstaller Build Spec
# =============================================================================
# AGY Step 17: Packages pc_desktop_client.py into a single Windows EXE
# using PyInstaller with windowed (no console) mode.
#
# Usage:
#   cd pc_client
#   pyinstaller pyinstaller_build.spec --clean
#
# Output: pc_client/dist/myBIZcon.exe
# =============================================================================

block_cipher = None

a = Analysis(
    ['pc_desktop_client.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Include any resource files (icons, config templates, etc.)
        # Example: ('../backend/app/config.py', 'backend/app'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.font',
        'threading',
        'json',
        'os',
        'sys',
        'urllib.request',
        'urllib.parse',
        'urllib.error',
        'http.client',
        'wave',
        'struct',
        'time',
        'datetime',
        'logging',
        # PyAudio / soundcard for WASAPI loopback (optional, include if installed)
        # 'pyaudio',
        # 'soundcard',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
    ],
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
    name='myBIZcon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # Compress the EXE using UPX if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # --windowed: no terminal console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='myBIZcon.ico',  # Uncomment and provide .ico file for production
)
