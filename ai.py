from config import Config
import json
import requests

class AiData:
    def __init__(self, model_type, system_text, user_text, history_list, tools):
        self.ai_message   = {"messages": [{"content": system_text, "role": "system"}, *history_list, {"content": user_text, "role": "user"}]}
        self.ai_model     = {"model": model_type}
        self.ai_tool      = {"tools": tools, "tool_choice": "auto"}
        self.ai_parameter = {"response_format": {"type": "text"}, "max_tokens": 8000, "frequency_penalty": 0, "presence_penalty": 0, "temperature": 0, "top_p": 0.9}
        self.ai_function  = {"stop": None, "stream": False, "stream_options": None, "logprobs": False, "top_logprobs": None}
        
class AiServer:
    def ai_deepseek(self, ai_data_obj):
        payload  = json.dumps(ai_data_obj.ai_message | ai_data_obj.ai_model | ai_data_obj.ai_tool | ai_data_obj.ai_parameter | ai_data_obj.ai_function)             
        headers  = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'Bearer {Config.DEEPSEEK_TOKEN}'}
        response = requests.request("POST", Config.DEEPSEEK_API, headers = headers, data = payload)
        ai_data_obj.original_list     = response.json()
        ai_data_obj.deposite_text     = ai_data_obj.original_list['choices'][0]['message']
        ai_data_obj.reasoning_content = ai_data_obj.deposite_text.get('reasoning_content', '')
        ai_data_obj.response_text     = ai_data_obj.deposite_text['content']
        print(ai_data_obj.reasoning_content)
        print(ai_data_obj.response_text)