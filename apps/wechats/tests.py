import random
import requests
# domain = "http://127.0.0.1:8081"
domain = "https://api.uat.tong-psy.com"
# headers = {
#     "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJfaWQiOiJvTEZDcTVWa2s0YjlWMjJDS1pWWEl5ZlZ5b1FBIiwiaWF0IjoxNzI0NTEzMTgzLjQyMzg1NTV9fQ.aBZWeBhqn4tp29nkIkNECD1wwc5tMicmksy3vZPd9hI"
# }
headers = {
    "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJfaWQiOiJvTEZDcTVWa2s0YjlWMjJDS1pWWEl5ZlZ5b1FBIiwiaWF0IjoxNzI0NjgxMDQyLjcxODE2MDl9fQ.rd8e26ry0VBOUbaO1Y8ftJldElGFZkuFWveabko3ET4"
}

def _get_question(data):
    url = f"{domain}/wechat/v1/get_question/"
    resp = requests.post(url, json=data, headers=headers)
    return resp.json()

def _answer_question(data):
    url = f"{domain}/wechat/v1/answer/"
    resp = requests.post(url, json=data, headers=headers)
    print(resp.json())
    return resp.json()

def _get_result(data):
    url = f"{domain}/wechat/v1/result/"
    resp = requests.post(url, json=data, headers=headers)
    print('=========结果=========')
    print(resp.json())
    return resp.json()

def test_answer(qt_id):
    last_q_id = ''
    last_number = ''
    last_o_number = ''
    q_id = ""
    o_number = ''
    text = ""
    ans_id = ""
    tmp = "tmpaaa"
    while True:
        data = {"u_id": qt_id,
                "last_q_id": last_q_id,
                "last_number": last_number,
                "last_o_number": last_o_number,
                "tmp": tmp}
        resp = _get_question(data)
        r_data = resp.get('data')
        q_id = r_data.get('q_id')
        q_type = r_data.get('q_type')
        number = r_data.get('number')
        end_number = r_data.get('end_number')
        options = r_data.get('options', [])
        o_list = []
        for o in options:
            o_number = o.get('o_number')
            o_list.append(o_number)

        # 回答问题
        if q_type == "问答题":
            text = "text"
        if q_type == "单选题":
            # o_number = random.choice(o_list)
            o_number = "A"
        if q_type == "多选题":
            o_number = random.choice(o_list)

        ans = {"u_id": qt_id, "q_id": q_id, "o_number": o_number, "text": text, "ans_id": ans_id, "tmp": tmp}
        ans_resp = _answer_question(ans)
        ans_id = ans_resp.get('data').get('ans_id')
        last_q_id = q_id
        last_number = number
        last_o_number = o_number

        if int(number) == int(end_number):
            r_data = {"u_id": qt_id, "ans_id": ans_id, "tmp":tmp}
            result = _get_result(r_data)
            print(result)
            data = result.get('data')
            for i in data.get('dim_list'):
                print(i)
            break


if __name__ == '__main__':
    test_answer('252445f4-3634-4261-a02e-3e7fd485f6a4')
    # test_answer('f885407b-db0b-475e-a026-38ebe7c7c0c2')
    # test_answer('55642b1e-1b29-487a-aafd-557ffdf3d088')