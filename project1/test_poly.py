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
    if isinstance(expected, list):
        return any(e in result['response'] for e in expected)
    else:
        return expected in result['response']


def judge_poly(result, expected):
    if isinstance(expected, list):
        return result['poly'] in expected
    else:
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
    add_test_case([0, 0], True, '0')
    add_test_case([0] * 1000, True, '0')

    ###############
    # Condition 7 #
    ###############
    add_test_case([1, 0], True, 'x')
    add_test_case([-1, 0], True, '-x')
    add_test_case([1, 0, 0], True, 'x^2')
    add_test_case([-0.1, 100.9, 1, -1, 234, 0, -33, 0, 0], True, '-0.1x^8+100.9x^7+x^6-x^5+234x^4-33x^2')

    ###############
    # Condition 8 #
    ###############
    add_test_case([1345, 0, -33, 0, 0], True, '1345x^4-33x^2')

    ###############
    # Condition 9 #
    ###############
    add_test_case([-1345, 0, -33, 0, 0], True, '-1345x^4-33x^2')

    ################
    # Condition 10 #
    ################
    add_test_case([0, 1], True, '1')

    ################
    # Condition 11 #
    ################
    add_test_case([0, 0, 0, 0, -1], True, '-1')

    ################
    # Condition 12 #
    ################
    add_test_case([1, 1], True, 'x+1')
    add_test_case([-1, -1], True, '-x-1')
    add_test_case([1, 1], True, 'x+1')
    add_test_case([0, -1, 1], True, '-x+1')
    add_test_case([1111.1, -0.02, 1, -1, 234, 0, -33, 0, -1], True, '1111.1x^8-0.02x^7+x^6-x^5+234x^4-33x^2-1')
    add_test_case([1111.1, -0.02, 1, -1, 234, 0, -33, 0, 1], True, '1111.1x^8-0.02x^7+x^6-x^5+234x^4-33x^2+1')

    ################
    # Condition 13 #
    ################
    add_test_case([1345, 0, -33, 0, 1], True, '1345x^4-33x^2+1')
    add_test_case([1345, 0, -33, 0, -1], True, '1345x^4-33x^2-1')

    ################
    # Condition 14 #
    ################
    add_test_case([-1345, 0, -33, 0, 1], True, '-1345x^4-33x^2+1')
    add_test_case([-1345, 0, -33, 0, -1], True, '-1345x^4-33x^2-1')

    ################
    # Condition 15 #
    ################
    add_test_case([0, 0, 0, 0, 1234], True, '1234')
    add_test_case([0, 0, 0, 0, -1234], True, '-1234')

    ################
    # Condition 16 #
    ################
    add_test_case([1111.1, -0.02, 1, -1, 234, 0, -33, 0, -1234], True, '1111.1x^8-0.02x^7+x^6-x^5+234x^4-33x^2-1234')
    add_test_case([1111.1, -0.02, 1, -1, 234, 0, -33, 0, 1234], True, '1111.1x^8-0.02x^7+x^6-x^5+234x^4-33x^2+1234')

    ################
    # Condition 17 #
    ################
    add_test_case([1000, -1000], True, '1000x-1000')

    ################
    # Condition 18 #
    ################
    add_test_case([-1000, 1000], True, '-1000x+1000')

    ############################
    # Unconventional int input #
    ############################
    add_test_case(['0xa', '0xB'], True, '10x+11')
    add_test_case(['0001', '-0001'], True, 'x-1')
    add_test_case(['   1   ', '  1   '], True, 'x+1')  # whitespace

    ###############
    # Float input #
    ###############
    add_test_case([0.1, -0.01], True, '0.1x-0.01')
    add_test_case(["1e4", "1e-3", "3.14e2", "-3.14e-3"], True,
                  '10000x^3+0.001x^2+314x-0.00314')  # scientific notation and necessary conversion to integer
    add_test_case([".100", "-1.230"], True, '0.1x-1.23')  # non conforming floats

    #################
    # Invalid input #
    #################
    add_test_case('x', False, 'Invalid coefficient list. Space delimited real numbers expected.')

    #############################
    # int32 input boundary test #
    #############################
    add_test_case(["2147483645", "-2147483646"], True, '2147483645x-2147483646')  # lower
    add_test_case(["2147483646", "-2147483647"], True, '2147483646x-2147483647')  # equal to
    add_test_case(["2147483647", "-2147483648"], True, '2147483647x-2147483648')  # higher

    #############################
    # int64 input boundary test #
    #############################
    add_test_case(["-9223372036854775806", "9223372036854775805"], True, '-9223372036854775806x+9223372036854775805')  # lower
    add_test_case(["-9223372036854775807", "9223372036854775806"], True, '-9223372036854775807x+9223372036854775806')  # equal to
    add_test_case(["-9223372036854775808", "9223372036854775807"], True, '-9223372036854775808x+9223372036854775807')  # higher
    add_test_case(["1e1000", "0"], True, thousand() + "x")  # real large input

    #############################
    # float input boundary test #
    #############################
    add_test_case(["3.3e+38", "-3.3e+38"], True, ['33'+'0'*37+'x-33'+'0'*37, '3.3e+38x-3.3e+38'])  # lower
    add_test_case(["3.4e+38", "-3.4e+38"], True, ['34'+'0'*37+'x-34'+'0'*37, '3.4e+38x-3.4e+38'])  # around
    add_test_case(["3.5e+38", "-3.5e+38"], True, ['35'+'0'*37+'x-35'+'0'*37, '3.5e+38x-3.5e+38'])  # higher
    add_test_case(["1.18e-38"], True, ['0.'+'0'*37+'116', '1.18e-38'])  # larger than min pos
    add_test_case(["1.17e-38"], True, ['0.'+'0'*37+'116', '1.17e-38'])  # around min pos
    add_test_case(["1.16e-38"], True, ['0.'+'0'*37+'116', '1.16e-38'])  # smaller than min pos

    ##############################
    # double input boundary test #
    ##############################
    add_test_case(["-1.6e+308", "1.6e+308"], True, ['-16'+'0'*307+'x+16'+'0'*307, '-1.6e+308x+1.6e+308'])  # lower
    add_test_case(["-1.7e+308", "1.7e+308"], True, ['-17'+'0'*307+'x+17'+'0'*307, '-1.7e+308x+1.7e+308'])  # around
    add_test_case(["-1.8e+308", "1.8e+308"], True, ['-18'+'0'*307+'x+18'+'0'*307, '-1.8e+308x+1.8e+308'])  # higher
    add_test_case(["2.23e-308"], True, ['0.'+'0'*307+'223', '2.23e-308'])  # larger than min pos
    add_test_case(["2.22e-308"], True, ['0.'+'0'*307+'222', '2.22e-308'])  # around min pos
    add_test_case(["2.21e-308"], True, ['0.'+'0'*307+'221', '2.21e-308'])  # smaller than min pos
    add_test_case(["1e-1000", "0"], True, [one_thousand() + "x", '1e-1000x'])  # real small input

    ####################################
    # Large number of coefficient test #
    ####################################
    add_test_case([1]+[0]*1000000+[1], True, 'x^1000001+1')

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
