# Final Project Remaining Work Guide

## Current Status

- The basic GUI chat system runs with a socket server and multiple Tkinter clients.
- The GUI repeated-message bug has been fixed in `simple_gui/GUI.py`.
- DeepSeek chatbot commands have been added in `simple_gui/client_state_machine.py`.
- Python syntax checks pass for the edited chat system files.
- The live DeepSeek API test has passed with `deepseek-v4-pro`.

## 1. Run the Current Chat System

### 1.1 Start the Server

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

Keep this terminal open.

### 1.2 Start Client Alice

Open PowerShell terminal 2:

```powershell
cd "D:\文件\NYU LEarning\作业\大二下\ICDS\final"
.\icdsproject\Scripts\Activate.ps1
$env:DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
cd simple_gui
python chat_cmdl_client.py -d 127.0.0.1
```

In the login window, enter:

```text
Alice
```

### 1.3 Start Client Bob

Open PowerShell terminal 3:

```powershell
cd "D:\文件\NYU LEarning\作业\大二下\ICDS\final"
.\icdsproject\Scripts\Activate.ps1
$env:DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
cd simple_gui
python chat_cmdl_client.py -d 127.0.0.1
```

In the login window, enter:

```text
Bob
```

## 2. Test Required GUI Features

### 2.1 Test Login

- Alice and Bob should each open a GUI chat window after login.
- Do not reuse the same username in two clients.

### 2.2 Test Online User List

In Alice's input box, type:

```text
who
```

Expected result:

- The GUI displays the current online users.
- Alice and Bob should both appear.

### 2.3 Test Server Time

In Alice's input box, type:

```text
time
```

Expected result:

- The GUI displays the server time.

### 2.4 Test Poem Command

In Alice's input box, type:

```text
p 1
```

Expected result:

- The GUI displays Sonnet 1.

### 2.5 Test Peer Connection

In Alice's input box, type:

```text
c Bob
```

Expected result:

- Alice enters chatting mode with Bob.
- Bob receives a connection request and enters chatting mode.

### 2.6 Test Two-Way Chat Display

In Alice's input box, type:

```text
hello Bob
```

In Bob's input box, type:

```text
hi Alice
```

Expected result:

- Alice sees her own sent message and Bob's reply.
- Bob sees Alice's message and his own sent message.
- Messages should not repeatedly duplicate in the GUI.

### 2.7 Test Disconnect

In Alice's input box, type:

```text
bye
```

Expected result:

- Alice returns to the menu state.
- Bob receives a disconnect message.

### 2.8 Test Chat Search

After sending several messages, type:

```text
? hello
```

Expected result:

- Matching chat history messages are displayed.

## 3. Test Chatbot Features

### 3.1 Test Direct Bot Question

