#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import os
os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")
import queue
import threading
import select
import socket
import sys
from pathlib import Path
from tkinter import *
from tkinter import font
from tkinter import ttk
from chat_utils import *
import json

try:
    import customtkinter as ctk
    if TkVersion < 8.6:
        ctk = None
except Exception:
    ctk = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window starts as the login window
        if ctk is not None:
            try:
                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("dark-blue")
            except Exception:
                pass
            self.Window = ctk.CTk()
        else:
            self.Window = Tk()
        print('GUI runtime:', sys.executable, 'Tk', TkVersion, 'renderer', 'customtkinter' if ctk is not None else 'tkinter')
        self.Window.withdraw()
        self.Window.title("Login")
        self.Window.geometry("460x320")
        self.Window.configure(bg = "#0F1720")
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        self.message_queue = queue.Queue()
        self.outgoing_queue = queue.Queue()
        self.running = True
        self.image_refs = []
        self.chatbot_choices = ['DeepSeek Assistant', 'Python Tutor', 'Friendly Classmate', 'Project Reviewer', 'Debug Helper']
        self.action_buttons = {}
        self.action_button_bg = "#ABB2B9"
        self.action_button_disabled_bg = "#4B5563"

    def login(self):
        self.login = self.Window
        self.login.title("Login")
        self.login.geometry("460x320")
        self.login.minsize(460, 320)
        self.login.resizable(width = False,
                             height = False)
        self.login.protocol("WM_DELETE_WINDOW", self.close_window)
        self.login_button_enabled = True

        if ctk is not None:
            self.loginFrame = ctk.CTkFrame(self.login,
                                           width = 380,
                                           height = 245,
                                           corner_radius = 18,
                                           fg_color = "#17202A")
            self.loginTitle = ctk.CTkLabel(self.loginFrame,
                                           text = "AI Chat Login",
                                           font = ("Helvetica", 24, "bold"),
                                           text_color = "#F8FAFC")
            self.nameLabel = ctk.CTkLabel(self.loginFrame,
                                          text = "Username input",
                                          anchor = W,
                                          font = ("Helvetica", 13, "bold"),
                                          text_color = "#F8FAFC")
            self.entryName = ctk.CTkEntry(self.loginFrame,
                                          height = 42,
                                          corner_radius = 10,
                                          font = ("Helvetica", 15),
                                          border_width = 2,
                                          border_color = "#60A5FA",
                                          fg_color = "#0F1720",
                                          text_color = "#F8FAFC")
            self.loginStatus = ctk.CTkLabel(self.loginFrame,
                                            text = "",
                                            text_color = "#F87171",
                                            wraplength = 310,
                                            font = ("Helvetica", 11))
            self.loginButton = ctk.CTkButton(self.loginFrame,
                                             text = "CONTINUE",
                                             height = 40,
                                             corner_radius = 10,
                                             command = self.click_login_button)
            self.loginFrame.place(relx = 0.5,
                                  rely = 0.5,
                                  anchor = CENTER)
            self.loginTitle.pack(pady = (24, 18))
            self.nameLabel.pack(fill = X,
                                padx = 34,
                                pady = (0, 6))
            self.entryName.pack(fill = X,
                                padx = 34)
            self.loginStatus.pack(fill = X,
                                  padx = 34,
                                  pady = (10, 8))
            self.loginButton.pack(fill = X,
                                  padx = 34)
        else:
            self.loginFrame = Frame(self.login,
                                    bg = "#17202A",
                                    padx = 36,
                                    pady = 28)
            self.loginFrame.place(relx = 0.5,
                                  rely = 0.5,
                                  anchor = CENTER,
                                  relwidth = 0.82,
                                  relheight = 0.76)
            self.loginTitle = Label(self.loginFrame,
                                    text = "AI Chat Login",
                                    bg = "#17202A",
                                    fg = "#F8FAFC",
                                    font = ("Helvetica", 24, "bold"))
            self.nameLabel = Label(self.loginFrame,
                                   text = "Username input",
                                   bg = "#17202A",
                                   fg = "#F8FAFC",
                                   anchor = W,
                                   font = ("Helvetica", 13, "bold"))
            self.entryName = Entry(self.loginFrame,
                                   bg = "#0F1720",
                                   fg = "#F8FAFC",
                                   insertbackground = "#F8FAFC",
                                   highlightthickness = 2,
                                   highlightbackground = "#60A5FA",
                                   highlightcolor = "#38BDF8",
                                   relief = SOLID,
                                   bd = 1,
                                   font = ("Helvetica", 16))
            self.loginStatus = Label(self.loginFrame,
                                     text = "",
                                     bg = "#17202A",
                                     fg = "#F87171",
                                     wraplength = 310,
                                     font = ("Helvetica", 11))
            self.loginButton = Button(self.loginFrame,
                                      text = "CONTINUE",
                                      bg = "#2563EB",
                                      fg = "white",
                                      activebackground = "#1D4ED8",
                                      font = ("Helvetica", 12, "bold"),
                                      command = self.click_login_button)
            self.loginTitle.pack(pady = (0, 20))
            self.nameLabel.pack(fill = X,
                                pady = (0, 6))
            self.entryName.pack(fill = X,
                                ipady = 8)
            self.loginStatus.pack(fill = X,
                                  pady = (10, 8))
            self.loginButton.pack(fill = X,
                                  ipady = 7)

        self.entryName.bind("<Return>", self.click_login_button)
        self.entryName.bind("<FocusIn>", lambda event: self.set_login_status("Typing username..."))
        self.entryName.bind("<FocusOut>", lambda event: self.set_login_status(""))
        self.login.deiconify()
        self.login.update_idletasks()
        self.login.update()
        try:
            self.entryName.focus_set()
            self.login.lift()
            self.login.attributes("-topmost", True)
            self.login.after(800, lambda: self.login.attributes("-topmost", False))
            self.login.after(100, self.login.focus_force)
        except TclError:
            pass
        self.Window.mainloop()

    def click_login_button(self, event = None):
        if self.login_button_enabled:
            self.goAhead(self.entryName.get())

    def set_login_status(self, message):
        self.loginStatus.configure(text = message)
        self.loginStatus.update_idletasks()

    def set_login_button_enabled(self, enabled):
        self.login_button_enabled = enabled
        state = NORMAL if enabled else DISABLED
        self.loginButton.configure(state = state)
        self.loginButton.update_idletasks()

    def goAhead(self, name):
        name = name.strip()
        if len(name) == 0:
            self.set_login_status("Please enter a name.")
            return

        self.set_login_button_enabled(False)
        self.set_login_status("Logging in...")
        self.login.update_idletasks()

        old_timeout = self.socket.gettimeout()
        try:
            self.socket.settimeout(5)
            msg = json.dumps({"action":"login", "name": name})
            self.send(msg)
            response = json.loads(self.recv())
        except socket.timeout:
            self.set_login_status("No response from server. Restart server and try again.")
            self.set_login_button_enabled(True)
            return
        except Exception as exc:
            self.set_login_status("Login failed: " + str(exc))
            self.set_login_button_enabled(True)
            return
        finally:
            self.socket.settimeout(old_timeout)

        if response["status"] == 'ok':
            self.clear_window()
            self.sm.set_state(S_LOGGEDIN)
            self.sm.set_myname(name)
            self.layout(name)
            self.display_message(menu)
            self.Window.after(100, self.flush_message_queue)
            process = threading.Thread(target=self.proc)
            process.daemon = True
            process.start()
        elif response["status"] == 'duplicate':
            self.set_login_status("This name is already logged in. Use another name.")
            self.set_login_button_enabled(True)
        else:
            self.set_login_status("Login rejected by server.")
            self.set_login_button_enabled(True)

    def clear_window(self):
        for child in self.Window.winfo_children():
            child.destroy()

    # The main layout of the chat
    def layout(self,name):

        self.clear_window()
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("AI-Enhanced Chatroom")
        self.Window.geometry("920x680")
        self.Window.minsize(860, 620)
        self.Window.resizable(width = True,
                              height = True)
        self.Window.configure(bg = "#17202A")
        self.Window.update_idletasks()
        self.Window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.labelHead = Label(self.Window,
                             bg = "#17202A",
                              fg = "#EAECEE",
                              text = "AI-Enhanced Chatroom — " + self.name,
                               font = "Helvetica 15 bold",
                               pady = 8)

        self.labelHead.place(relwidth = 1)
        self.modeBadge = Label(self.Window,
                               text = "Mode: Normal",
                               bg = "#2563EB",
                               fg = "white",
                               padx = 10,
                               pady = 3,
                               font = "Helvetica 10 bold")
        self.modeBadge.place(relx = 0.78,
                             rely = 0.015,
                             relwidth = 0.20,
                             relheight = 0.04)
        self.line = Label(self.Window,
                          width = 450,
                          bg = "#ABB2B9")

        self.line.place(relwidth = 1,
                        rely = 0.07,
                        relheight = 0.012)

        self.textCons = Text(self.Window,
                             width = 20,
                             height = 2,
                             bg = "#0F1720",
                             fg = "#EAECEE",
                             insertbackground = "#EAECEE",
                             font = "Helvetica 13",
                             padx = 10,
                             pady = 10,
                             relief = FLAT,
                             wrap = WORD)

        self.textCons.place(relheight = 0.745,
                            relwidth = 0.68,
                            rely = 0.08)
        self.systemTextFont = font.Font(family = "Helvetica", size = 12)
        self.chatTextFont = font.Font(family = "Helvetica", size = 13)
        self.botTextFont = font.Font(family = "Helvetica", size = 13)
        self.textCons.tag_configure("system", foreground = "#CBD5E1", font = self.systemTextFont)
        self.textCons.tag_configure("chat", foreground = "#F8FAFC", font = self.chatTextFont)
        self.textCons.tag_configure("bot", foreground = "#93C5FD", font = self.botTextFont)
        self.textCons.tag_configure("sentiment_positive", foreground = "#86EFAC", font = self.chatTextFont)
        self.textCons.tag_configure("sentiment_neutral", foreground = "#E5E7EB", font = self.chatTextFont)
        self.textCons.tag_configure("sentiment_negative", foreground = "#FCA5A5", font = self.chatTextFont)

        self.actionPanel = LabelFrame(self.Window,
                                      text = "GUI Actions",
                                      bg = "#17202A",
                                      fg = "#EAECEE",
                                      font = "Helvetica 11 bold",
                                      padx = 8,
                                      pady = 8)
        self.actionPanel.place(relx = 0.695,
                               rely = 0.08,
                               relheight = 0.745,
                               relwidth = 0.295)
        self.add_action_buttons()

        self.statusLine = Label(self.Window,
                                text = "Tip: select a chatbot role, then use /bot: or @bot. Bonus: /keywords and /summary. Sentiment is shown on chat messages.",
                                bg = "#22313F",
                                fg = "#EAECEE",
                                anchor = W,
                                padx = 10,
                                font = "Helvetica 10")
        self.statusLine.place(relwidth = 1,
                              rely = 0.825,
                              relheight = 0.035)

        self.labelBottom = Frame(self.Window,
                                 bg = "#E5E7EB",
                                 highlightthickness = 1,
                                 highlightbackground = "#CBD5E1")

        self.labelBottom.place(relwidth = 1,
                               rely = 0.86,
                               relheight = 0.14)

        self.inputLabel = Label(self.labelBottom,
                                text = "Message / Command Input",
                                bg = "#E5E7EB",
                                fg = "#0F1720",
                                anchor = W,
                                font = "Helvetica 10 bold")
        self.inputLabel.place(relwidth = 0.74,
                              relheight = 0.20,
                              rely = 0.04,
                              relx = 0.011)

        self.entryMsg = Text(self.labelBottom,
                             height = 3,
                             bg = "#F8FAFC",
                             fg = "#111827",
                             insertbackground = "#111827",
                             insertwidth = 3,
                             highlightthickness = 3,
                             highlightbackground = "#2563EB",
                             highlightcolor = "#FACC15",
                             relief = FLAT,
                             padx = 10,
                             pady = 8,
                             wrap = WORD,
                             font = "Helvetica 13")

        self.entryMsg.place(relwidth = 0.74,
                            relheight = 0.66,
                            rely = 0.27,
                            relx = 0.011)

        self.entryMsg.focus()
        self.entryMsg.bind("<Return>", self.on_text_return)
        self.entryMsg.bind("<FocusIn>", self.on_entry_focus_in)
        self.entryMsg.bind("<FocusOut>", self.on_entry_focus_out)

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text = "Send",
                                font = "Helvetica 10 bold",
                                width = 20,
                                bg = "#2563EB",
                                fg = "white",
                                activebackground = "#1D4ED8",
                                command = self.sendButton)

        self.buttonMsg.place(relx = 0.77,
                             rely = 0.27,
                             relheight = 0.29,
                             relwidth = 0.22)

        self.exitBotButton = Button(self.labelBottom,
                                    text = "Exit Bot",
                                    font = "Helvetica 10 bold",
                                    width = 20,
                                    bg = "#D1D5DB",
                                    fg = "#111827",
                                    activebackground = "#9CA3AF",
                                    command = lambda: self.sendButton("/exitbot"))
        self.exitBotButton.place(relx = 0.77,
                                 rely = 0.64,
                                 relheight = 0.29,
                                 relwidth = 0.22)

        self.textCons.config(cursor = "arrow")
        self.Window.update_idletasks()

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)

        scrollbar.config(command = self.textCons.yview)

        self.textCons.config(state = DISABLED,
                             yscrollcommand = scrollbar.set)
        self.update_mode_indicator()
        self.update_action_states()

    def add_action_buttons(self):
        self.chatbotLabel = Label(self.actionPanel,
                                  text = "Chatbot role",
                                  bg = "#17202A",
                                  fg = "#EAECEE",
                                  font = "Helvetica 10 bold")
        self.chatbotLabel.grid(row = 0,
                               column = 0,
                               columnspan = 2,
                               sticky = EW,
                               pady = (0, 2))
        self.chatbotChoice = ttk.Combobox(self.actionPanel,
                                          values = self.chatbot_choices,
                                          state = "readonly",
                                          font = "Helvetica 10")
        current_bot = getattr(self.sm, "bot_name", self.chatbot_choices[0])
        self.chatbotChoice.set(current_bot if current_bot in self.chatbot_choices else self.chatbot_choices[0])
        self.chatbotChoice.grid(row = 1,
                                column = 0,
                                columnspan = 2,
                                sticky = EW,
                                pady = (0, 5),
                                ipady = 2)
        self.chatbotChoice.bind("<<ComboboxSelected>>", self.select_chatbot)

        self.aiNlpVar = BooleanVar(value = getattr(self.sm, "deepseek_nlp_enabled", False))
        self.aiNlpSwitch = Checkbutton(self.actionPanel,
                                       text = "DeepSeek NLP",
                                       variable = self.aiNlpVar,
                                       command = self.toggle_deepseek_nlp,
                                       bg = "#17202A",
                                       fg = "#EAECEE",
                                       activebackground = "#17202A",
                                       activeforeground = "#F8FAFC",
                                       selectcolor = "#0F1720",
                                       disabledforeground = "#64748B",
                                       anchor = W,
                                       font = "Helvetica 9 bold")
        self.aiNlpSwitch.grid(row = 2,
                              column = 0,
                              columnspan = 2,
                              sticky = EW,
                              pady = (0, 5))

        actions = [
            ("list_chatbots", "List Chatbots", lambda: self.sendButton("/chatbots", "Loading chatbot roles...")),
            ("online_users", "Online Users", lambda: self.sendButton("who", "Requesting online users...")),
            ("server_time", "Server Time", lambda: self.sendButton("time", "Requesting server time...")),
            ("connect", "Connect", self.ask_connect),
            ("search_logs", "Search Logs", self.ask_search),
            ("sonnet", "Sonnet #", self.ask_poem),
            ("ask_bot", "Ask Bot Mode", lambda: self.sendButton("/askbot", "Entering AskBot mode...")),
            ("exit_bot", "Exit Bot", lambda: self.sendButton("/exitbot", "Leaving AskBot mode...")),
            ("custom_style", "Custom Bot Style", self.ask_personality),
            ("group_bot", "Group Bot", self.ask_group_bot),
            ("summary", "Summary", lambda: self.sendButton("/summary", "Summarizing chat history by sender...")),
            ("keywords", "Keywords", lambda: self.sendButton("/keywords", "Extracting chat keywords...")),
            ("ai_picture", "AI Picture", self.ask_ai_picture),
            ("archive", "Archive", lambda: self.sendButton("/archive", "Showing local chat archive path...")),
            ("disconnect", "Disconnect", lambda: self.sendButton("bye", "Disconnecting current chat...")),
            ("quit", "Quit", lambda: self.sendButton("q", "Quitting chatroom...")),
        ]
        for index, action in enumerate(actions):
            row = 3 + index // 2
            column = index % 2
            button = Button(self.actionPanel,
                            text = action[1],
                            command = action[2],
                            bg = self.action_button_bg,
                            disabledforeground = "#CBD5E1",
                            font = "Helvetica 9 bold")
            button.grid(row = row,
                        column = column,
                        sticky = EW,
                        padx = 2,
                        pady = 2,
                        ipady = 2)
            self.action_buttons[action[0]] = button
        self.actionPanel.grid_columnconfigure(0,
                                              weight = 1)
        self.actionPanel.grid_columnconfigure(1,
                                              weight = 1)
        self.update_action_states()

    def fill_command(self, prefix, hint):
        self.clear_input()
        self.entryMsg.insert("1.0", prefix)
        self.entryMsg.focus_set()
        self.entryMsg.mark_set(INSERT, END)
        self.statusLine.config(text = hint)

    def get_input_text(self):
        return self.entryMsg.get("1.0", END).strip()

    def clear_input(self):
        self.entryMsg.delete("1.0", END)

    def on_text_return(self, event = None):
        self.sendButton()
        return "break"

    def on_entry_focus_in(self, event = None):
        if getattr(self.sm, "bot_mode", False):
            self.inputLabel.config(text = "AskBot Input  |  typing...")
            self.statusLine.config(text = "AskBot mode is active. Type questions directly, or click Exit Bot.")
        else:
            self.inputLabel.config(text = "Message / Command Input  |  typing...")
            self.statusLine.config(text = "Input is active. Type a chat message or command, then press Enter or Send.")

    def on_entry_focus_out(self, event = None):
        if getattr(self.sm, "bot_mode", False):
            self.inputLabel.config(text = "AskBot Input  |  bot mode active")
        else:
            self.inputLabel.config(text = "Message / Command Input")

    def update_mode_indicator(self):
        if not hasattr(self, "modeBadge"):
            return
        state = self.sm.get_state()
        if state == S_OFFLINE:
            text = "Mode: Offline"
            bg = "#6B7280"
        elif getattr(self.sm, "bot_mode", False):
            text = "Mode: AskBot"
            bg = "#CA8A04"
        elif state == S_CHATTING and getattr(self.sm, "peer", ""):
            text = "Mode: Chatting with " + self.sm.peer
            bg = "#059669"
        elif state == S_CHATTING:
            text = "Mode: Chatting"
            bg = "#059669"
        else:
            text = "Mode: Normal"
            bg = "#2563EB"
        self.modeBadge.config(text = text,
                              bg = bg)

    def set_action_enabled(self, key, enabled):
        if not hasattr(self, "action_buttons") or key not in self.action_buttons:
            return
        button = self.action_buttons[key]
        if enabled:
            button.config(state = NORMAL,
                          bg = self.action_button_bg,
                          activebackground = "#CBD5E1")
        else:
            button.config(state = DISABLED,
                          bg = self.action_button_disabled_bg,
                          activebackground = self.action_button_disabled_bg)

    def update_action_states(self):
        if not hasattr(self, "action_buttons") or not self.action_buttons:
            return
        state = self.sm.get_state()
        is_online = state in (S_LOGGEDIN, S_CHATTING)
        is_chatting = state == S_CHATTING
        bot_active = getattr(self.sm, "bot_mode", False)
        states = {
            "list_chatbots": is_online,
            "online_users": is_online,
            "server_time": is_online,
            "connect": is_online and not is_chatting and not bot_active,
            "search_logs": is_online,
            "sonnet": is_online,
            "ask_bot": is_online and not bot_active,
            "exit_bot": is_online and bot_active,
            "custom_style": is_online,
            "group_bot": is_online and is_chatting and not bot_active,
            "summary": is_online,
            "keywords": is_online,
            "ai_picture": is_online,
            "archive": is_online,
            "disconnect": is_online and is_chatting,
            "quit": is_online,
        }
        for key, enabled in states.items():
            self.set_action_enabled(key, enabled)
        if hasattr(self, "chatbotChoice"):
            self.chatbotChoice.config(state = "readonly" if is_online else "disabled")
        if hasattr(self, "exitBotButton"):
            self.exitBotButton.config(state = NORMAL if bot_active else DISABLED)
        if hasattr(self, "aiNlpSwitch"):
            nlp_available = getattr(self.sm, "deepseek_nlp_available", lambda: False)()
            self.aiNlpSwitch.config(state = NORMAL if is_online and nlp_available else DISABLED)
            if not nlp_available:
                self.sm.deepseek_nlp_enabled = False
                self.aiNlpVar.set(False)
            else:
                self.aiNlpVar.set(getattr(self.sm, "deepseek_nlp_enabled", False))

    def toggle_deepseek_nlp(self):
        enabled = bool(self.aiNlpVar.get())
        success, message = self.sm.set_deepseek_nlp_enabled(enabled)
        if not success:
            self.aiNlpVar.set(False)
        self.statusLine.config(text = message)

    def is_slow_ai_request(self, msg):
        msg = msg.strip()
        if not msg:
            return False
        if msg in ("/summary", "/keywords") and getattr(self.sm, "deepseek_nlp_enabled", False):
            return True
        command_only = (
            "/askbot", "/exitbot", "/chatbots", "/summary", "/keywords",
            "/archive", "/nlp", "/nlp:on", "/nlp:off", "/nlp:status",
            "bye", "q", "who", "time", "c", "p",
        )
        command_prefixes = (
            "/chatbot:", "/personality:", "c ", "?",
            "p ",
        )
        if msg in command_only or msg.startswith(command_prefixes):
            return False
        return (
            getattr(self.sm, "bot_mode", False)
            or msg.startswith("/bot:")
            or msg.startswith("@bot")
            or msg.startswith("/aipic:")
        )

    def thinking_message(self, msg):
        if msg.startswith("/aipic:"):
            return "[AI Picture] Thinking... preparing the image prompt with DeepSeek."
        if msg == "/summary":
            return "[DeepSeek NLP] Thinking... summarizing the real chat history."
        if msg == "/keywords":
            return "[DeepSeek NLP] Thinking... extracting precise keywords."
        return "[Bot] Thinking... your message has been sent."

    def status_for_command(self, msg):
        if msg == "time":
            return "Server time request sent."
        if msg == "who":
            return "Online user list request sent."
        if msg == "/chatbots":
            return "Chatbot role list request sent."
        if msg == "/summary":
            return "Summary request sent."
        if msg == "/keywords":
            return "Keyword request sent."
        if msg.startswith("/nlp"):
            return "NLP mode request sent."
        if msg == "/archive":
            return "Archive status request sent."
        if msg == "/askbot":
            return "Entering AskBot mode..."
        if msg == "/exitbot":
            return "Leaving AskBot mode..."
        if msg == "bye":
            return "Disconnect request sent."
        if msg == "q":
            return "Quit request sent."
        if msg == "p" or msg.startswith("p "):
            return "Sonnet request sent."
        if msg.startswith("?"):
            return "Search request sent."
        if msg == "c" or msg.startswith("c "):
            return "Connect request sent."
        if msg.startswith("/aipic:"):
            return "AI picture request sent."
        if getattr(self.sm, "bot_mode", False) or msg.startswith("/bot:") or msg.startswith("@bot"):
            return "DeepSeek request sent."
        return "Message sent."

    def select_chatbot(self, event = None):
        self.sendButton('/chatbot: ' + self.chatbotChoice.get())
        self.statusLine.config(text = 'Selected chatbot role: ' + self.chatbotChoice.get())

    def ask_connect(self):
        self.fill_command("c ", "Type the username after c, then press Enter or Send.")

    def ask_search(self):
        self.fill_command("? ", "Type a chat-log search term after ?, then press Enter or Send.")

    def ask_poem(self):
        self.fill_command("p ", "Type a Shakespeare sonnet number from 1 to 154 after p.")

    def ask_bot(self):
        self.fill_command("/bot: ", "Type a chatbot question, then press Enter or Send")

    def ask_personality(self):
        self.fill_command("/personality: ", "Describe the custom chatbot style, then press Enter or Send")

    def ask_group_bot(self):
        self.fill_command("@bot ", "Type a group bot question while connected to another user")

    def ask_ai_picture(self):
        self.fill_command("/aipic: ", "Describe an image prompt, then press Enter or Send")

    def insert_generated_images(self, message):
        if Image is None or ImageTk is None:
            return
        for line in message.splitlines():
            if line.startswith("AI picture saved: "):
                image_path = Path(line.split(": ", 1)[1].strip())
                if image_path.exists():
                    image = Image.open(image_path)
                    image.thumbnail((280, 220))
                    photo = ImageTk.PhotoImage(image)
                    self.image_refs.append(photo)
                    self.textCons.insert(END, "\n")
                    self.textCons.image_create(END, image = photo)
                    self.textCons.insert(END, "\n")

    def display_message(self, message):
        self.textCons.config(state = NORMAL)
        self.insert_message_text(message)
        self.insert_generated_images(message)
        self.textCons.insert(END, "\n")
        self.textCons.config(state = DISABLED)
        self.textCons.see(END)

    def insert_message_text(self, message):
        for line in message.rstrip().splitlines():
            tag = "system"
            if "[Sentiment: Positive]" in line:
                tag = "sentiment_positive"
            elif "[Sentiment: Negative]" in line:
                tag = "sentiment_negative"
            elif "[Sentiment: Neutral]" in line:
                tag = "sentiment_neutral"
            elif line.startswith("[Bot]"):
                tag = "bot"
            elif line.startswith("[") and "]" in line:
                tag = "chat"
            self.textCons.insert(END, line + "\n", tag)

    def flush_message_queue(self):
        if not hasattr(self, 'textCons'):
            if self.running:
                self.Window.after(100, self.flush_message_queue)
            return
        while True:
            try:
                message = self.message_queue.get_nowait()
            except queue.Empty:
                break
            self.display_message(message)
            self.update_mode_indicator()
            self.update_action_states()
        if self.running:
            self.Window.after(100, self.flush_message_queue)

    # function to basically start the thread for sending messages
    def sendButton(self, msg = None, feedback = None):
        if msg is None:
            msg = self.get_input_text()
        msg = msg.strip()
        if not msg:
            return
        if msg == "/askbot":
            self.set_bot_mode_visual(True)
        elif msg == "/exitbot":
            self.set_bot_mode_visual(False)
        if self.is_slow_ai_request(msg):
            self.display_message(self.thinking_message(msg))
        self.statusLine.config(text = feedback or self.status_for_command(msg))
        self.outgoing_queue.put(msg)
        self.clear_input()
        self.entryMsg.focus_set()
        self.update_action_states()

    def set_bot_mode_visual(self, active):
        if active:
            self.inputLabel.config(text = "AskBot Input  |  bot mode active")
            self.statusLine.config(text = "AskBot mode is active. Type questions directly, or click Exit Bot.")
            self.exitBotButton.config(bg = "#FACC15", activebackground = "#EAB308")
        else:
            self.inputLabel.config(text = "Message / Command Input")
            self.statusLine.config(text = "Normal chat mode is active.")
            self.exitBotButton.config(bg = "#D1D5DB", activebackground = "#9CA3AF")
        if active and hasattr(self, "modeBadge"):
            self.modeBadge.config(text = "Mode: AskBot",
                                  bg = "#CA8A04")
        else:
            self.update_mode_indicator()
        self.update_action_states()

    def close_window(self):
        self.running = False
        try:
            self.Window.destroy()
        except TclError:
            pass

    def proc(self):
        # print(self.msg)
        while self.running:
            try:
                read, _, _ = select.select([self.socket], [], [], CHAT_WAIT)
                peer_msg = []
                my_msg = ""
                # print(self.msg)
                if self.socket in read:
                    peer_msg = self.recv()
                try:
                    my_msg = self.outgoing_queue.get_nowait()
                except queue.Empty:
                    my_msg = ""
                if len(my_msg) > 0 or len(peer_msg) > 0:
                    self.system_msg = self.sm.proc(my_msg, peer_msg)
                    if len(self.system_msg) > 0:
                        self.message_queue.put(self.system_msg)
                    self.system_msg = ""
                    self.Window.after(0, self.update_mode_indicator)
                    self.Window.after(0, self.update_action_states)
                    if self.sm.get_state() == S_OFFLINE:
                        self.Window.after(500, self.close_window)
            except (OSError, TclError, ValueError):
                self.running = False
                break

    def run(self):
        self.login()
# create a GUI class object
if __name__ == "__main__":
    g = GUI()
