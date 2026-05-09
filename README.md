# AI-Enhanced GUI Chat System

这是一个 Python socket 聊天系统项目，主要可运行版本在 `simple_gui/`。它支持多客户端登录、在线用户列表、点对点聊天、聊天记录搜索、莎士比亚十四行诗查询，以及基于 DeepSeek/OpenAI-compatible API 的聊天机器人功能。

## 作者与来源信息

我根据仓库里的 Git 记录、文件头注释和文档元数据整理了作者信息：

- 当前 Git 仓库只有 1 个提交作者：`eLiAshaun <zs3129@nyu.edu>`。
- 最新提交：`6dff10f icdsprojectforuse`，提交时间为 `2026-05-04`。
- PDF/DOCX 的 macOS 元数据没有显示作者字段。
- 部分代码文件保留了原始模板作者标注：
  - `simple_gui/chat_server.py` 和 `Chat_System_Full/chat_server.py`：`alina, zzhang`
  - `simple_gui/client_state_machine.py` 和 `Chat_System_Full/client_state_machine.py`：`zhengzhang`
  - `simple_gui/GUI.py`：`bing`
  - `simple_gui/indexer.py`、`simple_gui/indexer_good.py`、`simple_gui/roman2num.py` 以及 `Chat_System_Full/` 中对应文件：`zzhang`
  - `simple_gui/chat_group.py` 和 `Chat_System_Full/chat_group.py`：`zhengzhang`
- 这个 `README.md` 是本次根据现有仓库内容整理出来的使用说明；仓库里原有代码不是本次新写的。

## 项目结构

```text
final/
├── simple_gui/                 # 推荐运行的 GUI 聊天系统
│   ├── chat_server.py          # 服务端入口
│   ├── chat_cmdl_client.py     # GUI 客户端入口
│   ├── chat_client_class.py    # 客户端 socket 封装
│   ├── client_state_machine.py # 客户端命令、聊天状态、DeepSeek bot 逻辑
│   ├── GUI.py                  # Tkinter 图形界面
│   ├── chat_utils.py           # socket 协议和菜单常量
│   └── AllSonnets.txt          # 十四行诗数据
├── Chat_System_Full/           # 原始/参考版本，功能结构与 simple_gui 类似
├── ai_client.py                # 自定义 OpenAI-compatible LLM/VLM API 示例
├── chat_bot_client.py          # Ollama / OpenAI-compatible chatbot 示例
├── nlp_tools.py                # 关键词提取和摘要工具
├── ai_pic2.py                  # AI 图片下载示例
├── USER_MANUAL.md              # 更详细的英文用户手册
├── FINAL_PROJECT_TODO.md       # 项目剩余任务与 demo 清单
└── README.md                   # 当前说明文件
```

## 环境准备

需要 Python 3。GUI 使用 `tkinter`，通常随 Python 自带。聊天机器人和 NLP 示例需要额外包。

建议在项目根目录创建并启用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install openai requests ollama yake sumy nltk textblob pillow
```

Windows PowerShell 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install openai requests ollama yake sumy nltk textblob pillow
```

如果只运行基础聊天 GUI，主要需要 Python 标准库和 `openai`；如果不用 bot，连 `openai` 也可以暂时不配置。

## 启动聊天系统

推荐使用 `simple_gui/` 版本。

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

登录后，在 GUI 底部输入框输入命令或聊天内容。

| 命令 | 作用 |
| --- | --- |
| `who` | 查看当前在线用户 |
| `time` | 查看服务端时间 |
| `c Bob` | 连接到用户名为 Bob 的用户 |
| `hello` | 在已连接状态下发送普通聊天消息 |
| `bye` | 断开当前聊天连接 |
| `? hello` | 搜索聊天历史中包含 `hello` 的记录 |
| `p 1` | 查询第 1 首莎士比亚十四行诗 |
| `q` | 退出聊天系统 |

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
| `/personality: a funny Python tutor` | 修改机器人回答风格 |
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
9. Alice 输入 `/bot: explain socket programming simply`。
10. Alice 输入 `/personality: a funny Python tutor`。
11. Alice 输入 `@bot summarize what a socket server does`。
12. Alice 输入 `bye` 断开聊天。
13. Alice 输入 `? hello` 搜索历史。

## 其他脚本怎么用

### `nlp_tools.py`

提供两个函数：

- `extract_keywords_yake(messages)`：从消息列表提取关键词。
- `summarize_with_sumy(messages)`：从消息列表生成简短摘要。

运行内置 demo：

```bash
python nlp_tools.py
```

如果要把它接进 GUI，可以参考 `FINAL_PROJECT_TODO.md` 中 `/keywords` 和 `/summary` 的实现步骤。

### `chat_bot_client.py`

这是一个独立 bot 示例，默认连接本地 Ollama：

```bash
python chat_bot_client.py
```

使用前需要本地 Ollama 服务已启动，并且有对应模型，例如 `phi3:mini`。文件里也保留了切换到 OpenAI-compatible API 的示例代码。

### `ai_client.py`

这是自定义 OpenAI-compatible LLM/VLM API 调用示例：

```bash
python ai_client.py
```

它依赖文件中配置的自定义服务地址和模型路径；如果你没有对应服务器，这个脚本会无法连接。它不是主聊天系统必须运行的部分。

### `ai_pic2.py`

这是图片生成/下载示例：

```bash
python ai_pic2.py
```

运行后会把图片保存为 `cat.png`。这个脚本目前是独立示例，还没有接进 GUI。

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
- `Chat_System_Full/` 更像原始参考版本。
- `__MACOSX/`、`.DS_Store`、`__pycache__/` 是系统或 Python 生成文件，正常使用时不用管。
- 更详细的测试和 presentation checklist 可以看 `USER_MANUAL.md` 和 `FINAL_PROJECT_TODO.md`。
