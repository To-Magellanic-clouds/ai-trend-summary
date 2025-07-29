import unittest
from unittest.mock import patch, MagicMock
import os
from src.infrastructure.utils.LLMUtil import get_provider

class TestLLMProvider(unittest.TestCase):

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("requests.get")
    def test_openai_list_models(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": "gpt-3.5-turbo"}, {"id": "gpt-4"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = get_provider("openai")
        models = provider.list_models()
        self.assertEqual(models, ["gpt-3.5-turbo", "gpt-4"])

    @patch.dict(os.environ, {"LOCALAI_API_KEY": "test_key"})
    @patch("requests.get")
    def test_compatible_openai_list_models(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": "local-model-1"}, {"id": "local-model-2"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = get_provider("localai", api_base="http://localhost:8080/v1")
        models = provider.list_models()
        self.assertEqual(models, ["local-model-1", "local-model-2"])

    def test_huggingface_list_models(self):
        provider = get_provider("huggingface")
        models = provider.list_models()
        self.assertEqual(models, ["google/flan-t5-xl", "gpt2", "bert-base-uncased"])

    @patch("requests.get")
    def test_ollama_list_models(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"models": [{"name": "ollama-model-1"}, {"name": "ollama-model-2"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = get_provider("ollama", model_name="test")
        models = provider.list_models()
        self.assertEqual(models, ["ollama-model-1", "ollama-model-2"])

    def test_anthropic_list_models(self):
        provider = get_provider("claude")
        models = provider.list_models()
        self.assertEqual(models, ["claude-2", "claude-instant-1"])

if __name__ == '__main__':
    unittest.main()