import re
import sys
import socket
import random

assert sys.version_info[0] >= 3


def file_content(filename, encoding='utf-8'):
    with open(filename, 'rb') as fin:
        content = fin.read()
    return content.decode(encoding)


def get_server_config():
    t = file_content('server.txt').strip().split(' ')
    assert len(t) == 2
    return (t[0], int(t[1]))


target = get_server_config()


def test_raw(data):
    assert isinstance(data, (str, bytes))
    if isinstance(data, str):
        data = data.encode()

    s = socket.socket()
    s.connect(target)
    tips = s.recv(1024).decode()
    s.send(data + b'\n')
    f = s.makefile('r')
    response = f.read()
    f.close()
    s.close()

    res = re.findall(r'The polynomial is: (.*?)\r?\n', response)
    assert len(res) < 2

    return {
        'tips': tips,
        'response': response,
        'poly': res[0] if res else ''
    }


def judge_response(result, expected):
    return expected in result['response']


def judge_poly(result, expected):
    return result['poly'] == expected


test_cases = []


def add_test_case(input_, is_valid, expected_output):
    assert isinstance(input_, (str, list))

    if isinstance(input_, list):
        input_ = ' '.join(str(c) for c in input_)

    test_cases.append({
        'input': input_,
        'expected_output': expected_output,
        'judge_func': judge_poly if is_valid else judge_response
    })


def run_test():
    num_total = len(test_cases)
    num_passed = 0

    for i, test_case in enumerate(test_cases):
        test_case_no = i + 1
        print('Test case %d: ' % test_case_no, end='')

        result = test_raw(test_case['input'])

        judge_result = test_case['judge_func'](result, test_case['expected_output'])
        if judge_result:
            # print('Passed, with input: %r' % test_case['input'])
            print('Passed')
            num_passed += 1
        else:
            print('Failed')
            print('Input: %r' % test_case['input'])
            print('Expected: %r' % test_case['expected_output'])
            print('Got: %r' % result)

    print('---------------- Test Result ----------------')
    print('%d out of %d test cases passed.' % (num_passed, num_total))
    print('Pass rate: %.2f%%' % (num_passed / num_total * 100))


def thousand():
    str = "1" + "0" * 1000
    return str


def one_thousand():
    str = "0." + "0" * 999 + "1"
    return str


def set_up_test_cases():

    ####### number of coefficients X coefficient range #######
    # 0 coefficient
    add_test_case([], True, '')

    # 1 coefficient
    add_test_case([1000], True, '1000')  # normal value
    add_test_case([-1000], True, '-1000')  # normal value
    add_test_case([0], True, '0')  # 0 cannot be omitted
    add_test_case([1], True, '1')  # 1 cannot be omitted
    add_test_case([-1], True, '-1')  # -1 cannot be omitted
    add_test_case([2147483645], True, '2147483645')  # lower than int limit
    add_test_case([2147483646], True, '2147483646')  # equal to int limit
    add_test_case([2147483647], True, '2147483647')  # higher than int limit
    add_test_case([-2147483646], True, '-2147483646')  # lower than int limit
    add_test_case([-2147483647], True, '-2147483647')  # equal to int limit
    add_test_case([-2147483648], True, '-2147483648')  # higher than int limit
    # TODO: small and large float


    # 2 coefficients
    add_test_case([1000, -1000], True, '1000x-1000')  # normal value
    add_test_case([-1000, 1000], True, '-1000x+1000')  # normal value
    add_test_case([0, 0], True, '0')  # leading 0 coefficient should be omitted
    add_test_case([0, 1], True, '1')  # leading 0 coefficient should be omitted
    add_test_case([1, 0], True,
                  'x')  # 1 should be omitted (not expect: 1x); trailing 0 should be omitted (not expect: x+0)
    add_test_case([1, 1], True, 'x+1')  # first 1 should be omitted, second should not
    add_test_case([-1, 0], True,
                  '-x')  # -1 should be omitted (not expect: -1x); trailing 0 should be omitted (not expect: -x+0)
    add_test_case([-1, -1], True, '-x-1')  # first -1 should be omitted, second should not
    add_test_case([2147483645, -2147483646], True, '2147483645x-2147483646')  # lower than int limit
    add_test_case([2147483646, -2147483647], True, '2147483646x-2147483647')  # equal to int limit
    add_test_case([2147483647, -2147483648], True, '2147483647x-2147483648')  # higher than int limit
    # TODO: small and large float


    # 65537 coefficients
    # cannot test to limit 2147483646 due to py list length limit, instead, choose a relatively large number
    add_test_case([1000, -1000]+[0]*65535, True, '1000x^65536-1000x^65535')
    add_test_case([-1000, 1000]+[0]*65535, True, '-1000x^65536+1000x^65535')
    add_test_case([0]*65537,            True, '0')
    add_test_case([0]*65536+[1],        True, '1')
    add_test_case([1]+[0]*65536,        True, 'x^65536')
    add_test_case([1]+[0]*65535+[1],    True, 'x^65536+1')
    add_test_case([-1]+[0]*65536,       True, '-x^65536')
    add_test_case([-1]+[0]*65535+[-1],  True, '-x^65536-1')
    add_test_case([2147483645]+[0]*65535+[-2147483646], True, '2147483645x^65536-2147483646')
    add_test_case([2147483646]+[0]*65535+[-2147483647], True, '2147483646x^65536-2147483647')
    add_test_case([2147483647]+[0]*65535+[-2147483648], True, '2147483647x^65536-2147483648')
    # TODO: small and large float



    ####### random testcases #######
    cnt = 1  # cnt of random input
    for n in range(cnt):
        pos = random.randint(2, 10000)
        neg = -1 * random.randint(2, 10000)
        add_test_case([pos, neg], True, str(pos) + 'x' + str(neg))  # regular case with negative number
        add_test_case([neg, pos], True, str(neg) + 'x+' + str(pos))  # display first neg sign

    ####### invalid input #######
    add_test_case('x', False, 'Invalid coefficient list. Space delimited real numbers expected.')

    ####### input format #######
    add_test_case(["0001", "-0001"], True, 'x-1')  # non standard form of integers
    add_test_case([".100","-1.230"],True,'0.1x-1.23')   #non conforming floats
    add_test_case(["0xa", "0xB"], True, '10x+11')  # hex number support, upper and lower cases
    add_test_case(["1e4", "1e-3", "3.14e2", "-3.14e-3"], True,
                  '10000x^3+0.001x^2+314x-0.00314')  # scientific notation and necessary conversion to integer

    add_test_case([0.1, -0.01], True, '0.1x-0.01')  # float number support
    add_test_case(["1e1000", "0"], True, thousand() + "x")  # real large input
    add_test_case(["1e-1000", "0"], True, one_thousand() + "x")  # real small input


def main():
    set_up_test_cases()
    run_test()


if __name__ == '__main__':
    main()
