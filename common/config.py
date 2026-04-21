from dotenv import load_dotenv
import os


# 加载环境变量
load_dotenv()

PUBLIC_KEY = os.getenv('PUBLIC_KEY')

# url配置
SERVER_URL = os.getenv("SERVER_URL")

# ai_key
API_KEY = os.getenv("API_KEY")

# Ai接口URL
AI_URL = os.getenv("AI_URL")


