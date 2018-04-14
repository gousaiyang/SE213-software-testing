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


def high_power():
    l = ["0"] * 65535
    l = ["1"] + l + ["1"]
    return l


def set_up_test_cases():
    ###############
    # Condition 1 #
    ###############
    add_test_case([], True, '')

    ###############
    # Condition 2 #
    ###############
    add_test_case([0], True, '0')

    ###############
    # Condition 3 #
    ###############
    add_test_case([1], True, '1')

    ###############
    # Condition 4 #
    ###############
    add_test_case([-1], True, '-1')

    ###############
    # Condition 5 #
    ###############
    add_test_case([1000], True, '1000')
    add_test_case([-1000], True, '-1000')

    ###############
    # Condition 6 #
    ###############
    add_test_case([0, 0], True, '0')  # leading 0 coefficient should be omitted
    add_test_case([0] * 1000, True, '0')

    ###############
    # Condition 7 #
    ###############
    add_test_case([1, 0], True,
                  'x')  # 1 should be omitted (not expect: 1x); trailing 0 should be omitted (not expect: x+0)
    add_test_case([-1, 0], True,
                  '-x')  # -1 should be omitted (not expect: -1x); trailing 0 should be omitted (not expect: -x+0)
    add_test_case([1, 0, 0], True, 'x^2')  # omit coefficient @1; omit subexp @0

    ###############
    # Condition 8 #
    ###############

    ###############
    # Condition 9 #
    ###############

    ################
    # Condition 10 #
    ################
    add_test_case([0, 1], True, '1')  # leading 0 coefficient should be omitted

    ################
    # Condition 11 #
    ################

    ################
    # Condition 12 #
    ################
    add_test_case([1, 1], True, 'x+1')  # first 1 should be omitted, second should not
    add_test_case([-1, -1], True, '-x-1')  # first -1 should be omitted, second should not
    add_test_case([1, 1], True, 'x+1')  # omit first plus sign, omit x^0
    add_test_case([0, -1, 1], True, '-x+1')  # omit coefficient @-1; mask trailing 0s

    ################
    # Condition 13 #
    ################

    ################
    # Condition 14 #
    ################

    ################
    # Condition 15 #
    ################

    ################
    # Condition 16 #
    ################

    ################
    # Condition 17 #
    ################
    add_test_case([1000, -1000], True, '1000x-1000')  # normal value

    ################
    # Condition 18 #
    ################
    add_test_case([-1000, 1000], True, '-1000x+1000')  # normal value

    #############
    # Hex input #
    #############
    add_test_case(["0xa", "0xB"], True, '10x+11')  # hex number support, upper and lower cases

    ###############
    # Float input #
    ###############
    add_test_case([0.1, -0.01], True, '0.1x-0.01')  # float number support
    add_test_case(["1e4", "1e-3", "3.14e2", "-3.14e-3"], True,
                  '10000x^3+0.001x^2+314x-0.00314')  # scientific notation and necessary conversion to integer

    ###############
    # False input #
    ###############
    add_test_case('x', False, 'Invalid coefficient list. Space delimited real numbers expected.')
    add_test_case(["0001", "-0001"], True, 'x-1')  # non standard form of integers
    add_test_case([".100", "-1.230"], True, '0.1x-1.23')  # non conforming floats

    #################
    # Boundary test #
    #################
    # 1 coefficients
    add_test_case([2147483645], True, '2147483645')  # lower than int limit
    add_test_case([2147483646], True, '2147483646')  # equal to int limit
    add_test_case([2147483647], True, '2147483647')  # higher than int limit
    add_test_case([-2147483646], True, '-2147483646')  # lower than int limit
    add_test_case([-2147483647], True, '-2147483647')  # equal to int limit
    add_test_case([-2147483648], True, '-2147483648')  # higher than int limit

    # 2 coefficients
    add_test_case([2147483645, -2147483646], True, '2147483645x-2147483646')  # lower than int limit
    add_test_case([2147483646, -2147483647], True, '2147483646x-2147483647')  # equal to int limit
    add_test_case([2147483647, -2147483648], True, '2147483647x-2147483648')  # higher than int limit
    add_test_case([2147483647, -2147483648], True, '2147483647x-2147483648')  # large input exceeding integer bounds

    # 65533 coefficients (cannot test to 2147483646 due to py list length limit)
    add_test_case([1000, -1000] + [0] * 65531, True, '1000x^65532-1000x^65531')
    add_test_case([-1000, 1000] + [0] * 65531, True, '-1000x^65532+1000x^65531')
    add_test_case([0] * 65532 + [1], True, '1')
    add_test_case([1] + [0] * 65532, True, 'x^65532')
    add_test_case([1] + [0] * 65531 + [1], True, 'x^65532+1')
    add_test_case([-1] + [0] * 65532, True, '-x^65532')
    add_test_case([-1] + [0] * 65531 + [-1], True, '-x^65532-1')

    add_test_case(high_power(), True, "x^65536+1")  # excessively long testcase whose expected output is x^65536

    add_test_case(["1e1000", "0"], True, thousand() + "x")  # real large input
    add_test_case(["1e-1000", "0"], True, one_thousand() + "x")  # real small input

    ###############
    # Random test #
    ###############
    cnt = 50  # cnt of random input
    for n in range(cnt):
        pos = random.randint(2, 10000)
        neg = -1 * random.randint(2, 10000)
        add_test_case([pos, neg], True, str(pos) + 'x' + str(neg))  # regular case with negative number
        add_test_case([neg, pos], True, str(neg) + 'x+' + str(pos))  # display first neg sign


def main():
    set_up_test_cases()
    run_test()


if __name__ == '__main__':
    main()
