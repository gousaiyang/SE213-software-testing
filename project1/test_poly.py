import re
import sys
import socket

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

def set_up_test_cases():
    # TODO: add more test cases
    add_test_case([1, 1], True, 'x+1')
    add_test_case('x', False, 'Invalid coefficient list. Space delimited real numbers expected.')

def main():
    set_up_test_cases()
    run_test()

if __name__ == '__main__':
    main()
