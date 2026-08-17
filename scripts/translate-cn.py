#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


PHRASES = [
    ("Fatal error:", "致命错误："),
    ("Please run this script with root privilege", "请使用 root 权限运行此脚本"),
    ("Failed to check the system OS, please contact the author!", "检测系统失败，请联系作者！"),
    ("The OS release is:", "系统发行版："),
    ("Unsupported CPU architecture!", "不支持的 CPU 架构！"),
    ("Install result written to", "安装结果已写入"),
    ("Failed to write", "写入失败"),
    ("Installing PostgreSQL client tools", "正在安装 PostgreSQL 客户端工具"),
    ("Installing acme.sh for SSL certificate management", "正在安装 acme.sh 用于 SSL 证书管理"),
    ("Failed to install acme.sh", "安装 acme.sh 失败"),
    ("acme.sh installed successfully", "acme.sh 安装成功"),
    ("Setting up SSL certificate", "正在配置 SSL 证书"),
    ("Issuing SSL certificate for", "正在为此域名申请 SSL 证书："),
    ("Port 80 must be open and accessible from the internet", "80 端口必须开放并可从公网访问"),
    ("Failed to issue certificate", "证书申请失败"),
    ("Failed to install certificate", "证书安装失败"),
    ("Certificate files not found", "未找到证书文件"),
    ("Certificate files installed successfully", "证书文件安装成功"),
    ("Certificate paths configured successfully", "证书路径配置成功"),
    ("Please enter your domain name", "请输入你的域名"),
    ("Domain name cannot be empty. Please try again.", "域名不能为空，请重试。"),
    ("Invalid domain format", "域名格式无效"),
    ("Choose SSL certificate setup method", "请选择 SSL 证书配置方式"),
    ("Let's Encrypt for Domain", "Let's Encrypt 域名证书"),
    ("Let's Encrypt for IP Address", "Let's Encrypt IP 证书"),
    ("Custom SSL Certificate", "自定义 SSL 证书"),
    ("Skip SSL", "跳过 SSL"),
    ("Choose an option", "请选择一个选项"),
    ("Invalid option. Please select a valid number.", "选项无效，请输入有效数字。"),
    ("Please enter your server's public IPv4 address", "请输入服务器公网 IPv4 地址"),
    ("Invalid IPv4 address. Please try again.", "IPv4 地址无效，请重试。"),
    ("Database Selection", "数据库选择"),
    ("SQLite", "SQLite"),
    ("PostgreSQL", "PostgreSQL"),
    ("Choose [1]", "请选择 [1]"),
    ("Install PostgreSQL locally", "本机安装 PostgreSQL"),
    ("Use an existing PostgreSQL server", "使用已有 PostgreSQL 服务器"),
    ("Enter PostgreSQL DSN", "请输入 PostgreSQL DSN"),
    ("Panel Installation Complete!", "面板安装完成！"),
    ("Username:", "用户名："),
    ("Password:", "密码："),
    ("Port:", "端口："),
    ("WebBasePath:", "网页根路径："),
    ("Database:", "数据库："),
    ("Access URL:", "访问地址："),
    ("API Token:", "API Token："),
    ("IMPORTANT: Save these credentials securely!", "重要：请安全保存这些登录信息！"),
    ("Downloading x-ui failed", "下载 x-ui 失败"),
    ("Downloading and installing panel version", "正在下载并安装面板版本"),
    ("Beginning to install x-ui", "开始安装 x-ui"),
    ("Failed to download x-ui.sh", "下载 x-ui.sh 失败"),
    ("installation finished, it is running now", "安装完成，当前正在运行"),
    ("Running...", "运行中..."),
    ("Running", "运行中"),
    ("Admin Management Script", "管理脚本"),
    ("Panel Management Script", "面板管理脚本"),
    ("Exit Script", "退出脚本"),
    ("Press enter to return to the main menu", "按回车返回主菜单"),
    ("Updating Menu", "正在更新菜单"),
    ("Update Menu", "更新菜单"),
    ("Legacy Version", "历史版本"),
    ("Update successful. The panel has automatically restarted.", "更新成功，面板已自动重启。"),
    ("Failed to update the menu.", "菜单更新失败。"),
    ("Enter the panel version", "请输入面板版本"),
    ("Panel version cannot be empty. Exiting.", "面板版本不能为空，正在退出。"),
    ("Uninstalled Successfully.", "卸载成功。"),
    ("If you need to install this panel again, you can use below command:", "如需重新安装面板，可以使用以下命令："),
    ("Please set the login username", "请设置登录用户名"),
    ("Please set the login password", "请设置登录密码"),
    ("Do you want to disable currently configured two-factor authentication?", "是否禁用当前配置的两步验证？"),
    ("Two factor authentication has been disabled.", "两步验证已禁用。"),
    ("Panel login username has been reset to:", "面板登录用户名已重置为："),
    ("Panel login password has been reset to:", "面板登录密码已重置为："),
    ("Resetting Web Base Path", "正在重置网页根路径"),
    ("Operation canceled.", "操作已取消。"),
    ("All panel settings have been reset to default.", "所有面板设置已重置为默认值。"),
    ("Could not auto-detect server IP from any provider.", "无法从任何服务商自动检测服务器 IP。"),
    ("The certificate also covers:", "该证书还覆盖："),
    ("No SSL certificate configured!", "未配置 SSL 证书！"),
    ("Generate SSL certificate for IP now?", "现在为 IP 生成 SSL 证书吗？"),
    ("Enter port number", "请输入端口号"),
    ("The port is set", "端口已设置"),
    ("Back to Main Menu", "返回主菜单"),
    ("Clear All logs", "清空所有日志"),
    ("All Logs cleared.", "所有日志已清空。"),
    ("Enable BBR", "启用 BBR"),
    ("Disable BBR", "禁用 BBR"),
    ("BBR is not currently enabled.", "BBR 当前未启用。"),
    ("BBR is already enabled!", "BBR 已启用！"),
    ("BBR has been enabled successfully.", "BBR 启用成功。"),
    ("Panel state:", "面板状态："),
    ("xray state:", "xray 状态："),
    ("Start automatically:", "开机自启："),
    ("Not Running", "未运行"),
    ("Not Installed", "未安装"),
    ("Managed by Docker", "由 Docker 管理"),
    ("Yes", "是"),
    ("No", "否"),
    ("Firewall Status", "防火墙状态"),
    ("Open Ports", "开放端口"),
    ("Delete", "删除"),
    ("Firewall is already active", "防火墙已启用"),
    ("Current UFW rules:", "当前 UFW 规则："),
    ("Geo", "Geo"),
    ("have been updated successfully!", "已更新成功！"),
    ("are already up to date", "已经是最新，无需重启。"),
    ("SSL Certificate Management", "SSL 证书管理"),
    ("Cloudflare SSL Certificate", "Cloudflare SSL 证书"),
    ("IP Limit Management", "IP 限制管理"),
    ("SSH Port Forwarding Management", "SSH 端口转发管理"),
    ("Logs Management", "日志管理"),
    ("Geo Files", "Geo 文件"),
    ("Get SSL", "申请 SSL"),
    ("Force Renew", "强制续期"),
    ("Show Existing Domains", "显示已有域名"),
    ("No certificates found", "未找到证书"),
    ("Existing domains:", "已有域名："),
    ("Invalid domain entered.", "输入的域名无效。"),
    ("Install Fail2ban and configure IP Limit", "安装 Fail2ban 并配置 IP 限制"),
    ("Fail2ban and IP Limit", "Fail2ban 和 IP 限制"),
    ("IP Limit installed and configured successfully!", "IP 限制安装并配置成功！"),
    ("Only remove IP Limit configurations", "仅移除 IP 限制配置"),
    ("IP Limit removed successfully!", "IP 限制移除成功！"),
    ("Change Ban Duration", "修改封禁时长"),
    ("Unban Everyone", "解除所有封禁"),
    ("Ban Logs", "封禁日志"),
    ("Ban an IP Address", "封禁一个 IP 地址"),
    ("Unban an IP Address", "解封一个 IP 地址"),
    ("Service Status", "服务状态"),
    ("Service Restart", "重启服务"),
    ("Unsupported operating system", "不支持的操作系统"),
    ("Fail2ban installed successfully!", "Fail2ban 安装成功！"),
    ("Configuring IP Limit", "正在配置 IP 限制"),
    ("Checking ban logs", "正在检查封禁日志"),
    ("Current jail status", "当前 jail 状态"),
    ("Current SSH Port Forwarding Configuration", "当前 SSH 端口转发配置"),
    ("SSH Port Forwarding Configuration", "SSH 端口转发配置"),
    ("Connection DSN", "连接 DSN"),
    ("Use option 2 to migrate your SQLite data and switch the panel to PostgreSQL.", "使用选项 2 可迁移 SQLite 数据并切换面板到 PostgreSQL。"),
    ("Migrate SQLite", "迁移 SQLite"),
    ("Restart PostgreSQL", "重启 PostgreSQL"),
    ("View PostgreSQL Log", "查看 PostgreSQL 日志"),
    ("Back Up", "备份"),
    ("Restore", "恢复"),
    ("Input file", "输入文件"),
    ("Output file", "输出文件"),
    ("Please enter your selection", "请输入你的选择"),
]


