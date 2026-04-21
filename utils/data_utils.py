import csv
import os
import random
import re
import string
import time
import uuid
import yaml
import glob



def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        # collect non-empty rows (skip fully empty lines)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
        # if there's a header, drop the first row
        if rows:
            rows = rows[1:]
        # convert numeric-looking cells to int, leave others as stripped strings
        for r_index, row in enumerate(rows):
            for i in range(len(row)):
                cell = row[i].strip()
                try:
                    rows[r_index][i] = int(cell)
                except ValueError:
                    rows[r_index][i] = cell
        return rows

def read_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        s = f.read()
        data = yaml.safe_load(s)
        return data

def read_yaml_list(file_path):
    return list(read_yaml(file_path).values())

def extract_yaml(key,value):
    with open("config/extract.yaml", 'a+', encoding='utf-8') as f:
        data = {key:value}
        yaml.dump(data,f,allow_unicode=True)

def clear_extract_yaml():
    with open("config/extract.yaml", 'w', encoding='utf-8') as f:
        f.write("")


def resolve_dynamic_params(data):
    """解析动态参数，如 ${timestamp}, ${random}, ${env:VAR} 等"""
    if isinstance(data, dict):
        return {k: resolve_dynamic_params(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [resolve_dynamic_params(item) for item in data]
    elif isinstance(data, str):
        return _replace_params(data)
    return data


def _replace_params(text):
    """替换单个字符串中的动态参数"""
    if not isinstance(text, str):
        return text

    # ${timestamp} - 秒级时间戳
    text = re.sub(r'\$\{timestamp\}', str(int(time.time())), text)
    # ${timestamp_ms} - 毫秒时间戳
    text = re.sub(r'\$\{timestamp_ms\}', str(int(time.time() * 1000)), text)
    # ${date} - 当前日期
    text = re.sub(r'\$\{date\}', time.strftime("%Y-%m-%d"), text)
    # ${datetime} - 当前日期时间
    text = re.sub(r'\$\{datetime\}', time.strftime("%Y-%m-%d %H:%M:%S"), text)
    # ${random} - 6位随机字符串
    text = re.sub(r'\$\{random\}', ''.join(random.choices(string.ascii_letters + string.digits, k=6)), text)
    # ${random_int} - 随机整数
    text = re.sub(r'\$\{random_int\}', str(random.randint(100000, 999999)), text)
    # ${uuid} - UUID
    text = re.sub(r'\$\{uuid\}', str(uuid.uuid4()), text)
    # ${env:VAR} - 环境变量
    text = re.sub(r'\$\{env:([^}]+)\}', lambda m: os.environ.get(m.group(1), ''), text)
    # ${extract:VAR} - 从 extract.yaml 读取变量
    text = re.sub(r'\$\{extract:([^}]+)\}', _get_extract_var, text)

    return text


def _get_extract_var(match):
    """从 extract.yaml 获取变量值"""
    var_name = match.group(1)
    try:
        extract_data = read_yaml("config/extract.yaml")
        return str(extract_data.get(var_name, ''))
    except Exception:
        return ''


def get_testcases(test_dir):
    """读取 test_dir 目录下所有 YAML 测试用例"""
    yaml_files = glob.glob(os.path.join(test_dir, "*.yml"))
    all_data = []
    for yaml_file in yaml_files:
        all_data.extend(read_yaml_list(yaml_file))
    return all_data