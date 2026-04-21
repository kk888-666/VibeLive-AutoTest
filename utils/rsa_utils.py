import random
import string
import json
import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey


class PasswordEncryptor:
    """密码加密类"""
    def __init__(self, public_key=None):
        """
        初始化加密器
        :param public_key: RSA公钥字符串（PEM格式），可选，后续可通过set_public_key设置
        """
        self.publicKey = public_key  # 对应JS的this.publicKey
        self.encryptor = self._init_rsa_encryptor()  # 加密器实例（可替换为自定义加密逻辑）

    def _init_rsa_encryptor(self):
        """初始化RSA加密器"""

        class RSAEncryptor:
            def __init__(self, parent):
                self.parent = parent  # 引用外部类实例

            def encrypt(self, data):
                """RSA公钥加密实现（PKCS#1 v1.5填充）"""
                if not self.parent.publicKey:
                    raise ValueError("公钥未初始化")

                # 将PEM格式公钥字符串解析为公钥对象
                try:
                    public_key = serialization.load_pem_public_key(
                        self.parent.publicKey.encode('utf-8'),
                        backend=default_backend()
                    )
                except InvalidKey:
                    raise ValueError("公钥格式无效（请提供PEM格式的RSA公钥）")

                # 加密（RSA加密长度有限，若数据过长需分段，此处为基础示例）
                encrypted = public_key.encrypt(
                    data.encode('utf-8'),
                    padding.PKCS1v15()
                )
                # 返回Base64编码的加密结果（方便传输，和前端加密结果格式一致）
                import base64
                return base64.b64encode(encrypted).decode('utf-8')

        return RSAEncryptor(self)

    def set_public_key(self, public_key):
        """设置公钥"""
        self.publicKey = public_key

    def generate_random_str(self):
        """生成26位随机字符串（数字+小写字母），复刻JS逻辑"""
        char_set = string.digits + string.ascii_lowercase
        return ''.join(random.choice(char_set) for _ in range(26))

    def encryptPassword(self, password):
        """
        核心加密方法，复刻JS的encryptPassword
        :param password: 待加密的原始密码
        :return: 加密后的字符串
        """
        # 1. 检查公钥是否初始化
        if not self.publicKey:
            raise ValueError("公钥未初始化")

        # 2. 生成26位随机字符串
        random_str = self.generate_random_str()

        # 3. 组装数据并序列化为JSON（和JS的JSON.stringify行为一致）
        data_to_encrypt = {
            "password": password,
            "random": random_str,
            "timestamp": int(time.time() * 1000)  # 毫秒级时间戳，对应JS的Date.now()
        }
        # ensure_ascii=False：避免中文转义；separators：去除多余空格，和JS一致
        json_str = json.dumps(data_to_encrypt, ensure_ascii=False, separators=(',', ':'))

        # 4. 调用加密器加密并返回
        return self.encryptor.encrypt(json_str)


# ------------------- 测试示例 -------------------
if __name__ == "__main__":
    # 示例RSA公钥（替换为你自己的公钥）
    public_key = """
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwfJnZfq7SRJZsuYeB7xv8SVhB6dXU+q3USkoPwkxMefD6Jrg92T+7VjUcmCTyP5W98EEBQ6KvfVvqOXGCR+kimKiYw5vus+tM266+R8AC/89ujJs2onH0N1tTAJYqK+Ny7TDOih+5+jPTeszKDM1L4JLQGvYTJTb99yI024p0/VCelnc0AmTGtIJ86LMFmOZqv8d4GgYPLK4apPsk8Tqgjn5blWr653F2mV14NvKcL7cGshHkgvY26Aoytj6AIkFfabTnenrzmQiyc6k4QkZ8TBSSoqWYOiXGiRN6bo6nnyjRhzX5PLF1QQViS5jPTRDwl4eIulWFsuGxsgZcO8zEQIDAQAB
    -----END PUBLIC KEY-----
    """

    # 初始化加密器
    encryptor = PasswordEncryptor()
    # 设置公钥
    encryptor.set_public_key(public_key)

    # 加密密码
    try:
        encrypted_result = encryptor.encryptPassword("your_password_123")
        print("加密结果：", encrypted_result)
    except Exception as e:
        print("加密失败：", str(e))

