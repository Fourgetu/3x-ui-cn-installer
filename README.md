# 3x-ui 中文自动同步版

本仓库用于跟随官方 [`MHSanaei/3x-ui`](https://github.com/MHSanaei/3x-ui) 最新脚本，并自动生成中文安装脚本和中文管理菜单。

## 一键安装

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fourgetu/3x-ui-cn-installer/main/install-cn.sh)
```

如果你再次 fork 本仓库，请把命令里的 `Fourgetu/3x-ui-cn-installer` 改成你的仓库名，例如：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/你的用户名/3x-ui-cn-installer/main/install-cn.sh)
```

## 仓库文件

| 文件 | 用途 |
| --- | --- |
| [`install-cn.sh`](install-cn.sh) | 自动生成的中文安装脚本 |
| [`x-ui-cn.sh`](x-ui-cn.sh) | 自动生成的中文 `x-ui` 管理菜单 |
| [`upstream-version.txt`](upstream-version.txt) | 最近一次同步到的官方 Release 版本 |
| [`scripts/sync-official.sh`](scripts/sync-official.sh) | 下载官方脚本并生成中文脚本 |
| [`scripts/translate-cn.py`](scripts/translate-cn.py) | 中文化规则脚本 |
| [`.github/workflows/sync-official.yml`](.github/workflows/sync-official.yml) | GitHub Actions 自动同步任务 |

## 自动同步

GitHub Actions 会在每天 UTC 03:37 自动运行，也可以在 Actions 页面手动运行 `Sync official 3x-ui scripts`。

同步流程：

1. 从官方仓库下载最新 `install.sh` 和 `x-ui.sh`。
2. 使用 `scripts/translate-cn.py` 生成 `install-cn.sh` 和 `x-ui-cn.sh`。
3. 将脚本里的官方菜单更新地址改为当前 fork 的中文脚本地址。
4. 读取官方最新 Release 版本并写入 `upstream-version.txt`。
5. 如果文件有变化，自动提交到当前分支。

## 翻译策略

本仓库不会对 shell 脚本做整文件机器翻译。翻译器只替换常见菜单、提示、错误信息和状态文本，变量、命令、路径、URL、函数名会保留原样。

这样做的好处是同步更稳定：官方新增未覆盖的英文提示时，脚本仍然能正常运行，只是那一行会暂时保持英文。你可以继续在 `scripts/translate-cn.py` 的 `PHRASES` 或 `MENU_ITEMS` 里补充翻译规则。

## 手动同步

在本地运行：

```bash
bash scripts/sync-official.sh
```

如果你在本地仓库没有 GitHub Actions 环境变量，可以指定目标仓库：

```bash
TARGET_REPO=你的用户名/3x-ui-cn-installer TARGET_BRANCH=main bash scripts/sync-official.sh
```

## 官方项目

官方原项目：[`MHSanaei/3x-ui`](https://github.com/MHSanaei/3x-ui)
