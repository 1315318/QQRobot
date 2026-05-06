```markdown
# 🤖 QQRobot – 基于 LLBot 的 QQ 聊天机器人

一个运行在 **LLBot** 框架上的 QQ 机器人，内置 **DeepSeek 大模型**对话能力，并可**抽取塔罗牌**并进行牌面解读。  
机器人采用可爱女孩风格（Kiriko），支持颜文字，让聊天更有温度。

---

## ✨ 主要功能

- 💬 **智能对话**：接入 DeepSeek API，可自由设定人设与回复风格
- 🃏 **塔罗牌占卜**：发送特定指令抽取塔罗牌，自动调用 DeepSeek 解读牌面
- 🐳 **Docker 一键部署**：借助 LLBot 官方 Docker 脚本，快速搭建运行环境
- 🔐 **安全可控**：所有 API Key 及配置均通过 `.env` 文件管理

---

## 📋 前置要求

- 一台可运行 Docker 的机器（Linux / Windows WSL2 / macOS）
- 一个可以登录的 QQ 账号（用于机器人本体）
- 获取 [DeepSeek API Key](https://platform.deepseek.com/api_keys)

---

## 🚀 部署步骤

### 1. 克隆本项目

```bash
git clone https://github.com/1315318/QQRobot.git
cd QQRobot
```

### 2. 配置 `.env` 文件

在项目根目录创建 `.env` 文件，并根据你的信息填写：

```ini
ROBOT_QQ         = "你的机器人QQ号"
ONEBOT_API       = "http://llbot:3000"
ONEBOT_TOKEN     = "你的LLBot Token"
DEEPSEEK_API     = "https://api.deepseek.com/chat/completions"
DEEPSEEK_TOKEN   = "你的DeepSeek API Key"
MAIN_ROLE        = "你是聊天小助手Kiriko，根据对方的消息做出回复,尽量是可爱女孩风格，可以使用颜文字，在聊天的同时，可以通过调用工具来提供服务，用户明显希望调用工具时必须调用，禁止自己编造内容"
TAROT_ROLE       = "你是牌面解读助手Kiriko，你需要根据上传的塔罗牌牌名和牌面信息对牌面进行解释并对用户做出提醒，语气尽量是可爱女孩的风格，可以使用颜文字"
```

> **注意**：请妥善保管 `.env` 文件，不要提交到公开仓库（建议已加入 `.gitignore`）。

### 3. 安装 LLBot 框架（Docker 方式）

执行官方一键安装脚本，会自动拉取镜像并生成 `llbot-docker` 目录：

```bash
curl -fsSL https://gh-proxy.com/https://raw.githubusercontent.com/LLOneBot/LuckyLilliaBot/refs/heads/main/script/install-llbot-docker.sh -o llbot-docker.sh && \
chmod u+x ./llbot-docker.sh && \
./llbot-docker.sh
```

执行后，当前目录下会多出一个 `llbot-docker/` 文件夹。

### 4. 将本项目文件复制到 LLBot 目录，并替换 compose 文件

```bash
# 复制所有机器人代码到 llbot-docker 目录（覆盖原有的 docker-compose.yaml）
cp -r ./* ./llbot-docker/
# 或者手动将本项目中的 docker-compose.yaml 替换 llbot-docker 目录下的同名文件
```

> 此步骤中，本项目的 `docker-compose.yaml` 已经预先配置好了机器人服务与 LLBot 服务的组合。  
> 如果你没有修改过 compose 文件，直接覆盖即可。

### 5. 启动容器

进入 LLBot 目录并启动所有服务：

```bash
cd llbot-docker
docker-compose up -d
```

### 6. 查看日志 & 扫码登录 QQ

```bash
# 实时查看日志
docker-compose logs -f

# 打开浏览器，进入 LLBot 控制台
# 地址：http://localhost:3080/#dashboard
```

使用手机 QQ 扫描页面中的二维码完成机器人账号登录。  
登录成功后，机器人便会开始工作。

---

## 🧩 使用说明

- **对话**：直接 @机器人 或私聊它，机器人会以 DeepSeek 回复（角色为 `MAIN_ROLE`）。
- **塔罗牌**：发送指令（例如 `/tarot` 或 `抽牌`），机器人会随机抽取一张塔罗牌并调用 DeepSeek 按 `TAROT_ROLE` 进行解读。
- **指令定制**：你可以在代码中修改触发词和塔罗牌库。

---

## 🛠 常见问题

### Q1：扫码后提示“版本过低”或无法登录？
- 尝试更换 QQ 账号，或使用较旧的 QQ 版本（非最新版）。某些新账号或新版本可能受风控影响。

### Q2：机器人没有回复？
- 检查 DeepSeek API Key 是否有效，额度是否充足。
- 使用 `docker-compose logs -f` 查看错误日志，常见原因如网络超时、Token 错误等。

### Q3：如何更新 LLBot 或本项目？
- 更新 LLBot：在 `llbot-docker` 目录下执行 `docker-compose pull` 然后 `docker-compose up -d`。
- 更新本项目：重新 `git pull`，然后重复上述步骤 4~5。

### Q4：OneBot Token 在哪里获取？
- 首次启动 LLBot 后，会在日志中打印出随机生成的 Token，或者你可以自行在 `llbot-docker/config/onebot.yaml` 中设置。

---

## 📁 项目结构（简要）

```
QQRobot/
├── .env                   # 环境变量（不提交）
├── docker-compose.yaml    # 整合了 robot 与 llbot 服务的编排文件
├── main.py                # 机器人主程序（需要你自己编写）
├── tarot.py               # 塔罗牌抽取逻辑
└── README.md              # 你现在看到的文档
```

> **注意**：本仓库中未包含具体的业务代码，请根据 llbot 框架的 API 自行实现 `main.py` 和 `tarot.py`，或参考示例代码。

---

## 🙏 致谢

- [LLOneBot / LuckyLilliaBot](https://github.com/LLOneBot/LuckyLilliaBot) – 强大的 QQ 机器人框架
- [DeepSeek](https://www.deepseek.com/) – 高性价比的大语言模型 API

如果本项目对你有帮助，欢迎 Star ⭐ 或提出 Issue～
```
