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

        m = BFMachine(b'+[+]')
        self.assertEqual(m.code, b'+[+]')
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
        self.assertEqual(m.memory, b'\x00')

    def test_quine_test(self):
        with self.assertRaises(TypeError):
            BFMachine.quine_test(0)

        with self.assertRaises(ValueError):
            BFMachine.quine_test('')

        self.assertFalse(BFMachine.quine_test(self.code_hello))
        self.assertTrue(BFMachine.quine_test(self.code_quine))
        self.assertTrue(BFMachine.quine_test(self.code_quine.decode()))

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
        self.assertEqual(m.memory, b'\x00')
        m.run()
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

    def test_init_invalid_code(self):
        with self.assertRaises(TypeError):
            m = BFMachine(666)

    def test_run_with_invalid_input(self):
        m = BFMachine(b',.')

        with self.assertRaises(TypeError):
            m.run(1)

    def test_run_without_code(self):
        m = BFMachine()
        with self.assertRaises(ValueError):
            m.run()

    def test_input(self):
        m = BFMachine(b',>,')
        self.assertEqual(m.pc, 0)
        m.run(b'\xcc\xdd')
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.memory_pointer, 1)
        self.assertEqual(m.memory, b'\xcc\xdd')

        m.run('he')
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.memory_pointer, 1)
        self.assertEqual(m.memory, b'he')

    def test_halt(self):
        m = BFMachine(b'+!+')
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, 1)
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.memory, b'\x01')

    def test_whitespace(self):
        m = BFMachine(b'   .')
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.memory, b'\x00')

        m = BFMachine(b'   ') # purely whitespace
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.memory, b'\x00')

    def test_comment(self):
        m = BFMachine(b'#+\n')
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.memory, b'\x00')

        m = BFMachine(b'#+') # no '\n' to terminate the comment
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.pc, 3)
        self.assertEqual(m.memory_pointer, 0)
        self.assertEqual(m.memory, b'\x00')

    def test_invalid_opcode(self):
        m = BFMachine(b'+@+')
        self.assertEqual(m.pc, 0)

        with self.assertRaises(SyntaxError):
            m.run()

    def test_index_error(self):
        m = BFMachine(b'<.')
        self.assertEqual(m.pc, 0)

        with self.assertRaises(IndexError):
            m.run()

    def test_unmatched_left_bracket(self):
        m = BFMachine(b'[')
        self.assertEqual(m.pc, 0)
        with self.assertRaises(SyntaxError):
            m.run()

    def test_unmatched_right_bracket(self):
        m = BFMachine(b'-]') # note that an extra '-' is added to force interpreter to complain
        self.assertEqual(m.pc, 0)

        with self.assertRaises(SyntaxError):
            m.run()

    def test_cycle_limit(self):
        m = BFMachine(b'+[+]')
        self.assertEqual(m.pc, 0)

        with self.assertRaises(TypeError):
            m.run(cycle_limit="awesome")

        with self.assertRaises(ValueError):
            m.run(cycle_limit=-1)

        with self.assertRaises(TimeoutError):
            m.run(cycle_limit=100)

        m.run()
        self.assertEqual(m.pc, 4)
        self.assertEqual(m.memory, b'\x00')
        self.assertEqual(m.memory_pointer, 0)

    def test_run_without_reset_mem(self):
        m = BFMachine(b'+')
        self.assertEqual(m.pc, 0)
        m.run()
        self.assertEqual(m.memory, b'\x01')
        m.run(reset_mem=False)
        self.assertEqual(m.memory, b'\x02')

if __name__ == '__main__':
    unittest.main()
