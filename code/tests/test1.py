import unittest
from code.keychain import blockchain

class TestStringMethods(unittest.TestCase):

    def test_blockchain(self):
        bc = blockchain.Blockchain(bootstrap=0, difficulty=4)
        self.assertEqual(bc._blocks, [])
        self.assertEqual(bc._peers, [])
        self.assertEqual(bc._transactions, [])
        self.assertEqual(bc._difficulty, 4)

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()