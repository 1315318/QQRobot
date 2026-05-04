from database_manager import DatabaseManager
from ai_server        import AiServer
from robot_server     import RobotServer
from config           import Config
from msg_package      import MsgPackage
from ai_tools_list    import AiTools
from flask            import Flask,request
from ai_tools         import Tarot,Tarot_History
import threading
import json
   
app              = Flask(__name__)
database_manager = DatabaseManager()
msg_package      = MsgPackage()
ai_tools         = AiTools()
tarot            = Tarot()
tarot_history    = Tarot_History()
    
def deposit_without_toolcall(robot_server, ai_server):
    database_manager.deposit_chat_history("user", robot_server.user_id, robot_server.group_id, robot_server.msg, "", "")
    database_manager.deposit_chat_history("assistant", robot_server.user_id, robot_server.group_id, ai_server.ai_message['content'], "", "")
    database_manager.deposit_chat_history("tool", robot_server.user_id, robot_server.group_id, "", "", "")

def tools_call(robot_server, ai_server):
    tool = ai_server.ai_message.get("tool_calls")
    print(f"tool: {tool}")
    if tool:
        function_name = tool[0]["function"]["name"]
        function_arguments = tool[0]["function"]["arguments"]
        if function_name == "tarot":
            tarot.tarot_call(robot_server, ai_server)
        if function_name == "tarot_history":
            tarot_history.tarot_history_call(robot_server, ai_server)
    else:
        deposit_without_toolcall(robot_server, ai_server)

def history_takeout(robot_server):
    history_text = database_manager.takeout_chat_history(robot_server.user_id, robot_server.group_id)
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
    return history_list

def first_send(robot_server, ai_server):
    if ai_server.ai_message['content'] == "":
        print("ai返回文本内容为空,跳过发送")
    else:
        robot_server.text = ai_server.ai_message['content']
        if robot_server.msg_type == "group":
            group_msg_type = {"type": "at, text"}
            msg_package.robot_server_msg(group_msg_type, robot_server)
            robot_server.send_group()
        if robot_server.msg_type == "private":
            private_msg_type = {"type": "text"}
            msg_package.robot_server_msg(private_msg_type, robot_server)
            robot_server.send_private()

def main_logic(robot_server):
    if (robot_server.msg_type == "group" and robot_server.at_judgement) or robot_server.msg_type == "private":
        history_list = history_takeout(robot_server)
        if robot_server.msg_type == "group":
            user_text = f"群ID：{robot_server.group_id}，群聊名：{robot_server.group_name}，用户ID：{robot_server.user_id}，用户名：{robot_server.user_name}，\
                群等级：{robot_server.user_level}，群角色：{robot_server.user_role}，群头衔：{robot_server.user_title}，消息内容：{robot_server.msg}"
        if robot_server.msg_type == "private":
            user_text = f"用户ID：{robot_server.user_id}，用户名：{robot_server.user_name}，消息内容：{robot_server.msg}"
        tools = ai_tools.ai_tools()
        ai_server = AiServer(Config.MAIN_ROLE, user_text, history_list, tools, model_type = "deepseek-v4-pro", thinking_type = "disabled")
        ai_server.ai_request()
        first_send(robot_server, ai_server)
        tools_call(robot_server, ai_server)
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