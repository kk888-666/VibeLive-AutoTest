from typing import List

import allure


class AllureUtils:

    def allure_load(self,conf):
        """
                动态加载Allure配置
                :param conf: Allure配置字典
                """
        # 基础字段映射：{配置键: allure动态方法}
        basic_mapping = {
            "title": allure.dynamic.title,
            "description": allure.dynamic.description,
            "epic": allure.dynamic.epic,
            "feature": allure.dynamic.feature,
            "story": allure.dynamic.story,
            "severity": allure.dynamic.severity,
            "tag": allure.dynamic.tag
        }

        # 批量处理基础字段
        for key, method in basic_mapping.items():
            value = conf.get(key)
            #value 不能是list
            if value and not isinstance(value, list):
                method(value)
            else:
                if isinstance(value, list):
                    for item in value:
                        method(item)





