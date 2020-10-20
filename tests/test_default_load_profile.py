import pathlib
from unittest import TestCase

import numpy as np
import pandas as pd

from dlp import DefaultLoadProfile


class TestDefaultLoadProfile(TestCase):
    def setUp(self):
        self.dlp = DefaultLoadProfile()

    def test_calculate_profile(self):
        sample_df = pd.read_csv(pathlib.Path('default_load_profiles') / 'sample.csv')
        selection = 42
        calc_data = self.dlp.calculate_profile(sample_df.iloc[selection]['date'], 1000)
        sample_data = sample_df.iloc[selection][1:].astype('float64')
        self.assertTrue(np.allclose(calc_data.values, sample_data.values, rtol=0.1))
