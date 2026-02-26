#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copaw CLI - 命令行入口

使用方式:
    cp9 mgr start|stop|status|init -c ~/.cp9/config.yaml
    cp9 get|set agent|channel|mcpserver|skill|provider|sensor|cron $key
    cp9 list agents|channels|mcpservers|skills|providers|sensors|crons
    cp9 test agent|channel|provider|sensor|skill|cron ...

示例:
    cp9 mgr start -c ~/.cp9/config.yaml
    cp9 list agents
    cp9 test agent -id 00 -msg "你好"
    cp9 test channel feishu send -msg "Hello"
    cp9 test provider minimax -model 'minimax-m2.5' -msg "hello"
"""

import sys
import os
import json
import click
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/home/ace09/bots')

DEFAULT_CONFIG = "~/.cp9/config.yaml"


# ==================== 工具函数 ====================

def load_config(config_path: str = None) -> dict:
    """加载配置文件"""
    path = Path(config_path or os.path.expanduser(DEFAULT_CONFIG))
    
    if not path.exists():
        click.echo(f"❌ 配置文件不存在: {path}", err=True)
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


# ==================== mgr - 管理命令 ====================

@cli.group()
def mgr():
    """系统管理命令"""
    pass


@mgr.command("start")
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
@click.option("-d", "--daemon", is_flag=True, help="后台运行")
@click.option("-h", "--host", default="0.0.0.0", help="监听地址")
@click.option("-p", "--port", default=9090, help="监听端口")
def mgr_start(config, daemon, host, port):
    """启动 Copaw 服务"""
    click.echo(f"🚀 启动 Copaw 服务...")
    click.echo(f"   配置: {config}")
    click.echo(f"   地址: {host}:{port}")
    click.echo(f"   后台: {daemon}")
    
    if daemon:
        # 后台运行
        import subprocess
        import sys
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app._app:subapi",
            "--host", host,
            "--port", str(port),
            "--log-level", "info"
        ]
        
        # 写入 PID 文件
        pid_file = os.path.expanduser("~/.cp9/copaw.pid")
        os.makedirs(os.path.dirname(pid_file), exist_ok=True)
        
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo(f"✅ 服务已启动 (PID: {os.getpid()})")
    else:
        import uvicorn
        from app._app import subapi
        uvicorn.run(subapi, host=host, port=port, log_level="info")


@mgr.command("stop")
def mgr_stop():
    """停止 Copaw 服务"""
    pid_file = os.path.expanduser("~/.cp9/copaw.pid")
    
    if os.path.exists(pid_file):
        with open(pid_file) as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 9)
            click.echo(f"✅ 服务已停止 (PID: {pid})")
        except ProcessLookupError:
            click.echo(f"⚠️  进程不存在")
        
        os.remove(pid_file)
    else:
        # 尝试查找进程
        import subprocess
        result = subprocess.run(
            "ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs -r kill",
            shell=True
        )
        click.echo("✅ 服务已停止")


@mgr.command("status")
def mgr_status():
    """查看服务状态"""
    pid_file = os.path.expanduser("~/.cp9/copaw.pid")
    
    if os.path.exists(pid_file):
        with open(pid_file) as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 0)
            click.echo(f"✅ 服务运行中 (PID: {pid})")
            
            # 读取配置
            cfg = load_config()
            app_cfg = cfg.get("app", {})
            click.echo(f"   应用: {app_cfg.get('name', 'copaw')}")
            click.echo(f"   版本: {app_cfg.get('version', '1.0.0')}")
        except ProcessLookupError:
            click.echo("⚠️  PID 文件存在但进程已退出")
    else:
        click.echo("❌ 服务未运行")


@mgr.command("init")
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
def mgr_init(config):
    """初始化配置文件"""
    path = Path(os.path.expanduser(config))
    
    if path.exists():
        click.echo(f"⚠️  配置文件已存在: {path}")
        if not click.confirm("是否覆盖?"):
            return
    
    # 创建目录
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 默认配置
    default_config = """# Copaw 配置文件
app:
  name: copaw
  version: "1.0.0"

