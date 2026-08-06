[app]

# 应用名与包名
title = 虚拟小猫
package.name = virtualcat
package.domain = org.example

# python-for-android 固定到修复版(build: avoid pip self-upgrade corrupting the build venv, 2026-07-30)
# 默认版存在 pip 升级损坏 venv 的 bug,导致 ImportError: BuildDependencyInstallError / open_rich_spinner
p4a.commit = d2ee8c54d9d42375a95f18159e950a119671cf63

# 源码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = config.py, save.py, game.py, main.py
source.exclude_patterns = build, .git

# 版本
version = 1.0.0
version.code = 1

# 入口
orientation = landscape
fullscreen = 1

# Android 配置
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Python 依赖(kivy 2.3.1 为本机验证过的稳定版;
# hostpython3/python3 固定 3.11:p4a 默认的 3.14 会导致 pip 与 p4a 代码不兼容而构建崩溃)
requirements = hostpython3==3.11.6,python3==3.11.6,kivy==2.3.1

# 图标与启动图
icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
