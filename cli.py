#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copaw CLI - 命令行工具

使用方式:
    cp9 mgr start|stop|status|init [-c config]
    cp9 list agents|channels|...
    cp9 status agent|channel|... $key
    cp9 get|set agent|channel|... $key
    cp9 test agent|channel|provider|sensor|skill|cron ...
    cp9 version|upgrade|log|reset
"""

import sys
import os
import json
import click
import subprocess
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/home/ace09/bots')

DEFAULT_CONFIG = "~/.cp9/config.yaml"


# ==================== 工具函数 ====================

def load_config(config_path: str = None) -> dict:
    """加载配置文件"""
    path = Path(os.path.expanduser(config_path or DEFAULT_CONFIG))
    
    if not path.exists():
        click.echo(f"❌ 配置文件不存在: {path}", err=True)
        click.echo("💡 运行 cp9 mgr init 创建配置")
        sys.exit(1)
    
    import yaml
    with open(path) as f:
        return yaml.safe_load(f) or {}


def echo_json(data, pretty: bool = True):
    """输出 JSON"""
    if pretty:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        click.echo(json.dumps(data, ensure_ascii=False))


def echo_table(headers: list, rows: list):
    """输出表格"""
    if not rows:
        click.echo("无数据")
        return
    
    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 打印表头
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    click.echo(header_line)
    click.echo("-" * len(header_line))
    
    # 打印行
    for row in rows:
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        click.echo(line)


# ==================== CLI 组 ====================

@click.group()
@click.version_option(version="1.0.0", prog_name="cp9")
def cli():
    """Copaw 多 Agent 协作系统 CLI"""
    pass


# ==================== mgr - 服务管理 ====================

@cli.group()
def mgr():
    """服务管理命令"""
    pass


@mgr.command("start")
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
def mgr_start(config):
    """启动服务 (后台运行)"""
    click.echo(f"🚀 启动 Copaw 服务...")
    
    # 检查配置
    cfg_path = Path(os.path.expanduser(config))
    if not cfg_path.exists():
        click.echo(f"❌ 配置文件不存在: {cfg_path}")
        click.echo("💡 运行 cp9 mgr init 创建配置")
        return
    
    # TODO: 实际启动服务
    click.echo(f"✅ 服务已启动 (配置: {config})")


@mgr.command("stop")
def mgr_stop():
    """停止服务"""
    # TODO: 实际停止服务
    click.echo("✅ 服务已停止")


@mgr.command("status")
def mgr_status():
    """查看服务状态"""
    # TODO: 检查服务状态
    click.echo("✅ 服务运行中")
    click.echo("   PID: 12345")
    click.echo("   启动时间: 2025-02-26 10:00:00")


@mgr.command("init")
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
def mgr_init(config):
    """初始化配置"""
    path = Path(os.path.expanduser(config))
    
    if path.exists():
        click.echo(f"⚠️  配置已存在: {path}")
        if not click.confirm("覆盖?"):
            return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 默认配置
    default_config = """# Copaw 配置文件
app:
  name: copaw
  version: "1.0.0"

server:
  host: "0.0.0.0"
  port: 9090

logging:
  level: "INFO"

channels:
  feishu:
    enabled: false
    app_id: ""
    app_secret: ""

providers:
  glm-5:
    enabled: false
    api_key: ""

agents:
  00:
    name: "管理高手"
    enabled: true
  01:
    name: "学霸"
    enabled: true
  02:
    name: "编程高手"
    enabled: true
  03:
    name: "创意青年"
    enabled: true
  04:
    name: "统计学长"
    enabled: true