MENU_ITEMS = {
    "Install": "安装",
    "Update": "更新",
    "Custom Version": "自定义版本",
    "Legacy Version": "历史版本",
    "Uninstall": "卸载",
    "Reset Username & Password": "重置用户名和密码",
    "Reset Username & Password & Secret Token": "重置用户名、密码和密钥 Token",
    "Reset Web Base Path": "重置网页根路径",
    "Reset Settings": "重置设置",
    "Change Port": "修改端口",
    "View Current Settings": "查看当前设置",
    "Start": "启动",
    "Stop": "停止",
    "Restart": "重启",
    "Check Status": "查看状态",
    "Enable Autostart": "启用开机自启",
    "Disable Autostart": "禁用开机自启",
    "Log Management": "日志管理",
    "Logs Management": "日志管理",
    "BBR Management": "BBR 管理",
    "Firewall Management": "防火墙管理",
    "Update Geo Files": "更新 Geo 文件",
    "Cloudflare SSL Certificate": "Cloudflare SSL 证书",
    "IP Limit Management": "IP 限制管理",
    "SSH Port Forwarding Management": "SSH 端口转发管理",
    "SSL Certificate Management": "SSL 证书管理",
    "Speedtest by Ookla": "Ookla 测速",
    "Fail2ban Management": "Fail2ban 管理",
    "PostgreSQL Management": "PostgreSQL 管理",
    "Exit": "退出",
}


