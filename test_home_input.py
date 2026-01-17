"""
测试首页交互功能

这个脚本测试：
1. 首页记录功能 - 调用 /api/process
2. AI 对话功能（RAG增强）- 调用 /api/chat
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_home_input_text():
    """测试首页文字输入记录"""
    print("\n=== 测试首页文字输入 ===")
    
    text = "今天天气很好，心情不错。想到一个新点子：做一个治愈系应用。明天要记得买书。"
    
    response = requests.post(
        f"{BASE_URL}/api/process",
        data={"text": text}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 记录成功")
        print(f"Record ID: {result['record_id']}")
        
        if result.get('mood'):
            print(f"情绪: {result['mood']['type']} (强度: {result['mood']['intensity']})")
        
        if result.get('inspirations'):
            print(f"灵感数量: {len(result['inspirations'])}")
            for insp in result['inspirations']:
                print(f"  - {insp['core_idea']}")
        
        if result.get('todos'):
            print(f"待办数量: {len(result['todos'])}")
            for todo in result['todos']:
                print(f"  - {todo['task']}")
        
        return True
    else:
        print(f"❌ 记录失败: {response.status_code}")
        print(response.text)
        return False


def test_ai_chat_without_rag():
    """测试 AI 对话（无历史记录）"""
    print("\n=== 测试 AI 对话（无历史记录） ===")
    
    message = "你好呀！"
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        data={"text": message}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 对话成功")
        print(f"用户: {message}")
        print(f"AI: {result['response']}")
        return True
    else:
        print(f"❌ 对话失败: {response.status_code}")
        print(response.text)
        return False


def test_ai_chat_with_rag():
    """测试 AI 对话（有历史记录，RAG增强）"""
    print("\n=== 测试 AI 对话（RAG增强） ===")
    
    # 先添加一些记录
    print("添加测试记录...")
    test_records = [
        "今天工作很累，但是完成了一个重要项目，很有成就感。",
        "想到一个新点子：做一个帮助人们记录心情的应用。",
        "明天要早起去跑步，保持健康。"
    ]
    
    for text in test_records:
        requests.post(f"{BASE_URL}/api/process", data={"text": text})
    
    print("记录添加完成\n")
    
    # 测试对话
    message = "我最近在做什么？"
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        data={"text": message}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ RAG 对话成功")
        print(f"用户: {message}")
        print(f"AI: {result['response']}")
        print("\n注意：AI 的回复应该基于之前的记录内容")
        return True
    else:
        print(f"❌ 对话失败: {response.status_code}")
        print(response.text)
        return False


def test_get_records():
    """测试获取记录"""
    print("\n=== 测试获取记录 ===")
    
    response = requests.get(f"{BASE_URL}/api/records")
    
    if response.status_code == 200:
        result = response.json()
        records = result.get('records', [])
        print(f"✅ 获取成功")
        print(f"总记录数: {len(records)}")
        
        if records:
            print("\n最近 3 条记录:")
            for record in records[-3:]:
                print(f"  - [{record['timestamp']}] {record['original_text'][:50]}...")
        
        return True
    else:
        print(f"❌ 获取失败: {response.status_code}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("首页交互功能测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 后端服务未运行，请先启动后端")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("   启动命令: python -m uvicorn app.main:app --reload")
        return
    
    print("✅ 后端服务正常运行\n")
    
    # 运行测试
    results = []
    
    results.append(("首页文字输入", test_home_input_text()))
    results.append(("AI 对话（无历史）", test_ai_chat_without_rag()))
    results.append(("AI 对话（RAG增强）", test_ai_chat_with_rag()))
    results.append(("获取记录", test_get_records()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查日志")


if __name__ == "__main__":
    main()
