"""完整流程测试：从输入到存储的全流程模拟"""

import asyncio
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

from app.semantic_parser import SemanticParserService
from app.storage import StorageService
from app.models import RecordData, ParsedData

# 测试场景
SCENARIOS = [
    {
        "name": "场景1：工作压力与情绪记录",
        "text": "今天工作真的好累啊，老板又临时加了三个需求，感觉压力山大。不过下班的时候看到窗外的晚霞特别美，心情稍微好了一点。明天记得要把项目文档整理一下，还要准备周五的汇报材料。"
    },
    {
        "name": "场景2：学习灵感与创意记录",
        "text": "刚才看了一篇关于设计模式的文章，突然想到可以用观察者模式来重构我们的消息推送系统！这样可以让代码更解耦，维护起来也更方便。感觉豁然开朗，学习真的很有意思。周末去图书馆借几本架构设计的书来看看。"
    },
    {
        "name": "场景3：日常生活与待办清单",
        "text": "明天早上九点要去医院体检，记得空腹。中午约了小李在星巴克讨论新项目的事情。下午三点半要接孩子放学，顺便去超市买点菜。晚上想做个番茄炖牛腩，好久没做饭了，期待一下。"
    },
    {
        "name": "场景4：情感倾诉与心情记录",
        "text": "今天和妈妈视频聊天，她说最近身体不太好，我心里特别难受。虽然工作很忙，但还是要多关心家人。想起小时候妈妈照顾我的样子，现在轮到我照顾她了。下周请假回家看看她，给她做顿好吃的。人生真的很短，要珍惜和家人在一起的时光。"
    },
    {
        "name": "场景5：创意想法与项目规划",
        "text": "突然有个想法，可以做一个帮助人们记录灵感的 APP，用 AI 来自动分类和整理。现在市面上的笔记软件都太复杂了，我想做一个简单治愈的版本。先画个原型图，然后调研一下竞品。这个周末开始写技术方案，争取下个月能做出 MVP。感觉找到了一个很有意义的项目，有点小激动！"
    }
]


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def print_section(title):
    """打印章节标题"""
    print(f"\n{title}")
    print_separator("-", len(title))


async def process_single_scenario(
    parser: SemanticParserService,
    storage: StorageService,
    scenario: dict,
    index: int,
    total: int
):
    """处理单个场景的完整流程"""
    
    print_separator()
    print(f"测试 {index}/{total}: {scenario['name']}")
    print_separator()
    
    # 步骤 1: 显示输入
    print_section("📝 步骤 1: 用户输入")
    print(f"{scenario['text']}")
    
    # 步骤 2: AI 语义解析
    print_section("🤖 步骤 2: AI 语义解析")
    try:
        parsed_data = await parser.parse(scenario['text'])
        print("✅ 解析成功")
        
        # 显示解析结果
        if parsed_data.mood:
            print(f"\n情绪识别:")
            print(f"  类型: {parsed_data.mood.type}")
            print(f"  强度: {parsed_data.mood.intensity}/10")
            print(f"  关键词: {', '.join(parsed_data.mood.keywords)}")
        else:
            print(f"\n情绪识别: 未识别到情绪")
        
        if parsed_data.inspirations:
            print(f"\n灵感提取 ({len(parsed_data.inspirations)} 条):")
            for i, insp in enumerate(parsed_data.inspirations, 1):
                print(f"  {i}. {insp.core_idea}")
                print(f"     分类: {insp.category}")
                print(f"     标签: {', '.join(insp.tags)}")
        else:
            print(f"\n灵感提取: 无")
        
        if parsed_data.todos:
            print(f"\n待办提取 ({len(parsed_data.todos)} 条):")
            for i, todo in enumerate(parsed_data.todos, 1):
                time_str = f", 时间: {todo.time}" if todo.time else ""
                loc_str = f", 地点: {todo.location}" if todo.location else ""
                print(f"  {i}. {todo.task}{time_str}{loc_str}")
        else:
            print(f"\n待办提取: 无")
        
    except Exception as e:
        print(f"❌ 解析失败: {str(e)}")
        return False
    
    # 步骤 3: 生成记录
    print_section("📋 步骤 3: 生成记录数据")
    record_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    record = RecordData(
        record_id=record_id,
        timestamp=timestamp,
        input_type="text",
        original_text=scenario['text'],
        parsed_data=parsed_data
    )
    
    print(f"记录 ID: {record_id}")
    print(f"时间戳: {timestamp}")
    print(f"输入类型: text")
    
    # 步骤 4: 存储数据
    print_section("💾 步骤 4: 存储到 JSON 文件")
    try:
        # 保存主记录
        storage.save_record(record)
        print(f"✅ 保存主记录到: data/records.json")
        
        # 保存情绪数据
        if parsed_data.mood:
            storage.append_mood(parsed_data.mood, record_id, timestamp)
            print(f"✅ 保存情绪数据到: data/moods.json")
        
        # 保存灵感数据
        if parsed_data.inspirations:
            storage.append_inspirations(parsed_data.inspirations, record_id, timestamp)
            print(f"✅ 保存 {len(parsed_data.inspirations)} 条灵感到: data/inspirations.json")
        
        # 保存待办数据
        if parsed_data.todos:
            storage.append_todos(parsed_data.todos, record_id, timestamp)
            print(f"✅ 保存 {len(parsed_data.todos)} 条待办到: data/todos.json")
        
    except Exception as e:
        print(f"❌ 存储失败: {str(e)}")
        return False
    
    # 步骤 5: 验证存储
    print_section("✅ 步骤 5: 验证存储结果")
    try:
        # 读取并验证 records.json
        with open("data/records.json", "r", encoding="utf-8") as f:
            records = json.load(f)
            if any(r["record_id"] == record_id for r in records):
                print(f"✅ records.json 中找到记录 {record_id}")
            else:
                print(f"⚠️  records.json 中未找到记录")
        
        # 验证其他文件
        if parsed_data.mood:
            with open("data/moods.json", "r", encoding="utf-8") as f:
                moods = json.load(f)
                if any(m["record_id"] == record_id for m in moods):
                    print(f"✅ moods.json 中找到情绪数据")
        
        if parsed_data.inspirations:
            with open("data/inspirations.json", "r", encoding="utf-8") as f:
                inspirations = json.load(f)
                count = sum(1 for i in inspirations if i["record_id"] == record_id)
                print(f"✅ inspirations.json 中找到 {count} 条灵感")
        
        if parsed_data.todos:
            with open("data/todos.json", "r", encoding="utf-8") as f:
                todos = json.load(f)
                count = sum(1 for t in todos if t["record_id"] == record_id)
                print(f"✅ todos.json 中找到 {count} 条待办")
        
    except Exception as e:
        print(f"⚠️  验证时出错: {str(e)}")
    
    print(f"\n✅ 场景 {index} 处理完成！")
    return True