def translate_text(text: str) -> str:
    translated = text
    for source, target in PHRASES:
        translated = translated.replace(source, target)

    for source, target in MENU_ITEMS.items():
        translated = re.sub(rf"(?<![A-Za-z]){re.escape(source)}(?![A-Za-z])", target, translated)

    translated = translated.replace("[Default", "[默认")
    translated = translated.replace("default is a random username", "默认随机用户名")
    translated = translated.replace("default is a random password", "默认随机密码")
    translated = translated.replace("leave empty to skip", "留空跳过")
    translated = translated.replace("leave empty to abort", "留空取消")
    translated = translated.replace(
        "Please choose which port to use (default is 80): ",
        "请选择用于签发证书的端口（默认 80）: ",
    )
    translated = translated.replace(
        "Would you like to modify --reloadcmd for ACME? (y/n): ",
        "是否修改 ACME 证书续期后的重载命令？(y/n): ",
    )
    translated = translated.replace(
        "Would you like to set this certificate for the panel? (y/n): ",
        "是否将此证书设置到面板？(y/n): ",
    )
    translated = translated.replace(
        "Would you like to customize the Panel Port settings? (If not, a random port will be applied) [y/n]: ",
        "是否自定义面板端口？（不自定义将随机生成）[y/n]: ",
    )
    translated = translated.replace("Please set up the panel port: ", "请输入面板端口: ")
    translated = translated.replace("Your Panel Port is:", "面板端口为:")
    translated = translated.replace("Generated random port:", "已生成随机端口:")
    translated = translated.replace(
        "SQLite     (default — recommended for < 500 clients)",
        "SQLite     （默认，建议少于 500 个客户端时使用）",
    )
    translated = translated.replace(
        "PostgreSQL (recommended for high client counts / many nodes)",
        "PostgreSQL （建议大量客户端/多节点时使用）",
    )
    translated = translated.replace("y/n", "y/n")
    return translated


