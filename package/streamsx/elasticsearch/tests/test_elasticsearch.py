from unittest import TestCase

from streamsx.topology.topology import Topology
from streamsx.topology.tester import Tester
from streamsx.topology.schema import CommonSchema, StreamSchema
import streamsx.elasticsearch as es
import streamsx.spl.toolkit
import streamsx.rest as sr
import os
import uuid

##
## Test assumptions
##
## Streaming analytics service has:
##    application config 'es' configured for Elasticsearch database
## or
## ELASTICSEARCH_CONNECTION environment variable is set with Elasticsearch cloud service connection string
##

class JsonData(object):
    def __init__(self, prefix, count):
        self.prefix = prefix
        self.count = count
    def __call__(self):
        for i in range(self.count):
            yield {'p': self.prefix + '_' + str(i), 'c': i}

class StringData(object):
    def __init__(self, prefix, count):
        self.prefix = prefix
        self.count = count
    def __call__(self):
        for i in range(self.count):
            yield self.prefix + '_' + str(i)
        
def get_credentials():
    result = 'es'
    try:
        result = os.environ['ELASTICSEARCH_CONNECTION']
    except KeyError: 
        result = 'es'
    return result


class TestES(TestCase):
    def setUp(self):
        Tester.setup_distributed(self)
        self.es_toolkit_home = os.environ["ELASTICSEARCH_TOOLKIT_HOME"]

    def test_json(self):
        n = 100
        topo = Topology()
        streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        uid = str(uuid.uuid4())
        s = topo.source(JsonData(uid, n)).as_json()
        es.bulk_insert(s, 'test-index-cloud', 10, credentials=get_credentials(), ssl_trust_all_certificates=True)

        tester = Tester(topo)
        tester.run_for(60)
        # setup test config
        cfg = {}
        job_config = streamsx.topology.context.JobConfig(tracing='info')
        job_config.add(cfg)
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False     
        # Run the test
        tester.test(self.test_ctxtype, cfg, always_collect_logs=True)

    def test_string(self):
        n = 100
        topo = Topology()
        streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        uid = str(uuid.uuid4())
        s = topo.source(StringData(uid, n)).as_string()
        es.bulk_insert(s, 'test-index-cloud', 10, credentials=get_credentials(), ssl_trust_all_certificates=True)

        tester = Tester(topo)
        tester.run_for(60)
        # setup test config
        cfg = {}
        job_config = streamsx.topology.context.JobConfig(tracing='info')
        job_config.add(cfg)
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False     
        # Run the test
        tester.test(self.test_ctxtype, cfg, always_collect_logs=True)
 
    def test_hw(self):
        n = 100
        topo = Topology()
        streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        s = topo.source(['Hello', 'World!']).as_string()
        es.bulk_insert(s, 'test-index-cloud', credentials=get_credentials(), ssl_trust_all_certificates=True)

        tester = Tester(topo)
        tester.run_for(60)
        # setup test config
        cfg = {}
        job_config = streamsx.topology.context.JobConfig(tracing='info')
        job_config.add(cfg)
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False     
        # Run the test
        tester.test(self.test_ctxtype, cfg, always_collect_logs=True)

    def test_schema(self):
        schema = StreamSchema('tuple<rstring indexName, rstring document>')
        topo = Topology()
        streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        s = topo.source([('idx1','{"msg":"This is message number 1"}'), ('idx2','{"msg":"This is message number 2"}')])
        s = s.map(lambda x : x, schema=schema)
        s.print()
        es.bulk_insert_dynamic(s, index_name_attribute='indexName', message_attribute='document', credentials=get_credentials(), ssl_trust_all_certificates=True)

        tester = Tester(topo)
        tester.run_for(60)

        # setup test config
        cfg = {}
        job_config = streamsx.topology.context.JobConfig(tracing='info')
        job_config.add(cfg)
        cfg[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False     
        # Run the test
        tester.test(self.test_ctxtype, cfg, always_collect_logs=True)

class TestCloud(TestES):
    def setUp(self):
        self.es_toolkit_home = os.environ["ELASTICSEARCH_TOOLKIT_HOME"]
        Tester.setup_streaming_analytics(self, force_remote_build=True)

    @classmethod
    def setUpClass(self):
        # start streams service
        connection = sr.StreamingAnalyticsConnection()
        service = connection.get_streaming_analytics()
        result = service.start_instance()