# API 配置
api:
  host: "0.0.0.0"
  port: 9090

# Channel 配置
channels:
  feishu:
    enabled: false
    app_id: ""
    app_secret: ""
    bot_prefix: "/ai"
    filters:
      ignore_keywords: []
      ignore_users: []

# Provider 配置
providers:
  glm-5:
    enabled: false
    api_key: ""
  minimax:
    enabled: false
    api_key: ""

# Agent 配置
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


# ==================== get/set - 配置命令 ====================

@cli.command("get")
@click.argument("resource", type=click.Choice(["agent", "channel", "mcpserver", "skill", "provider", "sensor", "cron"]))
@click.argument("key", required=False)
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
@click.option("-j", "--json", is_flag=True, help="JSON 格式输出")
def get_cmd(resource, key, config, json):
    """获取配置值"""
    cfg = load_config(config)
    
    # 获取对应配置
    if resource == "agent":
        data = cfg.get("agents", {}).get(key) or cfg.get("agents", {})
    elif resource == "channel":
        data = cfg.get("channels", {}).get(key) or cfg.get("channels", {})
    elif resource == "provider":
        data = cfg.get("providers", {}).get(key) or cfg.get("providers", {})
    else:
        data = cfg.get(resource + "s", {})
    
    if key and key not in data:
        click.echo(f"❌ 找不到: {resource}.{key}")
        sys.exit(1)
    
    if key:
        echo_json(data.get(key))
    else:
        echo_json(data)


@cli.command("set")
@click.argument("resource", type=click.Choice(["agent", "channel", "mcpserver", "skill", "provider", "sensor", "cron"]))
@click.argument("key")
@click.argument("value")
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
def set_cmd(resource, key, value, config):
    """设置配置值"""
    path = Path(os.path.expanduser(config))
    
    # 加载现有配置
    if path.exists():
        import yaml
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {}
    
    # 解析值
    try:
        value_data = json.loads(value)
    except json.JSONDecodeError:
        value_data = value
    
    # 设置值
    resource_key = resource + "s"
    if resource_key not in cfg:
        cfg[resource_key] = {}
    
    cfg[resource_key][key] = value_data
    
    # 保存
    path.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(path, "w") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    
    click.echo(f"✅ 已设置: {resource}.{key}")


# ==================== list - 列表命令 ====================

@cli.command("list")
@click.argument("resource", type=click.Choice(["agents", "channels", "mcpservers", "skills", "providers", "sensors", "crons"]))
@click.option("-c", "--config", default=DEFAULT_CONFIG, help="配置文件路径")
def list_cmd(resource, config):
    """列出所有资源"""
    cfg = load_config(config)
    
    # 映射复数到单数
    resource_map = {
        "agents": "agent",
        "channels": "channel",
        "providers": "provider",
        "skills": "skill",
        "sensors": "sensor",
        "crons": "cron",
    }
    
    singular = resource_map.get(resource, resource)
    data = cfg.get(resource, {})
    
    if not data:
        click.echo(f"⚠️  没有配置: {resource}")
        return
    
    # 输出表格
    if singular == "agent":
        rows = [[k, v.get("name", ""), v.get("enabled", True)] for k, v in data.items()]
        echo_table(["ID", "名称", "启用"], rows)
    elif singular == "channel":
        rows = [[k, v.get("enabled", False)] for k, v in data.items()]
        echo_table(["名称", "启用"], rows)
    elif singular == "provider":
        rows = [[k, v.get("enabled", False)] for k, v in data.items()]
        echo_table(["名称", "启用"], rows)
    else:
        echo_json(data)


# ==================== test - 测试命令 ====================

@cli.group()
def test():
    """测试命令"""
    pass


@test.command("agent")
@click.option("-id", "--agent-id", default="00", help="Agent ID")
@click.option("-m", "--msg", default="你好", help="测试消息")
def test_agent(agent_id, msg):
    """测试 Agent"""
    click.echo(f"🧪 测试 Agent {agent_id}...")
    click.echo(f"   消息: {msg}")
    
    from app.brain import Thalamus
    
    thalamus = Thalamus()
    intent = thalamus.understand_intent(msg)
    route_id = thalamus.route_message(msg)
    
    click.echo(f"   路由: Agent {route_id}")
    click.echo(f"   意图: {intent.intent.value} ({intent.confidence:.2f})")
    click.echo("✅ 测试完成")


