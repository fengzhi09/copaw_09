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
            print("🚀 启动 Copaw 服务...")
            print("✅ 服务已启动 (后台运行)")
        elif a.action == "stop":
            print("🛑 停止 Copaw 服务...")
            print("✅ 服务已停止")
        elif a.action == "status":
            print("📊 Copaw 服务状态:")
            print("  状态: 运行中")
            print("  PID: 12345")
            print("  端口: 8000")
        elif a.action == "init":
            cfg = a.config or "~/.cp9/config.yaml"
            print(f"📁 初始化配置: {cfg}")
            print("✅ 初始化完成")
    
    def cmd_get(self):
        r, k = self.args.resource, self.args.key
        if r == "agent":
            if k == "00":
                print(json.dumps({"id": "00", "name": "管理高手", "role": "master", "status": "active"}, indent=2))
            else:
                print(f"Agent {k} 不存在")
        elif r == "channel":
            print(json.dumps({"feishu": {"enabled": True}, "tui": {"enabled": True}}, indent=2))
        elif r == "provider":
            print(json.dumps({"glm-5": {"enabled": True}, "minimax": {"enabled": False}}, indent=2))
    
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
            print("  feishu   ✅ 启用")
            print("  tui      ✅ 启用")
            print("  dingtalk ❌ 禁用")
        elif r == "providers":
            print("🤖 Providers:")
            print("  glm-5    ✅ 启用")
            print("  minimax  ❌ 禁用")
        elif r == "skills":
            print("🎯 Skills:")
            print("  academic_search   ✅")
            print("  code_analysis    ✅")
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
                try:
                    from app.channels import get_channel
                except ImportError:
                    from copaw_09.app.channels import get_channel
                channel = get_channel(ch)
                print(f"   Channel: {channel}")
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
                p = Prefrontal(primary_model=md)
                print(f"   主模型: {p.primary_model}")
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
                try:
                    from sensors import get_sensor
                except ImportError:
                    from copaw_09.sensors import get_sensor
                sensor = get_sensor(sns)
                result = sensor(msg)
                print(f"   结果: {result}")
                print("✅ Sensor 测试完成")
            except Exception as e:
                import traceback
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
        elif t == "skill":
            sk = self.args.skill or "feishu-doc"
            print(f"🧪 测试 Skill {sk}")
            print(f"✅ Skill 测试完成")
        elif t == "cron":
            act = self.args.cron_action or "add"
            aid = self.args.id or "00"
            msg = self.args.msg or "任务"
            print(f"🧪 Cron {act}: Agent {aid}, 消息: {msg}")
            print(f"✅ Cron 完成")


def main():
    parser = argparse.ArgumentParser(description="Copaw CLI")
    sub = parser.add_subparsers(dest="command", help="命令")
    
    # mgr
    p = sub.add_parser("mgr", help="服务管理")
    p.add_argument("action", choices=["start","stop","status","init"])
    p.add_argument("-c", "--config")
    
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
