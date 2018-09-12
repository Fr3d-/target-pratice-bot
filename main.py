import requests
import json
import sys

BASE = "https://konkurrencer.danskespil.dk"

class Bot:
    def __init__(self, username=None, password=None, sessionCookie=None):
        self.s = requests.Session()
        self.s.get(BASE + "/targetpractice")
        self.quizId = self.s.cookies.get_dict().keys()[0]

        if sessionCookie:
            self.s.cookies.set(self.quizId, None)
            self.s.cookies.set(self.quizId, sessionCookie)
        else:
            self.username = username
            self.password = password

        print(self.s.cookies)

    def login(self):
        payload = {
            "type": "login",
            "inputs[0][name]": "Email",
            "inputs[0][value]": self.username,
            "inputs[0][rules][ruleRequired]": "1",
            "inputs[1][name]": "login",
            "inputs[1][value]": "login-email",
            "inputs[2][name]": "Password",
            "inputs[2][value]": self.password,
            "inputs[2][rules][ruleRequired]": "0",
            "inputs[3][name]": "login",
            "inputs[3][value]": "login-password",
            "theme": "targetpractice",
            "quizId": self.quizId,
            "url": "konkurrencer.danskespil.dk/targetpractice"
        }
        resp = self.s.post(BASE + "/system/ajax/ajax.php", data=payload, headers={"X-Requested-With": "XMLHttpRequest"})

        if resp.json()["type"] != "success":
            print resp.json()
            raise Exception()
        else:
            print("Logged in")

    def startGame(self):
        payload = {
            "type": "start_game",
            "data": "data",
            "quizId": self.quizId,
            "theme": "targetpractice"
        }
        resp = self.s.post(BASE + "/modules/opsparings-spil/ajax.php", data=payload, headers={"X-Requested-With": "XMLHttpRequest"}).json()

        if resp["type"] == "error":
            print resp
            raise Exception()
        else:
            return resp

    def shootTargets(self, n):
        payload = {
            "type": "save_score",
            "balloons": ",".join(map(lambda x: "target-" + str(x), list(range(1, n+1)))),
            "quizId": self.quizId,
            "theme": "targetpractice"
        }
        resp = self.s.post(BASE + "/modules/opsparings-spil/ajax.php", data=payload, headers={"X-Requested-With": "XMLHttpRequest"}).json()

        if resp["type"] == "error":
            print resp
            raise Exception()
        else:
            return resp        

    def saldo(self):
        payload = {
            "type": "get_saldo",
            "quizId": self.quizId,
            "theme": "targetpractice"
        }
        resp = self.s.post(BASE + "/modules/opsparings-spil/ajax.php", data=payload, headers={"X-Requested-With": "XMLHttpRequest"}).json()

        if resp["type"] == "error":
            print resp
            raise Exception()
        else:
            return resp

if __name__ == "__main__":
    bot = Bot(sessionCookie=sys.argv[1])
    print("Previous saldo:")
    print(json.dumps(bot.saldo(), indent=2, sort_keys=True))

    print("\nGame information:")
    game = bot.startGame()
    print(json.dumps(game, indent=2, sort_keys=True))
    if bot.shootTargets(game["amountOfBalloons"])["type"] == "success":
        print("Targets shot")
    
    print("\nNew saldo:")
    print(json.dumps(bot.saldo(), indent=2, sort_keys=True))
