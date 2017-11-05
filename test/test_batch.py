#!/usr/bin/env python
"""Unit test for database module."""
import test_utils
import batch
import database
import unittest


class TestBatchModule(unittest.TestCase):
    """Class to execute unit tests for batch.py."""

    @classmethod
    def setUpClass(self):
        """Set up function called when class is consructed."""
        self.test_case_list = []

    def test_log_batch_batch_start(self):
        """Test log batch function with batch start batch."""
        test_case_name = test_utils.test_case_name(self.test_case_list)
        self.test_case_list.append({'class': 'BatchOwner', 'test_case': test_case_name})

        # Create batch owner
        with database.DbOperation('BatchOwner') as op:
            batch_owner = op.create(name=test_case_name)

        # Start batch
        batch_record = batch.log_batch(batch_owner.id, 'Batch start')

        self.assertEqual(batch_record.batchOwnerId, batch_owner.id)
        self.assertEqual(batch_record.statusId, 1)

    def test_log_batch_batch_stop(self):
        """Test log batch function with batch stop batch."""
        test_case_name = test_utils.test_case_name(self.test_case_list)
        self.test_case_list.append({'class': 'BatchOwner', 'test_case': test_case_name})

        # Create batch owner
        with database.DbOperation('BatchOwner') as op:
            batch_owner = op.create(name=test_case_name)

        # Start and stop batch
        batch_record = batch.log_batch(batch_owner.id, 'Batch start')
        batch_record = batch.log_batch(batch_owner.id, 'Batch stop')

        self.assertEqual(batch_record.batchOwnerId, batch_owner.id)
        self.assertEqual(batch_record.statusId, 2)

    @classmethod
    def tearDownClass(self):
        """Tear down function called when class is deconstructed."""
        for test_case in self.test_case_list:
            with database.DbOperation(test_case['class']) as op:
                op.delete(name=test_case['test_case'])


if __name__ == '__main__':
    # Test log batch function in batch module
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBatchModule)
    unittest.TextTestRunner(verbosity=2).run(suite)