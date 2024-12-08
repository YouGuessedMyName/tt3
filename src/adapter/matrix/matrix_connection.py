import logging
import requests

### CONSTANTS SET BY THE USER ###
SYNAPSE_DOCKER_NAME = "synapse"
BASE_URL = "http://localhost:8008"



FULL_URL = BASE_URL + "/_matrix/client/v3/"

class MatrixConnection:
    """
    This class handles the connection, sending and receiving of messages to the Matrix SUT

    Attributes:
        handler (adapter.Matrix.Handler)
        endpoint (str): URL of the Matrix SUT
    """

    def __init__(self, handler, endpoint):
        self.handler = handler
        self.endpoint = endpoint
        self.one_session = None
        self.two_session = None
        self.three_session = None

        self.websocket = None
        self.wst = None
    
    @staticmethod
    def login_user(user, password) -> dict:
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
            FULL_URL + "login",
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

        # Use lambda functions to correctly pass the self variable.
        self.one_session = self.login_user("one", "one")
        self.two_session = self.login_user("two", "two")
        self.three_session = self.login_user("three", "three")
        logging.info('User sessions established sucesfully.')

    def send(self, message):
        """
        Send a message to the SUT.

        Args:
            message (str): Message to send
        """
        logging.debug('Sending message to SUT: {msg}'.format(msg=message))

        self.websocket.send(message)

    def on_open(self):
        """
        Callback that is called when the socket to the SUT is opened.
        """
        logging.info('Connected to SUT')
        self.send('RESET')

    def on_close(self):
        """
        Callback that is called when the socket is closed.
        """
        logging.debug('Closed connection to SUT')

    def on_message(self, msg):
        """
        Callback that is called when the SUT sends a message.

        Args:
            msg (str): Message of the Matrix SUT
        """
        logging.debug('Received message from SUT: {msg}'.format(msg=msg))
        self.handler.send_message_to_amp(msg)

    def on_error(self, msg):
        """
        Callback that is called when something is wrong with the websocket connection

        Args:
            msg (str): Error message
        """
        logging.error("Error with connection to SUT: {e}".format(e=msg))

    def stop(self):
        """
        Perform any cleanup if the SUT is closed.
        """
        if self.websocket:
            self.websocket.close()
            logging.debug('Stopping thread which handles WebSocket connection with SUT')
            self.websocket.keep_running = False
            self.wst.join()
            logging.debug('Thread stopped')
            self.wst = None
