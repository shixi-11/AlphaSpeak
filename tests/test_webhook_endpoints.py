import importlib
import os
import unittest


class WebhookEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['BOT_TOKEN'] = 'dummy-token'
        os.environ.pop('GITHUB_WEBHOOK_SECRET', None)
        cls.webhook = importlib.import_module('webhook')
        cls.client = cls.webhook.app.test_client()

    def test_health_ok(self):
        resp = self.client.get('/health')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json.get('status'), 'ok')

    def test_github_webhook_disabled_without_secret(self):
        resp = self.client.post('/github-webhook', json={})
        self.assertEqual(resp.status_code, 503)


if __name__ == '__main__':
    unittest.main()
