import json
import unittest
import responses

from project.tests.base import BaseTestCase


class TestUserService(BaseTestCase):
    """Tests for the User Service."""

    def test_users_ping(self):
        """Ensure the ping route behaves correctly."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    @responses.activate
    def test_preregistration(self):
        """
        Ensure the preregistration, i.e. register, update and retrieve a new user
        and also the verification of the user and their token
        """
        responses.add(responses.POST, 'http://encryption:5000/keys', json={'status': 'success'}, status=201)

        with self.client:
            # Register new user
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'JohnDoe',
                    'password': 'catsanddogs123'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            self.assertIn('JohnDoe was successfully added', data['message'])
            user_id = data['user_id']

            responses.add(responses.GET, f'http://encryption:5000/keys/{user_id}',
                          json={'status': 'success', 'key': {
                              'key': '1b7acec1675eb24d64d3497726da095b',
                              'IV': '62743599b0b03af38cebd411cc0aa3f8'}
                                }, status=200)

            # Update user
            response = self.client.put(
                '/users',
                data=json.dumps({
                    'user_id': user_id,
                    'gender': 'M',
                    'country': 'Belgium',
                    'city': 'Antwerp',
                    'zip_code': '2000',
                    'street': 'Keyserlei 1',
                    'card_type': 'VISA',
                    'card_number': '4512018770127897',
                    'expiration_date_month': 4,
                    'expiration_date_year': 2023,
                    'cvv': '203'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('JohnDoe was successfully updated', data['message'])
            token = data['token']

            # Retrieve the newly added user
            response = self.client.get(f'/users/{user_id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('JohnDoe', data['user']['username'])
            self.assertNotEqual('4512018770127897', data['user']['card_number'])

            # Verify token
            response = self.client.post(
                '/users/verify',
                data=json.dumps({
                    'user_id': user_id,
                    'token': token
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertIn('success', data['status'])
            self.assertIn('JohnDoe has been verified', data['message'])
            self.assertTrue(data['valid_token'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])
            self.assertIn('Invalid payload', data['message'])

    def test_add_user_duplicate_username(self):
        """Ensure error is thrown if the username already exists."""
        with self.client:
            response = None
            for i in range(2):
                response = self.client.post(
                    '/users',
                    data=json.dumps({
                        'username': 'JohnDoe2',
                        'email': 'catsanddogs123'
                    }),
                    content_type='application/json',
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])
            self.assertIn('Username JohnDoe2 already exists', data['message'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/99999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        with self.client:
            for i in range(10):
                self.client.post(
                    '/users',
                    data=json.dumps({
                        'username': 'DoeJohn' + str(i),
                        'email': 'catsanddogs123'
                    }),
                    content_type='application/json',
                )

            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 10)


if __name__ == '__main__':
    unittest.main()
