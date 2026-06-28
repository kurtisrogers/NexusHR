from django.test import SimpleTestCase
from django.test.client import Client


class HealthzTests(SimpleTestCase):
    def test_healthz_returns_ok(self):
        response = Client().get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})
