import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from config import ConfigurationError, Settings, load_settings
import main


class ConfigurationTests(unittest.TestCase):
    def test_file_settings_and_environment_precedence(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            env_file = Path(folder) / '.env'
            env_file.write_text('OPENROUTER_API_KEY=file-key\nOPENROUTER_MODEL=file-model\n')
            with patch.dict(os.environ, {}, clear=True):
                settings = load_settings(env_file)
                self.assertEqual((settings.api_key, settings.model), ('file-key', 'file-model'))
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'env-key', 'OPENROUTER_MODEL': 'env-model'}, clear=True):
                settings = load_settings(env_file)
                self.assertEqual((settings.api_key, settings.model), ('env-key', 'env-model'))
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': ''}, clear=True):
                with self.assertRaises(ConfigurationError):
                    load_settings(env_file)

    def test_invalid_settings_and_key_redaction(self):
        for key, model in [('', 'model'), (' ', 'model'), ('replace_with_your_key', 'model'), ('key', ''), ('key', ' ')]:
            with self.subTest(key=key, model=model), self.assertRaises(ConfigurationError):
                Settings(key, model)
        settings = Settings(' secret-test-key ', ' model ')
        self.assertEqual(settings.api_key, 'secret-test-key')
        self.assertEqual(settings.model, 'model')
        self.assertNotIn('secret-test-key', repr(settings))

    def test_missing_file(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ConfigurationError):
            load_settings(Path(__file__).parent / 'nonexistent.env')

    def test_configuration_failure_prevents_client_creation(self):
        with patch.object(main, 'load_settings', side_effect=ConfigurationError('Set OPENROUTER_API_KEY')), patch.object(main, 'create_client') as client, contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(main.main([]), 1)
        client.assert_not_called()
        self.assertIn('Configuration error', output.getvalue())

    def test_client_closed_after_exit(self):
        with patch.object(main, 'load_settings', return_value=Settings('fake-key', 'model')), patch.object(main, 'create_client') as factory, patch('builtins.input', return_value='exit'), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main([]), 0)
        factory.return_value.__exit__.assert_called_once()
        factory.return_value.__enter__.return_value.chat.completions.create.assert_not_called()


if __name__ == '__main__':
    unittest.main()
