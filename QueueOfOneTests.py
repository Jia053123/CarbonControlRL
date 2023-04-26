import unittest
from QueueOfOne import QueueOfOne
from queue import Empty, Full

class TestStringMethods(unittest.TestCase):

    def test_access(self):
        q = QueueOfOne()
        q.put_overwrite(1)
        self.assertEqual(q.get_wait(), 1)
        return
    
    def test_overwrite(self):
        q = QueueOfOne()
        q.put_overwrite(1)
        q.put_overwrite(2)
        self.assertEqual(q.get_wait(), 2)
        return
    
    def test_empty(self):
        q = QueueOfOne(timeoutForGet=1)
        with self.assertRaises(Empty):
            q.get_wait()
        return

    def test_integrated(self):
        q = QueueOfOne(timeoutForGet=1)
        q.put_overwrite(1)
        q.put_overwrite(2)
        self.assertEqual(q.get_wait(), 2)
        with self.assertRaises(Empty):
            q.get_wait()
        return

if __name__ == '__main__':
    unittest.main()