# -*- coding: utf-8 -*-
"""
libthorvg recipe 修复版(本地覆盖 p4a develop 的内置 recipe)。

p4a develop 内置版在 build_arch 末尾用
    clang_lib_dir = glob(pattern)[0]
查找 NDK 里的 libomp.so,若 glob 匹配不到(NDK r25b 布局差异)
会直接抛 IndexError: list index out of range,导致整个构建失败。
本修复版把 glob 改为安全取值:匹配不到时跳过 libomp 复制,不致命。
"""
from pythonforandroid.recipe import Recipe, MesonRecipe
from os.path import join
from pythonforandroid.util import ensure_dir, current_directory
from pythonforandroid.logger import shprint, info
from multiprocessing import cpu_count
from glob import glob
import sh


class LibThorVGRecipe(MesonRecipe):
    name = "libthorvg"
    version = "1.0.5"
    url = "https://github.com/thorvg/thorvg/archive/refs/tags/v{version}.tar.gz"
    config_otps = [
        "-Dsimd=true",
        "-Dbindings=capi",
        "-Dtools=all",
        "-Dengines=cpu,gl",
        "-Dloaders=svg,png,jpg,ttf,webp",
        "-Dextra=opengl_es,lottie_exp,openmp",
    ]
    need_stl_shared = True
    skip_python = True
    depends = ["png", "libwebp", "jpeg"]
    patches = ["meson.patch"]
    bins = ["tvg-lottie2gif", "tvg-svg2png"]
    built_libraries = {
        "libthorvg-1.so": "install/lib",
        "libomp.so": "install/lib"
    }
    for bin in bins:
        built_libraries[f"lib{bin}bin.so"] = "install/bin"

    def should_build(self, arch):
        return Recipe.should_build(self, arch)

    def get_include_dir(self, arch):
        return join(self.get_build_dir(arch.arch), "install", "include")

    def build_arch(self, arch):
        super().build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_dir = join(build_dir, "install")
        ensure_dir(install_dir)
        env = self.get_recipe_env(arch)

        lib_dir = self.ctx.get_libs_dir(arch.arch)
        png_include = self.get_recipe("png", self.ctx).get_build_dir(arch.arch)
        webp_include = join(
            self.get_recipe("libwebp", self.ctx).get_build_dir(arch.arch), "src"
        )
        jpg_dir = self.get_recipe("jpeg", self.ctx).get_build_dir(arch.arch)

        with current_directory(build_dir):

            shprint(
                self.get_meson_command(env),
                "setup",
                "builddir",
                "--cross-file",
                join("/tmp", "android.meson.cross"),
                f"--prefix={install_dir}",
                # config opts
                *self.config_otps,
                # deps
                f"-Dpng_include_dir={png_include}",
                f"-Dpng_lib_dir={lib_dir}",
                f"-Dwebp_include_dir={webp_include}",
                f"-Dwebp_lib_dir={lib_dir}",
                f"-Djpg_include_dir={jpg_dir}",
                f"-Djpg_lib_dir={jpg_dir}",
                _env=env,
            )

            shprint(
                self.get_ninja_command(env),
                "-C", "builddir", "-j", str(cpu_count()),
                _env=env,
            )
            shprint(sh.rm, "-rf", install_dir)
            shprint(sh.mkdir, install_dir)
            shprint(
                self.get_ninja_command(env),
                "-C", "builddir", "install",
                _env=env,
            )

            # copy libomp.so(修复:glob 匹配不到时跳过,不再 IndexError 崩溃;
            # 若最终未复制,从 built_libraries 移除该条目,避免 install_libraries 阶段 cp 失败)
            arch_map = {
                "arm64-v8a": "aarch64",
                "armeabi-v7a": "arm",
                "x86": "i386",
                "x86_64": "x86_64",
            }
            lib_arch = arch_map[arch.arch]
            # clang version directory is variable, so glob it
            libomp_copied = False
            pattern = join(self.ctx.ndk.llvm_prebuilt_dir, "lib/clang/*/lib/linux", lib_arch)
            clang_lib_dirs = glob(pattern)
            if clang_lib_dirs:
                libomp = join(clang_lib_dirs[0], "libomp.so")
                if glob(libomp):
                    shprint(sh.cp, libomp, join("install", "lib"))
                    libomp_copied = True
            if not libomp_copied:
                # 递归再找一次(NDK r25b 等布局下 libomp 可能在其他子目录)
                recursive = glob(
                    join(self.ctx.ndk.llvm_prebuilt_dir, "**", "libomp.so"),
                    recursive=True,
                )
                if recursive:
                    shprint(sh.cp, recursive[0], join("install", "lib"))
                    libomp_copied = True
            if not libomp_copied:
                info("libthorvg: libomp.so not found in NDK, removing from built_libraries (non-fatal)")
                self.built_libraries.pop("libomp.so", None)

            # setup bins
            bin_dir = join("install", "bin")
            for bin in self.bins:
                shprint(sh.cp, join(bin_dir, bin), join(bin_dir, f"lib{bin}bin.so"))


recipe = LibThorVGRecipe()
