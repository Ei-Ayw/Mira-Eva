#!/usr/bin/env python3
"""
日志查看脚本
用于查看Mira-Eva系统的各种日志
"""

import os
import sys
import time
from datetime import datetime

def print_log_file(filename, lines=50, follow=False):
    """打印日志文件内容"""
    if not os.path.exists(filename):
        print(f"❌ 日志文件不存在: {filename}")
        return
    
    print(f"📋 查看日志文件: {filename}")
    print("=" * 80)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # 读取最后N行
            all_lines = f.readlines()
            if len(all_lines) <= lines:
                start_line = 0
            else:
                start_line = len(all_lines) - lines
            
            for i in range(start_line, len(all_lines)):
                line = all_lines[i].strip()
                if line:
                    print(line)
            
            if follow:
                print("\n🔄 实时监控日志 (按 Ctrl+C 停止)...")
                while True:
                    time.sleep(1)
                    new_lines = f.readlines()
                    for line in new_lines:
                        if line.strip():
                            print(line.strip())
                            
    except KeyboardInterrupt:
        print("\n⏹️ 停止监控")
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")

def show_log_stats():
    """显示日志统计信息"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        print("❌ 日志目录不存在")
        return
    
    print("📊 日志文件统计")
    print("=" * 50)
    
    total_size = 0
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            filepath = os.path.join(log_dir, filename)
            size = os.path.getsize(filepath)
            total_size += size
            
            # 获取文件修改时间
            mtime = os.path.getmtime(filepath)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"📄 {filename:<20} {size:>8} bytes  {mtime_str}")
    
    print("-" * 50)
    print(f"📁 总计: {len([f for f in os.listdir(log_dir) if f.endswith('.log')])} 个日志文件")
    print(f"💾 总大小: {total_size:,} bytes ({total_size/1024:.1f} KB)")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🚀 Mira-Eva 日志查看工具")
        print("=" * 50)
        print("用法:")
        print("  python view_logs.py <命令> [参数]")
        print("\n命令:")
        print("  stats                    - 显示日志统计")
        print("  chat [行数] [follow]     - 查看聊天日志")
        print("  error [行数] [follow]    - 查看错误日志")
        print("  all [行数] [follow]      - 查看所有日志")
        print("  follow <文件名>          - 实时监控指定日志")
        print("\n示例:")
        print("  python view_logs.py stats")
        print("  python view_logs.py chat 100")
        print("  python view_logs.py chat 50 follow")
        print("  python view_logs.py follow logs/chat.log")
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        show_log_stats()
    
    elif command == "chat":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        follow = "follow" in sys.argv
        print_log_file("logs/chat.log", lines, follow)
    
    elif command == "error":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        follow = "follow" in sys.argv
        print_log_file("logs/error.log", lines, follow)
    
    elif command == "all":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        follow = "follow" in sys.argv
        print_log_file("logs/mira_eva.log", lines, follow)
    
    elif command == "follow":
        if len(sys.argv) < 3:
            print("❌ 请指定要监控的日志文件")
            return
        filename = sys.argv[2]
        print_log_file(filename, follow=True)
    
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python view_logs.py' 查看帮助")

if __name__ == '__main__':
    main()