Before starting the client, make sure this is set in the client terminal:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
```

Then, after logging in, type:

```text
/bot: introduce yourself in one sentence
```

Expected result:

- The GUI displays `[You -> Bot] ...`.
- The GUI displays `[Bot] ...` with a DeepSeek response.

If `deepseek-v4-pro` fails with a model error, restart the client with:

```powershell
$env:DEEPSEEK_MODEL="deepseek-chat"
```

### 3.2 Test Bot Personality

In the GUI, type:

```text
/personality: a funny but helpful Python tutor
```

Then type:

```text
/bot: explain sockets
```

Expected result:

- The bot responds in the selected personality.

### 3.3 Test Group Chat Bot Interaction

First connect Alice to Bob:

```text
c Bob
```

Then in Alice's input box, type:

```text
@bot explain what a socket server does
```

Expected result:

- Alice sees the bot answer.
- Bob receives the bot answer in the chat window.
- This can be used for the chatbot group interaction bonus demo.

## 4. Add Bonus Feature 1: Summary and Keywords

### 4.1 Goal

Add commands that analyze real chat history:

```text
/summary
/keywords
```

### 4.2 Files to Modify

- `simple_gui/client_state_machine.py`
- Possibly `simple_gui/chat_server.py` if the server should store shared room history.
- Existing helper file: `simple_gui/nlp_tools.py`

### 4.3 Implementation Steps

1. Add `self.chat_history = []` to `ClientSM.__init__`.
2. Whenever the user sends a normal message, append the text to `self.chat_history`.
3. Whenever a peer message arrives, append the peer's message text to `self.chat_history`.
4. Import `extract_keywords_yake` and `summarize_with_sumy` from `simple_gui/nlp_tools.py`.
5. Add a `/keywords` branch in both logged-in and chatting states.
6. Add a `/summary` branch in both logged-in and chatting states.
7. Display results directly in the GUI.
8. Test with at least 5 normal chat messages before using `/summary` or `/keywords`.

### 4.4 Demo Script

Send these messages between Alice and Bob:

```text
We are building a GUI chat system.
The project uses sockets and Tkinter.
The chatbot is powered by DeepSeek.
We also want summary and keyword extraction.
This feature analyzes real chat history.
```

Then test:

```text
/keywords
/summary
```

## 5. Add Bonus Feature 2: Sentiment Analysis

### 5.1 Goal

Show emotion labels for messages:

```text
Positive
Neutral
Negative
```

### 5.2 Files to Modify

- `simple_gui/client_state_machine.py`

### 5.3 Implementation Steps

1. Add a helper function that takes message text and returns sentiment.
2. Use `textblob.TextBlob(message).sentiment.polarity`.
3. If polarity is greater than `0.1`, label it `Positive`.
4. If polarity is less than `-0.1`, label it `Negative`.
5. Otherwise label it `Neutral`.
6. When displaying a sent or received message, append the sentiment label.
7. Test with clearly positive, negative, and neutral messages.

### 5.4 Demo Messages

```text
I love this chat system!
This bug is terrible and frustrating.
The server is running on port 1112.
```

Expected labels:

- Positive
- Negative
- Neutral

## 6. Add Bonus Feature 3: AI Picture Generation

### 6.1 Goal

Support this command:

```text
/aipic: a white cat sitting in a classroom
```

### 6.2 Files to Modify

- `simple_gui/client_state_machine.py`
- Possibly `simple_gui/GUI.py` if images should be displayed inside the GUI.
- AI picture generation is implemented directly in `simple_gui/client_state_machine.py`; the old standalone example is archived in `unused_code/`.

### 6.3 Simple Implementation Steps

1. Detect messages starting with `/aipic:`.
2. Extract the prompt after the colon.
3. Use `requests.get()` to download from an image generation endpoint.
4. Save the image to a local folder such as `generated_images/`.
5. Display the saved file path in the chat GUI.
6. For the video demo, open the saved image file manually if embedding images in Tkinter is unstable.

### 6.4 Safer Demo Command

```text
/aipic: a cute robot helping students debug Python code
```

Expected result:

- The system saves an image file.
- The GUI displays the generated image path.

## 7. Pi-mono Requirement

### 7.1 What to Show in the Video

Show one meaningful use of pi-mono, for example:

```powershell
pi --provider deepseek-custom --model deepseek-v4-pro
```

Then ask:

```text
Explain why my Tkinter chat GUI repeats old messages and suggest a fix.
```

### 7.2 What to Say

Use this explanation in the video:

```text
We used pi-mono as an AI coding assistant during development. It helped us inspect the GUI message handling logic and identify that old system messages were not reset after display, which caused repeated messages. We then fixed the message rendering logic and tested the chat system again.
```

## 8. Final Video Checklist

### 8.1 Introduction

- Project name: AI-Enhanced GUI Chat System.
- Goal: Improve a terminal socket chat system with GUI, chatbot, and AI/NLP features.
- Team size: Two-person team.

### 8.2 Demo

Show these in order:

1. Start server.
2. Start Alice and Bob clients.
3. Login through GUI.
4. Use `who` and `time`.
5. Connect Alice to Bob.
6. Send messages both ways.
7. Use `/bot:`.
8. Use `/personality:`.
9. Use `@bot` in group chat.
10. Use `/summary` and `/keywords` after implementation.
11. Use sentiment analysis after implementation.
12. Use `/aipic:` after implementation.
13. Show pi-mono usage.

### 8.3 Discussion

Mention:

- Python socket programming.
- Client-server architecture.
- Tkinter GUI.
- DeepSeek API chatbot.
- Message protocol using JSON.
- Threading/select for real-time updates.

### 8.4 Analysis

Mention:

- The GUI bug and how it was fixed.
- Chatbot context/personality design.
- Challenges with API keys and model availability.
- Possible future improvement: better GUI layout, image preview inside chat, persistent group history.

## 9. Recommended Remaining Priority

Do these in order:

1. Run the current chatbot live test with your API key.
2. Record proof that `/bot:` works.
3. Implement `/summary` and `/keywords`.
4. Implement sentiment analysis.
5. Implement `/aipic:` as a saved-image feature.
6. Polish the GUI text display only if time remains.
7. Prepare slides and video script.
8. Record the 10-15 minute presentation video.
