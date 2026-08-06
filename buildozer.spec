[app]

# 应用名与包名
title = 虚拟小猫
package.name = virtualcat
package.domain = org.example

# python-for-android 用 develop 分支:
# master 分支的 run_pymodules_install 仍会执行 `pip install -U pip`,
# 把 venv 内 pip 升级到最新版导致自身损坏(ImportError: open_rich_spinner),
# 第五次构建(buildozer.spec 改 master 后)即因此失败;
# develop 分支已移除该 pip 自升级逻辑(2026-08-06 查证 build.py)
p4a.branch = develop

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
