import httpx
import random
import urllib.parse
from Utils import Console, Utils

class Create_headers:
    def __init__(self, proxy) -> None:
        self.client = httpx.Client(proxies=proxy)
        self.proxy = proxy
        Console().sprint(f'Using Proxy: {self.proxy}', True)
        self.__session()

    def get_cookies(self) -> bool:
        self.client.headers.update({
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'en-CA,en;q=0.9',
            'dnt': '1',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        })

        create_session = self.client.get('https://twitter.com/i/flow/signup')

        # Checks if status code is 200
        try:
            assert create_session.status_code == 200
        except AssertionError:
            return False

        # These 3 cookies always have the same value
        self.guest_id_marketing = self.guest_id_ads = self.guest_id = create_session.headers['set-cookie'].split('guest_id_ads=')[1].split(';')[0]

        self.personalization_id = create_session.headers['set-cookie'].split('personalization_id=')[1].split(';')[0]

        self.gt = str(create_session.content).split('gt=')[1].split(';')[0]

        return True

    def get_auth(self) -> bool:
        self.client.headers.update({'authority': 'abs.twimg.com'})

        get_bearer = self.client.get('https://abs.twimg.com/responsive-web/client-web/main.2d95c527.js')

        try:
            assert get_bearer.status_code == 200
        except AssertionError:
            return False

        self.authorization = 'Bearer ' + str(get_bearer.content).split('o="Web-12",s="')[1].split('",l="')[0]

        return True

    def get_sess(self) -> bool:
        get_person = self.client.get('https://twitter.com/i/api/1.1/account/personalization/p13n_preferences.json')

        try:
            assert get_person.status_code == 200
        except AssertionError:
            return False

        self._twitter_sess = str(get_person.headers['set-cookie']).split('_twitter_sess=')[1].split(';')[0]

        return True

    def get_flow_token(self) -> bool:
        get_flow_name = self.client.post('https://twitter.com/i/api/1.1/onboarding/task.json?flow_name=signup', json={
            "input_flow_data":{
                "flow_context":{
                    "debug_overrides":{},
                    "start_location":{
                        "location":"manual_link"
                    }
                }
            },
            "subtask_versions":{
                "contacts_live_sync_permission_prompt":0,
                "email_verification":1,
                "topics_selector":1,
                "wait_spinner":1,
                "cta":4
                }
            }
        )

        try:
            assert get_flow_name.status_code == 200 and get_flow_name.json()['status'] == 'success'
        except AssertionError:
            return False

        self.flow_token = get_flow_name.json()['flow_token']

        return True

    def __session(self) -> None:
        if not self.get_cookies():
            Console().sprint('Error while getting cookies', False)
            return

        if not self.get_auth():
            Console().sprint('Error while getting Bearer', False)
            return

        self.client.cookies.update({
            'guest_id_marketing': self.guest_id_marketing,
            'guest_id_ads': self.guest_id_ads,
            'personalization_id': self.personalization_id,
            'guest_id': self.guest_id,
            'ct0': '0d0e9d6e1a6a4654871a4bae7c620f9e',
            'gt': self.gt,
        })

        self.client.headers.update({
            'accept': '*/*',
            'accept-language': 'en-CA,en;q=0.9',
            'authorization': self.authorization,
            'dnt': '1',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'x-csrf-token': '0d0e9d6e1a6a4654871a4bae7c620f9e',
            'x-twitter-active-user': 'yes',
            'x-twitter-client-language': 'en',
        })

        self.client.headers.update({'authority': 'api.twitter.com'})
        self.guest_token = self.client.post('https://api.twitter.com/1.1/guest/activate.json').json()['guest_token']
        self.client.headers.update({'x-guest-token': self.guest_token})
        self.client.cookies.update({'x-guest-token': self.guest_token})

        self.client.headers.update({'authority': 'twitter.com'})

        if not self.get_flow_token():
            Console().sprint('Error while getting flow token', False)
            return

        if not self.get_sess():
            Console().sprint('Error while getting cookies', False)
            return

        self.client.cookies.update({'_twitter_sess': self._twitter_sess})

