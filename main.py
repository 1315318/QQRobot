from database_manager import DatabaseManager
from ai_server        import AiServer
from robot_server     import RobotServer
from config           import Config
from msg_package      import MsgPackage
from ai_tools         import AiTools
from flask            import Flask,request
import random
import threading
import json
   
app              = Flask(__name__)
database_manager = DatabaseManager()
msg_package      = MsgPackage()
ai_tools         = AiTools()

def tarot():
    tarot_text = database_manager.takeout("tarot_content", "card_name, card_text, card_path")
    tarot_list = []
    tarot_list.extend([{"card_name": card_name,"card_text":card_text, "card_path": card_path} for card_name, card_text, card_path in tarot_text])
    tarot_result = random.choice(tarot_list)
    return tarot_result

def tarot_ai_call(ai_server, tarot_result):
    ai_server.model_type    = "deepseek-v4-flash"
    ai_server.thinking_type = "disabled"
    ai_server.system_text   = Config.TAROT_ROLE
    ai_server.user_text     = f"抽牌结果：{tarot_result['card_name']}，牌面解释：{tarot_result['card_text']}"
    ai_server.ai_request()

def deposit_tarot_history(robot_server, ai_server, tarot_result):
    database_manager.deposit("tarot_history", "(user_id, card_name)", "(?, ?)", (robot_server.user_id, tarot_result['card_name']))
    database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", ("user", robot_server.user_id, robot_server.group_id, robot_server.msg, "", ""))
    airesponse_role = ai_server.ai_message['role']
    airesponse_text = ai_server.ai_message['content']
    database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", (airesponse_role, robot_server.user_id, robot_server.group_id, airesponse_text, json.dumps(ai_server.airesponse_tool_calls), ""))
    database_manager.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", ("tool", robot_server.user_id, robot_server.group_id,  ai_server.user_text, "", ai_server.airesponse_tool_id))

def tarot_call(robot_server, ai_server):
    tarot_result = tarot()
    robot_server.image_path = tarot_result["card_path"]           
    tarot_msg_type          = {"type": "image, at, text"}
    robot_server.text       = f"这是你的塔罗牌:\n{tarot_result['card_name']}\n{tarot_result['card_text']}\n"
    msg_package.robot_server_msg(tarot_msg_type, robot_server)
    ai_server.airesponse_tool_id      = ai_server.ai_message.get("tool_calls")[0].get('id')
    ai_server.airesponse_tool_calls   = ai_server.ai_message.get("tool_calls")
    tarot_ai_call(ai_server, tarot_result)
    robot_server.msg_list.append({"type": "text", "data": {"text": ai_server.ai_message['content']}})
    if robot_server.msg_type == "group":
        robot_server.send_group(robot_server)
    if robot_server.msg_type == "private":
        robot_server.send_private(robot_server)
    deposit_tarot_history(robot_server, ai_server, tarot_result)
    
def tarot_history_call(robot_server):
    tarot_history = database_manager.takeout("tarot_history", "card_name, timestamp", "user_id = ?", (robot_server.user_id,))
    robot_server.history_text = "\n".join([f"{timestamp}\n·{car_name}" for car_name, timestamp in tarot_history])
    robot_server.text = f"这是你的塔罗牌记录:\n{robot_server.history_text}"
    if robot_server.msg_type == "group":
                group_msg_type   = {"type": "at, text"}
                msg_package.robot_server_msg(group_msg_type, robot_server)
                robot_server.send_group(robot_server)
    if robot_server.msg_type == "private":
                private_msg_type = {"type": "text"}
                msg_package.robot_server_msg(private_msg_type, robot_server)
                robot_server.send_private(robot_server)

def main_logic(robot_server):
    if (robot_server.msg_type == "group" and robot_server.at_judgement) or robot_server.msg_type == "private":
        if robot_server.group_id:
            history_text = database_manager.takeout("history", "role, content, tool_calls, tool_call_id", "user_id = ? AND group_id = ?", (robot_server.user_id, robot_server.group_id))
        else:
            history_text = database_manager.takeout("history", "role, content, tool_calls, tool_call_id", "user_id = ? AND group_id IS NULL", (robot_server.user_id,))
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
        tools = ai_tools.ai_tools()
        ai_server = AiServer(Config.MAIN_ROLE, user_text, history_list, tools, model_type = "deepseek-v4-pro", thinking_type = "disabled")
        ai_server.ai_request()
        if ai_server.ai_message['content'] == "":
            print("ai返回文本内容为空,跳过发送")
        else:
            robot_server.text   = ai_server.ai_message['content']
            if robot_server.msg_type == "group":
                group_msg_type   = {"type": "at, text"}
                msg_package.robot_server_msg(group_msg_type, robot_server)
                robot_server.send_group(robot_server)
            if robot_server.msg_type == "private":
                private_msg_type = {"type": "text"}
                msg_package.robot_server_msg(private_msg_type, robot_server)
                robot_server.send_private(robot_server)
        tool = ai_server.ai_message.get("tool_calls")
        print(f"tool: {tool}")
        if tool:
            function_name = tool[0]["function"]["name"]
            function_arguments = tool[0]["function"]["arguments"]
            if function_name == "tarot":
                tarot_call(robot_server, ai_server)
            if function_name == "tarot_history":
                tarot_history_call(robot_server)
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