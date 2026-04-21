import pytest
from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list


class TestHmdpAPI:

    @pytest.mark.api
    @pytest.mark.final
    @pytest.mark.parametrize("data", read_yaml_list("data/test_data/music_shop.yaml"))
    def test_get_shop_type_list(self, data):
        """测试获取商铺类型列表接口"""
        # 实例化 ApiRunner，传入 YAML 里的数据
        runner = ApiRunner(data)
        # 执行请求并自动断言
        runner.run()
