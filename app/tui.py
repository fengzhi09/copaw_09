#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cp9 TUI - 交互式控制台测试工具

使用方法:
    python -m app.tui
    python -m app.tui --help
"""

import sys
import os
import asyncio
import cmd
import shlex
from typing import Optional

# 添加项目路径
sys.path.insert(0, '/home/ace09/bots')


class cp9TUI(cmd.Cmd):
    """cp9 交互式控制台"""
    
    intro = """
╔═══════════════════════════════════════════════════╗
║         🤖 cp9 多 Agent 协作系统                ║
║              交互式测试控制台                      ║
╠═══════════════════════════════════════════════════╣
║  输入 help 查看命令                                ║
║  输入 quit 退出                                   ║
╚═══════════════════════════════════════════════════╝
"""
    
    prompt = "(cp9) "
    
    def __init__(self):
        super().__init__()
        self._init_modules()
    
    def _init_modules(self):
        """初始化模块"""
        try:
            from cp9.app.brain import Thalamus, Prefrontal
            from cp9.app.gateway import GatewayAuth, GatewayFilter
            from cp9.app.router import AgentRouter
            from cp9.agents.agent_00_管理高手 import AgentCreator, AgentManager
            from cp9.app.channels.feishu_document import FeishuDocument
            
            self.thalamus = Thalamus()
            self.prefrontal = Prefrontal()
            self.auth = GatewayAuth()
            self.filter = GatewayFilter()
            self.router = AgentRouter()
            self.creator = AgentCreator('/tmp/cp9_tui_agents')
            self.manager = AgentManager('/tmp/cp9_tui_agents')
            self.feishu_doc = None  # 需要 channel 实例
            
            self.modules_loaded = True
        except Exception as e:
            self.modules_loaded = False
            self.load_error = str(e)
    
    # ==================== 帮助命令 ====================
    
    def do_help(self, arg):
        """显示帮助"""
        if arg:
            # 显示特定命令帮助
            super().do_help(arg)
            return
        
        print("""
