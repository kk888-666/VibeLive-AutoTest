import pytest

from common.api_utils import ApiRunner
from utils.data_utils import read_yaml_list


@pytest.mark.usefixtures("get_user_token")
class TestTryAPI:

    @pytest.mark.a
    @pytest.mark.parametrize("data",read_yaml_list("data/ai_testcases/user/test_get_homes_userInfo.yml"))
    def test_try(self, data,get_user_token):
        """AI生成的测试用例"""
        runner = ApiRunner(data,get_user_token)
        runner.run()


