# 🐱 虚拟小猫 · Android APK 打包指南

本项目是"虚拟小猫"的 **Kivy 版**(Android 可打包),由 tkinter 桌面版迁移而来,
全部功能保留(猫抓老鼠 / 成长 / 结婚 / 孕周 / 医院科室 / 商店 / 银行 / 市场 /
文具 / 宠物 / 衣柜 / 学校 / 公交 / 鱼缸 / 小鸟 / 造经验机 / 存档)。

## 一、本机预览(Windows / macOS / Linux)

```bash
pip install kivy
python main.py          # 弹出桌面窗口,触屏设备用鼠标拖动即可
```

> 注意:桌面预览用 `python main.py`;`config.py / save.py / game.py / main.py`
> 四个文件必须放在同一目录。

## 二、打包 APK(两种方式任选)

### 方式 A:GitHub Actions 云构建(推荐,不需要本机装 Linux)

1. 把整个 `virtual_cat_apk/` 目录上传到一个 GitHub 仓库(保持 `.github/workflows/build.yml` 存在)
2. 仓库 `Actions` 标签页会看到 **build-apk** 工作流,点 **Run workflow**
3. 约 20~40 分钟后构建完成,在 Actions 运行页面的 **Artifacts** 里下载 `virtualcat-apk.zip`
4. 解压得到 `virtualcat-0.1-*-arm64-v8a_armeabi-v7a-debug.apk`,传到平板安装即可

> 云构建自动完成:装 Java/Python/buildozer → 下载 Android SDK/NDK → 编译 → 产出 APK。

### 方式 B:本机手动构建(Windows 需先装 WSL2)

**Windows 用户(WSL2):**
```powershell
# 1. 管理员 PowerShell 安装 WSL2 Ubuntu
wsl --install -d Ubuntu
# 重启后进入 Ubuntu

# 2. Ubuntu 内:
sudo apt update && sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \
  autoconf libtool pkg-config zlib1g-dev libncurses-dev libffi-dev libssl-dev
pip3 install --user buildozer cython
cd /mnt/c/Users/<你的用户名>/WorkBuddy/2026-08-01-22-06-09/virtual_cat_apk
yes | buildozer android debug
# 产出 APK 在 bin/virtualcat-*.apk
```

**macOS / Linux 用户:**
```bash
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool \
  pkg-config zlib1g-dev libncurses-dev libffi-dev libssl-dev
pip3 install --user buildozer cython
cd virtual_cat_apk
yes | buildozer android debug
```

首次构建会下载 Android SDK / NDK(约 3~5 GB),耗时 30~60 分钟属正常。

## 三、安装到 Android 平板

- 把 `.apk` 传到平板(网盘 / USB / adb install)
- 允许"安装未知来源应用"
- 打开即玩;进度自动保存到应用数据目录

## 四、常见问题

| 问题 | 解决 |
|---|---|
| 构建报 SDK 下载失败 | 挂代理重试;或在 `buildozer.spec` 里把 `android.accept_sdk_license = True` 加上 |
| APK 安装后闪退 | 用 `adb logcat` 看日志;多半是字体/分辨率,代码已做自适应 |
| 想改数值(抓鼠奖励等) | 改同目录 `config.py`,重新打包 |
