import unittest
from brainfuck_interpreter import BFMachine

class TestBFMachine(unittest.TestCase):
    def test_init(self):
        m = BFMachine()
        self.assertIsNone(m.code)
        self.assertEqual(m.cycles, 0)
        self.assertEqual(m.memory, b'\x00')
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.pc, 0)

        m = BFMachine(b'[+]')
        self.assertEqual(m.code, b'[+]')
        self.assertEqual(m.cycles, 0)
        self.assertEqual(m.memory, b'\x00')
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.pc, 0)

    def test_load_code(self):
        m = BFMachine()

        with self.assertRaises(TypeError):
            m.load_code(0)

        with self.assertRaises(ValueError):
            m.load_code('')

        m.load_code('++')
        self.assertEqual(m.code, b'++')

        m.load_code(b'--')
        self.assertEqual(m.code, b'--')

    # TODO: fill in the following test functions

    def test_reset_mem(self):
        pass

    def test_run(self):
        pass

    def test_quine_test(self):
        pass

if __name__ == '__main__':
    unittest.main()
