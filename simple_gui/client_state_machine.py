"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
from datetime import datetime
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import quote

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def load_local_env():
    env_paths = [
        Path(__file__).resolve().parent.parent / '.env',
        Path(__file__).resolve().parent / '.env',
    ]
    for env_path in env_paths:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_local_env()

BOT_PERSONAS = {
    'DeepSeek Assistant': 'a helpful DeepSeek-powered assistant for an NYU Shanghai Python socket chat project',
    'Python Tutor': 'a patient Python tutor who explains ideas with short examples',
    'Friendly Classmate': 'a friendly classmate who gives concise and encouraging answers',
    'Project Reviewer': 'a careful project reviewer who focuses on requirements and demo quality',
    'Debug Helper': 'a practical debugging assistant who asks for symptoms and suggests checks',
}

POSITIVE_WORDS = {
    'amazing', 'awesome', 'best', 'clear', 'cool', 'enjoy', 'excellent',
    'fantastic', 'good', 'great', 'happy', 'helpful', 'impressive', 'love',
    'nice', 'perfect', 'smooth', 'thanks', 'wonderful',
}

NEGATIVE_WORDS = {
    'angry', 'annoying', 'awful', 'bad', 'broken', 'bug', 'confusing',
    'crash', 'difficult', 'error', 'fail', 'failed', 'frustrating', 'hate',
    'issue', 'problem', 'sad', 'terrible', 'worse', 'worst',
}


