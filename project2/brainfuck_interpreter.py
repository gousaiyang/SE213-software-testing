import sys
import string
from io import BytesIO

assert sys.version_info[0] >= 3

class BFMachine:
    def __init__(self, code=None):
        if code is not None:
            self.load_code(code)
        else:
            self._code = None

        self.reset_mem()
        self._cycles = 0
        self._pc = 0

    def load_code(self, code):
        if not isinstance(code, (str, bytes)):
            raise TypeError('code should be str or bytes')

        if not code:
            raise ValueError('code should not be empty')

        if isinstance(code, str):
            code = code.encode()

        self._code = code

    def reset_mem(self):
        self._mem = bytearray(1)
        self._mem_ptr = 0

    def _inc_mem_ptr(self):
        if self._mem_ptr + 1 >= len(self._mem):
            self._mem.append(0)

        self._mem_ptr += 1

    def _dec_mem_ptr(self):
        if self._mem_ptr == 0:
            raise IndexError('memory index out of range')

        self._mem_ptr -= 1

    def _inc_mem(self):
        self._mem[self._mem_ptr] = (self._mem[self._mem_ptr] + 1) % 256

    def _dec_mem(self):
        self._mem[self._mem_ptr] = (self._mem[self._mem_ptr] - 1) % 256

    def _output_byte(self):
        self._fout.write(bytes([self._mem[self._mem_ptr]]))

    def _input_byte(self):
        self._mem[self._mem_ptr] = ord(self._fin.read(1) or b'\x00') # return b'\x00' when EOF

    def _enter_loop(self):
        if self._mem[self._mem_ptr] == 0:
            num_lbracks = 1
            pos = self._pc + 1

            while pos < self._code_len:
                opcode = bytes([self._code[pos]])

                if opcode == b'[':
                    num_lbracks += 1
                elif opcode == b']':
                    num_lbracks -= 1
                    if num_lbracks == 0:
                        self._pc = pos + 1
                        return

                pos += 1

            raise SyntaxError('no matching right bracket for left bracket at position %d' % self._pc)
        else:
            self._pc += 1

    def _exit_loop(self):
        if self._mem[self._mem_ptr] != 0:
            num_rbracks = 1
            pos = self._pc - 1

            while pos >= 0:
                opcode = bytes([self._code[pos]])

                if opcode == b']':
                    num_rbracks += 1
                elif opcode == b'[':
                    num_rbracks -= 1
                    if num_rbracks == 0:
                        self._pc = pos + 1
                        return

                pos -= 1

            raise SyntaxError('no matching left bracket for right bracket at position %d' % self._pc)
        else:
            self._pc += 1

    def _skip_whitespaces(self):
        while self._pc < self._code_len:
            if bytes([self._code[self._pc]]) not in string.whitespace.encode():
                break
            self._pc += 1

    def _skip_comment(self):
        while self._pc < self._code_len: # single line comment
            if bytes([self._code[self._pc]]) == b'\n':
                self._pc += 1
                break
            self._pc += 1

    def run(self, input_=b'', *, reset_mem=True, cycle_limit=None):
        if not isinstance(input_, (str, bytes)):
            raise TypeError('input should be str or bytes')

        if isinstance(input_, str):
            input_ = input_.encode()

        if self._code is None:
            raise ValueError('code not loaded')

        if cycle_limit is not None:
            if not isinstance(cycle_limit, int):
                raise TypeError('cycle limit should be an integer')

            if cycle_limit <= 0:
                raise ValueError('cycle limit should be a positive integer')

        self._fin = BytesIO(input_)
        self._fout = BytesIO()
        self._pc = 0
        self._code_len = len(self._code)
        self._cycles = 0

        if reset_mem:
            self.reset_mem()

        while self._pc < self._code_len:
            opcode = bytes([self._code[self._pc]])

            if opcode == b'>':
                self._inc_mem_ptr()
                self._pc += 1
            elif opcode == b'<':
                self._dec_mem_ptr()
                self._pc += 1
            elif opcode == b'+':
                self._inc_mem()
                self._pc += 1
            elif opcode == b'-':
                self._dec_mem()
                self._pc += 1
            elif opcode == b'.':
                self._output_byte()
                self._pc += 1
            elif opcode == b',':
                self._input_byte()
                self._pc += 1
            elif opcode == b'[':
                self._enter_loop()
            elif opcode == b']':
                self._exit_loop()
            elif opcode == b'!': # halt program
                break
            elif opcode in string.whitespace.encode():
                self._skip_whitespaces()
                continue
            elif opcode == b'#':
                self._skip_comment()
                continue
            else:
                raise SyntaxError('invalid opcode %r at position %d' % (opcode, self._pc))

            self._cycles += 1

            if cycle_limit is not None and self._cycles > cycle_limit:
                raise TimeoutError('cycle limit exceeded')

        return self._fout.getvalue()

    @property
    def code(self):
        return self._code

    @property
    def cycles(self):
        return self._cycles

    @property
    def memory(self):
        return bytes(self._mem)

    @property
    def memory_pointer(self):
        return self._mem_ptr

    @property
    def pc(self):
        return self._pc

    @staticmethod
    def quine_test(code):
        if not isinstance(code, (str, bytes)):
            raise TypeError('code should be str or bytes')

        if not code:
            raise ValueError('code should not be empty')

        if isinstance(code, str):
            code = code.encode()

        return BFMachine(code).run() == code

__all__ = ['BFMachine']


#if __name__ == '__main__':
#    m=BFMachine(b'#\n.')
#    m.run()
#    print(m.memory)
#    print(m.memory_pointer)
#    print(m.pc)
