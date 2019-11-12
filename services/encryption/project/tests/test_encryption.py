import json
import unittest

from project.tests.base import BaseTestCase


class TestEncryptionService(BaseTestCase):
    """Tests for the Encryption Service."""

    def test_orders_ping(self):
        """Ensure the ping route behaves correctly."""
        response = self.client.get('/keys/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_key(self):
        """Test generating and retrieving a key"""
        with self.client:
            for i in range(3):  # Make sure we can generate a new key (i.e. overwrite the old one)
                response = self.client.post(
                    '/keys',
                    data=json.dumps({'user_id': 1}),
                    content_type='application/json'
                )
                data = json.loads(response.data.decode())
                self.assertEqual(response.status_code, 201)
                self.assertIn('success', data['status'])
                self.assertIn('Successfully generated a new key', data['message'])

            response = self.client.get('/keys/1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIsNotNone(data['key'])


if __name__ == '__main__':
    unittest.main()
