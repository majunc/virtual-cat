[app]

# 应用名与包名
title = 虚拟小猫
package.name = virtualcat
package.domain = org.example

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

# Python 依赖(2.3.1 为本机验证过的稳定版)
requirements = python3,kivy==2.3.1

# 图标与启动图
icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
