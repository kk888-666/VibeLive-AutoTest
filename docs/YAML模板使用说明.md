# YAML 测试用例模板说明

本文档详细介绍如何使用 YAML 格式编写接口自动化测试用例。

## 目录

- [基础结构](#基础结构)
- [用例元信息 (allure)](#用例元信息-allure)
- [请求配置 (request)](#请求配置-request)
- [预期断言 (expected)](#预期断言-expected)
- [变量提取 (extract)](#变量提取-extract)
- [动态参数](#动态参数)
- [完整示例](#完整示例)

---

## 基础结构

每个 YAML 测试用例文件可以包含多个测试用例，使用自定义的键名（如 `login`、`get_list`）作为用例标识：

```yaml
用例名称:
  allure: {}      # 用例元信息
  steps: {}      # 测试步骤
```

---

## 用例元信息 (allure)

配置测试用例的 Allure 报告标签和描述信息：

```yaml
allure:
  title: "测试用例标题"           # 必填，用例标题
  description: "用例描述信息"      # 可选，用例详细描述
  epic: "项目名称"                # 可选，Epic 标签
  feature: "功能模块"             # 可选，Feature 标签
  story: "用户故事"              # 可选，Story 标签
  tag: ["标签1", "标签2"]        # 可选，Tags 标签（数组）
  pytest_mark: "api"             # 可选，Pytest 标记
```

**示例：**

```yaml
allure:
  title: "用户登录接口"
  description: "测试使用正确的账号密码登录系统"
  epic: "InvEntropy"
  feature: "登录模块"
  story: "登录接口"
  tag: ["登录", "接口测试", "Smoke"]
  pytest_mark: "api"
```

---

## 请求配置 (request)

配置 HTTP 请求的详细信息：

```yaml
request:
  method: "GET"          # 必填，请求方法 (GET/POST/PUT/DELETE)
  url: "/api/path"      # 必填，请求路径（不含 base_url）
  headers: {}           # 可选，请求头
  params: {}            # 可选，URL 查询参数
  json: {}              # 可选，请求体（JSON 格式）
```

**method 支持的值：** `GET`、`POST`、`PUT`、`DELETE`、`PATCH`

**headers 示例：**

```yaml
headers:
  Content-Type: "application/json"
  Token: "${extract:token}"  # 使用提取的token
```

**params 示例：**

```yaml
params:
  page: 1
  size: 10
  keyword: "test"
```

**json 示例：**

```yaml
json:
  username: "admin"
  password: "123456"
  userType: "admin"
  timestamp: "${timestamp}"
```

---

## 预期断言 (expected)

配置响应结果的断言规则：

```yaml
expected:
  status_code: 200           # 必填，HTTP 状态码
  response:                  # 必填，响应体断言
    code: 200                # 业务状态码
    msg: "success"           # 提示信息
    data: {}                # 数据字段断言
```

### 响应体断言详解

#### 1. 校验必填字段

```yaml
data:
  required_fields: ["token", "userType", "id"]
```

#### 2. 精确值断言

```yaml
data:
  assert:
    eq:
      userType: "admin"
      status: "active"
    ne:
      code: 500
    contains:
      message: "成功"
```

#### 3. 类型校验

```yaml
data:
  assert:
    type:
      id: int
      name: str
      isActive: bool
      dataList: list
      userInfo: dict
```

#### 4. 列表校验

```yaml
data:
  list_check:
    records:
      length: 10                    # 校验列表长度
      object_required_items:       # 校验列表中对象的必填字段
        - "id"
        - "name"
        - "status"
```

#### 5. 响应码断言

```yaml
response:
  code: 200                        # 精确匹配
  msg: "success"                  # 精确匹配
```

---

## 变量提取 (extract)

从响应数据中提取变量供后续用例使用：

```yaml
extract:
  变量名: "JSONPath 表达式"
```

**示例：**

```yaml
extract:
  token: "$.data.token"           # 提取 token
  userId: "$.data.userId"        # 提取用户ID
  projectId: "$.data.records[0].id"  # 提取列表第一个元素的ID
```

### JSONPath 语法

| 表达式 | 说明 |
|--------|------|
| `$.data.token` | 提取 data 下的 token 字段 |
| `$.data.records[0].id` | 提取 records 数组第一个对象的 id |
| `$.data.records[*].id` | 提取所有 records 的 id（数组） |
| `$.data.userInfo.name` | 提取嵌套对象字段 |

---

## 动态参数

在请求参数中使用动态参数，框架会在运行时自动替换：

| 参数 | 说明 | 示例输出 |
|------|------|----------|
| `${timestamp}` | Unix 时间戳（秒） | `1704067200` |
| `${timestamp_ms}` | Unix 时间戳（毫秒） | `1704067200000` |
| `${date}` | 当前日期 | `2024-01-01` |
| `${datetime}` | 当前日期时间 | `2024-01-01 12:00:00` |
| `${random}` | 6 位随机字符串 | `aB3xYz` |
| `${random_int}` | 6 位随机整数 | `123456` |
| `${uuid}` | UUID | `550e8400-e29b-41d4-a716-446655440000` |
| `${env:VAR_NAME}` | 环境变量 | 读取系统环境变量 |
| `${extract:VAR_NAME}` | 提取的变量 | 读取 extract.yaml 中的值 |

**示例：**

```yaml
json:
  username: "user_${random}"
  timestamp: "${timestamp_ms}"
  orderId: "${uuid}"
```

---

## 完整示例

### 示例 1：POST 登录接口

```yaml
login:
  allure:
    title: "管理员登录"
    description: "测试使用正确的管理员账号密码登录"
    epic: "InvEntropy"
    feature: "登录模块"
    story: "登录接口"
    tag: ["登录", "Smoke"]
    pytest_mark: "api"

  steps:
    request:
      method: "POST"
      url: "/login"
      json:
        username: "admin"
        password: "123456"
        userType: "admin"
        timestamp: "${timestamp_ms}"

    expected:
      status_code: 200
      response:
        code: 200
        msg: "success"
        data:
          required_fields: ["token", "userType"]

    extract:
      token: "$.data.token"
```

### 示例 2：GET 列表接口（带分页）

```yaml
get_projects:
  allure:
    title: "获取项目列表"
    description: "获取待审批项目列表"
    epic: "InvEntropy"
    feature: "管理员模块"
    story: "项目审批"
    tag: ["管理员", "列表"]
    pytest_mark: "api"

  steps:
    request:
      method: "GET"
      url: "/admin/projectsApprovalList"
      headers:
        Token: "${extract:token}"
      params:
        page: 1
        size: 5

    expected:
      status_code: 200
      response:
        code: 200
        msg: "success"
        data:
          required_fields: ["records", "total", "page", "pageSize"]
          list_check:
            records:
              length: 5
              object_required_items:
                - "id"
                - "projectName"
                - "status"
```

### 示例 3：PUT 更新接口

```yaml
update_project_status:
  allure:
    title: "审批项目"
    description: "管理员审批项目通过"
    epic: "InvEntropy"
    feature: "管理员模块"
    story: "项目审批"
    tag: ["管理员", "更新"]
    pytest_mark: "api"

  steps:
    request:
      method: "PUT"
      url: "/admin/approvalProject/${extract:projectId}"
      headers:
        Token: "${extract:token}"
      json:
        status: "approved"
        comment: "审批通过"

    expected:
      status_code: 200
      response:
        code: 200
        msg: "success"
```

---

## 注意事项

1. **YAML 语法**：注意缩进，使用空格而非 Tab
2. **文件位置**：测试数据文件放在 `data/test_data/` 目录下
3. **键名唯一**：同一个 YAML 文件中的用例键名不能重复
4. **动态参数**：字符串类型的值才能使用动态参数占位符
5. **Token 管理**：需要认证的接口在 headers 中添加 `Token: "${extract:token}"`
