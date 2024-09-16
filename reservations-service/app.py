import json
import os
import uuid
from datetime import datetime

import structlog
from flask import Flask
from google.auth import jwt
from google.cloud import pubsub_v1


CREDENTIALS_FILE = "credentials.json"
AUDIENCE = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
PROJECT_ID = os.environ.get('PROJECT_ID')
TOPIC_ID = os.getenv('TOPIC_ID')

service_account_info = json.load(open(CREDENTIALS_FILE))
credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=AUDIENCE,
)
credentials_pub = credentials.with_claims(audience=AUDIENCE)

app = Flask(__name__)


class ReservationCreatedEvent:
    def __init__(self, reservation_id):
        self.reservation_id = reservation_id

    def to_dict(self):
        return {
            "time": datetime.now().isoformat(),
            "type": "reservation_created",
            "data": {
                "reservation_id": self.reservation_id
            }
        }


class GCPPublisherClient:
    def __init__(self, google_cloud_project, topic_id, credentials):
        """
            :param google_cloud_project: Google project ID
            :param topic_id: Topic ID
        """
        self._pub_client = pubsub_v1.PublisherClient(credentials=credentials_pub)
        self._pub_topic = self._pub_client.topic_path(google_cloud_project, topic_id)
        self._logger = structlog.get_logger()

    def publish(self, event):
        event_payload = json.dumps(event.to_dict()).encode("utf-8")
        self._logger.info("Publishing event", data=event_payload)
        future = self._pub_client.publish(
            self._pub_topic, data=event_payload,
        )
        r = future.result()
        self._logger.info("Message published successfully", r=r)


@app.route('/reservations', methods=['POST'])
def create_reservation():
    publisher_client = GCPPublisherClient(PROJECT_ID, TOPIC_ID, credentials_pub)

    # some logic checking if reservation can be created

    event = ReservationCreatedEvent(str(uuid.uuid4()))
    publisher_client.publish(event)
    return "Reservation created", 201
