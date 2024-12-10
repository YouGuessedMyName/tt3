import logging
import time

from datetime import datetime

from generic.api import label_pb2
from generic.api.configuration import ConfigurationItem, Configuration
from generic.api.label import Label, Sort
from generic.api.parameter import Type, Parameter
from generic.handler import Handler as AbstractHandler
from matrix.matrix_connection import MatrixConnection
from time import sleep

def _response(name, channel='matrix', parameters=None):
    """ Helper method to create a response Label. """
    return Label(Sort.RESPONSE, name, channel, parameters=parameters)

def _stimulus(name, channel='matrix', parameters=None):
    """ Helper method to create a stimulus Label. """
    return Label(Sort.STIMULUS, name, channel, parameters=parameters)

class MatrixHandler(AbstractHandler):
    """
    This class handles the interaction between AMP and the Matrix SUT.
    """

    def __init__(self):
        super().__init__()
        self.sut = None

    def send_message_to_amp(self, label: str, parameters: dict):
        """
        Send a message back to AMP. The message from the SUT needs to be converted to a Label.

        Args:
            raw_message (str): The message to send to AMP.
        """
        logging.info(f'response received: {label} {parameters}')
        label = self._message2label(label, parameters)
        self.adapter_core.send_response(label)

    def start(self):
        """
        Start a test.
        """
        end_point = self.configuration.items[0].value
        container_name = self.configuration.items[1].value
        self.sut = MatrixConnection(end_point, container_name)
        self.sut.connect()
        self.adapter_core.send_ready()

    def reset(self):
        """
        Prepare the SUT for the next test case and notify the SUT when reset is completed.
        """
        logging.info('Resetting the SUT for a new test case')
        self.sut.reset()
        self.adapter_core.send_ready()

    def stop(self):
        """
        Stop the SUT from testing.
        """
        logging.info('Stopping the plugin handler')
        self.sut.stop()
        self.sut = None

        logging.debug('Finished stopping the plugin handler')

    def stimulate(self, pb_label: label_pb2.Label):
        """
        Processes a stimulus of a given label at the SUT, and send the response to AMP.

        Args:
            pb_label (label_pb2.Label): stimulus that the Axini Modeling Platform has sent
        """
        # Sleep a little bit to prevent too many requests error.
        #sleep(0.2)

        label = Label.decode(pb_label)
        sut_msg, params = self._label2message(label)
        #print("SUT MESSAGE", sut_msg)

        # send confirmation of stimulus back to AMP
        pb_label.timestamp = time.time_ns()
        pb_label.physical_label = bytes(sut_msg, 'UTF-8')
        self.adapter_core.send_stimulus_confirmation(pb_label)

        # leading spaces are needed to justify the stimuli and responses
        logging.info('      Injecting stimulus @SUT: ?{name}'.format(name=label.name))
        raw_message, parameters = self.sut.send(sut_msg, params)
        self.send_message_to_amp(raw_message, parameters)

    def supported_labels(self):
        """
        The labels supported by the adapter.

        Returns:
             [Label]: List of all supported labels of this adapter
        """
        return [
            _stimulus('create_room', parameters=[Parameter('username', Type.STRING)]),
            _stimulus('join_room', parameters=[Parameter('room', Type.STRING), Parameter('username', Type.STRING)]),
            _stimulus('leave_room', parameters=[Parameter('room', Type.STRING), Parameter('username', Type.STRING)]),
            _stimulus('send_message', parameters=[Parameter('message', Type.STRING), Parameter('room', Type.STRING), Parameter('username', Type.STRING)]),
            _stimulus('invite_user', parameters=[Parameter('user_id', Type.STRING), Parameter('room', Type.STRING), Parameter('username', Type.STRING)]),
            _stimulus('ban_user', parameters=[Parameter('user_id', Type.STRING), Parameter('room', Type.STRING), Parameter('username', Type.STRING)]),
            _stimulus('unban_user', parameters=[Parameter('user_id', Type.STRING), Parameter('room', Type.STRING), Parameter('username', Type.STRING)]),

            _response('succes'),
            _response('room_created_success', parameters=[Parameter('room', Type.STRING)]),
            _response('fail', parameters=[Parameter('error_code', Type.INTEGER)])
        ]

    def default_configuration(self) -> Configuration:
        """
        The default configuration of this adapter.

        Returns:
            Configuration: the default configuration required by this adapter.
        """
        return Configuration([
            ConfigurationItem(
                name='endpoint',
                tipe=Type.STRING,
                description='Base websocket URL of the Synapse server',
                value='http://localhost:8008'),
            ConfigurationItem(
                name='docker_container',
                tipe=Type.STRING,
                description='name of the docker container that should be reset when appropriate.',
                value="synapse")
        ])

    def _label2message(self, label: Label):
        """
        Converts a Protobuf label to a SUT message.

        Args:
            label (Label)
        Returns:
            str, dict: The message to be sent to the SUT and the parameters.
        """
        if label.name == "unban_user":
            values = [p.value for p in label.parameters]
            logging.warning(f"No. params: {len(label.parameters)}, values: {values}")
        return label.name.upper(), {p.name: p.value for p in label.parameters}

    def _message2label(self, message: str, parameters: dict):
        """
        Converts a SUT message to a Protobuf Label.

        Args:
            message (str)
        Returns:
            Label: The converted message as a Label.
        """
        label_name = message.lower()
        parameters = [Parameter(k, Type.STRING, v) for k, v in parameters.items()]
        label = Label(
            sort=Sort.RESPONSE,
            name=label_name,
            channel='matrix',
            physical_label=bytes(message, 'UTF-8'),
            timestamp=datetime.now(),
            parameters=parameters)

        return label
