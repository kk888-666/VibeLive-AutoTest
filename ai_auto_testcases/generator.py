import os
import yaml
from openai import OpenAI

from common.config import API_KEY, AI_URL
from utils.swagger_utils import fetch_swagger_doc, parse_swagger_paths, SWAGGER_URL

# 配置
TEMPLATE_FILE = "template.yaml"
PROMPT_FILE = "prompt.md"
OUTPUT_DIR = "../data/ai_testcases"

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 预加载系统提示词，只读取一次
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 初始化AI客户端
client = OpenAI(api_key=API_KEY, base_url=AI_URL)


def generate_yaml(api_info):
    """单个接口生成YAML用例"""
    # 把接口文档转为YAML字符串，提升AI解析准确率
    api_doc_str = yaml.dump(api_info, allow_unicode=True, sort_keys=False)

    response = client.chat.completions.create(
        model="qwen-long-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"接口文档：{api_doc_str}\n请直接返回可用的YAML用例"}
        ],
        stream=True,
        top_p=0.8,
        temperature=0.7,
        extra_body={
            "enable_thinking": True,
            "thinking_budget": 6000
        }
    )
    reasoning_content = ""
    answer_content = ""
    is_answering = False
    print("\n" + "=" * 20 + f"生成用例：{api_info.get('接口名称', '未知接口')}" + "=" * 20)

    for chunk in response:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            if not is_answering:
                print(delta.reasoning_content, end="", flush=True)
            reasoning_content += delta.reasoning_content

        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                print("\n" + "=" * 20 + "用例内容" + "=" * 20)
                is_answering = True
            print(delta.content, end="", flush=True)
            answer_content += delta.content

    return answer_content.strip()


def save_yaml(content, filename):
    """保存单个接口的YAML用例文件"""
    path = os.path.join(OUTPUT_DIR, filename)

    # 去除 markdown 代码块格式
    content = content.strip()
    if content.startswith("```YAML"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # 简单校验YAML格式合法性
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        print(f"\n❌ 生成的YAML格式非法，文件：{filename}，错误：{e}")
        # 即使格式异常也保存文件，方便人工修正
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 用例生成成功：{path}")


if __name__ == "__main__":
    try:
        # 1. 拉取Swagger接口文档
        swagger_doc = fetch_swagger_doc(SWAGGER_URL)
        # 2. 解析拆分单个接口
        api_list = parse_swagger_paths(swagger_doc)
        if not api_list:
            print("❌ 未解析到有效接口，程序退出")
            exit(0)
        # 3. 批量生成用例
        success_count = 0
        for index, api in enumerate(api_list, 1):
            print(f"\n==================== 进度：{index}/{len(api_list)} ====================")
            try:
                yaml_content = generate_yaml(api["api_doc"])
                if yaml_content:
                    save_yaml(yaml_content, api["file_name"])
                    success_count += 1
                else:
                    print(f"\n❌ 接口 {api['api_name']} 生成内容为空，跳过")
            except Exception as e:
                print(f"\n❌ 接口 {api['api_name']} 生成失败：{str(e)}")
                continue

        print(f"\n🎉 全部执行完成！成功生成 {success_count}/{len(api_list)} 个接口用例")
        print(f"📂 用例保存目录：{os.path.abspath(OUTPUT_DIR)}")

    except Exception as e:
        print(f"\n❌ 程序执行失败：{str(e)}")