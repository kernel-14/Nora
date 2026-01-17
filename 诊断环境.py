"""
环境诊断脚本
检查项目环境是否正确配置
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_item(name, condition, success_msg, fail_msg):
    """检查单个项目"""
    status = "✅" if condition else "❌"
    message = success_msg if condition else fail_msg
    print(f"{status} {name}: {message}")
    return condition

def main():
    print_header("环境诊断")
    
    all_ok = True
    
    # 1. Python 版本
    print_header("1. Python 环境")
    python_version = sys.version_info
    version_ok = python_version >= (3, 8)
    all_ok &= check_item(
        "Python 版本",
        version_ok,
        f"{python_version.major}.{python_version.minor}.{python_version.micro}",
        f"{python_version.major}.{python_version.minor}.{python_version.micro} (需要 >= 3.8)"
    )
    
    # 2. 当前目录
    print_header("2. 目录结构")
    current_dir = Path.cwd()
    all_ok &= check_item(
        "当前目录",
        True,
        str(current_dir),
        ""
    )
    
    # 检查关键目录和文件
    app_dir = current_dir / "app"
    app_main = current_dir / "app" / "main.py"
    frontend_dir = current_dir / "frontend"
    data_dir = current_dir / "data"
    requirements = current_dir / "requirements.txt"
    env_file = current_dir / ".env"
    
    all_ok &= check_item(
        "app/ 目录",
        app_dir.exists(),
        "存在",
        "不存在 - 请确保在项目根目录运行"
    )
    
    all_ok &= check_item(
        "app/main.py",
        app_main.exists(),
        "存在",
        "不存在"
    )
    
    all_ok &= check_item(
        "frontend/ 目录",
        frontend_dir.exists(),
        "存在",
        "不存在"
    )
    
    all_ok &= check_item(
        "data/ 目录",
        data_dir.exists(),
        "存在",
        "不存在"
    )
    
    all_ok &= check_item(
        "requirements.txt",
        requirements.exists(),
        "存在",
        "不存在"
    )
    
    check_item(
        ".env 文件",
        env_file.exists(),
        "存在",
        "不存在 - 请从 .env.example 复制"
    )
    
    # 3. Python 依赖
    print_header("3. Python 依赖")
    
    # FastAPI
    try:
        import fastapi
        all_ok &= check_item(
            "FastAPI",
            True,
            f"已安装 (版本 {fastapi.__version__})",
            ""
        )
    except ImportError:
        all_ok &= check_item(
            "FastAPI",
            False,
            "",
            "未安装 - 运行: pip install fastapi"
        )
    
    # Uvicorn
    try:
        import uvicorn
        all_ok &= check_item(
            "Uvicorn",
            True,
            f"已安装 (版本 {uvicorn.__version__})",
            ""
        )
    except ImportError:
        all_ok &= check_item(
            "Uvicorn",
            False,
            "",
            "未安装 - 运行: pip install uvicorn"
        )
    
    # Pydantic
    try:
        import pydantic
        all_ok &= check_item(
            "Pydantic",
            True,
            f"已安装 (版本 {pydantic.__version__})",
            ""
        )
    except ImportError:
        all_ok &= check_item(
            "Pydantic",
            False,
            "",
            "未安装 - 运行: pip install pydantic"
        )
    
    # httpx
    try:
        import httpx
        all_ok &= check_item(
            "httpx",
            True,
            f"已安装 (版本 {httpx.__version__})",
            ""
        )
    except ImportError:
        all_ok &= check_item(
            "httpx",
            False,
            "",
            "未安装 - 运行: pip install httpx"
        )
    
    # python-multipart
    try:
        import multipart
        all_ok &= check_item(
            "python-multipart",
            True,
            "已安装",
            ""
        )
    except ImportError:
        all_ok &= check_item(
            "python-multipart",
            False,
            "",
            "未安装 - 运行: pip install python-multipart"
        )
    
    # 4. 模块导入测试
    print_header("4. 模块导入测试")
    
    try:
        sys.path.insert(0, str(current_dir))
        import app.main
        all_ok &= check_item(
            "导入 app.main",
            True,
            "成功",
            ""
        )
    except Exception as e:
        all_ok &= check_item(
            "导入 app.main",
            False,
            "",
            f"失败 - {str(e)}"
        )
    
    try:
        from app.config import get_config
        config = get_config()
        all_ok &= check_item(
            "加载配置",
            True,
            "成功",
            ""
        )
    except Exception as e:
        all_ok &= check_item(
            "加载配置",
            False,
            "",
            f"失败 - {str(e)}"
        )
    
    # 5. 环境变量
    print_header("5. 环境变量")
    
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            zhipu_key = os.getenv("ZHIPU_API_KEY")
            check_item(
                "ZHIPU_API_KEY",
                zhipu_key is not None and zhipu_key != "",
                "已配置",
                "未配置 - 请在 .env 文件中设置"
            )
            
            minimax_key = os.getenv("MINIMAX_API_KEY")
            check_item(
                "MINIMAX_API_KEY",
                minimax_key is not None and minimax_key != "",
                "已配置",
                "未配置（可选）"
            )
        except ImportError:
            print("⚠️  python-dotenv 未安装，跳过环境变量检查")
    else:
        print("⚠️  .env 文件不存在，跳过环境变量检查")
    
    # 6. 端口检查
    print_header("6. 端口检查")
    
    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    port_8000_free = not is_port_in_use(8000)
    check_item(
        "端口 8000",
        port_8000_free,
        "可用",
        "已被占用 - 请关闭占用进程或使用其他端口"
    )
    
    port_5173_free = not is_port_in_use(5173)
    check_item(
        "端口 5173",
        port_5173_free,
        "可用",
        "已被占用 - 请关闭占用进程或使用其他端口"
    )
    
    # 总结
    print_header("诊断总结")
    
    if all_ok:
        print("✅ 所有检查通过！环境配置正确。")
        print("\n可以启动应用：")
        print("  后端: python -m uvicorn app.main:app --reload")
        print("  前端: cd frontend && npm run dev")
    else:
        print("❌ 发现问题，请根据上述提示修复。")
        print("\n常见解决方法：")
        print("  1. 确保在项目根目录运行")
        print("  2. 安装依赖: pip install -r requirements.txt")
        print("  3. 配置 .env 文件")
        print("  4. 检查 Python 版本 >= 3.8")
    
    print("\n" + "=" * 60)
    print("详细文档: 后端启动问题排查.md")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
