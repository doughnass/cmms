from unittest import mock

from django.test import TestCase


class TasksEmailTests(TestCase):
    @mock.patch("cmms.tasks.send_mail")
    def test_send_assignment_email_success(self, mock_send):
        # simulate send_mail returning 1 (sent)
        mock_send.return_value = 1
        from cmms.tasks import send_assignment_email

        result = send_assignment_email("user@example.com", "subj", "body")
        self.assertTrue(result)
        mock_send.assert_called_once()

    @mock.patch("cmms.tasks.send_mail")
    def test_send_assignment_email_failure(self, mock_send):
        # simulate send_mail raising an exception
        mock_send.side_effect = Exception("SMTP error")
        from cmms.tasks import send_assignment_email

        result = send_assignment_email("user@example.com", "subj", "body")
        self.assertFalse(result)
        mock_send.assert_called_once()