def translate_file(src: Path, dst: Path) -> None:
    original = src.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    output = [translate_text(line) for line in lines]
    dst.write_text("".join(output), encoding="utf-8", newline="")


def apply_raw_rate_limit_fallbacks(text: str, upstream: str, upstream_ref: str, target_raw_base: str) -> str:
    if "download_github_file()" not in text:
        helper = r'''
github_raw_api_url() {
    local url="$1" path owner repo ref
    case "$url" in
        https://raw.githubusercontent.com/*) ;;
        *) return 1 ;;
    esac

    path="${url#https://raw.githubusercontent.com/}"
    owner="${path%%/*}"
    path="${path#*/}"
    repo="${path%%/*}"
    path="${path#*/}"
    ref="${path%%/*}"
    path="${path#*/}"

    [[ -n "$owner" && -n "$repo" && -n "$ref" && -n "$path" ]] || return 1
    printf 'https://api.github.com/repos/%s/%s/contents/%s?ref=%s\n' "$owner" "$repo" "$path" "$ref"
}

download_github_file() {
    local output="$1" url="$2" api_url tmp
    tmp="${output}.tmp.$$"

    if curl -4fLR --retry 5 --retry-delay 3 --connect-timeout 15 --max-time 120 -o "$tmp" "$url"; then
        mv -f "$tmp" "$output"
        return 0
    fi

    rm -f "$tmp"
    api_url="$(github_raw_api_url "$url")" || return 1

    if curl -4fsSL --retry 5 --retry-delay 3 --connect-timeout 15 --max-time 120 \
        -H 'Accept: application/vnd.github.raw' -o "$tmp" "$api_url"; then
        mv -f "$tmp" "$output"
        return 0
    fi

    rm -f "$tmp"
    return 1
}

run_github_script() {
    local url="$1" tmp rc
    shift
    tmp="$(mktemp)"

    if ! download_github_file "$tmp" "$url"; then
        rm -f "$tmp"
        return 1
    fi

    bash "$tmp" "$@"
    rc=$?
    rm -f "$tmp"
    return "$rc"
}
'''
        match = re.search(r'is_domain\(\) \{\n.*?\n\}\n\n', text, flags=re.S)
        if match:
            text = text[: match.end()] + helper + text[match.end():]
        else:
            text = helper + "\n" + text

    raw_repo_base = f"https://raw.githubusercontent.com/{upstream}/{upstream_ref}"
    install_url = f"{target_raw_base}/install-cn.sh"
    menu_url = f"{target_raw_base}/x-ui-cn.sh"
    update_url = f"{raw_repo_base}/update.sh"

    text = re.sub(
        rf'bash <\(curl [^)]*["\']?{re.escape(install_url)}["\']?\)',
        f"run_github_script {install_url}",
        text,
    )
    text = re.sub(
        rf'bash <\(curl [^)]*["\']?{re.escape(update_url)}["\']?\)',
        f"run_github_script {update_url}",
        text,
    )
    text = text.replace(
        f"curl -4fLRo /usr/bin/x-ui-temp {menu_url}",
        f"download_github_file /usr/bin/x-ui-temp {menu_url}",
    )
    text = text.replace(
        f'curl -fLRo "${{xui_script_temp}}" {menu_url}',
        f'download_github_file "${{xui_script_temp}}" {menu_url}',
    )
    text = text.replace(
        f"curl -fLRo /usr/bin/x-ui {menu_url}",
        f"download_github_file /usr/bin/x-ui {menu_url}",
    )
    text = text.replace(
        f"curl -fLRo /usr/bin/x-ui -z /usr/bin/x-ui {menu_url}",
        f"download_github_file /usr/bin/x-ui {menu_url}",
    )
    for service_name in ("x-ui.rc", "x-ui.service.debian", "x-ui.service.arch", "x-ui.service.rhel"):
        text = text.replace(
            f"curl -4fLRo /etc/init.d/x-ui {raw_repo_base}/{service_name}",
            f"download_github_file /etc/init.d/x-ui {raw_repo_base}/{service_name}",
        )
        text = text.replace(
            f'curl -fLRo "${{xui_rc_temp}}" {raw_repo_base}/{service_name}',
            f'download_github_file "${{xui_rc_temp}}" {raw_repo_base}/{service_name}',
        )
        text = re.sub(
            rf"curl -4fLRo (\$\{{xui_service\}}/x-ui\.service) {re.escape(raw_repo_base)}/{service_name}",
            rf"download_github_file \1 {raw_repo_base}/{service_name}",
            text,
        )
    text = text.replace(
        'curl -fLRo "$temp_file" "$source" > /dev/null 2>&1',
        'download_github_file "$temp_file" "$source" > /dev/null 2>&1',
    )
    text = text.replace(
        'curl -fLRo "$temp_file" -z /usr/bin/x-ui "$url"',
        'download_github_file "$temp_file" "$url"',
    )
    text = text.replace(
        'curl -fLRo "$temp_file" "$url"',
        'download_github_file "$temp_file" "$url"',
    )

    api_install_cmd = (
        "bash <(curl -Ls -H 'Accept: application/vnd.github.raw' "
        "'https://api.github.com/repos/Fourgetu/3x-ui-cn-installer/contents/install-cn.sh?ref=main')"
    )
    text = text.replace(
        f"bash <(curl -Ls {install_url})",
        api_install_cmd,
    )
    return text