async def main():
    """主函数"""
    print_separator("=")
    print("治愈系记录助手 - 完整流程测试")
    print("从输入 → AI 解析 → 数据存储 → 验证")
    print_separator("=")
    
    # 检查环境
    print_section("🔧 环境检查")
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("❌ 错误: 未找到 ZHIPU_API_KEY 环境变量")
        return
    
    print(f"✅ API Key: {api_key[:20]}...")
    
    data_dir = os.getenv('DATA_DIR', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ 创建数据目录: {data_dir}")
    else:
        print(f"✅ 数据目录存在: {data_dir}")
    
    # 初始化服务
    print_section("🚀 初始化服务")
    parser = SemanticParserService(api_key)
    storage = StorageService(data_dir)
    print("✅ 语义解析服务已初始化")
    print("✅ 存储服务已初始化")
    
    # 显示测试计划
    print_section("📋 测试计划")
    print(f"共 {len(SCENARIOS)} 个测试场景:")
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"  {i}. {scenario['name']}")
    
    print("\n开始测试...")
    
    # 执行测试
    results = []
    try:
        for i, scenario in enumerate(SCENARIOS, 1):
            success = await process_single_scenario(
                parser, storage, scenario, i, len(SCENARIOS)
            )
            results.append({
                "name": scenario["name"],
                "success": success
            })
            
            # 等待一下
            if i < len(SCENARIOS):
                print(f"\n⏳ 等待 3 秒后继续下一个场景...")
                await asyncio.sleep(3)
    
    finally:
        # 关闭服务
        await parser.close()
    
    # 输出总结
    print("\n\n")
    print_separator("=")
    print("测试总结")
    print_separator("=")
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    for result in results:
        status = "✅ 成功" if result["success"] else "❌ 失败"
        print(f"{status} - {result['name']}")
    
    print(f"\n总计: {success_count}/{total_count} 个场景成功")
    
    # 显示数据文件
    print_section("📁 生成的数据文件")
    data_files = [
        "data/records.json",
        "data/moods.json",
        "data/inspirations.json",
        "data/todos.json"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                count = len(data)
            print(f"✅ {file_path} ({count} 条记录, {size} 字节)")
        else:
            print(f"⚠️  {file_path} (不存在)")
    
    if success_count == total_count:
        print(f"\n🎉 所有测试场景都成功完成！")
        print(f"\n你可以查看 data/ 目录下的 JSON 文件来验证存储结果。")
    else:
        print(f"\n⚠️  有 {total_count - success_count} 个场景失败")
    
    print_separator("=")


if __name__ == "__main__":
    asyncio.run(main())
