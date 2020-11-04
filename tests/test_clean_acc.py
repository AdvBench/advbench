import unittest
import json

import torch

from tests.config import get_test_config
from robustbench.utils import load_model, clean_accuracy
from robustbench.data import load_cifar10
from robustbench.model_zoo.models import model_dicts
from tests.utils_testing import slow


class CleanAccTester(unittest.TestCase):
    def test_clean_acc_jsons_fast(self):
        config = get_test_config()
        device = torch.device(config['device'])
        n_ex = 200
        x_test, y_test = load_cifar10(n_ex, config['data_dir'])
        x_test, y_test = x_test.to(device), y_test.to(device)

        for norm in model_dicts.keys():
            print('Test models robust wrt {}'.format(norm))
            models = list(model_dicts[norm].keys())
            models.remove('Standard')  # removed temporarily to avoid an error for pytorch 1.4.0

            n_tests_passed = 0
            for model_name in models:
                model = load_model(model_name, config['model_dir'], norm).to(device)

                acc = clean_accuracy(model, x_test, y_test, batch_size=config['batch_size'])

                self.assertGreater(round(acc * 100., 2), 70.0)
                success = round(acc * 100., 2) > 70.0
                n_tests_passed += success
                print('{}: clean accuracy {:.2%} (on {} examples), test passed: {}'.format(model_name, acc, n_ex, success))

            print('Test is passed for {}/{} models.'.format(n_tests_passed, len(models)))

    @slow
    def test_clean_acc_jsons_exact(self):
        config = get_test_config()
        device = torch.device(config['device'])
        n_ex = 10000
        x_test, y_test = load_cifar10(n_ex, config['data_dir'])
        x_test, y_test = x_test.to(device), y_test.to(device)

        for norm in model_dicts.keys():
            print('Test models robust wrt {}'.format(norm))
            models = list(model_dicts[norm].keys())
            models.remove('Standard')  # removed temporarily to avoid an error for pytorch 1.4.0

            n_tests_passed = 0
            for model_name in models:
                model = load_model(model_name, config['model_dir'], norm).to(device)

                acc = clean_accuracy(model, x_test, y_test, batch_size=config['batch_size'])
                with open('./model_info/{}/{}.json'.format(norm, model_name), 'r') as model_info:
                    json_dict = json.load(model_info)

                success = abs(round(acc * 100., 2) - float(json_dict['clean_acc'])) <= 0.05
                print('{}: clean accuracy {:.2%}, test passed: {}'.format(model_name, acc, success))
                self.assertLessEqual(abs(round(acc * 100., 2) - float(json_dict['clean_acc'])), 0.05)
                n_tests_passed += success

            print('Test is passed for {}/{} models.'.format(n_tests_passed, len(models)))


