from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class MultiAccountFlowTests(TestCase):
    def setUp(self):
        # create two users
        self.u1 = User.objects.create_user(username="ta_test_a", password="pass_a")
        self.u2 = User.objects.create_user(username="ta_test_b", password="pass_b")
        self.client = Client()

    def test_add_and_switch_account(self):
        # login as first user
        logged = self.client.login(username="ta_test_a", password="pass_a")
        self.assertTrue(logged)

        # add second account
        resp = self.client.post(
            "/accounts/add/", {"username": "ta_test_b", "password": "pass_b"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("ok"))
        # session should contain alt_accounts
        self.assertIn("alt_accounts", self.client.session)
        alts = self.client.session.get("alt_accounts")
        self.assertTrue(any(a["username"] == "ta_test_b" for a in alts))

        # switch to second account
        resp2 = self.client.post("/accounts/switch/", {"username": "ta_test_b"})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertTrue(data2.get("ok"))

        # now session auth user id should be u2's id
        self.assertEqual(int(self.client.session.get("_auth_user_id")), self.u2.pk)

        # remove the account
        resp3 = self.client.post("/accounts/remove/", {"username": "ta_test_b"})
        self.assertEqual(resp3.status_code, 200)
        d3 = resp3.json()
        self.assertTrue(d3.get("ok"))
        # alt_accounts should no longer contain ta_test_b
        alts2 = self.client.session.get("alt_accounts", [])
        self.assertFalse(any(a["username"] == "ta_test_b" for a in alts2))