class Create_account(Create_headers):
    def __init__(self, proxy, username: str, email: str) -> None:
        super().__init__(proxy)
        self.username = username
        self.email = email

        if not self.check_email():
            Console().sprint('Error while checking email, or email is taken/invalid', False)
            return

        if not self.begin_verification():
            Console().sprint('Error, cannot start verification', False)
            return
        
        if not self.sumbit_code(input('Code: ')):
            Console().sprint('Error while sumbitting verification code', False)
            return

        if not self.sumbit_password():
            Console().sprint('Error while sumbitting password', False)
            return

        self.others()
        with open('Stuff.txt','a') as f:
            f.write(self.password)

    def check_email(self) -> bool:
        twitter_mail = self.client.get(f'https://twitter.com/i/api/i/users/email_available.json?email={urllib.parse.quote(self.email)}').json()
        if twitter_mail['valid'] and not twitter_mail['taken']:
            return True
        else:
            return False

    def begin_verification(self) -> bool:
        verification = self.client.post('https://twitter.com/i/api/1.1/onboarding/begin_verification.json', json={
            "email": self.email,
            "display_name": self.username,
            "flow_token": self.flow_token
        })

        try:
            assert verification.status_code == 204
        except AssertionError:
            return False

        return True

    def sumbit_code(self, code: int) -> bool:
        self.birth_day, self.birth_month, self.birth_year = random.randint(1,28), random.randint(1,12), random.randint(1980, 2000)
        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs":[
                {
                    "subtask_id":"Signup",
                    "sign_up":{
                        "js_instrumentation":{
                            "response":"{\"rf\":{\"af6f7b73eafcf5529209e1786caafcf2fb5282fa4487d2beb890b19fc35acd87\":62,\"ad211331e145ccba31bb356ffe41f734462471604cd53691560edaa675536c8d\":0,\"a9c1599829bd70f0895312fdd1e49e3aeb33aca3e7bebc356bd4bb726f8e6450\":-63,\"ec63eef08f45d61e1ddc6ffd06de732cf3325fd739ce2231634ff702fad1edca\":63},\"s\":\"AyUf-D7KrJHtNR231UZGwHUQbKmq6u7b-gp3mPQ-fr4m33k3mACZcIRq5A4Vpu40o8IY2xxSXi9HMz5tIT1IvNeFzxlnG0qxpr-wBZNBU7zrNpxbjmLXOaDVWYvfaQTvLQclIRoFJwViWf-PPib2KL2UCZIfDnrHCtcQEtlSr2jEOYAgx6VXd3ZW-egknsW4YMeGVvNIpQSAnIa_O-tHsVBl12L9haTsZUy0HYycVYsyfP_r4bpNh39MM2sW6cMAquFQaUsQAa-4iIfSucEyZZZkJSWcE1B9McLzif9f00W8b4aYphJCPtyKqHl3Xmuk9DTTcNXzGb9HmnVwHBTOZgAAAYFFLvhI\"}"
                        },
                    "link":"email_next_link",
                    "name": self.username,
                    "email": self.email,
                    "birthday":{
                        "day": self.birth_day,
                        "month": self.birth_month,
                        "year": self.birth_year
                    },
                    "personalization_settings":{
                        "allow_cookie_use":True,
                        "allow_device_personalization":True,
                        "allow_partnerships": True,
                        "allow_ads_personalization": True
                    }
                }
            },
            {
                "subtask_id":"SignupSettingsListEmailNonEU",
                "settings_list":{
                    "setting_responses":[
                        {
                            "key":"twitter_for_web",
                            "response_data":{
                                "boolean_data":{
                                    "result":True}
                                }
                        }
                    ],
                "link":"next_link"
                }
            },
            {
                "subtask_id":"SignupReview",
                "sign_up_review":{
                    "link":"signup_with_email_next_link"
                }
            },
            {
                "subtask_id":"EmailVerification",
                "email_verification":{
                    "code":code,
                    "email": self.email,
                    "link":"next_link"
                }
            }
        ]}

        send_code = self.client.post("https://twitter.com/i/api/1.1/onboarding/task.json", json=payload)

        try:
            assert send_code.status_code == 200 and send_code.json()['status'] == 'success'
        except AssertionError:
            return False    

        return True

    def sumbit_password(self) -> bool:
        self.password = Utils().get_password()

        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs":[
                {
                    "subtask_id":"EnterPassword",
                    "enter_password":{
                        "password": self.password,
                        "link":"next_link"
                    }
                }
            ]
        }

        set_password = self.client.post("https://twitter.com/i/api/1.1/onboarding/task.json", json=payload)

        try:
            assert set_password.status_code == 200 and set_password.json()['status'] == 'success'
        except AssertionError:
            return False    

        return True

    def others(self) -> None:
        self.client.post('https://twitter.com/i/api/1.1/onboarding/task.json', json={
            "flow_token": self.flow_token,
                "subtask_inputs":[
                    {
                        "subtask_id":"SelectAvatar",
                        "select_avatar":{
                            "link":"skip_link"
                        }
                    }
                ]
            })

Create_account(None, 'USERNAME', 'EMAIL')