#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copaw Control Manager (copaw_mgr.py)

管理 Copaw 应用的生命周期与配置。
配置文件位置: ~/.copaw_mgr.yaml
"""

import os
import sys
import subprocess
import signal
import time
import shutil
import re
import json
from pathlib import Path
from datetime import datetime
import yaml


# ==================== 全局常量 ====================
CONFIG_FILE = Path.home() / ".copaw_mgr.yaml"
COPAW_DIR = Path.home() / ".copaw"

DEFAULT_CONFIG = {
    "app": {
        "log_level": "info",
        "host": "0.0.0.0",
        "port": 9090,
        "workers": 4,
        "pid": "",
    },
    "log_rotate": {
        "days": 7,
        "rotate_file": "{{COPAW_LOG_DIR}}/app.%Y%m%d.log",
    },
    "models": {
        "custom": {"base_url": "", "api_key": ""},
        "llm_model": "",
    },
    "config": {
        "channel": {
            "feishu": {
                "enable": True,
                "app_id": "",
                "app_secret": "",
                "bot_prefix": "copaw",
                "encrypt_key": "",
                "verification_token": "",
                "media_dir": "{{COPAW_MEDIA_DIR}}",
            }
        },
        "show_tool_details": True,
    },
    "env": {
        "COPAW_WORKING_DIR": "/opt/ai_works/copaw",
        "GITHUB_TOKEN": "",
        "TAVILY_API_KEY": "",
        "COPAW_MEDIA_DIR": "/opt/ai_works/media",
        "COPAW_LOG_DIR": "~/.copaw/logs/",
    },
    "status_cmd": [
        "copaw env list",
        "copaw models list",
        "copaw channels list",
    ],
}


# ==================== 工具函数 ====================

def expand_path(path_str):
    """展开 ~ 和环境变量"""
    return Path(os.path.expandvars(os.path.expanduser(path_str)))


def run_cmd(cmd, capture=False, check=True, env=None):
    try:
        result = subprocess.run(
            cmd, shell=True, text=True, env=env,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if capture else None,
            check=check
        )
        return result.stdout.strip() if capture else None
    except subprocess.CalledProcessError:
        if not capture:
            sys.exit(1)
        return ""


def get_input_with_default(prompt, default=""):
    current = str(default) if default else ""
    val = input(f"{prompt} [{current}]: ").strip()
    return val if val else current


def render_template(text, context):
    """替换 {{KEY}} 为 context['KEY'] 的值"""
    def replacer(match):
        key = match.group(1)
        return str(context.get(key, match.group(0)))
    return re.sub(r"\{\{(\w+)\}\}", replacer, text)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = DEFAULT_CONFIG.copy()

    # 补全缺失的默认字段
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg:
            cfg[k] = v
    return cfg


def save_config(cfg):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def cleanup_old_logs(log_dir, pattern, max_days):
    now = datetime.now()
    log_dir = Path(log_dir)
    if not log_dir.exists():
        return
    for f in log_dir.glob(pattern):
        try:
            name = f.name
            if name.startswith("app.") and name.endswith(".log"):
                date_part = name[4:-4]
                log_date = datetime.strptime(date_part, "%Y%m%d")
                if (now - log_date).days > max_days:
                    f.unlink()
                    print(f"🗑️  删除旧日志: {f}")
        except (ValueError, IndexError):
            continue


def ensure_copaw_installed():
    """检查 copaw 是否已安装，否则自动 pip install"""
    if shutil.which("copaw"):
        print("✅ copaw 已安装")
        return

    print("⚠️  copaw 未安装，正在通过 pip 安装...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "copaw"], check=True)
        print("✅ copaw 安装成功")
    except subprocess.CalledProcessError:
        print("❌ 安装 copaw 失败，请手动运行: pip install copaw")
        sys.exit(1)


def get_pids_by_port(port):
    """返回监听指定端口的 PID 列表（字符串列表）"""
    try:
        result = subprocess.run(
            f"lsof -ti:{port}",
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return [p for p in result.stdout.strip().split() if p.isdigit()]
    except Exception:
        pass
    return []


def mask_secret(s: str) -> str:
    """对密钥类字符串进行脱敏：保留前2后4，中间用 * 替代"""
    if not s or len(s) <= 6:
        return "*" * len(s)
    return s[:2] + "*" * (len(s) - 6) + s[-4:]


# ==================== 核心：同步 mgr 配置到 config.json ====================

def sync_config_json(cfg):
    """将 mgr 配置中的 config 部分写入 COPAW_WORKING_DIR/config.json"""
    working_dir = expand_path(cfg["env"]["COPAW_WORKING_DIR"])
    config_json = working_dir / "config.json"

    if not config_json.exists():
        print(f"⚠️  config.json 不存在: {config_json}")
        return

    # 读取现有 config.json
    with open(config_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 更新 show_tool_details
    data["show_tool_details"] = cfg["config"]["show_tool_details"]

    # 更新 channels
    mgr_channels = cfg["config"]["channel"]
    for ch_name, mgr_ch_cfg in mgr_channels.items():
        if ch_name in data.get("channels", {}):
            target = data["channels"][ch_name]

            # 启用状态（mgr: enable → config.json: enabled）
            target["enabled"] = bool(mgr_ch_cfg.get("enable", False))

            # 字段映射
            field_map = {
                "app_id": "app_id",
                "app_secret": "app_secret",
                "bot_prefix": "bot_prefix",
                "encrypt_key": "encrypt_key",
                "verification_token": "verification_token",
                "media_dir": "media_dir",
            }

            for src_key, dst_key in field_map.items():
                if src_key in mgr_ch_cfg:
                    value = mgr_ch_cfg[src_key]
                    # 渲染模板变量（如 {{COPAW_MEDIA_DIR}}）
                    if isinstance(value, str):
                        ctx = {k: str(expand_path(v)) for k, v in cfg["env"].items()}
                        value = render_template(value, ctx)
                    target[dst_key] = value

    # 写回
    with open(config_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已更新 config.json: {config_json}")


# ==================== 命令实现 ====================

def cmd_init():
    ensure_copaw_installed()
    cfg = load_config()
    COPAW_DIR.mkdir(exist_ok=True)

    print("🔧 初始化 Copaw 配置（回车使用当前值）")

    # App 配置
    cfg["app"]["workers"] = int(get_input_with_default("App Workers", cfg["app"]["workers"]))
    cfg["app"]["host"] = get_input_with_default("Host", cfg["app"]["host"])
    cfg["app"]["port"] = get_input_with_default("Port", cfg["app"]["port"])
    cfg["app"]["log_level"] = get_input_with_default("Log Level", cfg["app"]["log_level"])

    # Models
    custom = cfg["models"]["custom"]
    custom["base_url"] = get_input_with_default("Custom LLM Base URL", custom.get("base_url", ""))
    custom["api_key"] = get_input_with_default("Custom LLM API Key", custom.get("api_key", ""))
    cfg["models"]["llm_model"] = get_input_with_default("LLM Model Name", cfg["models"].get("llm_model", ""))

    # Tavily
    tavily_key = get_input_with_default("Tavily API Key (留空则跳过)", cfg["env"].get("TAVILY_API_KEY", ""))
    cfg["env"]["TAVILY_API_KEY"] = tavily_key

    # 目录创建
    dir_keys = ["COPAW_WORKING_DIR", "COPAW_MEDIA_DIR", "COPAW_LOG_DIR"]
    for key in dir_keys:
        raw_val = cfg["env"][key]
        expanded = expand_path(raw_val)
        expanded.mkdir(parents=True, exist_ok=True)
        cfg["env"][key] = str(expanded.resolve())

    # Feishu（强制启用）
    feishu = cfg["config"]["channel"]["feishu"]
    feishu["enable"] = True
    while not feishu.get("app_id"):
        feishu["app_id"] = get_input_with_default("Feishu App ID", feishu.get("app_id", ""))
    while not feishu.get("app_secret"):
        feishu["app_secret"] = get_input_with_default("Feishu App Secret", feishu.get("app_secret", ""))

    save_config(cfg)

    # 备份旧 config.json
    working_dir = expand_path(cfg["env"]["COPAW_WORKING_DIR"])
    old_config = working_dir / "config.json"
    if old_config.exists():
        bak = working_dir / "config.json.bak"
        shutil.copy2(old_config, bak)
        print(f"💾 已备份旧配置: {bak}")

    # 执行 copaw init
    print("🔄 执行 copaw init --defaults --force ...")
    run_cmd("copaw init --defaults --force")

    # 设置环境变量
    for key, value in cfg["env"].items():
        if value:
            run_cmd(f'copaw env set {key} "{value}"')

    # 同步配置
    sync_config_json(cfg)

    # 模型交互配置
    print("\n" + "="*60)
    print("📌 模型配置提示")
    print("="*60)
    print(f"Base URL     : {cfg['models']['custom']['base_url']}")
    print(f"API Key      : {mask_secret(cfg['models']['custom']['api_key'])}")
    print(f"LLM Model    : {cfg['models']['llm_model']}")
    if cfg["env"]["TAVILY_API_KEY"]:
        print(f"Tavily Key   : {mask_secret(cfg['env']['TAVILY_API_KEY'])}")
    print("="*60)
    print("👉 接下来将启动交互式模型配置，请按提示操作...\n")

    subprocess.run(["copaw", "models", "config-key", "custom"])
    subprocess.run(["copaw", "models", "set-llm"])

    # 自动启动
    print("\n🚀 自动启动服务...")
    cmd_start([])

    print("\n📊 当前状态:")
    cmd_status()


def cmd_start(_extra_args):
    cfg = load_config()
    sync_config_json(cfg)  # 🔑 启动前强制同步

    args = [
        "--workers", str(cfg["app"]["workers"]),
        "--host", cfg["app"]["host"],
        "--port", str(cfg["app"]["port"]),
        "--log-level", cfg["app"]["log_level"]
    ]
    log_dir = expand_path(cfg["env"]["COPAW_LOG_DIR"])
    log_dir.mkdir(parents=True, exist_ok=True)
    main_log = log_dir / "app.log"
    rotate_pattern = cfg["log_rotate"]["rotate_file"]
    ctx = {"COPAW_LOG_DIR": str(log_dir.resolve())}
    rotated_name = render_template(rotate_pattern, ctx)
    rotated_path = Path(rotated_name)
    if main_log.exists() and main_log.stat().st_size > 0:
        if not rotated_path.exists():
            shutil.move(str(main_log), str(rotated_path))
            print(f"🔄 日志已轮转: {rotated_path}")
    cleanup_old_logs(log_dir, "app.*.log", cfg["log_rotate"]["days"])

    full_cmd = f"copaw app {' '.join(args)}"
    pid_file = log_dir / "copaw.pid"
    working_dir = str(expand_path(cfg["env"]["COPAW_WORKING_DIR"]))
    nohup_cmd = (
        f"COPAW_WORKING_DIR='{working_dir}' "
        f"nohup {full_cmd} >> '{main_log}' 2>&1 & "
        f"echo $! > '{pid_file}'"
    )
    print(f"▶️  启动命令: {full_cmd}")
    print(f"📄 日志文件: {main_log}")
    print(f"📁 COPAW_WORKING_DIR: {working_dir}")
    os.system(nohup_cmd)
    time.sleep(2)
    if pid_file.exists():
        pid = pid_file.read_text().strip()
        if pid.isdigit() and os.path.exists(f"/proc/{pid}"):
            cfg["app"]["pid"] = pid
            save_config(cfg)
            print(f"✅ 启动成功 (PID: {pid})")
            return
    print("❌ 启动失败，请检查日志")
    sys.exit(1)


def cmd_stop(extra_args=None):
    extra_args = extra_args or []
    force = "--force" in extra_args
    cfg = load_config()
    port = cfg["app"]["port"]
    if force:
        print(f"💥 强制模式 (--force): kill -9 所有监听端口 {port} 的进程")
        pids = get_pids_by_port(port)
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGKILL)
                print(f"🛑 强制终止 PID {pid}")
            except ProcessLookupError:
                continue
    else:
        stopped = False
        pid_str = cfg["app"].get("pid")
        if pid_str and pid_str.isdigit():
            pid = int(pid_str)
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                if os.path.exists(f"/proc/{pid}"):
                    os.kill(pid, signal.SIGKILL)
                print(f"🛑 终止主进程 PID {pid}")
                cfg["app"]["pid"] = ""
                save_config(cfg)
                stopped = True
            except ProcessLookupError:
                cfg["app"]["pid"] = ""
                save_config(cfg)
        if not stopped:
            pids = get_pids_by_port(port)
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"🛑 终止残留进程 PID {pid}")
                    stopped = True
                except ProcessLookupError:
                    continue
    time.sleep(0.5)
    remaining = get_pids_by_port(port)
    if not remaining:
        print("✅ Copaw 服务已停止")
    else:
        print(f"❌ 仍有进程占用端口 {port}: {remaining}")


def cmd_restart():
    print("🔄 重启 Copaw (stop + start)...")
    cmd_stop()
    time.sleep(2)
    cmd_start([])


def cmd_status():
    cfg = load_config()
    port = cfg["app"]["port"]
    working_dir = expand_path(cfg["env"]["COPAW_WORKING_DIR"])
    config_json_path = working_dir / "config.json"

    # ===== 1. 检查服务是否运行 =====
    try:
        result = subprocess.run(f"lsof -i:{port}", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"🟢 Copaw 正在运行 (端口 {port})")
            print("\n--- 监听进程详情 ---")
            print(result.stdout)
        else:
            print(f"🔴 Copaw 未运行 (端口 {port} 空闲)")
    except Exception as e:
        print(f"⚠️  检查端口状态失败: {e}")

    # ===== 2. 加载实际运行配置 =====
    actual_config = {}
    if config_json_path.exists():
        try:
            with open(config_json_path, "r", encoding="utf-8") as f:
                actual_config = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"❌ 无法解析实际配置文件 {config_json_path}: {e}")
    else:
        print(f"⚠️  实际配置文件不存在: {config_json_path}")

    # ===== 3. 配置一致性检查 =====
    print("\n🔍 配置一致性检查 (mgr 配置 vs 实际 config.json):")
    drift_detected = False

    # show_tool_details
    mgr_show = cfg["config"].get("show_tool_details")
    actual_show = actual_config.get("show_tool_details")
    if mgr_show != actual_show:
        print(f"  ⚠️  show_tool_details: mgr={mgr_show}, actual={actual_show}")
        drift_detected = True

    # Feishu Channel
    mgr_feishu = cfg["config"]["channel"].get("feishu", {})
    actual_feishu = actual_config.get("channels", {}).get("feishu", {})

    mgr_enabled = bool(mgr_feishu.get("enable", False))
    actual_enabled = bool(actual_feishu.get("enabled", False))
    if mgr_enabled != actual_enabled:
        print(f"  ⚠️  Feishu.enabled: mgr={mgr_enabled}, actual={actual_enabled}")
        drift_detected = True

    if mgr_enabled:
        for key in ["app_id", "app_secret", "bot_prefix", "verification_token"]:
            mgr_val = mgr_feishu.get(key, "")
            actual_val = actual_feishu.get(key, "")

            # 渲染模板
            if isinstance(mgr_val, str) and "{{" in mgr_val:
                ctx = {k: str(expand_path(v)) for k, v in cfg["env"].items()}
                mgr_val = render_template(mgr_val, ctx)

            if mgr_val != actual_val:
                display_mgr = mask_secret(mgr_val) if key in ("app_secret", "verification_token") else mgr_val
                display_actual = mask_secret(actual_val) if key in ("app_secret", "verification_token") else actual_val
                print(f"  ⚠️  Feishu.{key}: mgr='{display_mgr}', actual='{display_actual}'")
                drift_detected = True

    if not drift_detected:
        print("  ✅ 所有关键配置一致")
    else:
        print("\n❗ 警告：检测到配置漂移！")
        print("   若需以管理器配置为准，请执行: python copaw_mgr.py restart")

    # ===== 4. CLI 状态信息 =====
    print("\n📊 其他运行时信息 (copaw CLI):")
    for cmd in cfg["status_cmd"]:
        print(f"\n--- {cmd} ---")
        try:
            output = run_cmd(cmd, capture=True, check=False)
            print(output if output.strip() else "<无输出>")
        except Exception as e:
            print(f"❌ 执行失败: {e}")


def cmd_log():
    cfg = load_config()
    log_dir = expand_path(cfg["env"]["COPAW_LOG_DIR"])
    main_log = log_dir / "app.log"
    if not main_log.exists():
        print(f"⚠️  日志文件不存在: {main_log}")
        return
    cleanup_old_logs(log_dir, "app.*.log", cfg["log_rotate"]["days"])
    lines = main_log.read_text().splitlines()
    print("📄 最新日志 (最后 200 行):")
    for line in lines[-200:]:
        print(line)


# ==================== 主程序入口 ====================

def main():
    if len(sys.argv) < 2:
        print("用法: python3 copaw_mgr.py {init|start|stop|restart|status|log} [--force]")
        sys.exit(1)
    command = sys.argv[1]
    extra_args = sys.argv[2:] if len(sys.argv) > 2 else []
    try:
        if command == "init":
            cmd_init()
        elif command == "start":
            cmd_start(extra_args)
        elif command == "stop":
            cmd_stop(extra_args)
        elif command == "restart":
            cmd_restart()
        elif command == "status":
            cmd_status()
        elif command == "log":
            cmd_log()
        else:
            print(f"❌ 未知命令: {command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        sys.exit(1)


if __name__ == "__main__":
    main()
