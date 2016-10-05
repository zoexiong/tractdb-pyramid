import requests
import unittest

ACCOUNT_URL = 'http://localhost:8080/account'
ACCOUNT_COLLECTION_URL = 'http://localhost:8080/accounts'

TEST_ACCOUNT = 'testaccountview_account'
TEST_ACCOUNT_PASSWORD = 'testaccountview_password'


class TestAccountView(unittest.TestCase):
    def test_create_and_delete_account(self):
        # Get the current accounts
        r = requests.get(
            ACCOUNT_COLLECTION_URL,
        )
        self.assertEqual(r.status_code, 200)

        # Ensure it does not already exist (this could fail silently if the account doesn't exist)
        r = requests.delete(
            '{}/{}'.format(
                ACCOUNT_URL,
                TEST_ACCOUNT
            )
        )

        # Create the account
        r = requests.post(
            ACCOUNT_COLLECTION_URL,
            json={
                'account': TEST_ACCOUNT,
                'password': TEST_ACCOUNT_PASSWORD
            }
        )
        self.assertEqual(r.status_code, 201)

        # Test the creating it again fails
        r = requests.post(
            ACCOUNT_COLLECTION_URL,
            json={
                'account': TEST_ACCOUNT,
                'password': TEST_ACCOUNT_PASSWORD
            }
        )
        self.assertEqual(r.status_code, 409)

        # Test the account exists
        r = requests.get(
            ACCOUNT_COLLECTION_URL,
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn(TEST_ACCOUNT, r.json()['accounts'])

        # Delete the account
        r = requests.delete(
            '{}/{}'.format(
                ACCOUNT_URL,
                TEST_ACCOUNT
            )
        )
        self.assertEqual(r.status_code, 200)

        # Test that deleting the account again fails
        r = requests.delete(
            '{}/{}'.format(
                ACCOUNT_URL,
                TEST_ACCOUNT
            )
        )
        self.assertEqual(r.status_code, 404)

        # Test the account is gone
        r = requests.get(
            ACCOUNT_COLLECTION_URL,
        )
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(TEST_ACCOUNT, r.json()['accounts'])
