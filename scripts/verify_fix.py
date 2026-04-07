#!/usr/bin/env python3
"""
验证脚本 - 用于验证代码修改是否成功
用法：python scripts/verify_fix.py <文件路径> <测试命令>
"""

import sys
import subprocess
import os

def run_test(test_command):
    """运行测试命令"""
    print(f"🧪 运行测试：{test_command}")
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 测试通过")
            return True
        else:
            print("❌ 测试失败")
            print(f"输出：{result.stdout}")
            print(f"错误：{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 运行测试失败：{e}")
        return False

def check_file_exists(file_path):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ 文件存在：{file_path}")
        return True
    else:
        print(f"❌ 文件不存在：{file_path}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法：python verify_fix.py <文件路径> [测试命令]")
        print("示例：python verify_fix.py robot.py python test_robot.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_command = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print("🔍 验证修改")
    print("=" * 60)
    
    # 检查文件
    if not check_file_exists(file_path):
        sys.exit(1)
    
    # 运行测试
    if test_command:
        print()
        if not run_test(test_command):
            print()
            print("=" * 60)
            print("❌ 验证失败 - 修改可能未生效")
            print("=" * 60)
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ 验证成功 - 修改已生效")
    print("=" * 60)

if __name__ == "__main__":
    main()
