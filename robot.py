from config import Config
import requests

class RobotData:
    def __init__(self, msg_data):
        self.msg_type     = msg_data.get('message_type')
        self.user_id      = msg_data.get('user_id')
        self.group_id     = msg_data.get('group_id')
        self.group_name   = msg_data.get('group_name')
        message           = msg_data.get('message')
        self.at_judgement = any(m.get('type') == 'at' and m.get('data', {}).get('qq') == f'{Config.ROBOT_QQ}' for m in message)
        self.msg          = "".join(m['data']['text'] for m in message if m['type'] == 'text')
        sender            = msg_data.get('sender')
        self.user_name    = sender.get('nickname')
        self.user_role    = sender.get('role')
        self.user_level   = sender.get('level')
        self.user_title   = sender.get('title') 
        print("消息载入完成")

class RobotServer:
    def send_msg(self, send_data_obj):
        headers = {"Authorization": f"Bearer {Config.ONEBOT_TOKEN}"}
        if send_data_obj.msg_type == "private":
            url      = f"{Config.ONEBOT_API}/send_private_msg"
            payload  = {"user_id": send_data_obj.user_id, "message": send_data_obj.msg_send_private} 
            response = requests.post(url, json=payload, headers=headers)
        elif send_data_obj.msg_type == "group" and send_data_obj.at_judgement:
            url      = f"{Config.ONEBOT_API}/send_group_msg"
            payload  = {"group_id": send_data_obj.group_id, "message": send_data_obj.msg_send_group} 
            response = requests.post(url, json=payload, headers=headers)
        else:
            print("消息发送失败")