import unittest
from brainfuck_interpreter import BFMachine


class TestBFMachine(unittest.TestCase):
    code_hello = b'++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'
    code_quine = b'->+>+++>>+>++>+>+++>>+>++>>>+>+>+>++>+>>>>+++>+>>++>+>+++>>++>++>>+>>+>++>++>+>>>>+++>+>>>>++>++>>>>+>>++>+>+++>>>++>>++++++>>+>>++>+>>>>+++>>+++++>>+>+++>>>++>>++>>+>>++>+>+++>>>++>>+++++++++++++>>+>>++>+>+++>+>+++>>>++>>++++>>+>>++>+>>>>+++>>+++++>>>>++>>>>+>+>++>>+++>+>>>>+++>+>>>>+++>+>>>>+++>>++>++>+>+++>+>++>++>>>>>>++>+>+++>>>>>+++>>>++>+>+++>+>+>++>>>>>>++>>>+>>>++>+>>>>+++>+>>>+>>++>+>++++++++++++++++++>>>>+>+>>>+>>++>+>+++>>>++>>++++++++>>+>>++>+>>>>+++>>++++++>>>+>++>>+++>+>+>++>+>+++>>>>>+++>>>+>+>>++>+>+++>>>++>>++++++++>>+>>++>+>>>>+++>>++++>>+>+++>>>>>>++>+>+++>>+>++>>>>+>+>++>+>>>>+++>>+++>>>+[[->>+<<]<+]+++++[->+++++++++<]>.[+]>>[<<+++++++[->+++++++++<]>-.------------------->-[-<.<+>>]<[+]<+>>>]<<<[-[-[-[>>+<++++++[->+++++<]]>++++++++++++++<]>+++<]++++++[->+++++++<]>+<<<-[->>>++<<<]>[->>.<<]<<]'
    code_no_loop = b'++++++++>->-->--->----<<'
    code_loop = b'+++[-]'

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

    def test_reset_mem(self):
        m = BFMachine(b'+++')  # modifies mem first
        m.run()
        m.reset_mem()
        self.assertEqual(len(m.memory), 1)
        self.assertEqual(m.memory, b'\x00')

    def test_quine_test(self):
        with self.assertRaises(TypeError):
            BFMachine.quine_test(0)

        with self.assertRaises(ValueError):
            BFMachine.quine_test('')


        self.assertFalse(BFMachine.quine_test(self.code_hello))
        self.assertTrue(BFMachine.quine_test(self.code_quine))

    def test_hello_world(self):
        m = BFMachine(self.code_hello)
        out = m.run()
        self.assertEqual(out, b'Hello World!\n')

    def test_property_code(self):
        m = BFMachine(self.code_hello)
        self.assertEqual(m.code, self.code_hello)

    def test_property_cycles(self):
        m = BFMachine(self.code_no_loop)
        self.assertEqual(m.cycles, 0)
        m.run()
        self.assertEqual(m.cycles, len(self.code_no_loop))

    def test_property_memory(self):
        m = BFMachine(self.code_no_loop)
        self.assertEqual(len(m.memory), 1)
        self.assertEqual(m.memory, b'\x00')
        m.run()
        self.assertEqual(len(m.memory), 5)
        self.assertEqual(m.memory, b'\x08\xff\xfe\xfd\xfc')

    def test_property_memory_pointer(self):
        m = BFMachine(self.code_no_loop)
        self.assertEqual(m.memory_pointer, 0)
        m.run()
        self.assertEqual(m.memory_pointer, 2)

    def test_property_pc(self):
        m = BFMachine(self.code_no_loop)
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, len(self.code_no_loop))

        m = BFMachine(self.code_loop)
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, len(self.code_loop))



if __name__ == '__main__':
    unittest.main()