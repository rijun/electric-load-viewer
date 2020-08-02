from unittest import TestCase

import default_load_profile


class TestDefaultLoadProfile(TestCase):
    def setUp(self) -> None:
        self.dlp = default_load_profile.DefaultLoadProfile()

    def test_calculate_profile(self):
        self.assertEqual(self.dlp.calculate_profile('2020-06-01', 13200), 534.3)
