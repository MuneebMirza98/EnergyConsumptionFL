"""
Author: Hugo Miralles
Module to transmit (receive/send/get the response/send back the response)
the messages received to the different parties (if available).
Ask the computation and communication simulations to simulate what is needed.
"""

# IMPORT IBM-FL
from ibmfl.message.message import ResponseMessage, Message
from ibmfl.util.config import configure_logging_from_file
from ibmfl.connection.router_handler import Router

# IMPORT
import sys
import os
import re
import logging
import threading
from multiprocessing.pool import ThreadPool

fl_path = os.path.abspath("..")
if fl_path not in sys.path:
    sys.path.insert(0, fl_path)

# IMPORT CLUSTERED-FL
from clustered_fl.ibmfl_extension.cluster_message_type import ClusterMessageType
from clustered_fl.ibmfl_extension.config import get_sim_env_config
from clustered_fl.ibmfl_extension.route_declarations import get_sim_env_router

logger = logging.getLogger(__name__)


class SimEnvServer:
    def __init__(self, **kwargs):
        """
        Initiate the protohandler.
        """
        configure_logging_from_file()

        cls_config = get_sim_env_config(**kwargs)

        env_config = cls_config.get("sim_env_config")
        connection_config = cls_config.get("connection")

        self.pool = ThreadPool(processes=1)
        self.lock = threading.Lock()

        try:
            # Load simulation environment
            env_cls_ref = env_config.get("cls_ref")
            env_info = env_config.get("hyperparams")
            self.env = env_cls_ref(**env_info)

            # Initalize connection
            connection_cls_ref = connection_config.get("cls_ref")
            connection_info = connection_config.get("info")
            # connection_synch = connection_config.get("sync")
            self.connection = connection_cls_ref(connection_info)
            self.connection.initialize_sender()

            # Init router to routes the received messages the good methods
            self.router = Router()
            get_sim_env_router(self.router, self)
            self.connection.initialize_receiver(router=self.router)

        except Exception as e:
            logger.exception(
                "Exception occured while initializing simulation environment."
            )
            logger.info(str(e))
        else:
            logger.info("Simulation environment initialisation successful.")

    def handle_request(self, message):
        """
        Handle the request received, simuate the environment and send
        the request to the destination.
        """
        response_data = {"status": "success"}
        try:
            response_msg = None
            if message.message_type == ClusterMessageType.GET_STATES.value:
                response_data["states"] = self.env.get_states(message.get_data())
            if message.message_type == ClusterMessageType.SIMULATE_TRAIN.value:
                self.env.simulate_training(message.get_data())
        except Exception as e:
            logger.exception(str(e))
            response_data = {"status": "error", "details": str(e)}
        response_msg = ResponseMessage(req_msg=message)
        response_msg.set_data(response_data)
        return response_msg

    def execute_async(self, msg):  # id_request
        """
        Handle run in a different thread to allow asynchronous requests.

        :param msg: Message object form connection
        :type msg: `Message`
        """
        try:
            logger.info("Trying to acquire lock")
            # Acquire lock so that we do not run train twice
            self.lock.acquire()
            logger.info("Handling async request in a separate thread")
            response_msg = self.handle_request(msg)

        except Exception as ex:
            logger.info("Exception occurred while async handling of msg: " + msg)
            logger.exception(ex)

            response_msg = ResponseMessage(msg)
            response_msg.set_data({"status": "error", "payload": None})
        logger.info("successfully finished async request")

        # self.connection.send_message(self.agg_info, response_msg)

        # if self.metrics_recorder:
        #     with open(self.metrics_recorder.get_output_file(), "w") as metrics_file:
        #         metrics_output_type = self.metrics_recorder.get_output_type()
        #         if metrics_output_type == "json":
        #             metrics_output_data = self.metrics_recorder.to_json()
        #         else:
        #             logger.info("Bad metrics output filetype. Defaulting to json.")
        #             metrics_output_data = self.metrics_recorder.to_json()
        #         metrics_file.write("{}\n".format(metrics_output_data))

        # Release lock
        self.lock.release()
        return

    def handle_async_request(self, msg):
        """
        Handle all incoming requests asynchronously and route it to respective
         methods in local training handler.

        :param msg: Message object form connection
        :type msg: `Message`
        :return: Response message sent back to requester
        :rtype: ResponseMessage
        """
        try:
            response_msg = ResponseMessage(
                message_type=ClusterMessageType.ACK.value,
                # id_request=-1,
                data={"ACK": True, "status": "success"},
            )
            logger.info("received a async request")

            # id_request = msg.get_header()["id_request"]

            self.pool.apply_async(self.execute_async, args=(msg,))  # id_request
            logger.info("finished async request")
        except Exception as ex:
            logger.info(ex)

        return response_msg

    def start(self):
        """
        Start a server for the Simulation env in a new thread
        Parties can connect to register
        """
        try:
            self.connection.start()
        except Exception as ex:
            logger.error("Error occurred during start")
            logger.error(ex)
        else:
            logger.info("Simulation env = start successful")

    def stop(self):
        """
        Stop the sim_env and the connection.
        """
        try:
            self.connection.stop()
        except Exception as ex:
            logger.error("Error occurred during stop")
            logger.error(str(ex))
        else:
            logger.info("Simulation env stop successful")


class TestEnv:
    def __init__(self, **kwargs):
        logger.info(f"Init args: {kwargs} \n")

    def get_states(self, data):
        states = {_id: {"available": True} for _id in data["party_ids"]}
        logger.info(f"get_states inputs:\n {data} \n return: \n {states} \n")
        return states

    def simulate_training(self, data):
        logger.info(f"simulate_training inputs:\n {data} \n")


if __name__ == "__main__":
    """
    Main function can be used to create an application out
    of our party class which could be interactive
    """
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        logging.error("Please provide yaml configuration")
    config_file = sys.argv[1]
    sim_env = SimEnvServer(config_file=config_file)

    sim_env.start()

    # Indefinite loop to accept user commands to execute
    while 1:
        msg = sys.stdin.readline()
        # if re.match("START", msg):
        #     # Start server
        #     p.start()

        if re.match("STOP", msg):
            sim_env.stop()
            break

        # if re.match("REGISTER", msg):
        #     p.register()

        # if re.match("EVAL", msg):
        #     p.evaluate_model()

        # if re.match("SAVE", msg):
        #     commands = msg.split(" ")
        #     filename = commands[1] if len(commands) > 1 else None
        #     p.save_model(filename)

        # if sim_env.proto_handler.status == StatusType.STOPPING:
        #     sim_env.stop()
        #     break