╔═══════════════════════════════════════════════════╗
║                    命令列表                        ║
╠═══════════════════════════════════════════════════╣
║  brain     - 测试脑部模块                          ║
║  gateway   - 测试网关模块                          ║
║  router    - 测试路由模块                          ║
║  agent     - 测试 Agent 管理                       ║
║  feishu    - 测试飞书文档功能                      ║
║  all       - 测试所有模块                          ║
║  clear     - 清屏                                  ║
║  quit      - 退出                                 ║
╚═══════════════════════════════════════════════════╝
        """)
    
    # ==================== Brain 测试 ====================
    
    def do_brain(self, arg):
        """测试脑部模块"""
        print("\n" + "="*50)
        print("🧠 Brain 模块测试")
        print("="*50)
        
        # 测试意图识别
        print("\n📌 意图识别测试:")
        tests = [
            "搜索机器学习论文",
            "帮我写个Python代码",
            "创作一段文案",
            "查看成本统计",
            "创建一个新Agent",
        ]
        
        for msg in tests:
            intent = self.thalamus.understand_intent(msg)
            agent_id = self.thalamus.route_message(msg)
            print(f"  '{msg}'")
            print(f"    → 意图: {intent.intent.value} (置信度: {intent.confidence:.2f})")
            print(f"    → 路由: Agent {agent_id}")
        
        print("\n✅ Brain 模块测试完成")
    
    # ==================== Gateway 测试 ====================
    
    def do_gateway(self, arg):
        """测试网关模块"""
        print("\n" + "="*50)
        print("🔐 Gateway 模块测试")
        print("="*50)
        
        # 测试认证
        print("\n📌 认证测试:")
        
        # 无白名单 - 允许所有
        auth = GatewayAuth()
        result = auth.authenticate("test_user")
        print(f"  无白名单 → {result.result.value}")
        
        # 有白名单
        auth2 = GatewayAuth(allow_from=["user1", "user2"])
        result1 = auth2.authenticate("user1")
        result2 = auth2.authenticate("user3")
        print(f"  白名单用户 user1 → {result1.result.value}")
        print(f"  非白名单用户 user3 → {result2.result.value}")
        
        # 测试限流
        print("\n📌 限流测试:")
        auth3 = GatewayAuth(enable_rate_limit=True, rate_limit_count=3, rate_limit_window=60)
        for i in range(5):
            result = auth3.authenticate("rate_user")
            print(f"  请求 {i+1}: {result.result.value}")
        
        # 测试过滤
        print("\n📌 过滤测试:")
        f = GatewayFilter(ignore_keywords=["spam", "广告"])
        
        tests = [
            ("正常消息", True),
            ("这是spam", False),
            ("广告信息", False),
        ]
        
        for msg, expected in tests:
            result = f.should_process({"type": "message", "content": msg})
            status = "✅" if result == expected else "❌"
            print(f"  {status} '{msg}' → {'通过' if result else '过滤'}")
        
        print("\n✅ Gateway 模块测试完成")
    
    # ==================== Router 测试 ====================
    
    def do_router(self, arg):
        """测试路由模块"""
        print("\n" + "="*50)
        print("📡 Router 模块测试")
        print("="*50)
        
        tests = [
            ("搜索论文", "01"),
            ("写代码", "02"),
            ("创意文案", "03"),
            ("成本统计", "04"),
            ("创建Agent", "00"),
            ("你好", "00"),
            ("今天天气", "00"),
        ]
        
        print("\n📌 路由测试:")
        for msg, expected in tests:
            result = self.router.route(msg)
            status = "✅" if result == expected else "❌"
            print(f"  {status} '{msg}' → Agent {result} (期望: {expected})")
        
        # 列出所有 Agent
        print("\n📌 Agent 列表:")
        agents = self.router.list_agents()
        for agent in agents:
            print(f"  • Agent {agent['id']}: {agent['name']} ({agent['role']})")
        
        print("\n✅ Router 模块测试完成")
    
    # ==================== Agent 管理测试 ====================
    
    def do_agent(self, arg):
        """测试 Agent 管理"""
        print("\n" + "="*50)
        print("🤖 Agent 管理测试")
        print("="*50)
        
        # 测试需求分析
        print("\n📌 需求分析:")
        tests = [
            "创建一个学术助手",
            "需要一个编程助手",
            "帮我写创意文案",
        ]
        
        for req in tests:
            spec = self.creator.create_agent_spec(req)
            print(f"  需求: '{req}'")
            print(f"    → 名称: {spec.name}")
            print(f"    → 角色: {spec.role}")
            print(f"    → 技能: {spec.skills.get('required', [])[:2]}...")
        
        # 测试创建 Agent
        print("\n📌 创建 Agent:")
        spec = self.creator.create_agent_spec("测试助手")
        result = self.creator.create(spec)
        print(f"  创建结果: {result.success}")
        print(f"  消息: {result.message}")
        
        # 测试状态查看
        print("\n📌 状态查看:")
        status = self.manager.get_all_status()
        print(f"  Agent 总数: {status['total']}")
        print(f"  活跃: {status['active']}")
        
        print("\n✅ Agent 管理测试完成")
    
    # ==================== 飞书测试 ====================
    
    def do_feishu(self, arg):
        """测试飞书文档功能"""
        print("\n" + "="*50)
        print("📄 飞书文档功能测试")
        print("="*50)
        
        print("\n📌 FeishuDocument 类方法检查:")
        
        methods = [
            'upload_file',
            'download_file',
            'create_document',
            'get_document',
            'update_document',
            'create_bitable',
            'get_bitable_records',
            'create_bitable_record',
            'list_spaces',
            'list_space_nodes',
            'create_knowledge_doc',
        ]
        
        for method in methods:
            has = hasattr(self.feishu_doc, method) if self.feishu_doc else False
            status = "✅" if has else "⚠️"
            print(f"  {status} {method}")
        
        print("\n⚠️  注意: 完整功能需要飞书 API 凭证")
        print("  设置环境变量: FEISHU_APP_ID, FEISHU_APP_SECRET")
        
        print("\n✅ 飞书文档功能检查完成")
    
    # ==================== 全部测试 ====================
    
    def do_all(self, arg):
        """测试所有模块"""
        print("\n" + "="*50)
        print("🔬 全部模块测试")
        print("="*50)
        
        self.do_brain("")
        self.do_gateway("")
        self.do_router("")
        self.do_agent("")
        self.do_feishu("")
        
        print("\n" + "="*50)
        print("🎉 全部测试完成!")
        print("="*50)
    
    # ==================== 工具命令 ====================
    
    def do_clear(self, arg):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def do_status(self, arg):
        """查看模块状态"""
        print("\n" + "="*50)
        print("📊 模块状态")
        print("="*50)
        
        if self.modules_loaded:
            print("  ✅ 所有模块加载成功")
            print(f"  • Thalamus: {type(self.thalamus).__name__}")
            print(f"  • GatewayAuth: {type(self.auth).__name__}")
            print(f"  • AgentRouter: {type(self.router).__name__}")
            print(f"  • AgentCreator: {type(self.creator).__name__}")
        else:
            print(f"  ❌ 模块加载失败: {self.load_error}")
        
        print("")
    
    # ==================== 退出 ====================
    
    def do_quit(self, arg):
        """退出"""
        print("\n👋 再见!")
        return True
    
    def do_exit(self, arg):
        """退出"""
        return self.do_quit(arg)
    
    def do_EOF(self, arg):
        """Ctrl+D 退出"""
        print("\n👋 再见!")
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="cp9 TUI 控制台")
    parser.add_argument("--command", "-c", help="执行单个命令后退出")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式")
    args = parser.parse_args()
    
    if args.quiet:
        # 静默模式，不显示 intro
        cp9TUI().onecmd(args.command or "help")
    elif args.command:
        # 执行单命令
        cp9TUI().onecmd(args.command)
    else:
        # 交互模式
        cp9TUI().cmdloop()


if __name__ == "__main__":
    main()
