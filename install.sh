#!/usr/bin/env bash
# Copaw 一键安装脚本
# 支持: Linux, macOS, Windows (WSL)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检测操作系统
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)         echo "unknown";;
    esac
}

# 检测包管理器
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v brew &> /dev/null; then
        echo "brew"
    elif command -v conda &> /dev/null; then
        echo "conda"
    else
        echo "none"
    fi
}

# 打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 版本
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2]))')
        info "Python 版本: $PYTHON_VERSION"
        
        # 检查版本 >= 3.10
        if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
            return 0
        else
            error "Python 版本需要 >= 3.10"
            return 1
        fi
    else
        error "未找到 Python，请先安装 Python 3.10+"
        return 1
    fi
}

# 安装 Python (Linux)
install_python_linux() {
    local pkg_manager=$(detect_package_manager)
    
    if [ "$pkg_manager" = "apt" ]; then
        info "安装 Python 3.12..."
        sudo apt-get update
        sudo apt-get install -y python3.12 python3.12-venv python3-pip
    elif [ "$pkg_manager" = "yum" ]; then
        info "安装 Python 3.12..."
        sudo yum install -y python312 python312-pip
    else
        error "不支持的包管理器，请手动安装 Python 3.10+"
        exit 1
    fi
}

# 安装 Python (macOS)
install_python_mac() {
    info "安装 Python 3.12..."
    if command -v brew &> /dev/null; then
        brew install python@3.12
    else
        error "请先安装 Homebrew: https://brew.sh"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    local venv_path="$1"
    
    if [ -d "$venv_path" ]; then
        warn "虚拟环境已存在: $venv_path"
        return 0
    fi
    
    info "创建虚拟环境: $venv_path"
    python3 -m venv "$venv_path"
}

# 安装依赖
install_dependencies() {
    local venv_path="$1"
    local pip="$venv_path/bin/pip"
    
    info "升级 pip..."
    $pip install --upgrade pip
    
    info "安装依赖..."
    if [ -f "requirements.txt" ]; then
        $pip install -r requirements.txt
    fi
    
    # 安装 copaw
    $pip install -e .
}

# 创建配置目录
create_config_dir() {
    local config_dir="${HOME}/.cp9"
    
    if [ -d "$config_dir" ]; then
        info "配置目录已存在: $config_dir"
        return 0
    fi
    
    info "创建配置目录: $config_dir"
    mkdir -p "$config_dir"
    
    # 创建默认配置
    cat > "${config_dir}/config.yaml" << 'EOF'
# Copaw 配置文件

app:
  name: copaw
  version: "1.0.0"

server:
  host: "0.0.0.0"
  port: 9090

logging:
  level: "INFO"
  file: "~/.cp9/logs/app.log"

channels:
  feishu:
    enabled: false
    app_id: ""
    app_secret: ""
    bot_prefix: "/ai"
    filters:
      ignore_keywords: []
      ignore_users: []

providers:
  glm-5:
    enabled: false
    api_key: ""
  minimax:
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

skills:
  text_creative:
    enabled: true
  image_prompt:
    enabled: true

sensors:
  dispatch:
    enabled: true
  print:
    enabled: false

crons:
  daily_report:
    enabled: false
    agent_id: "04"
    cron: "0 18 * * *"
EOF
    
    info "默认配置已创建: ${config_dir}/config.yaml"
}

# 创建日志目录
create_log_dir() {
    local log_dir="${HOME}/.cp9/logs"
    
    if [ -d "$log_dir" ]; then
        return 0
    fi
    
    info "创建日志目录: $log_dir"
    mkdir -p "$log_dir"
}

# 创建符号链接或别名
setup_cli() {
    local install_path="$1"
    
    # 创建符号链接
    info "创建 CLI 符号链接..."
    
    if [ -w "/usr/local/bin" ]; then
        sudo ln -sf "$install_path" /usr/local/bin/cp9
    else
        # 用户目录
        mkdir -p "${HOME}/.local/bin"
        ln -sf "$install_path" "${HOME}/.local/bin/cp9"
        
        # 添加到 PATH
        if ! grep -q ".local/bin" "${HOME}/.bashrc" 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
        fi
    fi
    
    info "CLI 命令已安装: cp9"
}

# 主安装流程
main() {
    local os=$(detect_os)
    local pkg_manager=$(detect_package_manager)
    
    echo "========================================"
    echo "  Copaw 一键安装脚本"
    echo "========================================"
    echo ""
    info "操作系统: $os"
    info "包管理器: $pkg_manager"
    echo ""
    
    # 检查 Python
    if ! check_python; then
        warn "开始安装 Python..."
        case "$os" in
            linux) install_python_linux ;;
            macos) install_python_mac ;;
            windows) 
                error "Windows 请安装 WSL 或手动安装 Python"
                exit 1
                ;;
        esac
    fi
    
    # 获取项目目录
    local script_dir="$(cd "$(dirname "$0")" && pwd)"
    
    # 创建虚拟环境
    local venv_path="${script_dir}/venv"
    create_venv "$venv_path"
    
    # 安装依赖
    install_dependencies "$venv_path"
    
    # 创建配置
    create_config_dir
    create_log_dir
    
    # 安装 CLI
    local cli_path="${script_dir}/cli.py"
    setup_cli "$cli_path"
    
    echo ""
    echo "========================================"
    echo -e "${GREEN}  安装完成!${NC}"
    echo "========================================"
    echo ""
    info "运行以下命令开始:"
    echo "  cp9 mgr init"
    echo "  cp9 mgr start"
    echo ""
}

# 卸载
uninstall() {
    local venv_path="${HOME}/.cpaw/venv"
    local config_dir="${HOME}/.cp9"
    
    warn "卸载 Copaw..."
    
    # 停止服务
    if command -v cp9 &> /dev/null; then
        cp9 mgr stop 2>/dev/null || true
    fi
    
    # 删除文件
    rm -rf "$venv_path"
    rm -f /usr/local/bin/cp9
    rm -f "${HOME}/.local/bin/cp9"
    
    # 询问是否删除配置
    if [ -d "$config_dir" ]; then
        read -p "是否删除配置目录? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf "$config_dir"
        fi
    fi
    
    info "卸载完成"
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  install   安装 Copaw (默认)"
    echo "  uninstall 卸载 Copaw"
    echo "  help      显示帮助"
}

# 主入口
case "${1:-install}" in
    install)
        main
        ;;
    uninstall)
        uninstall
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
