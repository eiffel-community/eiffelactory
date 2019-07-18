from eiffelactory.utils import current_time_millis, generate_uuid

# Eiffel event types
EIFFEL_ARTIFACT_PUBLISHED_EVENT = "EiffelArtifactPublishedEvent"
EIFFEL_ARTIFACT_CREATED_EVENT = "EiffelArtifactCreatedEvent"

# Eiffel schema version
VERSION_3_0_0 = "3.0.0"


class Event(dict):
    """
    Represents an Eiffel event, all events have data, links and meta fields.
    Inherits from primitive type dict for easy json serialization using json.dumps().
    """
    def __init__(self, data, links, meta):
        super().__init__(self, data=data, links=links, meta=meta)


class Meta(dict):
    """
    Represents an Eiffel event meta object, all events have the same meta object fields.
    Parameters with None as default value are non-required fields according to the Eiffel specification.
    Inherits from primitive type dict for easy json serialization using json.dumps().
    """
    def __init__(self,
                 event_type,
                 version,
                 event_id=generate_uuid(),
                 time=current_time_millis(),
                 tags=None,
                 source=None):

        super().__init__(self, id=event_id, type=event_type, version=version, time=time, tags=tags, source=source)


class Source(dict):
    """
    Represents an Eiffel event meta.source object, all meta object have the same source object fields.
    Parameters with None as default value are non-required fields according to the Eiffel specification.
    Inherits from primitive type dict for easy json serialization using json.dumps().
    """
    def __init__(self, domain_id=None, host=None, name=None, serializer=None, uri=None):
        super().__init__(self, domainId=domain_id, host=host, name=name, serializer=serializer, uri=uri)


class Link(dict):
    """
    Represents an Eiffel link object.
    Inherits from primitive type dict for easy json serialization using json.dumps().
    """
    ARTIFACT = "ARTIFACT"

    def __init__(self, link_type, target):
        super().__init__(self, type=link_type, target=target)


class ArtifactPublishedData(dict):
    """
    Represents a data object with specific fields for an EiffelArtifactPublishedEvent
    Inherits from primitive type dict for easy json serialization using json.dumps().
    """
    def __init__(self, locations):
        super().__init__(self, locations=locations)


class Location(dict):
    """
    Represents a data.locations object with specific fields for an EiffelArtifactPublishedEvent
    Inherits from primitive type dict for easy json serialization using json.dumps().
    """
    ARTIFACTORY = "ARTIFACTORY"

    def __init__(self, uri, location_type=ARTIFACTORY):
        super().__init__(self, type=location_type, uri=uri)


def create_artifact_published_meta():
    """Returns  a meta object for an EiffelArtifactPublished event"""
    source = Source(name='EIFFELACTORY')
    return Meta(EIFFEL_ARTIFACT_PUBLISHED_EVENT, VERSION_3_0_0, source=source)


def is_eiffel_event_type(message, event_type):
    return message['meta']['type'] == event_type


def is_artifact_created_event(message):
    return is_eiffel_event_type(message, EIFFEL_ARTIFACT_CREATED_EVENT)