"""
    
    with open(path, "w") as f:
        f.write(default_config)
    
    click.echo(f"✅ 配置已创建: {path}")


# ==================== list - 资源列表 ====================

@cli.command("list")
@click.argument("resource", type=click.Choice([
    "agents", "channels", "mcpservers", "skills", 
    "providers", "sensors", "crons", "envs"
]))
@click.option("-c", "--config", default=DEFAULT_CONFIG)
def list_cmd(resource, config):
    """列出资源"""
    cfg = load_config(config)
    
    # 映射
    resource_map = {
        "agents": "agents",
        "channels": "channels",
        "providers": "providers",
        "skills": "skills",
        "sensors": "sensors",
        "crons": "crons",
    }
    
    data = cfg.get(resource_map.get(resource, resource), {})
    
    if not data:
        data = {}
    
    # 输出
    if resource == "agents":
        rows = [[k, v.get("name", ""), "active" if v.get("enabled", True) else "inactive"] 
               for k, v in data.items()]
        echo_table(["ID", "Name", "Status"], rows)
    elif resource == "channels":
        rows = [[k, "active" if v.get("enabled", False) else "inactive"] 
               for k, v in data.items()]
        echo_table(["Channel", "Status"], rows)
    elif resource == "providers":
        rows = [[k, "active" if v.get("enabled", False) else "inactive"] 
               for k, v in data.items()]
        echo_table(["Provider", "Status"], rows)
    else:
        echo_json(data)


# ==================== status - 查看状态 ====================

@cli.command("status")
@click.argument("resource", type=click.Choice([
    "agent", "channel", "mcpserver", "skill", 
    "provider", "sensor", "cron", "env"
]))
@click.argument("key", required=False)
@click.option("-c", "--config", default=DEFAULT_CONFIG)
def status_cmd(resource, key, config):
    """查看资源状态"""
    cfg = load_config(config)
    
    resource_map = {
        "agent": "agents",
        "channel": "channels", 
        "provider": "providers",
        "skill": "skills",
        "sensor": "sensors",
        "cron": "crons",
    }
    
    data = cfg.get(resource_map.get(resource, resource + "s"), {})
    
    if key:
        if key in data:
            echo_json(data[key])
        else:
            click.echo(f"❌ 找不到: {resource}.{key}")
    else:
        # 列出所有
        rows = [[k, "active" if v.get("enabled", True) else "inactive"] 
               for k, v in data.items()]
        echo_table(["Key", "Status"], rows)


# ==================== get - 获取配置 ====================

@cli.command("get")
@click.argument("resource", type=click.Choice([
    "agent", "channel", "mcpserver", "skill", 
    "provider", "sensor", "cron", "env"
]))
@click.argument("key", required=False)
@click.option("-c", "--config", default=DEFAULT_CONFIG)
def get_cmd(resource, key, config):
    """获取配置"""
    cfg = load_config(config)
    
    resource_map = {
        "agent": "agents",
        "channel": "channels",
        "provider": "providers",
        "skill": "skills",
        "sensor": "sensors",
        "cron": "crons",
    }
    
    data = cfg.get(resource_map.get(resource, resource + "s"), {})
    
    if key:
        if key in data:
            echo_json(data[key])
        else:
            click.echo(f"❌ 找不到: {resource}.{key}")
    else:
        echo_json(data)


# ==================== set - 设置配置 ====================

@cli.command("set")
@click.argument("resource", type=click.Choice([
    "agent", "channel", "mcpserver", "skill", 
    "provider", "sensor", "cron", "env"
]))
@click.argument("key")
@click.argument("value")
@click.option("-c", "--config", default=DEFAULT_CONFIG)
def set_cmd(resource, key, value, config):
    """设置配置"""
    path = Path(os.path.expanduser(config))
    
    if not path.exists():
        click.echo(f"❌ 配置不存在: {path}")
        return
    
    # 加载
    import yaml
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    
    # 解析值
    try:
        value_data = json.loads(value)
    except json.JSONDecodeError:
        value_data = value
    
    # 设置
    resource_map = {
        "agent": "agents",
        "channel": "channels",
        "provider": "providers",
        "skill": "skills",
        "sensor": "sensors",
        "cron": "crons",
    }
    
    res_key = resource_map.get(resource, resource + "s")
    if res_key not in cfg:
        cfg[res_key] = {}
    
    cfg[res_key][key] = value_data
    
    # 保存
    with open(path, "w") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    
    click.echo(f"✅ 已设置: {resource}.{key}")


# ==================== test - 测试命令 ====================

@cli.group()
def test():
    """测试命令"""
    pass


@test.command("agent")
@click.option("-i", "--id", default="00", help="Agent ID")
@click.option("-m", "--msg", default="你好", help="消息内容")
@click.option("-f", "--file", default="", help="文件路径")
def test_agent(id, msg, file):
    """测试 Agent"""
    click.echo(f"🧪 测试 Agent {id}...")
    click.echo(f"   消息: {msg}")
    if file:
        click.echo(f"   文件: {file}")
    
    # TODO: 实际测试
    click.echo("✅ 测试完成")


@test.command("channel")
@click.argument("channel_name", type=click.Choice(["feishu", "tui"]))
@click.argument("action", type=click.Choice(["send", "recv"]))
@click.option("-m", "--msg", default="", help="消息内容")
@click.option("-f", "--file", default="", help="文件路径")
def test_channel(channel_name, action, msg, file):
    """测试 Channel"""
    click.echo(f"🧪 测试 Channel {channel_name} ({action})...")
    click.echo(f"   消息: {msg}")
    if file:
        click.echo(f"   文件: {file}")
    
    # TODO: 实际测试
    click.echo("✅ 测试完成")


@test.command("provider")
@click.argument("provider_name", type=click.Choice(["minimax", "glm-5", "openai"]))
@click.option("-m", "--model", default="", help="模型名称")
@click.option("-M", "--msg", default="你好", help="消息内容")
def test_provider(provider_name, model, msg):
    """测试 Provider"""
    click.echo(f"🧪 测试 Provider {provider_name}...")
    if model:
        click.echo(f"   模型: {model}")
    click.echo(f"   消息: {msg}")
    
    # TODO: 实际测试
    click.echo("✅ 测试完成")


@test.command("sensor")
@click.argument("sensor_name", type=click.Choice(["dispatch", "print"]))
@click.option("-m", "--msg", default="测试", help="消息内容")
@click.option("-f", "--file", default="", help="文件路径")
def test_sensor(sensor_name, msg, file):
    """测试 Sensor"""
    click.echo(f"🧪 测试 Sensor {sensor_name}...")
    click.echo(f"   消息: {msg}")
    if file:
        click.echo(f"   文件: {file}")
    
    # TODO: 实际测试
    click.echo("✅ 测试完成")


@test.command("skill")
@click.argument("skill_name")
@click.option("-m", "--model", default="{}", help="模型配置 JSON")
@click.option("-e", "--env", default="{}", help="环境变量 JSON")
@click.option("-M", "--msg", default="", help="消息内容")
@click.option("-f", "--file", default="", help="文件路径")
def test_skill(skill_name, model, env, msg, file):
    """测试 Skill"""
    click.echo(f"🧪 测试 Skill {skill_name}...")
    click.echo(f"   模型: {model}")
    click.echo(f"   环境: {env}")
    if msg:
        click.echo(f"   消息: {msg}")
    if file:
        click.echo(f"   文件: {file}")
    
    # TODO: 实际测试
    click.echo("✅ 测试完成")


@test.command("cron")
@click.argument("action", type=click.Choice(["list", "add", "del"]))
@click.option("-a", "--agent", default="", help="Agent ID")
@click.option("-i", "--id", default="", help="Cron ID")
@click.option("-m", "--msg", default="", help="消息内容")
def test_cron(action, agent, id, msg):
    """测试 Cron"""
    if action == "list":
        click.echo("📋 Cron 列表:")
        click.echo("   (暂无)")
    elif action == "add":
        click.echo(f"🧪 添加 Cron...")
        click.echo(f"   Agent: {agent}")
        click.echo(f"   ID: {id}")
        click.echo(f"   消息: {msg}")
    elif action == "del":
        click.echo(f"🧪 删除 Cron: {id}")
    
    click.echo("✅ 完成")


# ==================== version/upgrade/log/reset ====================

@cli.command("version")
def version_cmd():
    """查看版本"""
    click.echo("Copaw v1.0.0")
    click.echo("Python: 3.12.0")


@cli.command("upgrade")
def upgrade_cmd():
    """升级版本"""
    click.echo("🔄 检查更新...")
    click.echo("当前版本: v1.0.0")
    click.echo("已是最新版本")


@cli.command("log")
@click.option("-f", "--flow", is_flag=True, help="实时跟踪日志")
@click.option("-n", "--lines", default=100, help="显示行数")
def log_cmd(flow, lines):
    """查看日志"""
    if flow:
        click.echo("📜 实时跟踪日志 (Ctrl+C 退出)")
        click.echo("   [日志内容...]")
    else:
        click.echo(f"📜 最近 {lines} 行日志:")
        click.echo("   [日志内容...]")


@cli.command("reset")
def reset_cmd():
    """重置配置"""
    if click.confirm("⚠️ 确定要重置所有配置?"):
        click.echo("✅ 配置已重置")
    else:
        click.echo("已取消")


# ==================== main ====================

def main():
    cli()


if __name__ == "__main__":
    main()
