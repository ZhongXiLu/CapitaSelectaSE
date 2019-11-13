import json
import unittest
import responses

from project.tests.base import BaseTestCase


class TestPaymentService(BaseTestCase):
    """Tests for the Payment Service."""

    def test_orders_ping(self):
        """Ensure the ping route behaves correctly."""
        response = self.client.get('/payment/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    @responses.activate
    def test_create_payment(self):
        """Test creating a new payment"""
        responses.add(responses.GET, 'http://encryption:5000/keys/1',
                      json={'status': 'success', 'key': {
                          'key': '1b7acec1675eb24d64d3497726da095b',
                          'IV': '62743599b0b03af38cebd411cc0aa3f8'}
                            }, status=200)

        with self.client:
            response = self.client.post(
                '/payment',
                data=json.dumps({
                    'user_id': 1,
                    'card_type': 'VISA',
                    'card_holder_name': 'YnQ1mbCwOvOM69QRzAqj+KzCKx69J0JzhLIyb+XeUVA=',
                    'card_number': 'YnQ1mbCwOvOM69QRzAqj+Fi5e0J7KK0RGUnSsKmyyX0ac21kvRfEcafDIfy6krB3',
                    'expiration_date_month': 'YnQ1mbCwOvOM69QRzAqj+Pt3yrjRpg7exXoJLIHJKiw=',
                    'expiration_date_year': 'YnQ1mbCwOvOM69QRzAqj+KdnlGk4qD/cclQNy1Wn0Uw=',
                    'cvv': 'YnQ1mbCwOvOM69QRzAqj+L1ssgB+BwoiZ9bZnWRaKoA=',
                    'amount': 100
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            self.assertIn('Successfully processed transaction', data['message'])
            self.assertTrue(data['payment_successful'])

    @responses.activate
    def test_create_payment_unsupported_credit_card(self):
        """Test creating a new payment with an unsupported credit card type"""
        responses.add(responses.GET, 'http://encryption:5000/keys/1',
                      json={'status': 'success', 'key': {
                          'key': '1b7acec1675eb24d64d3497726da095b',
                          'IV': '62743599b0b03af38cebd411cc0aa3f8'}
                            }, status=200)

        with self.client:
            response = self.client.post(
                '/payment',
                data=json.dumps({
                    'user_id': 1,
                    'card_type': 'Unsupported Credit Card',
                    'card_holder_name': 'YnQ1mbCwOvOM69QRzAqj+KzCKx69J0JzhLIyb+XeUVA=',
                    'card_number': 'YnQ1mbCwOvOM69QRzAqj+Fi5e0J7KK0RGUnSsKmyyX0ac21kvRfEcafDIfy6krB3',
                    'expiration_date_month': 'YnQ1mbCwOvOM69QRzAqj+Pt3yrjRpg7exXoJLIHJKiw=',
                    'expiration_date_year': 'YnQ1mbCwOvOM69QRzAqj+KdnlGk4qD/cclQNy1Wn0Uw=',
                    'cvv': 'YnQ1mbCwOvOM69QRzAqj+L1ssgB+BwoiZ9bZnWRaKoA=',
                    'amount': 100
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])


if __name__ == '__main__':
    unittest.main()
