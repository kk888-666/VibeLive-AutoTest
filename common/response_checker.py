import re
import logging

logger = logging.getLogger("Hsyuan")

TYPE_MAP = {
    "str": str, "int": int, "float": float,
    "bool": bool, "list": list, "dict": dict,
}


def _get_nested_value(data, key_path: str):
    """点号路径取值: 'a.b.c' => data['a']['b']['c']"""
    current = data
    for key in key_path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            current = current[int(key)]
        else:
            raise KeyError(f"路径 '{key_path}' 在 '{key}' 处中断")
    return current


def _run_assertions(data: dict, assertions: dict, path: str, errors: list):
    """执行断言"""
    for way, kv in assertions.items():
        if not kv:
            continue
        for key, expected in kv.items():
            full = f"{path}.{key}"
            try:
                actual = _get_nested_value(data, key)
            except KeyError:
                errors.append(f"[{way}] 字段不存在: {full}")
                continue
            try:
                match way:
                    case "eq":
                        assert actual == expected, f"[eq] {full}: 期望 {expected!r}, 实际 {actual!r}"
                    case "contains":
                        assert expected in str(actual), f"[contains] {full}: 期望包含 {expected!r}"
                    case "regex":
                        assert re.match(expected, str(actual)), f"[regex] {full}: 不匹配 {expected!r}"
                    case "type":
                        t = TYPE_MAP.get(expected)
                        assert t and isinstance(actual, t), f"[type] {full}: 期望 {expected}, 实际 {type(actual).__name__}"
                    case "gt":
                        assert actual > expected, f"[gt] {full}: 期望 > {expected}, 实际 {actual}"
                    case "gte":
                        assert actual >= expected, f"[gte] {full}: 期望 >= {expected}, 实际 {actual}"
                    case "lt":
                        assert actual < expected, f"[lt] {full}: 期望 < {expected}, 实际 {actual}"
                    case "lte":
                        assert actual <= expected, f"[lte] {full}: 期望 <= {expected}, 实际 {actual}"
            except AssertionError as e:
                errors.append(str(e))


def _check_list(data: dict, list_config: dict, path: str, errors: list):
    """列表校验 - 只做最实用的三件事"""
    for list_key, config in list_config.items():
        full = f"{path}.{list_key}"
        try:
            actual_list = _get_nested_value(data, list_key)
        except KeyError:
            errors.append(f"列表字段不存在: {full}")
            continue

        if not isinstance(actual_list, list):
            errors.append(f"{full} 不是 list")
            continue

        # 1. 长度校验
        if "length" in config:
            if len(actual_list) != config["length"]:
                errors.append(f"[length] {full}: 期望 {config['length']}, 实际 {len(actual_list)}")

        # 2. 每个元素的必需字段
        if "object_required_items" in config:
            for idx, item in enumerate(actual_list):
                for field in config["object_required_items"]:
                    if field and field not in item:
                        errors.append(f"缺少字段: {full}[{idx}].{field}")

        # 3. 每个元素的断言
        if "every_item_assert" in config:
            for idx, item in enumerate(actual_list):
                _run_assertions(item, config["every_item_assert"], f"{full}[{idx}]", errors)

def _check_list_data(data: dict,list_config: dict, path: str, errors: list):
    """列表校验 - 只做最实用的三件事"""
    if list_config:
        config = list_config
        full = f"{path}"
        actual_list = data

        if not isinstance(actual_list, list):
            errors.append(f"{full} 不是 list")

        # 1. 长度校验
        if "length" in config:
            if len(actual_list) != config["length"]:
                errors.append(f"[length] {full}: 期望 {config['length']}, 实际 {len(actual_list)}")

        # 2. 每个元素的必需字段
        if "object_required_items" in config:
            for idx, item in enumerate(actual_list):
                for field in config["object_required_items"]:
                    if field and field not in item:
                        errors.append(f"缺少字段: {full}[{idx}].{field}")

        # 3. 每个元素的断言
        if "every_item_assert" in config:
            for idx, item in enumerate(actual_list):
                _run_assertions(item, config["every_item_assert"], f"{full}[{idx}]", errors)


class ResponseChecker:
    def __init__(self, resp):
        self.resp = resp

    def check_response(self, expected=None):
        if expected is None:
            logger.info("未设置预期结果，跳过断言")
            return

        if self.resp is None:
            raise AssertionError("请求失败，响应对象为空")

        errors = []

        # 处理非JSON响应的错误
        try:
            json_data = self.resp.json()
        except Exception:
            json_data = {}

        logger.info(f"resp.json: {json_data}")

        # 1. HTTP 状态码
        if "status_code" in expected:
            if self.resp.status_code != expected["status_code"]:
                errors.append(f"状态码: 期望 {expected['status_code']}, 实际 {self.resp.status_code}")

        # 2. 顶层字段 (code, msg)
        resp_config = expected.get("response", {})
        for k, v in resp_config.items():
            if k == "data":
                continue
            if k not in json_data:
                errors.append(f"缺少响应字段: {k}")
            elif json_data[k] != v:
                errors.append(f"响应字段: 期望 {k}={v!r}, 实际 {json_data[k]!r}")

        # 3. data 层
        data_config = resp_config.get("data")
        if data_config and "data" in json_data:
            data = json_data["data"]

            if "required_fields" in data_config:
                for field in data_config["required_fields"]:
                    if field and field not in data:
                        errors.append(f"缺少字段: data.{field}")

            if "assert" in data_config:
                _run_assertions(data, data_config["assert"], "data", errors)

            if "list_check" in data_config:
                _check_list(data, data_config["list_check"], "data", errors)

            if "list_data" in data_config:
                _check_list_data(data,data_config["list_data"], "data", errors)


        # 4. 结果
        if errors:
            msg = f"共 {len(errors)} 个断言失败:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(msg)
            raise AssertionError(msg)
        else:
            logger.info("所有断言通过")