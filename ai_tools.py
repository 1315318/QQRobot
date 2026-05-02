class AiTools():
    def ai_tools(self):
        function_parameter     = {"type": "object", "properties": {}, "required": []}
        function_tarot         = {"name": "tarot", "description": "当用户表示想要进行占卜,算命或询问运势以及想要抽取塔罗牌时,才调用此函数", "parameters": function_parameter}
        function_tarot_history = {"name": "tarot_history", "description": "当用户表示想要知道自己占卜,算命或询问运势结果或塔罗牌抽取的历史记录,才调用此函数", "parameters": function_parameter}
        tool_tarot             = {"type": "function", "function": function_tarot}
        tool_tarot_history     = {"type": "function", "function": function_tarot_history}
        tools                  = [tool_tarot, tool_tarot_history]
        return tools