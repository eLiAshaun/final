"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import os
from openai import OpenAI

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.bot_personality = 'a helpful chat assistant for an NYU Shanghai Python socket chat project'
        self.bot_messages = []
        self.bot_client = None
        self.bot_model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-v4-pro')

    def ask_bot(self, query):
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return 'Chatbot is not ready. Please set DEEPSEEK_API_KEY before starting the client.'
        if self.bot_client is None:
            self.bot_client = OpenAI(api_key=api_key, base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'))
        messages = [{"role": "system", "content": "You are " + self.bot_personality + ". Reply clearly and keep answers under 120 words."}]
        messages.extend(self.bot_messages[-8:])
        messages.append({"role": "user", "content": query})
        try:
            response = self.bot_client.chat.completions.create(
                model=self.bot_model,
                messages=messages,
                temperature=0.4,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as exc:
            return 'Chatbot error: ' + str(exc)
        self.bot_messages.append({"role": "user", "content": query})
        self.bot_messages.append({"role": "assistant", "content": answer})
        return answer

    def set_bot_personality(self, personality):
        self.bot_personality = personality.strip() or self.bot_personality
        self.bot_messages = []
        return 'Bot personality is now: ' + self.bot_personality

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg.startswith('/personality:'):
                    personality = my_msg.split(':', 1)[1]
                    self.out_msg += self.set_bot_personality(personality)

                elif my_msg.startswith('/bot:'):
                    query = my_msg.split(':', 1)[1].strip()
                    if len(query) > 0:
                        self.out_msg += '[You -> Bot] ' + query + '\n'
                        self.out_msg += '[Bot] ' + self.ask_bot(query)
                    else:
                        self.out_msg += 'Usage: /bot: your question'

                elif my_msg.startswith('@bot'):
                    query = my_msg[4:].strip()
                    if len(query) > 0:
                        self.out_msg += '[You -> Bot] ' + query + '\n'
                        self.out_msg += '[Bot] ' + self.ask_bot(query)
                    else:
                        self.out_msg += 'Usage: @bot your question'

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                if my_msg.startswith('/personality:'):
                    personality = my_msg.split(':', 1)[1]
                    self.out_msg += self.set_bot_personality(personality)
                elif my_msg.startswith('/bot:'):
                    query = my_msg.split(':', 1)[1].strip()
                    if len(query) > 0:
                        self.out_msg += '[You -> Bot] ' + query + '\n'
                        self.out_msg += '[Bot] ' + self.ask_bot(query)
                    else:
                        self.out_msg += 'Usage: /bot: your question'
                elif my_msg.startswith('@bot'):
                    query = my_msg[4:].strip()
                    if len(query) > 0:
                        mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                        self.out_msg += '[' + self.me + ']' + my_msg + '\n'
                        answer = self.ask_bot(query)
                        self.out_msg += '[Bot] ' + answer
                        mysend(self.s, json.dumps({"action":"exchange", "from":"[Bot]", "message":answer}))
                    else:
                        self.out_msg += 'Usage: @bot your question'
                else:
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                    self.out_msg += '[' + self.me + ']' + my_msg
                    if my_msg == 'bye':
                        self.disconnect()
                        self.state = S_LOGGEDIN
                        self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
