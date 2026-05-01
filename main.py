from flask    import Flask,request
from database import DatabaseManager
from ai       import AiServer
from robot    import RobotServer
from config   import Config
import random
import threading
import json
   
app              = Flask(__name__)
database_manager = DatabaseManager()

def tarot(msg_obj):
    tarot_text = database_manager.takeout("tarot_content", "card_name, card_text, card_path")
    tarot_list = []
    tarot_list.extend([{"card_name": card_name,"card_text":card_text, "card_path": card_path} for card_name, card_text, card_path in tarot_text])
    result_tarot = random.choice(tarot_list)
    msg_obj.card_name = result_tarot["card_name"]
    msg_obj.card_text = result_tarot["card_text"]
    msg_obj.card_path = result_tarot["card_path"]           
    msg_obj.msg_file  = {"type": "image", "data": {"file": msg_obj.card_path}}
    msg_obj.msg_at    = {"type": "at", "data": {"qq": msg_obj.user_id}}
    msg_obj.msg_text  = {"type": "text", "data": {"text": f"这是你的塔罗牌: \n{msg_obj.card_name}\n{msg_obj.card_text}\n"}}
    return None

def main_logic(robot_server):
    if (robot_server.msg_type == "group" and robot_server.at_judgement) or robot_server.msg_type == "private":
        user_id  = robot_server.user_id
        group_id = robot_server.group_id
        if robot_server.group_id:
            history_text = database_manager.takeout("history", "role, content, tool_calls, tool_call_id", "user_id = ? AND group_id = ?", (user_id, group_id))
        else:
            history_text = database_manager.takeout("history", "role, content, tool_calls, tool_call_id", "user_id = ? AND group_id IS NULL", (user_id,))
        history_list = []
        for role, content, tool_calls, tool_call_id in history_text:
            if role == "user":
                history_list.extend([{"role": role, "content": content}])
            if role == "assistant" :
                if tool_calls:
                    history_list.extend([{"role": role, "content": content, "tool_calls": json.loads(tool_calls)}])
                else:
                    history_list.extend([{"role": role, "content": content}])
            if role == "tool" and tool_call_id:
                history_list.extend([{"role": role, "content": content, "tool_call_id": tool_call_id}])
        print(history_list)
        user_text   = f"群ID：{robot_server.group_id}，群聊名：{robot_server.group_name}，用户ID：{robot_server.user_id}，用户名：{robot_server.user_name}，群等级：{robot_server.user_level}，群角色：{robot_server.user_role}，群头衔：{robot_server.user_title}，消息内容：{robot_server.msg}"
        function_parameter     = {"type": "object", "properties": {}, "required": []}
        function_tarot         = {"name": "tarot", "description": "当用户表示想要进行占卜,算命或询问运势以及想要抽取塔罗牌时,才调用此函数", "parameters": function_parameter}
        function_tarot_history = {"name": "tarot_history", "description": "当用户表示想要知道自己占卜,算命或询问运势结果或塔罗牌抽取的历史记录,才调用此函数", "parameters": function_parameter}
        tool_tarot             = {"type": "function", "function": function_tarot}
        tool_tarot_history     = {"type": "function", "function": function_tarot_history}
        tools                  = [tool_tarot, tool_tarot_history]
        ai_server = AiServer(Config.MAIN_ROLE, user_text, history_list, tools, model_type = "deepseek-v4-pro", thinking_type = "disabled")
        ai_server.ai_request()
        if ai_server.ai_message['content'] == "":
            print("ai返回文本内容为空,跳过发送")
        else:
            robot_server.msg_send_group   = [{"type": "at", "data": {"qq": robot_server.user_id}},{"type": "text", "data": {"text": ai_server.ai_message['content']}}]
            robot_server.msg_send_private = {"type": "text", "data": {"text": ai_server.ai_message['content']}}
            robot_server.send_msg(robot_server)
        tool = ai_server.ai_message.get("tool_calls")
        print(f"tool: {tool}")
        if tool:
            function_name = tool[0]["function"]["name"]
            function_arguments = tool[0]["function"]["arguments"]
            if function_name == "tarot":
                tarot(robot_server)
                ai_server.model_type    = "deepseek-v4-flash"
                ai_server.thinking_type = "disabled"
                ai_server.system_text   = Config.TAROT_ROLE
                ai_server.user_text     = f"抽牌结果：{robot_server.card_name}，牌面解释：{robot_server.card_text}"
                airesponse_tool_id      = ai_server.ai_message.get("tool_calls")[0].get('id')
                airesponse_tool_calls   = ai_server.ai_message.get("tool_calls")
                ai_server.ai_request()
                robot_server.msg_ai_explian   = {"type": "text", "data": {"text": ai_server.ai_message['content']}} 
                robot_server.msg_send_private = [robot_server.msg_file, robot_server.msg_text, robot_server.msg_ai_explian]
                robot_server.msg_send_group   = [robot_server.msg_file, robot_server.msg_at, robot_server.msg_text, robot_server.msg_ai_explian]
                robot_server.send_msg(robot_server)
                database_manager.deposit("tarot_history", "(user_id, card_name)", "(?, ?)", (robot_server.user_id, robot_server.card_name))
                database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", ("user", robot_server.user_id, robot_server.group_id, robot_server.msg, "", ""))
                airesponse_role = ai_server.ai_message['role']
                airesponse_text = ai_server.ai_message['content']
                database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", (airesponse_role, robot_server.user_id, robot_server.group_id, airesponse_text, json.dumps(airesponse_tool_calls), ""))
                database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", ("tool", robot_server.user_id, robot_server.group_id,  ai_server.user_text, "", airesponse_tool_id))
            if function_name == "tarot_history":
                tarot_history = database_manager.takeout("tarot_history", "card_name, timestamp", "user_id = ?", (user_id,))
                robot_server.history_text = "\n".join([f"{timestamp}\n·{car_name}" for car_name, timestamp in tarot_history])
                robot_server.msg_send_group   = [{"type": "at", "data": {"qq": robot_server.user_id}}, {"type": "text", "data": {"text": f"这是你的塔罗牌记录:\n{robot_server.history_text}"}}]
                robot_server.msg_send_private = {"type": "text", "data": {"text": f"这是你的塔罗牌记录:\n{robot_server.history_text}"}}
                robot_server.send_msg(robot_server)
        else:
            database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", ("user", robot_server.user_id, robot_server.group_id, robot_server.msg, "", ""))
            airesponse_role = ai_server.ai_message['role']
            airesponse_text = ai_server.ai_message['content']
            database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", (airesponse_role, robot_server.user_id, robot_server.group_id, airesponse_text, "", ""))
            database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", ("tool", robot_server.user_id, robot_server.group_id, "", "", ""))
    else:
        print("无关消息")

@app.route('/',methods = ['POST'])
def receive():
    msg_data = request.json
    if not msg_data:
        return "nodata"
    robot_server = RobotServer(msg_data)
    task = threading.Thread(target = main_logic, args = (robot_server,))
    task.start()
    return "Success"    

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 5000) 