def patch_urls(path: Path, upstream: str, upstream_ref: str, target_raw_base: str, release_repo: str) -> None:
    text = path.read_text(encoding="utf-8")
    upstream_owner, upstream_repo = upstream.split("/", 1)
    owner_variants = {upstream_owner, upstream_owner.lower(), upstream_owner.upper()}
    ref_variants = {upstream_ref, "master", "main"}

    for owner in owner_variants:
        for ref in ref_variants:
            base = f"https://raw.githubusercontent.com/{owner}/{upstream_repo}/{ref}"
            text = text.replace(f"{base}/install.sh", f"{target_raw_base}/install-cn.sh")
            text = text.replace(f"{base}/x-ui.sh", f"{target_raw_base}/x-ui-cn.sh")

    # Keep release assets on the official upstream, but make menu/install script refreshes stay Chinese.
    text = re.sub(
        r"https://raw\.githubusercontent\.com/[Mm][Hh][Ss]anaei/3x-ui/[^\"' )]+/install\.sh",
        f"{target_raw_base}/install-cn.sh",
        text,
    )
    text = re.sub(
        r"https://raw\.githubusercontent\.com/[Mm][Hh][Ss]anaei/3x-ui/[^\"' )]+/x-ui\.sh",
        f"{target_raw_base}/x-ui-cn.sh",
        text,
    )
    text = re.sub(
        r"https://github\.com/[Mm][Hh][Ss]anaei/3x-ui/raw/[^\"' )]+/x-ui\.sh",
        f"{target_raw_base}/x-ui-cn.sh",
        text,
    )
    raw_repo_base = f"https://raw.githubusercontent.com/{upstream}/{upstream_ref}"
    text = re.sub(
        r"https://raw\.githubusercontent\.com/[Mm][Hh][Ss]anaei/3x-ui/[^\"' )]+/(update\.sh|x-ui\.rc|x-ui\.service\.(?:debian|arch|rhel))",
        lambda m: f"{raw_repo_base}/{m.group(1)}",
        text,
    )
    for repo in {upstream, "MHSanaei/3x-ui", "mhsanaei/3x-ui"}:
        text = text.replace(
            f"https://api.github.com/repos/{repo}/releases",
            f"https://api.github.com/repos/{release_repo}/releases",
        )
        text = text.replace(
            f"https://github.com/{repo}/releases",
            f"https://github.com/{release_repo}/releases",
        )
    if "XUI_SSL_PROMPT" not in text:
        text = text.replace(
            "# If the panel is already installed but no certificate is configured, prompt for SSL now",
            "# Existing installs should upgrade without stopping for SSL setup.\n"
            "            # Set XUI_SSL_PROMPT=1 when you explicitly want this installer to ask.",
        )
        text = text.replace(
            "# Existing install: if no cert configured, prompt user for SSL setup",
            "# Existing installs should upgrade without stopping for SSL setup.\n"
            "        # Set XUI_SSL_PROMPT=1 when you explicitly want this installer to ask.",
        )
        text = text.replace(
            'prompt_and_setup_ssl "${existing_port}" "${config_webBasePath}" "${server_ip}"',
            'if [[ "${XUI_SSL_PROMPT:-0}" == "1" ]]; then\n'
            '                    prompt_and_setup_ssl "${existing_port}" "${config_webBasePath}" "${server_ip}"\n'
            '                else\n'
            '                    SSL_SCHEME="http"\n'
            '                    SSL_HOST="${server_ip}"\n'
            '                    echo -e "${yellow}Existing install has no SSL certificate; skipping SSL setup during upgrade.${plain}"\n'
            '                    echo -e "${yellow}Run with XUI_SSL_PROMPT=1 if you want to configure SSL now.${plain}"\n'
            '                fi',
        )
        text = text.replace(
            'prompt_and_setup_ssl "${existing_port}" "${existing_webBasePath}" "${server_ip}"',
            'if [[ "${XUI_SSL_PROMPT:-0}" == "1" ]]; then\n'
            '                prompt_and_setup_ssl "${existing_port}" "${existing_webBasePath}" "${server_ip}"\n'
            '            else\n'
            '                SSL_SCHEME="http"\n'
            '                SSL_HOST="${server_ip}"\n'
            '                echo -e "${yellow}Existing install has no SSL certificate; skipping SSL setup during upgrade.${plain}"\n'
            '                echo -e "${yellow}Run with XUI_SSL_PROMPT=1 if you want to configure SSL now.${plain}"\n'
            '            fi',
        )
    text = apply_raw_rate_limit_fallbacks(text, upstream, upstream_ref, target_raw_base)
    path.write_text(text, encoding="utf-8", newline="")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?")
    parser.add_argument("destination", nargs="?")
    parser.add_argument("--patch-urls", action="store_true")
    parser.add_argument("--upstream", default="Fourgetu/3x-ui")
    parser.add_argument("--upstream-ref", default="main")
    parser.add_argument("--release-repo", default="")
    parser.add_argument("--target-raw-base")
    args = parser.parse_args()

    if args.patch_urls:
        if not args.source or not args.target_raw_base:
            parser.error("--patch-urls requires source and --target-raw-base")
        patch_urls(Path(args.source), args.upstream, args.upstream_ref, args.target_raw_base, args.release_repo or args.upstream)
        return

    if not args.source or not args.destination:
        parser.error("source and destination are required")

    translate_file(Path(args.source), Path(args.destination))


if __name__ == "__main__":
    main()
