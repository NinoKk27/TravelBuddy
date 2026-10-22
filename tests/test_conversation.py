import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from chatbot import Step, TravelBuddy, TRIP_TYPES
from config import Settings
from llm_client import request_reply
import main


class ConversationTests(unittest.TestCase):
    def test_greeting_and_session_isolation(self):
        first, second = TravelBuddy(), TravelBuddy()
        self.assertIn('exit', first.start())
        first.start()
        self.assertEqual(len(first.state.history), 1)
        self.assertEqual(second.state.history, [])

    def test_each_choice_by_number_and_name(self):
        for index, name in enumerate(TRIP_TYPES, 1):
            for answer in (str(index), '  ' + name.upper() + '  '):
                with self.subTest(answer=answer):
                    bot = TravelBuddy()
                    greeting = bot.start()
                    reply = bot.respond(answer)
                    self.assertEqual(bot.state.trip_type, name)
                    self.assertEqual(bot.state.step, Step.ACCOMMODATION)
                    self.assertEqual(bot.state.history, [
                        {'role': 'assistant', 'content': greeting},
                        {'role': 'user', 'content': answer},
                        {'role': 'assistant', 'content': reply},
                    ])
                    self.assertIsNone(bot.state.accommodation)
                    self.assertIsNone(bot.state.activity)

    def test_invalid_input_then_valid_choice(self):
        bot = TravelBuddy()
        for answer in ('', '0', '4', 'hello'):
            bot.respond(answer)
            self.assertEqual(bot.state.step, Step.TRIP_TYPE)
            self.assertIsNone(bot.state.trip_type)
        bot.respond('2')
        self.assertEqual(bot.state.trip_type, TRIP_TYPES[1])

    def test_exit(self):
        bot = TravelBuddy()
        self.assertIn('Goodbye', bot.respond(' EXIT '))
        self.assertEqual(bot.state.step, Step.EXITED)
        bot.respond('1')
        self.assertIsNone(bot.state.trip_type)

    def test_console_selection(self):
        with patch.object(main, 'create_client'), patch.object(main, 'ModelAssistant', return_value=lambda messages: 'Happy travels!'), patch.object(main, 'load_settings', return_value=Settings('fake-key', 'test-model')), patch('builtins.input', side_effect=['1', '2', '3', 'exit']), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main([]), 0)
        self.assertIn('Beach getaway', output.getvalue())
        self.assertIn('saved', output.getvalue())

    def test_console_eof(self):
        with patch.object(main, 'create_client'), patch.object(main, 'ModelAssistant', return_value=lambda messages: 'Happy travels!'), patch.object(main, 'load_settings', return_value=Settings('fake-key', 'test-model')), patch('builtins.input', side_effect=EOFError), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.main([]), 0)
        self.assertIn('Goodbye', output.getvalue())


class RequestTests(unittest.TestCase):
    def test_request_and_text_extraction(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=' Hello! '))])
        messages = [{'role': 'user', 'content': 'Hi'}]
        self.assertEqual(request_reply(client, 'test-model', messages), 'Hello!')
        client.chat.completions.create.assert_called_once_with(model='test-model', messages=messages, max_tokens=150)
        self.assertEqual(messages, [{'role': 'user', 'content': 'Hi'}])

    def test_empty_responses(self):
        for choices in ([], [SimpleNamespace(message=SimpleNamespace(content=None))], [SimpleNamespace(message=SimpleNamespace(content=' '))]):
            client = Mock()
            client.chat.completions.create.return_value = SimpleNamespace(choices=choices)
            with self.assertRaises(ValueError):
                request_reply(client, 'test-model', [])


if __name__ == '__main__':
    unittest.main()
