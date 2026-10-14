#!/usr/bin/env python3
import unittest
import sys
import os
import importlib.util

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    test_file = os.path.join(project_dir, "tests", "test_sst.py")
    spec = importlib.util.spec_from_file_location("test_sst", test_file)
    test_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_mod)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_mod)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
