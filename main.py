import re
import sys
import json
import requests
import subprocess
from bs4 import BeautifulSoup


class VnsSession:
    session = None
    running_tests = {} # TODO make a dict of running tests, so you can continue them if needed

    url_login = "https://vns.lpnu.ua/login/index.php"
    url_test_start = "https://vns.lpnu.ua/mod/quiz/startattempt.php"
    url_test_process = "https://vns.lpnu.ua/mod/quiz/processattempt.php"
    url_test_review = "https://vns.lpnu.ua/mod/quiz/review.php"
    pattern_cmid = 'name="cmid" value="(.*?)"'
    pattern_session= 'name="sesskey" value="(.*?)"'
    pattern_attempt = 'name="attempt" value="(.*?)"'
    

    def __init__(self, login, password):
        self.session = requests.Session()

        # login into account 
        login_page = self.get(self.url_login)
        pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
        token = re.findall(pattern, login_page.text)
        token = re.findall("\w{32}", token[0])
        payload = {'username': login, 'password': password, 'anchor': '', 'logintoken': token[0]}
        ret = self.post(self.url_login, payload)

    def get(self, url, params = None):
        return self.session.get(url, params=params)

    def post(self, url, payload, headers = None):
        return self.session.post(url, data=payload, headers=headers)

    def test_start(self, test_id):
        url_test = "https://vns.lpnu.ua/mod/quiz/view.php?id={}".format(test_id)
        test_page = self.get(url_test)
        self.cmid = re.findall(self.pattern_cmid, test_page.text)[0]
        self.sesskey = re.findall(self.pattern_session, test_page.text)[0]

        payload = {'cmid': self.cmid, 'sesskey': self.sesskey}
        started_test_page = self.post(self.url_test_start, payload)
        self.test_page = started_test_page # TODO remove and use ret val
        self.attempt = re.findall(self.pattern_attempt, started_test_page.text)[0]
        return started_test_page

    def test_process_d(self, answers):
        answer_input_pattern = 'q\d+'
        answer_input = re.search(answer_input_pattern, self.test_page.text).group()

        # generating form-data reponse
        boundary = "--boundary--"
        content = 'Content-Disposition: form-data; name="{}"'

        payload = ""
        answer_id = 1
        slots = ""
        for answer in answers:
            payload += boundary + "\n" + content.format(answer_input + f":{answer_id}_flagged") + "\n\n"
            payload += str(0) + "\n"
            payload += boundary + "\n" + content.format(answer_input + f":{answer_id}_flagged") + "\n\n"
            payload += str(0) + "\n"
            payload += boundary + "\n" + content.format(answer_input + f":{answer_id}_sequancecheck") + "\n\n"
            payload += str(1) + "\n"
            payload += boundary + "\n" + content.format(answer_input + f":{answer_id}_answer") + "\n\n"
            payload += str(answer) + "\n"
            if slots != "": slots += "," 
            slots += str(answer_id)
            answer_id += 1
        
        payload += boundary + content.format("attempt") + "\n\n"
        payload += str(self.attempt) + "\n"

        payload += boundary + content.format("sesskey") + "\n\n"
        payload += str(self.sesskey) + "\n"

        payload += boundary + content.format("slots") + "\n\n"
        payload += str(slots) + "\n"

        payload += boundary

        print(payload)

        headers = {"Content-Type": "multipart/form-data; boundary={}".format(boundary)}
        self.post(self.url_test_process, payload, headers)

    def test_process(self):
        # TODO make this method send payload or data with answers
        payload = {'attempt': self.attempt, 'cmid': self.cmid, 'sesskey': self.sesskey, 'finishattempt': 1, 'timeup': 0}
        self.post(self.url_test_process, payload)

    def test_review(self):
        payload = {'attempt': self.attempt, 'cmid': self.cmid}
        # TODO think what should it return and in what format
        return self.get(self.url_test_review, payload)

def main():
    login = sys.argv[1]
    password = sys.argv[2]
    test_id = sys.argv[3]
    times = int(sys.argv[4])
    s = VnsSession(login, password)
    print("test")
    if times == -1:
        r = s.test_start(test_id)
        questions_raw = re.findall(r"Текст питання<.+?>((.).*)</div><div", r.text)
        questions = []
        for i in range(len(questions_raw)):
            soup = BeautifulSoup(questions[i][0].strip(), features="html.parser")
            question = soup.get_text()
            questions.append(question)

        exit(0)


    subprocess.run("mkdir -p tests", shell=True)

    f = open(f"./tests/{test_id}.txt", "a")

    for i in range(times):
        print(f"Progress {i+1} out of {times}")
        s.test_start(test_id)
        s.test_process()
        r = s.test_review()
        questions = re.findall(r"Текст питання<.+?>((.).*)</div><div", r.text)
        answers = re.findall(r"Правильна відповідь: (.+?)", r.text)
        for i in range(len(questions)):
            soup = BeautifulSoup(questions[i][0].strip(), features="html.parser")
            question = soup.get_text()

            a = "question: " + question.replace("\n", "") + "\n"
            a += "answer: " + answers[i][0].strip() + "\n\n";
            f.write(a)


        # in r.text you have the whole html page
        # do whatever you want with it
        #test_results.write(r.text)
    f.close()



if __name__ == "__main__":
    main()




