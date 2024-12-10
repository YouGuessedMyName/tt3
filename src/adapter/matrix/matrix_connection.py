import logging
from typing import Tuple
import requests
import subprocess
from time import sleep
import random
import string

class MatrixConnection:
    """
    This class handles the connection, sending and receiving of messages to the Matrix SUT

    Attributes:
        handler (adapter.Matrix.Handler)
        endpoint (str): URL of the Matrix SUT
        container_Name (str): Name of the matrix container that is running on the same local machine.
            Needed in order to restart the SUT.
    """

    def __init__(self, endpoint, container_name):
        self.endpoint = endpoint
        self.one_session = None
        self.two_session = None
        self.three_session = None
        self.session_dict = None
        self.full_url = endpoint + "/_matrix/client/v3/"
        self.container_name = container_name
    
    @staticmethod
    def get_auth_header(user_session):
        return {"Authorization": f"Bearer {user_session["access_token"]}"}

    def get_room_ids(self, admin_session) -> list:
        response = requests.get(
            self.endpoint + "/_synapse/admin/v1/rooms",
            headers=self.get_auth_header(admin_session),
        )
        assert response.ok
        return [x["room_id"] for x in response.json()["rooms"]]

    def delete_room(self, room_id: str, admin_session):
        response = requests.delete(
            self.endpoint + "/_synapse/admin/v2/rooms/" + room_id,
            headers=self.get_auth_header(admin_session),
            json={
                "purge": True,
                "force_purge": True,
                "block": False
                }
            )
        #assert response.ok
        print("Tried to delete", room_id)
    
    def login_user(self, user, password) -> dict:
        """Log this user in and return their session."""
        def generate_login_body(user, password) -> dict:
            body = {
                    "type": "m.login.password",
                    "identifier": {
                        "type": "m.id.user",
                        "user": user
                    },
                    "password": password
                    }
            return body
        
        response = requests.post(
            self.full_url + "login",
            json = generate_login_body(user, password)
        )
        # logging.debug(response)
        assert response.ok, f"Login failed for user {user}. You might need to restart the container"
        return response.json()

    def connect(self):
        """
        Connect to the Matrix SUT. In our case this means establishing the user sessions.
        """
        logging.info('Connecting to Matrix and establishing user sessions...')
        self.reset()
        # Use lambda functions to correctly pass the self variable.
        self.one_session = self.login_user("one", "one")
        self.two_session = self.login_user("two", "two")
        self.three_session = self.login_user("three", "three")
        self.session_dict = {
            "one": self.one_session,
            "two": self.two_session,
            "three": self.three_session
        }
        logging.info('User sessions established sucesfully.')
    
    def reset(self):
        """Rest the SUT and wait for 5 seconds.
        """
        admin_session = self.login_user("admin", "admin")
        logging.info(f"Deleting all rooms, restarting synapse container and waiting 5 seconds...")
        [self.delete_room(room_id, admin_session) for room_id in self.get_room_ids(admin_session)]
        subprocess.run(["docker", "restart", self.container_name])
        sleep(5)
        logging.info("Done restarting the container.")

    def send(self, label: str, params: dict) -> Tuple[str, dict]:
        """
        Send a message to the SUT, and return the response as a raw string message.

        Args:
            message (str): Message to send
        """
        logging.info(f'Sending message to SUT: {label}: {params}')
        status_code = None
        try:
            user_session = self.session_dict[params["username"]]
        except KeyError:
            logging.warning(f"User with the name {params["username"]} does not exist")
            return "FAIL", {}
        if label == "CREATE_ROOM":
            status_code, room_id = self.create_room(user_session)
            if status_code == 200:
                return "ROOM_CREATED_SUCCESS", {"room_id": room_id}
            else:
                return "FAIL", {}
        else:
            room_id = params["room_id"]
            if label == "JOIN_ROOM":
                status_code = self.join_room(room_id=room_id, user_session=user_session)
            elif label == "LEAVE_ROOM":
                status_code = self.leave_room(room_id=room_id, user_session=user_session)
            elif label == "SEND_MESSAGE":
                message = params["message"]
                status_code = self.send_message(room_id=room_id, user_session=user_session, message=message)
            if label == "BAN_USER" or label == "UNBAN_USER":
                try:
                    target_user = params["user_id"]
                    target_user_session = self.session_dict[target_user]
                except KeyError as e:
                    logging.error(f"Targeted user with name {params["user_id"]} does not exist! Terminating the adapter.")
                    return "FAIL", {}
                if label == "BAN_USER":
                    status_code = self.ban_user(room_id=room_id, user_session=user_session, target_user_session=target_user_session)
                elif label == "UNBAN_USER":
                    status_code = self.unban_user(room_id=room_id, user_session=user_session, target_user_session=target_user_session)
                    logging.info(f"UNBAN INFO: User {params["username"]} to ban {params["user_id"]}!\tSTATUS CODE: {status_code}")
            elif label == "INVITE_USER":
                # TODO remove invites.
                return "SUCCESS", {}
        
        #logging.error(f"Unkown label: {label}")
        logging.info(f"Response status code: {status_code}")
        # TODO make it return the actual status code.
        if status_code == 200:
            return "SUCCESS", {}
        else:
            return "FAIL", {}
    
    def create_room(self, user_session: str):
        def random_room_name():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
        
        def create_room_json():
            name_and_alias = random_room_name()
            return {
                    "name":name_and_alias,
                    "visibility":"public",
                    "preset":"public_chat",
                    "room_alias_name":name_and_alias,
                    "topic":"TOPIC",
                    "initial_state":[]
                }
        response = requests.post(
            self.full_url + "createRoom",
            headers=self.get_auth_header(user_session=user_session),
            json= create_room_json()
        )
        room_id = response.json()["room_id"]
        return response.status_code, room_id
        
    def join_room(self, room_id: str, user_session: str):
        response = requests.post(
            self.full_url + "join/" + room_id,
            headers=self.get_auth_header(user_session=user_session),
        )
        return response.status_code

    def leave_room(self, room_id: str, user_session: str):
        response = requests.post(
            self.full_url + "join/" + room_id,
            headers=self.get_auth_header(user_session=user_session),
        )
        return response.status_code

    def send_message(self, room_id: str, user_session: str, message: str):
        response = requests.put(
            self.full_url + "rooms/" + room_id + "/send/m.room.message/" + str(random.randint),
            headers=self.get_auth_header(user_session=user_session),
            json= {
                "msgtype": "m.text",
                "body": message
            }
        )
        return response.status_code

    def ban_user(self, room_id: str, user_session: str, target_user_session: str):
        response = requests.post(
            self.full_url + "rooms/" + room_id + "/ban",
            headers=user_session,
            json = {"user_id": target_user_session["user_id"],
                    "reason": "Should be banned."}
        )
        return response.status_code

    def unban_user(self, room_id: str, user_session: str, target_user_session: str):
        response = requests.post(
            self.full_url + "rooms/" + room_id + "/unban",
            headers=user_session,
            json = {"user_id": target_user_session["user_id"]}
        )
        return response.status_code

    def on_open(self):
        """
        Callback that is called when the socket to the SUT is opened.
        """
        logging.info('Connected to SUT')
        self.send('RESET')

    def stop(self):
        """
        Perform any cleanup if the SUT is closed.
        """
        self.one_session = None
        self.two_session = None
        self.three_session = None
