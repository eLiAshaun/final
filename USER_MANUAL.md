# AI-Enhanced GUI Chat System User Manual

## 1. Project Overview

This project is a Python socket-based chat system with a Tkinter graphical user interface. It supports multiple clients connected through a central server. Users can log in, view online users, connect to another user, exchange messages in real time, and use an AI chatbot powered by DeepSeek.

Main features:

- GUI login window
- Real-time message display
- Two-way chat between clients
- Server time command
- Online user list command
- Shakespeare sonnet retrieval
- Chat history search
- DeepSeek chatbot command
- Chatbot personality setting
- Group chat bot interaction with `@bot`

## 2. Requirements

The project has been configured with a virtual environment named `icdsproject`.

Required software:

- Python 3
- PowerShell
- DeepSeek API key
- Project virtual environment: `icdsproject`

Installed Python packages include:

- `openai`
- `requests`
- `ollama`
- `yake`
- `sumy`
- `nltk`
- `textblob`
- `pillow`

## 3. Project Structure

Important files:

```text
final/
├── simple_gui/
│   ├── chat_server.py           # Chat server entry point
│   ├── chat_cmdl_client.py      # GUI client entry point
│   ├── chat_client_class.py     # Client socket wrapper
│   ├── client_state_machine.py  # Client command logic and chatbot integration
│   ├── GUI.py                   # Tkinter GUI
│   ├── chat_utils.py            # Socket protocol helpers
│   └── AllSonnets.txt           # Sonnet data
├── chat_bot_client.py           # Provided chatbot template
├── ai_client.py                 # Provided LLM API example
├── nlp_tools.py                 # NLP helper functions
├── ai_pic2.py                   # AI image generation example
├── FINAL_PROJECT_TODO.md        # Remaining project work guide
└── USER_MANUAL.md               # This manual
```

## 4. Environment Setup

Open PowerShell and go to the project folder:

```powershell
cd "D:\文件\NYU LEarning\作业\大二下\ICDS\final"
```

Activate the virtual environment:

```powershell
.\icdsproject\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\icdsproject\Scripts\Activate.ps1
```

Set the DeepSeek model:

```powershell
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
```

