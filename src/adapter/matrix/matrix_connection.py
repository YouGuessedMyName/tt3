import logging
import requests
import subprocess
from time import sleep

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
        assert response.ok
    
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

    def send(self, message) -> str:
        """
        Send a message to the SUT, and return the response as a raw string message.

        Args:
            message (str): Message to send
        """
        logging.debug('Sending message to SUT: {msg}'.format(msg=message))
        logging.error('Sending messages to the SUT is not yet implemented.')
        return "TEST_RESP"

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