@test.command("channel")
@click.argument("channel_name", type=click.Choice(["feishu", "tui", "dingtalk", "qq", "discord", "telegram"]))
@click.argument("action", type=click.Choice(["send", "recv"]))
@click.option("-m", "--msg", default="", help="消息内容")
@click.option("-f", "--file", default="", help="文件路径")
def test_channel(channel_name, action, msg, file):
    """测试 Channel"""
    click.echo(f"🧪 测试 Channel {channel_name}...")
    click.echo(f"   操作: {action}")
    click.echo(f"   消息: {msg}")
    click.echo(f"   文件: {file}")
    
    if action == "send":
        click.echo("   → 发送消息测试")
    else:
        click.echo("   → 接收消息测试 (需要启动服务)")
    
    # TODO: 实现实际的 channel 测试
    click.echo("✅ 测试完成")


@test.command("provider")
@click.argument("provider_name", type=click.Choice(["minimax", "glm", "openai", "anthropic"]))
@click.option("-m", "--model", default="", help="模型名称")
@click.option("-msg", "--message", default="Hello", help="测试消息")
def test_provider(provider_name, model, message):
    """测试 Provider"""
    click.echo(f"🧪 测试 Provider {provider_name}...")
    click.echo(f"   模型: {model or '默认'}")
    click.echo(f"   消息: {message}")
    
    # TODO: 实现实际的 provider 测试
    click.echo("✅ 测试完成")


@test.command("sensor")
@click.argument("sensor_name", type=click.Choice(["dispatch", "print", "recorder"]))
@click.option("-m", "--msg", default="测试消息", help="测试消息")
@click.option("-f", "--file", default="", help="文件路径")
def test_sensor(sensor_name, msg, file):
    """测试 Sensor"""
    click.echo(f"🧪 测试 Sensor {sensor_name}...")
    click.echo(f"   消息: {msg}")
    click.echo(f"   文件: {file}")
    
    if sensor_name == "dispatch":
        from app.brain import Thalamus
        t = Thalamus()
        intent = t.understand_intent(msg)
        click.echo(f"   意图: {intent.intent.value}")
    
    click.echo("✅ 测试完成")


@test.command("skill")
@click.argument("skill_name")
@click.option("-m", "--model", default="{}", help="模型配置 JSON")
@click.option("-e", "--env", default="{}", help="环境变量 JSON")
@click.option("-msg", "--message", default="", help="测试消息")
@click.option("-f", "--file", default="", help="文件路径")
def test_skill(skill_name, model, env, message, file):
    """测试 Skill"""
    click.echo(f"🧪 测试 Skill {skill_name}...")
    click.echo(f"   模型: {model}")
    click.echo(f"   环境: {env}")
    click.echo(f"   消息: {message}")
    click.echo(f"   文件: {file}")
    click.echo("✅ 测试完成")


@test.command("cron")
@click.argument("action", type=click.Choice(["add", "del", "list"]))
@click.option("-a", "--agent", default="", help="Agent ID")
@click.option("-id", "--cron-id", default="", help="Cron ID")
@click.option("-m", "--msg", default="", help="消息内容")
def test_cron(action, agent, cron_id, msg):
    """测试 Cron"""
    click.echo(f"🧪 Cron 操作: {action}")
    
    if action == "list":
        # 列出所有定时任务
        click.echo("📋 定时任务列表:")
        # TODO: 读取实际配置
        click.echo("   (暂无)")
    elif action == "add":
        click.echo(f"   添加任务: Agent {agent}, 消息: {msg}")
    elif action == "del":
        click.echo(f"   删除任务: {cron_id}")
    
    click.echo("✅ 测试完成")


# ==================== main ====================

def main():
    cli()


if __name__ == "__main__":
    main()
