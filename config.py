from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    ROBOT_QQ       = os.getenv("ROBOT_QQ")
    ONEBOT_API     = os.getenv("ONEBOT_API")
    ONEBOT_TOKEN   = os.getenv("ONEBOT_TOKEN")
    DEEPSEEK_API   = os.getenv("DEEPSEEK_API")
    DEEPSEEK_TOKEN = os.getenv("DEEPSEEK_TOKEN")