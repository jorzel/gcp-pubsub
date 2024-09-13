import json

import structlog
from google.auth import jwt
from google.cloud import pubsub_v1

CREDENTIALS_FILE = "credentials.json"
AUDIENCE = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"
PROJECT_ID = 'virtual-cycling-435506-d8'
SUBSCRIPTION_ID = 'reservation-created-sub'

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id=PROJECT_ID,
    sub=SUBSCRIPTION_ID
)

logger = structlog.get_logger()

service_account_info = json.load(open(CREDENTIALS_FILE))
credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=AUDIENCE,
)
credentials_sub = credentials.with_claims(audience=AUDIENCE)


def event_handler(message):
    message.ack()
    data = json.loads(message.data)
    logger.info("Received event", message=data)

    # Do something with the data, e.g. store in the reports database


with pubsub_v1.SubscriberClient(credentials=credentials_sub) as subscriber:
    logger.info("Subscribing to topic", topic=subscription_name)
    future = subscriber.subscribe(subscription_name, event_handler)
    try:
        future.result()
    except Exception as e:
        future.cancel()
        logger.info("Cancelled subscription", error=e)
