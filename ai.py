from config import Config
import json
import requests

class AiServer:
    def __init__(self, system_text, user_text, history_list = None, tools = None, model_type = "deepseek-v4-flash", thinking_type = "disabled"):
        if history_list is None:
            history_list = []
        self.system_text   = system_text
        self.user_text     = user_text
        self.model_type    = model_type
        self.thinking_type = thinking_type 
        self.history_list  = history_list
        self.tools         = tools        
    
    def ai_request(self):
        request_dict = {
        "messages": [{"content": self.system_text, "role": "system"}, *self.history_list, {"content": self.user_text, "role": "user"}], 
        "model": self.model_type, "thinking": {"type": self.thinking_type},
        "tools": self.tools, "tool_choice": "auto",
        "response_format": {"type": "text"}, "max_tokens": 8000, "frequency_penalty": 0, "presence_penalty": 0, "temperature": 0, "top_p": 0.9,
        "stop": None, "stream": False, "stream_options": None, "logprobs": False, "top_logprobs": None
        }
        payload  = json.dumps(request_dict)             
        headers  = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'Bearer {Config.DEEPSEEK_TOKEN}'}
        response = requests.request("POST", Config.DEEPSEEK_API, headers = headers, data = payload)
        print(response)
        ai_message = response.json()['choices'][0]['message']
        self.ai_message = ai_message


