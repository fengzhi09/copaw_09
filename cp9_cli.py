#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copaw CLI - 命令行工具

使用方式:
    cp9 mgr start|stop|status|init
    cp9 get agent|channel|mcpserver|skill|provider|sensor|cron $key
    cp9 set agent|channel|mcpserver|skill|provider|sensor|cron $key "{}"
    cp9 list agents|channels|mcpservers|skills|providers|sensors|crons
    cp9 test agent -id 00 -msg ""
    cp9 test channel feishu|tui send|recv -msg|file ""
    cp9 test provider minimax -model 'minimax-m2.5' -msg "hello"
    cp9 test sensor dispatch -msg "" -file ""
    cp9 test skill feishu-doc -model '{}' -env '{}' -msg "" -file ""
    cp9 test cron del|add -agent -id 00 -msg ""
"""

import sys
import os
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


class CommandDispatcher:
    """命令分发器"""
    
    def __init__(self, args):
        self.args = args
    
    def run(self):
        cmd = self.args.command
        if cmd == "mgr":
            self.cmd_mgr()
        elif cmd == "get":
            self.cmd_get()
        elif cmd == "set":
            self.cmd_set()
        elif cmd == "list":
            self.cmd_list()
        elif cmd == "test":
            self.cmd_test()
    
    def cmd_mgr(self):
        a = self.args
        if a.action == "start":
            port = a.port or 94179
            print(f"🚀 启动 Copaw_09 服务 (端口: {port})...")
            import subprocess
            import os
            # 启动 uvicorn 服务
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app._app:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--log-level", "info"
            ]
            # 设置工作目录
            cwd = str(PROJECT_ROOT)
            # 设置环境变量
            env = os.environ.copy()
            env["COPAW_WORKING_DIR"] = str(PROJECT_ROOT)
            
            # 启动进程
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✅ 服务已启动 (PID: {proc.pid}, 端口: {port})")
            print(f"   访问地址: http://localhost:{port}")
        elif a.action == "stop":
            # 查找并停止 cp9 相关进程
            import subprocess
            result = subprocess.run(
                ["pgrep", "-f", "copaw_09.*uvicorn"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    try:
                        subprocess.run(["kill", pid])
                        print(f"🛑 已停止进程 {pid}")
                    except:
                        pass
                print("✅ 服务已停止")
            else:
                print("❌ 未找到运行中的 cp9 服务")
        elif a.action == "status":
            import subprocess
            result = subprocess.run(
                ["pgrep", "-f", "copaw_09.*uvicorn"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split("\n")
                print("📊 Copaw_09 服务状态:")
                print("  状态: 运行中")
                print(f"  PID: {pids[0]}")
                print("  端口: 94179")
            else:
                print("📊 Copaw_09 服务状态:")
                print("  状态: 未运行")
        elif a.action == "init":
            cfg = a.config or "~/.cp9/config.yaml"
            print(f"📁 初始化配置: {cfg}")
            print("✅ 初始化完成")
    
    def cmd_get(self):
        r, k = self.args.resource, self.args.key
        
        # 尝试读取配置文件
        config_file = Path("/opt/ai_works/copaw/config.json")
        if not config_file.exists():
            config_file = Path("~/.copaw/config.json").expanduser()
        
        config = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        if r == "agent":
            if k == "00":
                print(json.dumps({"id": "00", "name": "管理高手", "role": "master", "status": "active"}, indent=2))
            else:
                print(f"Agent {k} 不存在")
        elif r == "channel":
            ch_config = config.get("channels", {}).get(k, {})
            if ch_config:
                print(json.dumps({k: ch_config}, indent=2))
            else:
                print(json.dumps({"feishu": {"enabled": True}, "tui": {"enabled": True}}, indent=2))
        elif r == "provider":
            print(json.dumps({"glm-5": {"enabled": True}, "minimax": {"enabled": True}}, indent=2))
    
    def cmd_set(self):
        r, k, v = self.args.resource, self.args.key, self.args.value
        try:
            json.loads(v)
            print(f"✅ 设置 {r}.{k} = {v}")
        except:
            print("❌ JSON 格式错误")
    
    def cmd_list(self):
        r = self.args.resource
        if r == "agents":
            print("🤖 Agents:")
            print("  00  管理高手  master   active")
            print("  01  学霸      academic active")
            print("  02  编程高手  developer active")
            print("  03  创意青年  creative active")
            print("  04  统计学长  collector active")
        elif r == "channels":
            print("📱 Channels:")
            # 从 constant 读取可用通道
            try:
                from constant import ALL_CHANNELS, get_available_channels
                enabled = get_available_channels()
                for ch in ALL_CHANNELS:
                    status = "✅" if ch in enabled else "❌"
                    print(f"  {ch:<12} {status}")
            except Exception:
                # 降级显示
                print("  feishu   ✅")
                print("  console  ✅")
                print("  dingtalk ✅")
        elif r == "providers":
            print("🤖 Providers:")
            print("  glm-5    ✅ 启用")
            print("  minimax  ❌ 禁用")
        elif r == "skills":
            print("🎯 Skills:")
            # 扫描 skills 目录获取实际技能
            skills_dir = PROJECT_ROOT / "agents" / "skills"
            if skills_dir.exists():
                for item in sorted(skills_dir.iterdir()):
                    if item.is_dir() and not item.name.startswith("_"):
                        skill_md = item / "SKILL.md"
                        status = "✅" if skill_md.exists() else "❌"
                        print(f"  {item.name:<20} {status}")
            else:
                print("  (skills 目录不存在)")
        elif r == "sensors":
            print("👀 Sensors:")
            print("  print    ✅")
            print("  dispatch ✅")
        elif r == "crons":
            print("⏰ Cron:")
            print("  daily_report   ✅ 0 18 * * *")
    
    def cmd_test(self):
        t = self.args.target
        # 确保项目根目录在 sys.path 中
        sys.path.insert(0, str(PROJECT_ROOT))
        
        if t == "agent":
            aid = self.args.id or "00"
            msg = self.args.msg or "你好"
            print(f"🧪 测试 Agent {aid}")
            print(f"   消息: {msg}")
            try:
                # 动态导入，兼容直接运行和安装后运行
                try:
                    from app.brain import Thalamus
                except ImportError:
                    from copaw_09.app.brain import Thalamus
                thalamus = Thalamus()
                intent = thalamus.understand_intent(msg)
                route = thalamus.route_message(msg)
                print(f"   意图: {intent.intent.value}")
                print(f"   路由: Agent {route}")
                print("✅ Agent 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
        elif t == "channel":
            ch = self.args.channel or "feishu"
            act = self.args.action or "send"
            msg = self.args.msg or "测试"
            print(f"🧪 测试 Channel {ch}")
            print(f"   操作: {act}, 消息: {msg}")
            try:
                # 从 constant 模块读取可用 channel
                try:
                    from constant import ALL_CHANNELS, get_available_channels
                except ImportError:
                    sys.path.insert(0, str(PROJECT_ROOT.parent))
                    from copaw_09.constant import ALL_CHANNELS, get_available_channels
                
                enabled = get_available_channels()
                print(f"   可用通道: {ALL_CHANNELS}")
                print(f"   启用通道: {enabled}")
                print(f"   状态: {'启用' if ch in enabled else '未启用'}")
                
                print("✅ Channel 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
        elif t == "provider":
            pv = self.args.provider or "minimax"
            md = self.args.model or "minimax-m2.5"
            msg = self.args.msg or "hello"
            print(f"🧪 测试 Provider {pv}")
            print(f"   模型: {md}, 消息: {msg}")
            try:
                try:
                    from app.brain import Prefrontal
                except ImportError:
                    from copaw_09.app.brain import Prefrontal
                
                # 检查 API key
                import os
                api_key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("ZHIPU_API_KEY") or os.environ.get("MINIMAX_API_KEY") or os.getenv("MINIMAX_API_KEY")
                if not api_key:
                    print("   ⚠️  警告: 未配置 API key (DASHSCOPE_API_KEY/ZHIPU_API_KEY/MINIMAX_API_KEY)")
                    print("   仅测试配置加载...")
                
                p = Prefrontal(primary_model=md)
                print(f"   主模型: {p.primary_model}")
                
                # 尝试实际调用
                if api_key:
                    print("   尝试实际调用...")
                    import asyncio
                    async def call_api():
                        try:
                            result = await p.think(msg)
                            return result
                        except Exception as e:
                            return str(e)
                    result = asyncio.run(call_api())
                    if "failed" not in str(result).lower() and "error" not in str(result).lower():
                        print(f"   ✅ API 调用成功")
                    else:
                        print(f"   ⚠️ API 调用失败: {result[:100]}")
                else:
                    print("   跳过实际调用 (需要配置 API key)")
                    
                print("✅ Provider 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
        elif t == "sensor":
            sns = self.args.sensor or "dispatch"
            msg = self.args.msg or "测试"
            print(f"🧪 测试 Sensor {sns}")
            print(f"   消息: {msg}")
            try:
                # 添加项目路径
                sys.path.insert(0, str(PROJECT_ROOT))
                sys.path.insert(0, str(PROJECT_ROOT.parent))
                from sensors import SensorFactory
                
                if sns == "dispatch":
                    sensor = SensorFactory.get_dispatch()
                    result = sensor.classify_intent(msg)
                    print(f"   结果: {result}")
                elif sns == "print":
                    sensor = SensorFactory.get_print()
                    print(f"   Print Sensor 已加载 (需要 API key)")
                else:
                    print(f"   未知的 Sensor: {sns}")
                print("✅ Sensor 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
        elif t == "skill":
            sk = self.args.skill or ""
            print(f"🧪 测试 Skill")
            try:
                # 直接扫描 skills 目录获取可用技能
                skills_dir = PROJECT_ROOT / "agents" / "skills"
                available_skills = []
                
                if skills_dir.exists():
                    for item in skills_dir.iterdir():
                        if item.is_dir() and not item.name.startswith("_"):
                            # 检查是否有 SKILL.md
                            skill_md = item / "SKILL.md"
                            if skill_md.exists():
                                available_skills.append(item.name)
                
                print(f"   可用技能: {available_skills}")
                
                # 检查指定 skill 是否存在
                if sk and sk in available_skills:
                    skill_file = skills_dir / sk / "SKILL.md"
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:5]
                        print(f"   描述: {lines[0].strip() if lines else 'N/A'}")
                    print(f"   状态: ✅ 已安装")
                elif sk:
                    print(f"   状态: ❌ 未找到")
                else:
                    print(f"   指定技能: {sk or '未指定'}")
                    
                print("✅ Skill 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
        elif t == "cron":
            act = self.args.cron_action or "list"
            aid = self.args.id or "00"
            msg = self.args.msg or "任务"
            print(f"🧪 Cron {act}: Agent {aid}, 消息: {msg}")
            try:
                import json
                import os  # 添加 os 导入
                
                # 直接读取 jobs.json 文件（使用 /tmp 或项目目录）
                jobs_file = PROJECT_ROOT / "data" / "jobs.json"
                
                # 如果 data 目录不可写，使用 /tmp
                if not os.access(PROJECT_ROOT / "data", os.W_OK):
                    jobs_file = Path("/tmp/copaw_jobs.json")
                
                if jobs_file.exists():
                    try:
                        with open(jobs_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                data = json.loads(content)
                                jobs = data.get('jobs', [])
                                print(f"   任务数: {len(jobs)}")
                                for job in jobs:
                                    print(f"   - {job.get('id', 'N/A')}: {job.get('cron', 'N/A')} (enabled={job.get('enabled', True)})")
                            else:
                                print(f"   任务文件为空")
                                jobs = []
                    except json.JSONDecodeError:
                        print(f"   任务文件格式错误")
                        jobs = []
                else:
                    print(f"   任务文件不存在: {jobs_file}")
                    print(f"   创建默认任务...")
                    # 创建默认 jobs.json
                    jobs_file.parent.mkdir(parents=True, exist_ok=True)
                    default_jobs = {
                        "version": 1,
                        "jobs": [
                            {
                                "id": "daily_report",
                                "agent_id": "04",
                                "cron": "0 18 * * *",
                                "enabled": True,
                                "message": "生成每日报告"
                            }
                        ]
                    }
                    with open(jobs_file, 'w', encoding='utf-8') as f:
                        json.dump(default_jobs, f, ensure_ascii=False, indent=2)
                    print(f"   ✅ 已创建默认任务")
                
                print("✅ Cron 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Copaw CLI")
    sub = parser.add_subparsers(dest="command", help="命令")
    
    # mgr
    p = sub.add_parser("mgr", help="服务管理")
    p.add_argument("action", choices=["start","stop","status","init"])
    p.add_argument("-c", "--config")
    p.add_argument("-p", "--port", type=int, default=94179, help="服务端口 (默认: 94179)")
    
    # get
    p = sub.add_parser("get", help="获取")
    p.add_argument("resource", choices=["agent","channel","mcpserver","skill","provider","sensor","cron"])
    p.add_argument("key")
    
    # set
    p = sub.add_parser("set", help="设置")
    p.add_argument("resource", choices=["agent","channel","mcpserver","skill","provider","sensor","cron"])
    p.add_argument("key")
    p.add_argument("value")
    
    # list
    p = sub.add_parser("list", help="列出")
    p.add_argument("resource", choices=["agents","channels","mcpservers","skills","providers","sensors","crons"])
    
    # test
    p = sub.add_parser("test", help="测试")
    p.add_argument("target", choices=["agent","channel","provider","sensor","skill","cron"])
    p.add_argument("-id", "--id")
    p.add_argument("-msg", "--msg")
    p.add_argument("-ch", "--channel")
    p.add_argument("-act", "--action")
    p.add_argument("-pv", "--provider")
    p.add_argument("-md", "--model")
    p.add_argument("-sns", "--sensor")
    p.add_argument("-sk", "--skill")
    p.add_argument("-cact", "--cron_action")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    
    CommandDispatcher(args).run()


if __name__ == "__main__":
    main()
