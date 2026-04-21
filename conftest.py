import pytest
import logging

logger = logging.getLogger(__name__)

def pytest_sessionstart(session):
    logger.info("初始化配置中...测试会话即将开始...")
    logger.info("初始化配置完成,测试会话开始!")




