# -*- coding: utf-8 -*-
"""
Security Guard Module - 安全检查模块

用于对 Agent 的输入、输出、操作进行安全检查。
"""

import re
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


# 敏感词列表（可配置）
DEFAULT_SENSITIVE_WORDS = [
    "敏感词1", "敏感词2",  # TODO: 配置实际敏感词
]


class SecurityGuard:
    """安全检查器"""
    
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id
        self.sensitive_words = DEFAULT_SENSITIVE_WORDS.copy()
        self.load_agent_guard()
    
    def load_agent_guard(self):
        """加载 Agent 专属安全配置"""
        if self.agent_id:
            guard_file = Path(__file__).parent.parent / f"agent_{self.agent_id}_" / "guard.md"
            if guard_file.exists():
                # 加载 Agent 专属配置
                pass
    
    # ==================== 输入检查 ====================
    
    def check_input(self, text: str) -> Tuple[bool, str]:
        """
        检查输入内容是否安全。
        
        Returns:
            (is_safe, reason)
        """
        if not text or not text.strip():
            return False, "输入为空"
        
        # 检查长度
        if len(text) > 10000:
            return False, "输入过长"
        
        # 检查敏感词
        for word in self.sensitive_words:
            if word in text:
                return False, f"包含敏感词: {word}"
        
        return True, ""
    
    # ==================== SQL 注入检查 ====================
    
    def check_sql_injection(self, text: str) -> bool:
        """检查 SQL 注入"""
        sql_keywords = [
            "union", "select", "insert", "update", "delete",
            "drop", "create", "alter", "exec", "execute",
            "--", ";--", ";", "/*", "*/", "@@", "@",
            "char", "nchar", "varchar", "nvarchar",
            "alter", "begin", "cast", "cursor", "declare",
            "delete", "drop", "end", "exec", "execute",
        ]
        
        text_lower = text.lower()
        for keyword in sql_keywords:
            if re.search(r'\b' + keyword + r'\b', text_lower):
                return True
        
        return False
    
    # ==================== 路径检查 ====================
    
    def check_path_traversal(self, path: str) -> bool:
        """检查路径遍历攻击"""
        # 禁止相对路径
        if ".." in path or path.startswith("/"):
            return True
        
        # 禁止危险路径
        dangerous_paths = [
            "/etc/", "/root/", "/home/", "/var/",
            "~/.ssh/", "~/.aws/", "/.env"
        ]
        
        for dp in dangerous_paths:
            if dp in path:
                return True
        
        return False
    
    # ==================== 文件检查 ====================
    
    def check_file_access(self, path: str, allowed_dirs: List[str] = None) -> bool:
        """检查文件访问权限"""
        if allowed_dirs is None:
            allowed_dirs = [os.getcwd()]
        
        abs_path = Path(path).resolve()
        
        for allowed_dir in allowed_dirs:
            allowed_abs = Path(allowed_dir).resolve()
            try:
                abs_path.relative_to(allowed_abs)
                return True
            except ValueError:
                continue
        
        return False
    
    # ==================== 命令检查 ====================
    
    def check_shell_command(self, cmd: str) -> bool:
        """检查危险命令"""
        dangerous_cmds = [
            "rm -rf", "dd if=", "mkfs", "fdisk",
            "curl | sh", "wget | sh", "eval", "bash -c",
            "chmod 777", "chown", "kill -9", "pkill",
        ]
        
        cmd_lower = cmd.lower()
        for dcmd in dangerous_cmds:
            if dcmd in cmd_lower:
                return True
        
        return False
    
    # ==================== 输出过滤 ====================
    
    def filter_output(self, text: str) -> str:
        """过滤输出内容"""
        # 替换敏感词
        for word in self.sensitive_words:
            text = text.replace(word, "***")
        
        return text
    
    def mask_sensitive_info(self, text: str) -> str:
        """脱敏处理"""
        # 脱敏邮箱
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '***@***.***',
            text
        )
        
        # 脱敏手机号
        text = re.sub(
            r'\b1[3-9]\d{9}\b',
            '1**********',
            text
        )
        
        # 脱敏身份证号
        text = re.sub(
            r'\b[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b',
            '******************',
            text
        )
        
        # 脱敏 API Key
        text = re.sub(
            r'(api[_-]?key|token|secret)[=:]\s*[\w-]{10,}',
            r'\1=***',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    # ==================== 综合检查 ====================
    
    def validate_request(self, request: Dict[str, Any]) -> Tuple[bool, str]:
        """
        综合验证请求安全性。
        
        Returns:
            (is_safe, reason)
        """
        # 检查输入
        if "input" in request:
            is_safe, reason = self.check_input(str(request["input"]))
            if not is_safe:
                return False, f"输入检查失败: {reason}"
        
        # 检查命令
        if "command" in request:
            if self.check_shell_command(request["command"]):
                return False, "检测到危险命令"
        
        # 检查文件路径
        if "path" in request:
            if self.check_path_traversal(request["path"]):
                return False, "检测到路径遍历攻击"
        
        return True, ""


class GuardManager:
    """安全检查管理器"""
    
    _guards: Dict[str, SecurityGuard] = {}
    
    @classmethod
    def get_guard(cls, agent_id: str = None) -> SecurityGuard:
        """获取指定 Agent 的安全检查器"""
        if agent_id not in cls._guards:
            cls._guards[agent_id] = SecurityGuard(agent_id)
        return cls._guards[agent_id]
    
    @classmethod
    def check_all(cls, agent_id: str, request: Dict[str, Any]) -> Tuple[bool, str]:
        """检查所有安全规则"""
        guard = cls.get_guard(agent_id)
        return guard.validate_request(request)


__all__ = [
    "SecurityGuard",
    "GuardManager",
]
