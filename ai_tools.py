from database_manager import DatabaseManager
from msg_package      import MsgPackage
from config           import Config
import random
import json

database_manager = DatabaseManager()
msg_package      = MsgPackage()

class Tarot:
    def tarot(self):
        tarot_text = database_manager.takeout("tarot_content", "card_name, card_text, card_path")
        tarot_list = []
        tarot_list.extend([{"card_name": card_name,"card_text":card_text, "card_path": card_path} for card_name, card_text, card_path in tarot_text])
        tarot_result = random.choice(tarot_list)
        return tarot_result

    def tarot_ai_call(self, ai_server, tarot_result):
        ai_server.model_type    = "deepseek-v4-flash"
        ai_server.thinking_type = "disabled"
        ai_server.system_text   = Config.TAROT_ROLE
        ai_server.user_text     = f"抽牌结果：{tarot_result['card_name']}，牌面解释：{tarot_result['card_text']}"
        ai_server.ai_request()
    
    def deposit_tarot_call_history(self, robot_server, ai_server, tarot_result):
        database_manager.deposit_tarot_history(robot_server.user_id, tarot_result['card_name'])
        database_manager.deposit_chat_history("user", robot_server.user_id, robot_server.group_id, robot_server.msg, "", "")
        database_manager.deposit_chat_history("assistant", robot_server.user_id, robot_server.group_id, ai_server.ai_message['content'], json.dumps(ai_server.airesponse_tool_calls), "")
        database_manager.deposit_chat_history("tool", robot_server.user_id, robot_server.group_id,  ai_server.user_text, "", ai_server.airesponse_tool_id)
    
    def tarot_send(self, robot_server, ai_server):
        robot_server.msg_list.append({"type": "text", "data": {"text": ai_server.ai_message['content']}})
        if robot_server.msg_type == "group":
            robot_server.send_group()
        if robot_server.msg_type == "private":
            robot_server.send_private()
    
    def tarot_call(self, robot_server, ai_server):
        tarot_result = self.tarot()
        robot_server.image_path = tarot_result["card_path"]           
        tarot_msg_type          = {"type": "image, at, text"}
        robot_server.text       = f"这是你的塔罗牌:\n{tarot_result['card_name']}\n{tarot_result['card_text']}\n"
        msg_package.robot_server_msg(tarot_msg_type, robot_server)
        ai_server.airesponse_tool_id      = ai_server.ai_message.get("tool_calls")[0].get('id')
        ai_server.airesponse_tool_calls   = ai_server.ai_message.get("tool_calls")
        self.tarot_ai_call(ai_server, tarot_result)
        self.tarot_send(robot_server, ai_server)
        self.deposit_tarot_call_history(robot_server, ai_server, tarot_result)

class Tarot_History:
    def deposit_tarot_history_call(self, robot_server, ai_server):
        database_manager.deposit_chat_history("user", robot_server.user_id, robot_server.group_id, robot_server.msg, "", "")
        database_manager.deposit_chat_history("assistant", robot_server.user_id, robot_server.group_id, ai_server.ai_message['content'], json.dumps(ai_server.airesponse_tool_calls), "")
        database_manager.deposit_chat_history("tool", robot_server.user_id, robot_server.group_id, ai_server.user_text, "", ai_server.airesponse_tool_id)

    def tarot_history_send(self, robot_server):
        if robot_server.msg_type == "group":
            group_msg_type   = {"type": "at, text"}
            msg_package.robot_server_msg(group_msg_type, robot_server)
            robot_server.send_group()
        if robot_server.msg_type == "private":
            private_msg_type = {"type": "text"}
            msg_package.robot_server_msg(private_msg_type, robot_server)
            robot_server.send_private()

    def tarot_history_call(self, robot_server, ai_server):
        tarot_history = database_manager.takeout_tarot_history(robot_server.user_id)
        robot_server.history_text = "\n".join([f"{timestamp}\n·{car_name}" for car_name, timestamp in tarot_history])
        robot_server.text = f"这是你的塔罗牌记录:\n{robot_server.history_text}"
        self.tarot_history_send(robot_server)
        ai_server.airesponse_tool_id      = ai_server.ai_message.get("tool_calls")[0].get('id')
        ai_server.airesponse_tool_calls   = ai_server.ai_message.get("tool_calls")
        ai_server.user_text = robot_server.text
        self.deposit_tarot_history_call(robot_server, ai_server)