If the DeepSeek API key is not already saved as a Windows user environment variable, set it in the current terminal:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
```

Do not put the real API key in submitted screenshots, slides, or public files.

## 5. Start the Chat System

### 5.1 Start the Server

Open PowerShell terminal 1:

```powershell
cd "D:\文件\NYU LEarning\作业\大二下\ICDS\final"
.\icdsproject\Scripts\Activate.ps1
cd simple_gui
python chat_server.py
```

Expected output:

```text
starting server...
```

Keep this terminal open while using the chat system.

### 5.2 Start Client 1

Open PowerShell terminal 2:

```powershell
cd "D:\文件\NYU LEarning\作业\大二下\ICDS\final"
.\icdsproject\Scripts\Activate.ps1
cd simple_gui
python chat_cmdl_client.py -d 127.0.0.1
```

A login window will appear. Enter a username, for example:

```text
Alice
```

### 5.3 Start Client 2

Open PowerShell terminal 3:

```powershell
cd "D:\文件\NYU LEarning\作业\大二下\ICDS\final"
.\icdsproject\Scripts\Activate.ps1
cd simple_gui
python chat_cmdl_client.py -d 127.0.0.1
```

Enter a different username, for example:

```text
Bob
```

Do not log in two clients with the same username.

## 6. Basic Commands

After logging in, users can type commands into the GUI input box.

### 6.1 Show Online Users

```text
who
```

Expected result:

- The GUI displays all online users.

### 6.2 Show Server Time

```text
time
```

Expected result:

- The GUI displays the current server time.

### 6.3 Connect to Another User

From Alice's GUI, type:

```text
c Bob
```

Expected result:

- Alice connects to Bob.
- Bob receives a connection request.
- Both users enter chatting mode.

### 6.4 Send Chat Messages

After connecting, type any normal message:

```text
hello Bob
```

Expected result:

- The sender sees their own message.
- The receiver sees the incoming message.
- Messages update in real time.

### 6.5 Disconnect from Chat

```text
bye
```

Expected result:

- The current chat connection ends.
- The user returns to the command menu state.

### 6.6 Search Chat History

```text
? hello
```

Expected result:

- The system searches chat history for messages containing `hello`.

### 6.7 Retrieve a Sonnet

```text
p 1
```

Expected result:

- The GUI displays Sonnet 1.

### 6.8 Quit

```text
q
```

Expected result:

- The user leaves the chat system.

## 7. Chatbot Features

The chatbot uses the DeepSeek API. Make sure `DEEPSEEK_API_KEY` is set before starting the client.

### 7.1 Ask the Bot Directly

```text
/bot: introduce yourself in one sentence
```

Expected result:

```text
[You -> Bot] introduce yourself in one sentence
[Bot] ...
```

### 7.2 Set Bot Personality

```text
/personality: a funny but helpful Python tutor
```

Then ask:

```text
/bot: explain socket programming simply
```

Expected result:

- The bot answers using the selected personality.

### 7.3 Use Bot in Group Chat

First connect Alice to Bob:

```text
c Bob
```

Then type:

```text
@bot explain what a socket server does
```

Expected result:

- The sender sees the bot answer.
- The connected peer also receives the bot answer.
- This demonstrates chatbot group interaction.

## 8. Recommended Demo Flow

Use this flow for testing or recording the project video:

1. Start the server.
2. Start Alice client.
3. Start Bob client.
4. Log in through the GUI.
5. Alice types `who`.
6. Alice types `time`.
7. Alice types `p 1`.
8. Alice types `c Bob`.
9. Alice sends `hello Bob`.
10. Bob sends `hi Alice`.
11. Alice types `/bot: introduce yourself in one sentence`.
12. Alice types `/personality: a funny Python tutor`.
13. Alice types `/bot: explain sockets`.
14. Alice types `@bot summarize what a socket server does`.
15. Alice types `bye`.
16. Alice types `? hello`.

## 9. Testing Checklist

### 9.1 Server Test

Pass criteria:

- `chat_server.py` starts without crashing.
- The server prints `starting server...`.
- New client connections appear in the server terminal.

### 9.2 Login Test

Pass criteria:

- GUI login window appears.
- Different usernames can log in.
- Duplicate usernames are rejected.

### 9.3 Messaging Test

Pass criteria:

- Alice can connect to Bob.
- Alice sees her own sent messages.
- Bob sees Alice's messages.
- Bob sees his own sent messages.
- Alice sees Bob's messages.
- Messages do not repeat unexpectedly.

### 9.4 Command Test

Pass criteria:

- `who` displays online users.
- `time` displays server time.
- `p 1` displays a sonnet.
- `? keyword` searches chat history.
- `bye` disconnects the current chat.

### 9.5 Chatbot Test

Pass criteria:

- `/bot:` returns a DeepSeek response.
- `/personality:` changes the bot's response style.
- `@bot` works during a connected chat.
- The connected peer can see the group bot response.

## 10. Troubleshooting

### 10.1 Client Cannot Connect

Check that:

- The server is running.
- The client uses `-d 127.0.0.1`.
- The server terminal has not crashed.
- Port `1112` is not already occupied by an old server process.

### 10.2 PowerShell Cannot Activate Environment

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\icdsproject\Scripts\Activate.ps1
```

### 10.3 Chatbot Says API Key Is Missing

Set the key before starting the client:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
```

Then restart the client.

### 10.4 DeepSeek Model Error

If `deepseek-v4-pro` fails, try:

```powershell
$env:DEEPSEEK_MODEL="deepseek-chat"
```

Then restart the client.

### 10.5 GUI Repeats Messages

This bug has been fixed by resetting the displayed system message after insertion. If it appears again, check the message rendering logic in `simple_gui/GUI.py`.

## 11. Notes for Presentation

Mention these technical points during the video:

- The server handles multiple socket clients.
- Clients communicate with the server using JSON messages.
- The GUI is built with Tkinter.
- A background thread checks for incoming messages.
- DeepSeek is used as the chatbot backend.
- The bot keeps short conversation context and supports custom personality.
- `@bot` demonstrates group chat interaction.
- Pi-mono was used as an AI coding assistant during development and debugging.

## 12. Known Limitations

- The GUI layout is simple and focuses on functionality rather than visual design.
- The chatbot requires internet access and a valid DeepSeek API key.
- The current chatbot context is stored on the client side.
- Image generation, summary, keywords, and sentiment analysis are planned bonus features if not yet implemented.
