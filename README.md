# VibeLive-AutoTest 智能接口自动化测试框架

### 技术栈：Python + Pytest + Requests + YAML + Jinja2 + Allure + GitHub Actions(CI/CD) + OpenAI API

面向**“跃动现场”独立音乐演出服务平台**打造的轻量级接口自动化智能测试框架。核心解决高并发抢票、演出检索与用户鉴权等关键业务链路中，手工回归效率低、接口耦合度高的问题。打通从代码提交到测试报告产出的 CI/CD 全流程闭环，显著提升回归效率与交易链路的质量稳定性。

## 核心特性
✅ **底层重构与稳定增强**：对 Requests 进行二次封装，实现统一请求入口、日志追踪、失败重试及全局异常处理，提升复杂接口链路的执行稳定性与可维护性。  
✅ **多环境无侵入适配**：结合 `python-dotenv` 实现多环境配置解耦与无侵入切换，保障开发、测试及线上环境一致性。  
✅ **动态数据驱动**：采用 YAML 管理用例与测试数据，通过 Jinja2 实现跨接口参数动态透传（如 Token、订单 ID、场次 ID），显著降低用例耦合度。  
✅ **核心链路深度覆盖**：覆盖“跃动现场”演出查询、用户鉴权及早鸟票下单等 40+ 核心接口。通过自动化回归模拟并发场景，有效定位并拦截超卖、Redis 缓存穿透及分布式锁失效等高风险问题。  
✅ **AI 智能化赋能**：接入 OpenAI API 对接口文档进行语义解析与结构化提取，辅助生成边界值及异常场景测试数据，将用例复用率提升至 90%+。  
✅ **CI/CD 全自动化**：基于 GitHub Actions 搭建流水线，代码提交自动触发环境初始化、依赖安装、全量回归及可视化报告部署。**将整体回归耗时从约 4 小时大幅压缩至 20 分钟以内。** 


## 效果展示
Allure 报告查看：[GitHub Pages](https://kk888-666.github.io/VibeLive-AutoTest/)  
 ![img/img.png](img/img.png)

CI/CD 工作流：  
 ![img/workflow.png](img/workflow.png)

YAML 测试用例示例：
[YAML模板使用说明](docs/YAML%E6%A8%A1%E6%9D%BF%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.md)

### 快速开始
#### 克隆项目
```bash
git clone https://github.com/kk888-666/VibeLive-AutoTest.git
```
#### 安装依赖
```bash
pip install -r requirements.txt
```
#### 配置.env文件
```text
主要是设置base_url和环境变量((common/config.py))，支持多环境切换
```
#### 运行测试
###### 方法一：(命令行启动,需要手动生成Allure报告)
```bash
pytest
```
###### 方法二：(运行启动文件，会自动生成Allure报告)
```bash
python3 start.py
```
