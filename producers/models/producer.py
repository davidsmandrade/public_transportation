"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)
## kafka setup
BOOTSTRAP_SERVERS = "PLAINTEXT://0.0.0.0:9092,PLAINTEXT://0.0.0.0:9093,PLAINTEXT://0.0.0.0:9094"
SCHEMA_REGISTRY_URL = 'http://schema-registry:8081/'

class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        # Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry! ##step1
        self.broker_properties = {
            "bootstrap.servers": BOOTSTRAP_SERVERS,
            "schema.registry.url": SCHEMA_REGISTRY_URL
        }

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # Configure the AvroProducer ##step2
        self.producer = AvroProducer(
            self.broker_properties,
            default_key_schema=key_schema,
            default_value_schema=value_schema,
         )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        # Write code that creates the topic for this producer if it does not already exist on
        # the Kafka Broker.##step3
        #logger.info("topic creation kafka integration incomplete - skipping")

        client = AdminClient(
            {"bootstrap.servers": self.broker_properties["bootstrap.servers"]}
        )
        topic_metadata = client.list_topics(timeout=5)
        if self.topic_name in set(
            t.topic for t in iter(topic_metadata.topics.values())
        ):
            logger.info("not recreating existing topic %s", self.topic_name)
            return
        logger.info(
            "creating topic %s with partition %s replicas %s",
            self.topic_name,
            self.num_partitions,
            self.num_replicas,
        )
        futures = client.create_topics(
            [
                NewTopic(
                    topic=self.topic_name,
                    num_partitions=self.num_partitions,
                    replication_factor=self.num_replicas,
                )
            ]
        )

        for topic, future in futures.items():
            try:
                future.result()
                logger.info("topic created")
            except Exception as e:
                logger.fatal("failed to create topic %s: %s", topic, e)

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        #Write cleanup code for the Producer here ##step4
        if self.producer is not None:
            return logger.debug("flushing producer...")
            self.producer.flush()
        #logger.info("producer close incomplete - skipping")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
