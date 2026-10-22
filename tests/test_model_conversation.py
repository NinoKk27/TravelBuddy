import contextlib
import io
import unittest
from unittest.mock import Mock, patch

import httpx2 as httpx
from openai import AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError, APIStatusError

from chatbot import Step, TravelBuddy
from llm_client import ModelAssistant, api_error_message
import main


class ModelConversationTests(unittest.TestCase):
    def test_model_receives_instructions_state_and_history(self):
        generate = Mock(return_value='Sounds wonderful!')
        bot = TravelBuddy(generate)
        greeting = bot.start()
        reply = bot.respond('2')
        messages = generate.call_args.args[0]
        self.assertEqual(messages[0]['role'], 'system')
        self.assertIn('Mountain adventure', messages[0]['content'])
        self.assertIn('accommodation', messages[0]['content'])
        self.assertEqual(messages[1], {'role': 'assistant', 'content': greeting})
        self.assertEqual(messages[2], {'role': 'user', 'content': '2'})
        self.assertIn('Sounds wonderful!', reply)
        self.assertIn('Hotel', reply)
        self.assertEqual(bot.state.history[-1]['content'], reply)
        messages[1]['content'] = 'mutated snapshot'
        self.assertEqual(bot.state.history[0]['content'], greeting)

    def test_unrelated_message_preserves_step_and_returns_menu(self):
        generate = Mock(return_value="Let's get back to your getaway.")
        bot = TravelBuddy(generate)
        bot.respond('1')
        reply = bot.respond('Tell me about programming')
        self.assertEqual(bot.state.step, Step.ACCOMMODATION)
        self.assertEqual(bot.state.trip_type, 'Beach getaway')
        self.assertIsNone(bot.state.accommodation)
        self.assertIn('Hotel', reply)
        self.assertEqual(generate.call_args.args[0][-1]['content'], 'Tell me about programming')

    def test_summary_is_exact_even_when_model_fails(self):
        client = Mock()
        client.chat.completions.create.side_effect = APIConnectionError(request=httpx.Request('POST', 'https://example.com'))
        bot = TravelBuddy(ModelAssistant(client, 'test-model'))
        for answer in ('3', '2', '1'):
            reply = bot.respond(answer)
        for value in ('City break', 'Hostel', 'Museum visit', 'Could not connect'):
            self.assertIn(value, reply)
        self.assertEqual(bot.state.step, Step.SUMMARY)
        self.assertEqual(len(bot.state.history), 7)
        self.assertIn('Museum visit', bot.respond('What should I bring?'))

    def test_exit_never_calls_model_at_any_stage(self):
        for answers in ([], ['1'], ['1', '2'], ['1', '2', '3']):
            generate = Mock(return_value='Great!')
            bot = TravelBuddy(generate)
            for answer in answers:
                bot.respond(answer)
            generate.reset_mock()
            self.assertIn('Goodbye', bot.respond(' EXIT '))
            generate.assert_not_called()
            self.assertEqual(bot.state.step, Step.EXITED)

    def test_console_interrupt_during_request(self):
        bot = TravelBuddy(Mock(side_effect=KeyboardInterrupt))
        with patch('builtins.input', return_value='1'), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main.run_conversation(bot), 0)
        self.assertIn('Goodbye', output.getvalue())
        self.assertEqual(bot.state.step, Step.EXITED)

    def test_error_messages_and_adapter_fallback(self):
        request = httpx.Request('POST', 'https://example.com')
        errors = [
            (AuthenticationError('SECRET', response=httpx.Response(401, request=request), body=None), 'API key'),
            (RateLimitError('SECRET', response=httpx.Response(429, request=request), body=None), 'rate-limited'),
            (APIConnectionError(request=request), 'connect'),
            (APITimeoutError(request=request), 'too long'),
            (APIStatusError('SECRET', response=httpx.Response(402, request=request), body=None), 'credits'),
            (APIStatusError('SECRET', response=httpx.Response(404, request=request), body=None), 'OPENROUTER_MODEL'),
            (APIStatusError('SECRET', response=httpx.Response(503, request=request), body=None), 'temporarily unavailable'),
            (ValueError('SECRET'), 'no usable text'),
        ]
        for error, expected in errors:
            with self.subTest(error=type(error).__name__, expected=expected):
                client = Mock()
                client.chat.completions.create.side_effect = error
                reply = ModelAssistant(client, 'test-model')([])
                self.assertIn(expected, reply)
                self.assertNotIn('SECRET', reply)
                self.assertIn('still use the planner', reply)

    def test_cli_api_check_failure_returns_error_status(self):
        with patch.object(main, 'load_settings'), patch.object(main, 'create_client'), patch.object(main, 'request_reply', side_effect=ValueError('SECRET')), contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(main.main(['--check-api']), 1)
        self.assertNotIn('SECRET', output.getvalue())
        self.assertIn('no usable text', output.getvalue())


if __name__ == '__main__':
    unittest.main()
