"""Swagger/OpenAPI 文档解析工具类"""

import requests
from requests.exceptions import RequestException, JSONDecodeError
from urllib.parse import unquote

# Swagger 配置
SWAGGER_URL = "http://localhost:8080/v3/api-docs"
REQUEST_TIMEOUT = 30
# 过滤配置：只生成指定请求方法的接口，空列表=不限制
ALLOW_METHODS = ["get", "post", "put", "delete", "patch"]
# 排除配置：跳过指定路径的接口（支持前缀匹配）
EXCLUDE_PATH_PREFIX = ["/actuator", "/error", "/favicon.ico"]


def fetch_swagger_doc(swagger_url: str = SWAGGER_URL, timeout: int = REQUEST_TIMEOUT) -> dict:
    """
    拉取Swagger/OpenAPI接口文档原始JSON数据

    :param swagger_url: Swagger文档地址
    :param timeout: 请求超时时间（秒）
    :return: Swagger文档JSON数据
    :raises RuntimeError: 拉取或解析失败时抛出
    """
    print(f"正在拉取接口文档：{swagger_url}")
    try:
        response = requests.get(swagger_url, timeout=timeout)
        response.raise_for_status()
        swagger_json = response.json()
        print(f"✅ 接口文档拉取成功，文档版本：{swagger_json.get('openapi', swagger_json.get('swagger', '未知'))}")
        print(f"📌 总接口数量：{len(swagger_json.get('paths', {}))} 个")
        return swagger_json
    except RequestException as e:
        raise RuntimeError(f"接口文档拉取失败！请检查服务是否启动、URL是否正确：{str(e)}") from e
    except JSONDecodeError as e:
        raise RuntimeError(f"接口文档解析失败！URL返回的不是合法JSON格式：{str(e)}") from e


def parse_swagger_paths(
    swagger_doc: dict,
    allow_methods: list = ALLOW_METHODS,
    exclude_prefix: list = EXCLUDE_PATH_PREFIX
) -> list:
    """
    解析OpenAPI文档，拆分单个接口信息

    :param swagger_doc: Swagger文档JSON数据
    :param allow_methods: 允许的请求方法列表
    :param exclude_prefix: 排除的路径前缀列表
    :return: 解析后的接口列表，每个元素包含单个接口的完整信息
    """
    paths = swagger_doc.get("paths", {})
    # 全局组件（请求/响应模型，用于AI理解字段含义）
    components = swagger_doc.get("components", {})
    api_list = []

    for path, path_info in paths.items():
        # 跳过排除的接口路径
        if any(path.startswith(prefix) for prefix in exclude_prefix):
            print(f"⏭️  跳过排除接口：{path}")
            continue

        # 遍历接口的请求方法（GET/POST/PUT等）
        for method, api_info in path_info.items():
            # 过滤不支持的请求方法
            if allow_methods and method.lower() not in allow_methods:
                continue

            # 解析接口基础信息
            api_name = api_info.get("summary", api_info.get("operationId", f"{method}_{path.replace('/', '_')}"))
            # 清理文件名非法字符
            file_name = f"test_{method.lower()}{unquote(path).replace('/', '_').replace('{', '').replace('}', '')}.yml"

            # 组装单个接口的完整文档，给AI用
            single_api_doc = {
                "接口名称": api_name,
                "接口地址": path,
                "请求方法": method.upper(),
                "接口描述": api_info.get("description", "无"),
                "请求参数": api_info.get("parameters", []),
                "请求体": api_info.get("requestBody", {}),
                "响应参数": api_info.get("responses", {}),
                "全局数据模型": components
            }

            api_list.append({
                "api_name": api_name,
                "file_name": file_name,
                "api_doc": single_api_doc
            })
            print(f"📦 解析接口：{method.upper()} {path} -> {api_name}")

    print(f"✅ 接口解析完成，共 {len(api_list)} 个有效接口待生成")
    return api_list
