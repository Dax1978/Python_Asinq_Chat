import unittest
import time


def create_presence(account_name='Guest'):
    '''
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    '''
    out = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': account_name
        }
    }
    return out


def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        return f'400 : {message["error"]}'
    raise ValueError


class TestClient(unittest.TestCase):
    def test_def_presense(self):
        """Тест коректного запроса"""
        test = create_presence()
        # время необходимо приравнять принудительно
        test['time'] = 1.1
        # иначе тест никогда не будет пройден
        self.assertEqual(
            test, {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'Guest'}}, 'Тест корректного запроса не пройден')

    def test_200_ans(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(process_ans({'response': 200}), '200 : OK',
                         'Тест корректтного разбора ответа 200 не пройден')

    def test_400_ans(self):
        """Тест корректного разбора 400"""
        self.assertEqual(process_ans({'response': 400, 'error': 'Bad Request'}), '400 : Bad Request',
                         'Тест корректного разбора 400 не пройден')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, process_ans, {
                          'error': 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
# python test_client.py
