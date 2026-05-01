class MsgPackage:
    def robot_server_msg(self, msg_type_dict, robot_server):
        msg_type = msg_type_dict.get('type')
        robot_server.msg_list = []
        if "image" in msg_type:
            robot_server.msg_list.append({"type": "image", "data": {"file": robot_server.image_path}})
        if "at" in msg_type:
            robot_server.msg_list.append({"type": "at", "data": {"qq": robot_server.user_id}})
        if "text" in msg_type:
            robot_server.msg_list.append({"type": "text", "data": {"text": robot_server.text}})
