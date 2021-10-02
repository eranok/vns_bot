import requests
import subprocess
import re
import sys


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

    def post(self, url, payload):
        return self.session.post(url, data=payload)

    def test_start(self, test_id):
        url_test = "https://vns.lpnu.ua/mod/quiz/view.php?id={}".format(test_id)
        test_page = self.get(url_test)
        self.cmid = re.findall(self.pattern_cmid, test_page.text)[0]
        self.sesskey = re.findall(self.pattern_session, test_page.text)[0]

        payload = {'cmid': self.cmid, 'sesskey': self.sesskey}
        started_test_page = self.post(self.url_test_start, payload)
        self.attempt = re.findall(self.pattern_attempt, started_test_page.text)[0]

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
    subprocess.run("mkdir -p tests_html", shell=True, check=True)
    test_results = open(f"./tests_html/{test_id}.html", "a")
    for i in range(times):
        print(f"Progress {i+1} out of {times}")
        s.test_start(test_id)
        s.test_process()
        r = s.test_review()
        # in r.text you have the whole html page
        # do whatever you want with it
        test_results.write(r.text)
    test_results.close()


if __name__ == "__main__":
    main()




