import json
import unittest
import responses

from project.tests.base import BaseTestCase


class TestOrderService(BaseTestCase):
    """Tests for the Order Service."""

    def order_ticket(self, user_id, token):
        with self.client:
            response = self.client.post(
                '/orders',
                data=json.dumps({
                    'user_id': 1,
                    'token': '123456789'
                }),
                content_type='application/json',
            )
            return response

    def test_orders_ping(self):
        """Ensure the ping route behaves correctly."""
        response = self.client.get('/orders/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    @responses.activate
    def test_order(self):
        """Test an order"""
        responses.add(responses.POST, 'http://user:5000/users/verify',
                      json={'data': {'valid_token': True}}, status=200)

        response = self.order_ticket(1, '123456789')

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('Successfully ordered a new ticket', data['message'])
        self.assertIsNotNone(data['ticket_id'])

    @responses.activate
    def test_out_of_order(self):
        """Test out of order scenario"""
        responses.add(responses.POST, 'http://user:5000/users/verify',
                      json={'data': {'valid_token': True}}, status=200)

        for i in range(350):
            response = self.order_ticket(1, '123456789')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])

        # No more tickets left
        response = self.order_ticket(1, '123456789')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('No more tickets left', data['message'])

    @responses.activate
    def failed_user_verification(self):
        """Test failed user verification"""
        responses.add(responses.POST, 'http://user:5000/users/verify',
                      json={'data': {'valid_token': False}}, status=200)

        response = self.order_ticket(1, '123456789')

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('User verification failed', data['message'])


if __name__ == '__main__':
    unittest.main()
