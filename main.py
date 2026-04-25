from flask    import Flask,request
from database import DatabaseManager
from ai       import AiData,AiServer
from robot    import RobotData,RobotServer
import random
   
app              = Flask(__name__)
robot_server     = RobotServer()
ai_server        = AiServer()
database_manager = DatabaseManager()

def tarot(msg_obj):
    tarot_text = database_manager.takeout("tarot_content", "card_name, card_text, card_path")
    tarot_list = []
    tarot_list.extend([{"card_name": card_name, "card_text": card_text, "card_path": card_path} for card_name, card_text, card_path in tarot_text])
    result_tarot = random.choice(tarot_list)
    msg_obj.card_name = result_tarot["card_name"]
    msg_obj.card_text = result_tarot["card_text"]
    msg_obj.card_path = result_tarot["card_path"]           
    msg_obj.msg_file  = {"type": "image", "data": {"file": msg_obj.card_path}}
    msg_obj.msg_at    = {"type": "at", "data": {"qq": msg_obj.user_id}}
    msg_obj.msg_text  = {"type": "text", "data": {"text": f"这是你的塔罗牌: \n{msg_obj.card_name}\n{msg_obj.card_text}\n"}}
    return None

@app.route('/',methods = ['POST'])
def receive():
    msg_data = request.json
    if not msg_data:
        return "nodata"
    msg_obj = RobotData(msg_data)    
    if (msg_obj.msg_type == "group" and msg_obj.at_judgement) or msg_obj.msg_type == "private":
        user_id  = msg_obj.user_id
        group_id = msg_obj.group_id
        if msg_obj.group_id:
            history_text = database_manager.takeout("history", "role, text", "user_id = ? AND group_id = ?", (user_id, group_id))

        else:
            history_text = database_manager.takeout("history", "role, text", "user_id = ? AND group_id IS NULL", (user_id,))
        history_list = []
        history_list.extend([{"content": text, "role": role} for role, text in history_text])
        model_type  = "deepseek-reasoner"
        system_text = "你的是ai小助手Kiriko,根据群友的消息做出回复,尽量是可爱女孩风格,可以使用颜文字,在可爱聊天的同时,必须优先通过调用工具来提供服务,不要自己编造结果"
        user_text   = f"群ID：{msg_obj.group_id}，群聊名：{msg_obj.group_name}，用户ID：{msg_obj.user_id}，用户名：{msg_obj.user_name}，群等级：{msg_obj.user_level}，群角色：{msg_obj.user_role}，群头衔：{msg_obj.user_title}，消息内容：{msg_obj.msg}"
        function_parameter     = {"type": "object", "properties": {}, "required": []}
        function_tarot         = {"name": "tarot", "description": "当用户表示想要进行占卜,算命或询问运势以及想要抽取塔罗牌时,才调用此函数", "parameters": function_parameter}
        function_tarot_history = {"name": "tarot_history", "description": "当用户表示想要知道自己占卜,算命或询问运势结果或塔罗牌抽取的历史记录,才调用此函数", "parameters": function_parameter}
        tool_tarot             = {"type": "function", "function": function_tarot}
        tool_tarot_history     = {"type": "function", "function": function_tarot_history}
        tools                  = [tool_tarot, tool_tarot_history]
        ai_data_obj = AiData(model_type, system_text, user_text, history_list, tools)
        ai_server.ai_deepseek(ai_data_obj)
        if ai_data_obj.response_text == "":
            print("ai返回文本内容为空,跳过发送")
        else:
            msg_obj.msg_send_group   = [{"type": "at", "data": {"qq": msg_obj.user_id}},{"type": "text", "data": {"text": ai_data_obj.response_text}}]
            msg_obj.msg_send_private = {"type": "text", "data": {"text": ai_data_obj.response_text}}
            robot_server.send_msg(msg_obj)
        tool = ai_data_obj.original_list["choices"][0]["message"].get("tool_calls")
        print(f"tool: {tool}")
        if tool:
            function_name = tool[0]["function"]["name"]
            function_arguments = tool[0]["function"]["arguments"]
            if function_name == "tarot":
                tarot(msg_obj)
                model_type   = "deepseek-chat"
                system_text  = "你是一个ai牌面解读助手Kiriko,你需要根据上传的塔罗牌牌名和牌面信息对牌面进行解释并对用户做出提醒,语气尽量是可爱女孩的风格,可以使用颜文字"
                tarot_text   = f"抽牌结果:{msg_obj.card_name},牌面解释:{msg_obj.card_text}"
                ai_tarot_obj = AiData(model_type, system_text, tarot_text, history_list = [], tools = None)
                ai_server.ai_deepseek(ai_tarot_obj)
                msg_obj.msg_ai_explian = {"type": "text", "data": {"text": ai_tarot_obj.response_text}} 
                msg_obj.msg_send_private = [msg_obj.msg_file, msg_obj.msg_text, msg_obj.msg_ai_explian]
                msg_obj.msg_send_group = [msg_obj.msg_file, msg_obj.msg_at, msg_obj.msg_text, msg_obj.msg_ai_explian]
                robot_server.send_msg(msg_obj)
                database_manager.deposit("tarot_history", "(user_id, card_name)", "(?, ?)", (msg_obj.user_id, msg_obj.card_name))
                database_manager.deposit("history", "(role, user_id, group_id, text)", "(?, ?, ?, ?)", ("user", msg_obj.user_id, msg_obj.group_id, msg_obj.msg))
                airesponse_role = ai_data_obj.deposite_text['role']
                airesponse_text = ai_data_obj.deposite_text['content']
                database_manager.deposit("history", "(role, user_id, group_id, text)", "(?, ?, ?, ?)", (airesponse_role, msg_obj.user_id, msg_obj.group_id, airesponse_text))
            
            if function_name == "tarot_history":
                tarot_history = database_manager.takeout("tarot_history", "card_name, timestamp", "user_id = ?", (user_id,))
                msg_obj.history_text = "\n".join([f"·{car_name} {timestamp}" for car_name, timestamp in tarot_history])
                msg_obj.msg_send_group   = [{"type": "at", "data": {"qq": msg_obj.user_id}}, {"type": "text", "data": {"text": f"这是你的塔罗牌记录:\n{msg_obj.history_text}"}}]
                msg_obj.msg_send_private = {"type": "text", "data": {"text": f"这是你的塔罗牌记录:\n{msg_obj.history_text}"}}
                robot_server.send_msg(msg_obj)
        else:
            database_manager.deposit("history", "(role, user_id, group_id, text)", "(?, ?, ?, ?)", ("user", msg_obj.user_id, msg_obj.group_id, msg_obj.msg))
            airesponse_role = ai_data_obj.deposite_text['role']
            airesponse_text = ai_data_obj.deposite_text['content']
            database_manager.deposit("history", "(role, user_id, group_id, text)", "(?, ?, ?, ?)", (airesponse_role, msg_obj.user_id, msg_obj.group_id, airesponse_text))
            
    else:
        print("无关消息")
    return "ok"

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 5000) 
    