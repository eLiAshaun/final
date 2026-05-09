# AI-Enhanced GUI Chat System

这是一个 Python socket 聊天系统项目，主要可运行版本在 `simple_gui/`。它支持多客户端登录、在线用户列表、点对点聊天、聊天记录搜索、莎士比亚十四行诗查询，以及基于 DeepSeek/OpenAI-compatible API 的聊天机器人功能。

## 项目结构

```text
final/
├── start_chat_system.py        # 一键启动服务端和客户端
├── simple_gui/                 # 推荐运行的 GUI 聊天系统
│   ├── chat_server.py          # 服务端入口
│   ├── chat_cmdl_client.py     # GUI 客户端入口
│   ├── chat_client_class.py    # 客户端 socket 封装
│   ├── client_state_machine.py # 客户端命令、聊天状态、DeepSeek bot 逻辑
│   ├── GUI.py                  # Tkinter 图形界面
│   ├── chat_utils.py           # socket 协议和菜单常量
│   ├── nlp_tools.py            # 关键词提取和摘要工具
│   └── AllSonnets.txt          # 十四行诗数据
├── docs/                       # README、用户手册、项目说明和 PDF/DOCX 文档
└── unused_code/                # 本地未跟踪归档；不提交到 Git
```

## 环境准备

需要 Python 3。GUI 使用 `tkinter`，通常随 Python 自带。聊天机器人和 NLP 示例需要额外包。

建议在项目根目录创建并启用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install openai requests ollama yake sumy nltk textblob pillow customtkinter
```

Windows PowerShell 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install openai requests ollama yake sumy nltk textblob pillow customtkinter
```

如果只运行基础聊天 GUI，主要需要 Python 标准库和 `openai`；如果不用 bot，连 `openai` 也可以暂时不配置。

## 启动聊天系统

推荐使用 `simple_gui/` 版本。

### 一键启动推荐方式

在项目根目录运行：

```bash
python start_chat_system.py
```

这个脚本会自动打开 1 个服务端终端，并直接启动 2 个 Tkinter 客户端登录窗口。它会等服务端端口 `1112` 准备好后再启动客户端；如果服务端已经在运行，它不会再重复启动一个服务端。两个客户端弹出登录窗口后，分别输入不同用户名，例如 `Alice` 和 `Bob`。

如果想打开更多客户端：

```bash
python start_chat_system.py --clients 3
```

### 手动启动方式

### 1. 启动服务端

打开第一个终端：

```bash
cd simple_gui
python chat_server.py
```

看到类似输出说明服务端已启动：

```text
starting server...
```

服务端默认监听端口是 `1112`，配置在 `simple_gui/chat_utils.py`。

### 2. 启动第一个客户端

打开第二个终端：

```bash
cd simple_gui
python chat_cmdl_client.py -d 127.0.0.1
```

弹出登录窗口后输入一个用户名，例如：

```text
Alice
```

### 3. 启动第二个客户端

打开第三个终端：

```bash
cd simple_gui
python chat_cmdl_client.py -d 127.0.0.1
```

输入不同用户名，例如：

```text
Bob
```

注意：不能让两个客户端使用同一个用户名。

## GUI 内可用命令

登录后，可以在 GUI 底部输入框输入命令或聊天内容，也可以使用右侧 `GUI Actions` 面板按钮打开对应输入窗口。

| 命令/按钮 | 作用 |
| --- | --- |
| `who` / Online Users | 查看当前在线用户 |
| `time` / Server Time | 查看服务端时间 |
| `c Bob` / Connect | 连接到用户名为 Bob 的用户 |
| `hello` | 在已连接状态下发送普通聊天消息，并显示情感标签 |
| `bye` / Disconnect | 断开当前聊天连接 |
| `? hello` / Search Logs | 搜索聊天历史中包含 `hello` 的记录 |
| `p 1` / Sonnet | 查询第 1 首莎士比亚十四行诗 |
| `/summary` / Summary | 总结本地聊天记录 |
| `/keywords` / Keywords | 提取本地聊天关键词 |
| `/nlp:on` / DeepSeek NLP | 开启 DeepSeek 版情感分析、摘要和关键词提取 |
| `/nlp:off` / DeepSeek NLP | 关闭 DeepSeek NLP，回到本地 fallback |
| `/archive` / Archive | 查看当前用户的本地 JSONL 聊天存档路径 |
| `/aipic: a robot coding` / AI Picture | 生成并保存 AI 图片，GUI 会尝试预览 |
| `q` / Quit | 退出聊天系统 |

