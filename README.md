# Eiffelactory
Eiffelactory is a service written in Python that consumes EiffelArtifactCreated 
events from a RabbitMQ message bus. The event data is then used to query Artifactory 
in order to find the location of the artifact referenced in the EiffelArtifactCreated 
event. When an artifact has been found an EiffelArtifactPublished event is generated 
and broadcasted on the RabbitMQ message bus. 

For more information about Eiffel, see https://github.com/eiffel-community/eiffel.

## How it works

### Consume EiffelArtifactCreatedEvent
*For more information about this event, see the [specification](https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelArtifactCreatedEvent.md).*

Eiffelactory can be configured to listen for messages sent to a RabbitMQ message bus. 
Once set up, Eiffelactory will listen for all messages sent to a given queue. 
The messages are expected to be formatted according to the Eiffel protocol specification.
Users can choose to process all ArtC events or only ArtC events sent from certain sources. 

#### Event source filtering
If event source filtering is used, only ArtC events with the corresponding meta.source.name will be processed.
Users can specify event sources in the **eiffelactory.config** file. 

#### The data.identity PURL
Eiffelactory parses the data.identity purl to extract information about the created 
artifact. 

*TODO: Describe what information is extracted and how*

### Query Artifactory
*For more information about Artifactory, see their [website](https://jfrog.com/artifactory/).*

The data extracted from an ArtC is used to send an [AQL](https://www.jfrog.com/confluence/display/RTF/Artifactory+Query+Language) 
query to Artifactory in order find the location of the artifact referenced in the ArtC event.   

### Broadcast EiffelArtifactPublishedEvent
*For more information about this event, see the [specification](https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelArtifactPublishedEvent.md).*

*TODO: describe the generated event*

## Installation
*TODO: how to install*

## Usage
### The eiffelactory.config file
Eiffelactory can be configured by placing the *eiffelactory.config* file in the *conf* directory. 
The config file contains 3 different sections, one for RabbitMQ options, one for Artifactory 
options and one for Eiffelactory options. Users can use *eiffelactory.config.example* as a starting point.

*conf/eiffelactory.config.example:*
```
[rabbitmq]
username = someusername
password = somepassword
host = localhost
port = 15672
vhost = /
exchange = someexchange
exchange_type = topic
routing_key = #
queue = somequeue
prefetch_count = 50

[artifactory]
url = https://localhost:8081/artifactory
username = someusername
password = somepassword
aql_search_string =
    items.find(
        {{
            "name":"{artifact_name}",
            "artifact.module.build.url":
                {{"$match":"*{build_path_substring}*"}}
         }}
    ).include("name","repo","path")

[eiffelactory]
# used to filter received messages by meta.source.name
# if event_sources is not included, all ArtC events are processed
event_sources = META_SOURCE_NAME, another-source_name
``` 

Not all keys are mandatory, Eiffelactory will provide default values for the following options:
``` 
[rabbitmq]
vhost = /
prefetch_count = 50
routing_key = #

[artifactory]
aql_search_string =
    items.find(
        {{
            "name":"{artifact_name}",
            "artifact.module.build.url":
                {{"$match":"*{build_path_substring}*"}}
         }}
    ).include("name","repo","path")
    
[eiffelactory]
event_sources = None
``` 
All other keys must be present otherwise KeyError and configparser.NoOptionError will be raised. 

## Running tests
Run all tests:
```bash
$ python -m unittest discover
```

Run all tests corresponding to a specific module:
```bash
$ python -m unittest tests.test_eiffel.TestEiffel
```

Run a single test case:
```bash
$ python -m unittest tests.test_eiffel.TestEiffel.test_create_eiffel_published_event
```
## License
[MIT](https://choosealicense.com/licenses/mit/)