class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        env_bot_name = os.environ.get('CHATBOT_NAME', 'DeepSeek Assistant')
        self.bot_name = env_bot_name if env_bot_name in BOT_PERSONAS else 'DeepSeek Assistant'
        self.bot_personality = BOT_PERSONAS[self.bot_name]
        self.bot_messages = []
        self.bot_client = None
        self.bot_model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-v4-pro')
        self.bot_mode = False
        self.deepseek_nlp_enabled = os.environ.get('DEEPSEEK_NLP_DEFAULT', '').lower() in ('1', 'true', 'yes', 'on')
        self.chat_history = []
        self.session_id = time.strftime('%Y%m%d_%H%M%S')

    def call_deepseek(self, messages, temperature=0.4):
        api_key = os.environ.get('DEEPSEEK_API_KEY', '').strip()
        if not api_key:
            return 'DeepSeek API is not ready. Please set DEEPSEEK_API_KEY before starting the client.'
        if OpenAI is None:
            return 'DeepSeek API is not ready. Please install openai or start the project virtual environment.'
        if self.bot_client is None:
            self.bot_client = OpenAI(api_key=api_key, base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'))

        fallback_model = os.environ.get('DEEPSEEK_FALLBACK_MODEL', 'deepseek-chat')
        model_candidates = [self.bot_model]
        if fallback_model and fallback_model not in model_candidates:
            model_candidates.append(fallback_model)

        last_error = None
        answer = ''
        for model in model_candidates:
            try:
                response = self.bot_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                answer = response.choices[0].message.content.strip()
                self.bot_model = model
                break
            except Exception as exc:
                last_error = exc
                error_text = str(exc).lower()
                if 'model' not in error_text and 'not found' not in error_text:
                    break
        else:
            answer = ''

        if not answer:
            return 'DeepSeek API error: ' + str(last_error)

        return answer

    def deepseek_nlp_available(self):
        return bool(os.environ.get('DEEPSEEK_API_KEY', '').strip()) and OpenAI is not None

    def set_deepseek_nlp_enabled(self, enabled):
        if enabled and not self.deepseek_nlp_available():
            self.deepseek_nlp_enabled = False
            return False, 'DeepSeek NLP is unavailable. Check DEEPSEEK_API_KEY and the openai package.'
        self.deepseek_nlp_enabled = bool(enabled)
        if self.deepseek_nlp_enabled:
            return True, 'DeepSeek NLP enabled: sentiment, summary, and keywords will use DeepSeek first.'
        return True, 'DeepSeek NLP disabled: local sentiment and NLP fallback are active.'

    def nlp_status(self):
        mode = 'DeepSeek' if self.deepseek_nlp_enabled else 'Local fallback'
        availability = 'available' if self.deepseek_nlp_available() else 'unavailable'
        return 'NLP mode: ' + mode + ' (DeepSeek API ' + availability + ').'

    def ask_bot(self, query):
        messages = [{"role": "system", "content": "You are " + self.bot_name + ", powered by DeepSeek API model " + self.bot_model + ". Personality: " + self.bot_personality + ". Reply clearly and keep answers under 120 words."}]
        messages.extend(self.bot_messages[-8:])
        messages.append({"role": "user", "content": query})
        answer = self.call_deepseek(messages, temperature=0.4)

        if answer.startswith('DeepSeek API is not ready.') or answer.startswith('DeepSeek API error:'):
            return answer

        self.bot_messages.append({"role": "user", "content": query})
        self.bot_messages.append({"role": "assistant", "content": answer})
        return answer

    def enter_bot_mode(self):
        self.bot_mode = True
        return 'AskBot mode is active. Type questions directly, or click Exit Bot when you are done.'

    def exit_bot_mode(self):
        if not self.bot_mode:
            return 'AskBot mode is already inactive.'
        self.bot_mode = False
        return 'AskBot mode closed. You are back to normal chat commands.'

    def list_chatbots(self):
        lines = ['Available chatbots:']
        lines.append('DeepSeek model: ' + self.bot_model)
        for name, personality in BOT_PERSONAS.items():
            marker = ' * ' if name == self.bot_name else ' - '
            lines.append(marker + name + ': ' + personality)
        if self.bot_name == 'Custom':
            lines.append(' * Custom: ' + self.bot_personality)
        lines.append('Use /chatbot: name or the GUI dropdown to switch.')
        return '\n'.join(lines)

    def resolve_chatbot_name(self, name):
        normalized = name.strip().lower()
        for bot_name in BOT_PERSONAS:
            if bot_name.lower() == normalized:
                return bot_name
        return ''

    def select_chatbot(self, name):
        requested_name = name.strip()
        resolved_name = self.resolve_chatbot_name(requested_name)
        if not resolved_name:
            return 'Unknown chatbot "' + requested_name + '".\n' + self.list_chatbots()
        self.bot_name = resolved_name
        self.bot_personality = BOT_PERSONAS[resolved_name]
        self.bot_messages = []
        return 'Selected chatbot: ' + self.bot_name + '\nPersonality: ' + self.bot_personality

    def set_bot_personality(self, personality):
        if not personality.strip():
            return 'Usage: /personality: describe the chatbot style'
        self.bot_name = 'Custom'
        self.bot_personality = personality.strip() or self.bot_personality
        self.bot_messages = []
        return 'Bot personality is now: ' + self.bot_personality

    def add_chat_history(self, speaker, message=None, sentiment='', source='chat'):
        if message is None:
            message = speaker
            speaker = 'Chat'
        speaker = speaker.strip() or 'Chat'
        message = message.strip()
        if message:
            entry = {
                "timestamp": self.current_timestamp(),
                "speaker": speaker,
                "message": message,
                "sentiment": sentiment,
                "source": source,
                "peer": self.peer,
            }
            self.chat_history.append(entry)
            self.archive_chat_entry(entry)

    def current_timestamp(self):
        return datetime.now().astimezone().isoformat(timespec='seconds')

    def safe_uid(self, uid):
        uid = str(uid or 'unknown').strip()
        safe = re.sub(r'[^A-Za-z0-9_.-]+', '_', uid)
        return safe or 'unknown'

    def archive_path(self):
        archive_dir = Path(__file__).resolve().parent / 'chat_archives'
        archive_dir.mkdir(exist_ok=True)
        return archive_dir / (self.safe_uid(self.me) + '.jsonl')

    def archive_chat_entry(self, entry):
        if not self.me:
            return
        record = dict(entry)
        record["owner_uid"] = self.me
        record["speaker_uid"] = self.history_speaker(entry)
        record["session_id"] = self.session_id
        record["saved_at"] = self.current_timestamp()
        try:
            with self.archive_path().open('a', encoding='utf-8') as archive_file:
                archive_file.write(json.dumps(record, ensure_ascii=False) + '\n')
        except OSError:
            pass

    def archive_status(self):
        if not self.me:
            return 'Archive is not ready before login.'
        return (
            'Chat archive is saving automatically.\n'
            + 'Current user archive: ' + str(self.archive_path()) + '\n'
            + 'Saved messages in this session: ' + str(len(self.chat_history))
        )

    def handle_nlp_command(self, command):
        command = command.strip().lower()
        if command in ('/nlp', '/nlp:status'):
            return self.nlp_status()
        if command in ('/nlp:on', '/nlp on'):
            _, message = self.set_deepseek_nlp_enabled(True)
            return message
        if command in ('/nlp:off', '/nlp off'):
            _, message = self.set_deepseek_nlp_enabled(False)
            return message
        return 'Usage: /nlp:on, /nlp:off, or /nlp:status'

    def history_speaker(self, entry):
        if isinstance(entry, dict):
            speaker = entry.get("speaker", "Chat")
        else:
            speaker = "Chat"
        speaker = str(speaker).strip()
        if speaker.startswith("[") and speaker.endswith("]"):
            speaker = speaker[1:-1].strip()
        return speaker or "Chat"

    def history_message(self, entry):
        if isinstance(entry, dict):
            return str(entry.get("message", "")).strip()
        return str(entry).strip()

    def history_line(self, entry):
        timestamp = ''
        if isinstance(entry, dict):
            timestamp = str(entry.get("timestamp", "")).strip()
        speaker = self.history_speaker(entry)
        message = self.history_message(entry)
        if timestamp:
            return timestamp + ' | ' + speaker + ': ' + message
        return speaker + ': ' + message

    def history_transcript(self, limit=80):
        entries = self.chat_history[-limit:] if limit else self.chat_history
        return '\n'.join(self.history_line(entry) for entry in entries if self.history_message(entry))

    def parse_deepseek_keywords(self, answer):
        if not answer or answer.startswith('DeepSeek API is not ready.') or answer.startswith('DeepSeek API error:'):
            return []
        cleaned = answer.strip()
        cleaned = re.sub(r'^[\[\{].*?keywords["\']?\s*[:=]\s*', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = cleaned.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
        parts = re.split(r'[,;\n]+', cleaned)
        keywords = []
        seen = set()
        for part in parts:
            word = re.sub(r'^\s*[-*\d.)]+\s*', '', part).strip().strip('"').strip("'")
            word = re.sub(r'\s+', ' ', word)
            if not word:
                continue
            marker = word.lower()
            if marker not in seen:
                keywords.append(word)
                seen.add(marker)
            if len(keywords) >= 8:
                break
        return keywords

    def deepseek_sentiment_label(self, message):
        messages = [
            {
                "role": "system",
                "content": "Classify the sentiment of the user's chat message. Output exactly one word: Positive, Neutral, or Negative. Consider English and Chinese accurately.",
            },
            {"role": "user", "content": message},
        ]
        answer = self.call_deepseek(messages, temperature=0)
        lowered = answer.strip().lower()
        if 'positive' in lowered:
            return 'Positive'
        if 'negative' in lowered:
            return 'Negative'
        if 'neutral' in lowered:
            return 'Neutral'
        return ''

    def deepseek_keywords(self):
        transcript = self.history_transcript()
        if not transcript:
            return []
        messages = [
            {
                "role": "system",
                "content": "Extract 5 to 8 precise keywords or short key phrases from the actual chat transcript. Preserve names, APIs, technical terms, and project-specific words. Prefer accurate nouns over vague words. Output comma-separated keywords only, no explanation.",
            },
            {"role": "user", "content": transcript},
        ]
        return self.parse_deepseek_keywords(self.call_deepseek(messages, temperature=0.1))

    def deepseek_summary(self):
        transcript = self.history_transcript()
        if not transcript:
            return ''
        messages = [
            {
                "role": "system",
                "content": "Summarize the actual chat transcript concisely. Use the same language as the conversation when possible. Include: Summary by sender, key topics, and open tasks if any. Do not invent details.",
            },
            {"role": "user", "content": transcript},
        ]
        answer = self.call_deepseek(messages, temperature=0.2)
        if answer.startswith('DeepSeek API is not ready.') or answer.startswith('DeepSeek API error:'):
            return ''
        return answer.strip()

    def sentiment_label(self, message):
        if self.deepseek_nlp_enabled and self.deepseek_nlp_available():
            label = self.deepseek_sentiment_label(message)
            if label:
                return label
        try:
            from textblob import TextBlob
            polarity = TextBlob(message).sentiment.polarity
        except Exception:
            words = re.findall(r"[A-Za-z][A-Za-z']+", message.lower())
            positive = sum(1 for word in words if word in POSITIVE_WORDS)
            negative = sum(1 for word in words if word in NEGATIVE_WORDS)
            polarity = positive - negative
        if polarity > 0.1:
            return 'Positive'
        if polarity < -0.1:
            return 'Negative'
        return 'Neutral'

    def format_chat_message(self, speaker, message):
        sentiment = self.sentiment_label(message)
        self.add_chat_history(speaker, message, sentiment=sentiment, source='chat')
        return speaker + ' ' + message + ' [Sentiment: ' + sentiment + ']\n'

    def format_bot_exchange(self, query):
        answer = self.ask_bot(query)
        self.add_chat_history('[You -> Bot]', query, source='bot_query')
        self.add_chat_history('[Bot]', answer, source='bot_response')
        return '[You -> Bot] ' + query + '\n[Bot] ' + answer

    def summarize_history(self):
        if not self.chat_history:
            return 'No chat history to summarize yet.'
        if self.deepseek_nlp_enabled and self.deepseek_nlp_available():
            summary = self.deepseek_summary()
            if summary:
                return 'Chat summary (DeepSeek):\n' + summary

        try:
            from nlp_tools import summarize_with_sumy
        except Exception as exc:
            return 'Summary error: ' + str(exc)

        grouped = {}
        order = []
        for entry in self.chat_history:
            speaker = self.history_speaker(entry)
            message = self.history_message(entry)
            if not message:
                continue
            if speaker not in grouped:
                grouped[speaker] = []
                order.append(speaker)
            grouped[speaker].append(message)

        if not grouped:
            return 'No summary generated yet. Send more chat messages first.'

        lines = ['Chat summary by sender:']
        try:
            for speaker in order:
                messages = grouped[speaker]
                summary = summarize_with_sumy(messages)
                if not summary:
                    summary = messages[-3:]
                lines.append(speaker + ' (' + str(len(messages)) + ' messages):')
                for sentence in summary:
                    lines.append('- ' + sentence)
        except Exception as exc:
            return 'Summary error: ' + str(exc)
        return '\n'.join(lines)

    def extract_keywords(self):
        if not self.chat_history:
            return 'No chat history for keywords yet.'
        if self.deepseek_nlp_enabled and self.deepseek_nlp_available():
            keywords = self.deepseek_keywords()
            if keywords:
                return 'Chat keywords (DeepSeek): ' + ', '.join(keywords)

        try:
            from nlp_tools import extract_keywords_yake
            messages = [self.history_message(entry) for entry in self.chat_history]
            keywords = extract_keywords_yake(messages)
        except Exception as exc:
            return 'Keywords error: ' + str(exc)
        if not keywords:
            return 'No keywords found yet. Send more chat messages first.'
        return 'Chat keywords: ' + ', '.join(keywords)

    def request_server_time(self):
        mysend(self.s, json.dumps({"action":"time"}))
        response = json.loads(myrecv(self.s))
        if "results" not in response:
            return 'Server time response was not recognized.\n'
        time_in = response["results"]
        return "Server time: " + time_in + '\n'

    def list_online_users(self):
        mysend(self.s, json.dumps({"action":"list"}))
        response = json.loads(myrecv(self.s))
        if "results" not in response:
            return 'Online users response was not recognized.\n'
        logged_in = response["results"].strip()
        if not logged_in:
            logged_in = '(no other users online)'
        return 'Online users:\n' + logged_in + '\n'

    def search_logs(self, term):
        term = term.strip()
        if not term:
            return 'Usage: ? search_term\n'
        mysend(self.s, json.dumps({"action":"search", "target":term}))
        response = json.loads(myrecv(self.s))
        if "results" not in response:
            return 'Search response was not recognized.\n'
        search_rslt = response["results"].strip()
        if len(search_rslt) > 0:
            return search_rslt + '\n\n'
        return '\'' + term + '\'' + ' not found\n\n'

    def request_sonnet(self, poem_idx):
        poem_idx = poem_idx.strip()
        if not poem_idx.isdigit():
            return 'Usage: p sonnet_number (1-154), for example: p 18\n'
        poem_number = int(poem_idx)
        if poem_number < 1 or poem_number > 154:
            return 'Please enter a Shakespeare sonnet number from 1 to 154.\n'
        mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
        response = json.loads(myrecv(self.s))
        if "results" not in response:
            return 'Sonnet response was not recognized.\n'
        poem = response["results"].strip()
        if len(poem) > 0:
            return 'Shakespeare Sonnet ' + poem_idx + ':\n' + poem + '\n\n'
        return 'Sonnet ' + poem_idx + ' was not found. Try a number from 1 to 154.\n\n'

    def prepare_image_prompt(self, prompt):
        messages = [
            {
                "role": "system",
                "content": "Rewrite the user request into one concise English text-to-image prompt. Output only the final prompt, with no quotation marks and no explanation.",
            },
            {"role": "user", "content": prompt},
        ]
        prepared_prompt = self.call_deepseek(messages, temperature=0.2)
        if prepared_prompt.startswith('DeepSeek API is not ready.') or prepared_prompt.startswith('DeepSeek API error:'):
            return prompt, prepared_prompt
        return prepared_prompt.strip(), ''

    def generate_ai_picture(self, prompt):
        prompt = prompt.strip()
        if not prompt:
            return 'Usage: /aipic: describe the image you want'
        try:
            prepared_prompt, prompt_note = self.prepare_image_prompt(prompt)
            images_dir = Path(__file__).resolve().parent / 'generated_images'
            images_dir.mkdir(exist_ok=True)
            filename = 'aipic_' + time.strftime('%Y%m%d_%H%M%S') + '.png'
            image_path = images_dir / filename
            url = 'https://image.pollinations.ai/prompt/' + quote(prepared_prompt)
            try:
                import requests
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                image_bytes = response.content
            except ImportError:
                from urllib.request import Request, urlopen
                request = Request(url, headers={'User-Agent': 'ICDS-Chat-System/1.0'})
                with urlopen(request, timeout=30) as response:
                    image_bytes = response.read()
            if len(image_bytes) < 1000:
                return 'AI picture error: image service returned an empty response.'
            image_path.write_bytes(image_bytes)
        except Exception as exc:
            return 'AI picture error: ' + str(exc)
        result = ''
        if prompt_note:
            result += 'Image prompt used original text because prompt preparation failed: ' + prompt_note + '\n'
        else:
            result += 'Image prompt prepared by DeepSeek:\n' + prepared_prompt + '\n'
        result += 'AI picture saved: ' + str(image_path)
        return result

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
            self.out_msg += 'Cannot connect to yourself.\n'
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

                elif my_msg == 'bye':
                    self.out_msg += 'You are not connected to another user right now.\n'

                elif my_msg == '/askbot':
                    self.out_msg += self.enter_bot_mode()

                elif my_msg == '/exitbot':
                    self.out_msg += self.exit_bot_mode()

                elif my_msg.startswith('/nlp'):
                    self.out_msg += self.handle_nlp_command(my_msg)

                elif my_msg == '/archive':
                    self.out_msg += self.archive_status()

                elif my_msg == 'time':
                    self.out_msg += self.request_server_time()

                elif my_msg == 'who':
                    self.out_msg += self.list_online_users()

                elif my_msg == '/chatbots':
                    self.out_msg += self.list_chatbots()

                elif my_msg.startswith('/chatbot:'):
                    bot_name = my_msg.split(':', 1)[1]
                    self.out_msg += self.select_chatbot(bot_name)

                elif my_msg.startswith('/personality:'):
                    personality = my_msg.split(':', 1)[1]
                    self.out_msg += self.set_bot_personality(personality)

                elif my_msg.startswith('/bot:'):
                    query = my_msg.split(':', 1)[1].strip()
                    if len(query) > 0:
                        self.out_msg += self.format_bot_exchange(query)
                    else:
                        self.out_msg += 'Usage: /bot: your question'

                elif my_msg.startswith('@bot'):
                    query = my_msg[4:].strip()
                    if len(query) > 0:
                        self.out_msg += self.format_bot_exchange(query)
                    else:
                        self.out_msg += 'Usage: @bot your question'

                elif my_msg == '/summary':
                    self.out_msg += self.summarize_history()

                elif my_msg == '/keywords':
                    self.out_msg += self.extract_keywords()

                elif my_msg.startswith('/aipic:'):
                    prompt = my_msg.split(':', 1)[1]
                    self.out_msg += self.generate_ai_picture(prompt)

                elif my_msg == 'c' or my_msg.startswith('c '):
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if len(peer) == 0:
                        self.out_msg += 'Usage: c username\n'
                    elif self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    self.out_msg += self.search_logs(term)

                elif my_msg == 'p' or my_msg.startswith('p '):
                    poem_idx = my_msg[1:].strip()
                    self.out_msg += self.request_sonnet(poem_idx)

                elif self.bot_mode:
                    self.out_msg += self.format_bot_exchange(my_msg)

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
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                elif my_msg == 'q':
                    self.disconnect()
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE
                    self.peer = ''
                elif my_msg == '/askbot':
                    self.out_msg += self.enter_bot_mode()
                elif my_msg == '/exitbot':
                    self.out_msg += self.exit_bot_mode()
                elif my_msg.startswith('/nlp'):
                    self.out_msg += self.handle_nlp_command(my_msg)
                elif my_msg == '/archive':
                    self.out_msg += self.archive_status()
                elif my_msg == 'time':
                    self.out_msg += self.request_server_time()
                elif my_msg == 'who':
                    self.out_msg += self.list_online_users()
                elif my_msg == '/chatbots':
                    self.out_msg += self.list_chatbots()
                elif my_msg.startswith('/chatbot:'):
                    bot_name = my_msg.split(':', 1)[1]
                    self.out_msg += self.select_chatbot(bot_name)
                elif my_msg.startswith('/personality:'):
                    personality = my_msg.split(':', 1)[1]
                    self.out_msg += self.set_bot_personality(personality)
                elif my_msg.startswith('/bot:'):
                    query = my_msg.split(':', 1)[1].strip()
                    if len(query) > 0:
                        self.out_msg += self.format_bot_exchange(query)
                    else:
                        self.out_msg += 'Usage: /bot: your question'
                elif my_msg.startswith('@bot'):
                    query = my_msg[4:].strip()
                    if len(query) > 0:
                        mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                        self.out_msg += self.format_chat_message('[' + self.me + ']', my_msg)
                        answer = self.ask_bot(query)
                        self.out_msg += self.format_chat_message('[Bot]', answer)
                        mysend(self.s, json.dumps({"action":"exchange", "from":"[Bot]", "message":answer}))
                    else:
                        self.out_msg += 'Usage: @bot your question'
                elif my_msg == '/summary':
                    self.out_msg += self.summarize_history()
                elif my_msg == '/keywords':
                    self.out_msg += self.extract_keywords()
                elif my_msg.startswith('/aipic:'):
                    prompt = my_msg.split(':', 1)[1]
                    self.out_msg += self.generate_ai_picture(prompt)
                elif my_msg == 'p' or my_msg.startswith('p '):
                    poem_idx = my_msg[1:].strip()
                    self.out_msg += self.request_sonnet(poem_idx)
                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    self.out_msg += self.search_logs(term)
                elif my_msg == 'c' or my_msg.startswith('c '):
                    self.out_msg += 'You are already connected with ' + self.peer + '. Disconnect first before connecting to someone else.\n'
                elif self.bot_mode:
                    self.out_msg += self.format_bot_exchange(my_msg)
                else:
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                    self.out_msg += self.format_chat_message('[' + self.me + ']', my_msg)
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.out_msg += self.peer + ' disconnected. You are back at the menu.\n'
                    self.peer = ''
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += self.format_chat_message(peer_msg["from"], peer_msg["message"])


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