## DeepSeek 聊天机器人功能

`simple_gui/client_state_machine.py` 使用 OpenAI Python SDK 连接 DeepSeek 的 OpenAI-compatible API。启动客户端前设置环境变量：

macOS / Linux：

```bash
export DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
export DEEPSEEK_MODEL="deepseek-v4-pro"
```

Windows PowerShell：

```powershell
$env:DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
```

如果 `deepseek-v4-pro` 不可用，可以改成：

```bash
export DEEPSEEK_MODEL="deepseek-chat"
```

机器人命令：

| 命令 | 作用 |
| --- | --- |
| `/bot: introduce yourself` | 直接向机器人提问 |
| `/chatbots` | 查看可选 chatbot 角色 |
| `/chatbot: Python Tutor` | 选择一个预设 chatbot 角色，也可用 GUI 下拉框选择 |
| `/personality: a funny Python tutor` | 自定义机器人回答风格 |
| `@bot explain sockets` | 在连接聊天时让机器人参与对话，bot 回复也会发给对方 |

不要把真实 API key 写进代码、截图、报告或提交记录里。

## 推荐演示流程

1. 启动 `simple_gui/chat_server.py`。
2. 启动 Alice 客户端并登录。
3. 启动 Bob 客户端并登录。
4. Alice 输入 `who` 查看在线用户。
5. Alice 输入 `time` 查看服务端时间。
6. Alice 输入 `p 1` 查询十四行诗。
7. Alice 输入 `c Bob` 连接 Bob。
8. Alice 和 Bob 互相发送普通消息。
9. Alice 用右侧下拉框选择 `Python Tutor`，或输入 `/chatbot: Python Tutor`。
10. Alice 输入 `/bot: explain socket programming simply`。
11. Alice 输入 `/personality: a funny Python tutor`。
12. Alice 输入 `@bot summarize what a socket server does`。
13. Alice 输入 `/summary`、`/keywords` 和 `/aipic: a cute robot helping students debug Python code`。
14. Alice 输入 `bye` 断开聊天。
15. Alice 输入 `? hello` 搜索历史。

## 辅助模块

### `simple_gui/nlp_tools.py`

提供两个函数：

- `extract_keywords_yake(messages)`：从消息列表提取关键词。
- `summarize_with_sumy(messages)`：从消息列表生成简短摘要。

运行内置 demo：

```bash
cd simple_gui
python nlp_tools.py
```

主 GUI 已经通过 Summary 和 Keywords 按钮接入这两个函数，也可以直接输入 `/summary` 和 `/keywords`。

原始参考版本和独立 AI 示例脚本已经移动到 `unused_code/`，并通过 `.gitignore` 取消 Git 跟踪。

## 常见问题

### 客户端连不上服务端

- 确认服务端终端还在运行。
- 确认客户端使用 `python chat_cmdl_client.py -d 127.0.0.1`。
- 确认没有其他程序占用端口 `1112`。
- 如果服务端崩溃，重新启动服务端，再重新登录客户端。

### GUI 登录后没反应

- 不要重复使用同一个用户名。
- 先启动服务端，再启动客户端。
- 在 `simple_gui/` 目录下运行脚本，避免找不到 `AllSonnets.txt` 或本地模块。

### Bot 提示缺少 API key

设置 `DEEPSEEK_API_KEY` 后重新启动客户端。环境变量必须在启动客户端之前设置。

### Bot 模型报错

把 `DEEPSEEK_MODEL` 从 `deepseek-v4-pro` 改成 `deepseek-chat` 后重新启动客户端。

## 备注

- `simple_gui/` 是主要可演示版本。
- `docs/` 集中保存说明文档、手册、任务清单和课程资料。
- `unused_code/` 是本地归档目录，已加入 `.gitignore`，不会再被 Git 跟踪。
- `__MACOSX/`、`.DS_Store`、`__pycache__/` 和 `*.idx` 是系统、Python 或运行时生成文件，已从 Git 跟踪中移除。
- 更详细的测试和 presentation checklist 可以看 `docs/USER_MANUAL.md` 和 `docs/FINAL_PROJECT_TODO.md`。
