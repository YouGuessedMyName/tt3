import logging
import time

from datetime import datetime

from generic.api import label_pb2
from generic.api.configuration import ConfigurationItem, Configuration
from generic.api.label import Label, Sort
from generic.api.parameter import Type, Parameter
from generic.handler import Handler as AbstractHandler
from matrix.matrix_connection import MatrixConnection

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

    def send_message_to_amp(self, raw_message: Label):
        """
        Send a message back to AMP. The message from the SUT needs to be converted to a Label.

        Args:
            raw_message (str): The message to send to AMP.
        """
        logging.debug('response received: {label}'.format(label=raw_message))
        label = self._message2label(raw_message)
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

        label = Label.decode(pb_label)
        sut_msg = self._label2message(label)
        print("SUT MESSAGE", sut_msg)

        # send confirmation of stimulus back to AMP
        pb_label.timestamp = time.time_ns()
        pb_label.physical_label = bytes(sut_msg, 'UTF-8')
        self.adapter_core.send_stimulus_confirmation(pb_label)

        # leading spaces are needed to justify the stimuli and responses
        logging.info('      Injecting stimulus @SUT: ?{name}'.format(name=label.name))
        raw_message = self.sut.send(sut_msg)
        self.send_message_to_amp(raw_message)

    def supported_labels(self):
        """
        The labels supported by the adapter.

        Returns:
             [Label]: List of all supported labels of this adapter
        """
        return [
            _stimulus('test_stim'),
            _response('test_resp'),
            # _stimulus('open'),
            # _response('opened'),
            # _stimulus('close'),
            # _response('closed'),
            # _stimulus('lock', parameters=[Parameter('passcode', Type.INTEGER)]),
            # _response('locked'),
            # _stimulus('unlock', parameters=[Parameter('passcode', Type.INTEGER)]),
            # _response('unlocked'),
            # _stimulus('reset'),
            # _response('invalid_command'),
            # _response('invalid_passcode'),
            # _response('incorrect_passcode'),
            # _response('shut_off'),
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
            str: The message to be sent to the SUT.
        """

        # sut_msg = None
        # command_name = label.name.upper()
        # if label.name in ['lock', 'unlock']:
        #     sut_msg = '{msg}:{passcode}'.format(msg=command_name, passcode=label.parameters[0].value)
        # else:
        #     sut_msg = '{msg}'.format(msg=command_name)

        # return sut_msg
        command_name = label.name.upper()
        return '{msg}'.format(msg=command_name)

    def _message2label(self, message: str):
        """
        Converts a SUT message to a Protobuf Label.

        Args:
            message (str)
        Returns:
            Label: The converted message as a Label.
        """

        label_name = message.lower()
        label = Label(
            sort=Sort.RESPONSE,
            name=label_name,
            channel='matrix',
            physical_label=bytes(message, 'UTF-8'),
            timestamp=datetime.now())

        return label
