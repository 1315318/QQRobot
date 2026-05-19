from config import Config
import requests

class RobotServer:
    def __init__(self, msg_data):
        self.msg_type     = msg_data.get('message_type')
        self.user_id      = msg_data.get('user_id')
        self.group_id     = msg_data.get('group_id')
        self.group_name   = msg_data.get('group_name')
        message           = msg_data.get('message') or []
        self.at_judgement = any(m.get('type') == 'at' and m.get('data', {}).get('qq') == f'{Config.ROBOT_QQ}' for m in message)
        self.msg          = "".join(m['data']['text'] for m in message if m['type'] == 'text')
        sender            = msg_data.get('sender')
        self.user_name    = sender.get('nickname')
        self.user_role    = sender.get('role')
        self.user_level   = sender.get('level')
        self.user_title   = sender.get('title') 
        print("消息载入完成")

    def send_private(self):
        headers = {"Authorization": f"Bearer {Config.ONEBOT_TOKEN}"}
        url      = f"{Config.ONEBOT_API}/send_private_msg"
        payload  = {"user_id": self.user_id, "message": self.msg_list} 
        response = requests.post(url, json=payload, headers=headers)
    
    def send_group(self):
        headers = {"Authorization": f"Bearer {Config.ONEBOT_TOKEN}"}
        url      = f"{Config.ONEBOT_API}/send_group_msg"
        payload  = {"group_id": self.group_id, "message": self.msg_list} 
        response = requests.post(url, json=payload, headers=headers)