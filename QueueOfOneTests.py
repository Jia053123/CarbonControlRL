import unittest
from QueueOfOne import QueueOfOne
from queue import Empty, Full

class TestStringMethods(unittest.TestCase):

    def test_access(self):
        q = QueueOfOne()
        q.put(1)
        self.assertEqual(q.get(), 1)
        return
    
    def test_overwrite(self):
        q = QueueOfOne()
        q.put(1)
        q.put(2)
        self.assertEqual(q.get(), 2)
        return
    
    def test_empty(self):
        q = QueueOfOne(timeoutForGet=1)
        q.put(1)
        self.assertEqual(q.get(), 1)
        with self.assertRaises(Empty):
            q.get()
        return

if __name__ == '__main__':
    unittest.main()