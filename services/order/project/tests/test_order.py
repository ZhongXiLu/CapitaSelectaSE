import json
import unittest
import responses

from project.tests.base import BaseTestCase


class TestOrderService(BaseTestCase):
    """Tests for the Order Service."""

    # Some dummy user data to use in the tests
    user_data = {
        'id': 1,
        'card_type': 'VISA',
        'card_holder_name': 'YnQ1mbCwOvOM69QRzAqj+KzCKx69J0JzhLIyb+XeUVA=',
        'card_number': 'YnQ1mbCwOvOM69QRzAqj+Fi5e0J7KK0RGUnSsKmyyX0ac21kvRfEcafDIfy6krB3',
        'expiration_date_month': 'YnQ1mbCwOvOM69QRzAqj+Pt3yrjRpg7exXoJLIHJKiw=',
        'expiration_date_year': 'YnQ1mbCwOvOM69QRzAqj+KdnlGk4qD/cclQNy1Wn0Uw=',
        'cvv': 'YnQ1mbCwOvOM69QRzAqj+L1ssgB+BwoiZ9bZnWRaKoA='
    }

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
                      json={'valid_token': True, 'user': self.user_data}, status=200)
        responses.add(responses.POST, 'http://payment:5000/payment',
                      json={'payment_successful': True}, status=201)

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
                      json={'valid_token': True, 'user': self.user_data}, status=200)
        responses.add(responses.POST, 'http://payment:5000/payment',
                      json={'payment_successful': True}, status=201)

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
                      json={'valid_token': False, 'user': self.user_data}, status=200)

        response = self.order_ticket(1, '123456789')

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('User verification failed', data['message'])

    @responses.activate
    def failed_payment(self):
        """Test failed payment"""
        responses.add(responses.POST, 'http://user:5000/users/verify',
                      json={'valid_token': True, 'user': self.user_data}, status=200)
        responses.add(responses.POST, 'http://payment:5000/payment',
                      json={'payment_successful': False}, status=201)

        response = self.order_ticket(1, '123456789')

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn(f'Failed processing the payment with {self.user_data["card_type"]}', data['message'])


if __name__ == '__main__':
    unittest.main()
