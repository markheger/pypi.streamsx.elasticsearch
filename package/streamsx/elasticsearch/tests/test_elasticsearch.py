from unittest import TestCase

from streamsx.topology.topology import Topology
from streamsx.topology.tester import Tester
from streamsx.topology.schema import CommonSchema, StreamSchema
import streamsx.elasticsearch as es
import streamsx.spl.toolkit
import streamsx.rest as sr
import os

##
## Test assumptions
##
## Streaming analytics service has:
##    application config 'es' configured for Elasticsearch database
## or
## ELASTICSEARCH_CONNECTION environment variable is set with Elasticsearch cloud service connection string
##

      
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
        # setup test config
        self.test_config = {}
        job_config = streamsx.topology.context.JobConfig(tracing='info')
        job_config.add(self.test_config)
        self.test_config[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False  
 
    def _build_only(self, name, topo):
        result = streamsx.topology.context.submit("TOOLKIT", topo.graph) # creates tk* directory
        print(name + ' (TOOLKIT):' + str(result))
        assert(result.return_code == 0)
        result = streamsx.topology.context.submit("BUNDLE", topo.graph)  # creates sab file
        print(name + ' (BUNDLE):' + str(result))
        assert(result.return_code == 0)

    def test_hw(self):
        print ('\n---------'+str(self))
        name = 'test_hw'
        n = 100
        topo = Topology(name)
        if self.es_toolkit_home is not None:
            streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        s = topo.source(['Hello', 'World!']).as_string()
        es.bulk_insert(s, 'test-index-cloud', credentials=get_credentials(), ssl_trust_all_certificates=True)

        tester = Tester(topo)
        tester.run_for(60)
    
        # Run the test
        tester.test(self.test_ctxtype, self.test_config, always_collect_logs=True)

    def test_composite(self):
        print ('\n---------'+str(self))
        name = 'test_composite'
        n = 100
        topo = Topology(name)
        if self.es_toolkit_home is not None:
            streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        s = topo.source(['Hello', 'World!']).as_string()
        config = {
            'ssl_trust_all_certificates': True
        }
        s.for_each(es.Insert(credentials=get_credentials(), index_name='test-index-cloud', **config))

        tester = Tester(topo)
        tester.run_for(60)
    
        # Run the test
        tester.test(self.test_ctxtype, self.test_config, always_collect_logs=True)

    def test_composite_with_index_attribute(self):
        print ('\n---------'+str(self))
        name = 'test_composite_with_index_attribute'
        schema = StreamSchema('tuple<rstring indexName, rstring document>')
        topo = Topology(name)
        if self.es_toolkit_home is not None:
            streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        s = topo.source([('idx1','{"msg":"This is message number 1"}'), ('idx2','{"msg":"This is message number 2"}')])
        s = s.map(lambda x : x, schema=schema)
        config = {
            'ssl_trust_all_certificates': True,
            'index_name_attribute': 'indexName',
            'message_attribute': 'document'
        }
        s.for_each(es.Insert(credentials=get_credentials(), index_name=None, **config))
        # build only
        self._build_only(name, topo)

    def test_schema(self):
        print ('\n---------'+str(self))
        name = 'test_schema'
        schema = StreamSchema('tuple<rstring indexName, rstring document>')
        topo = Topology(name)
        if self.es_toolkit_home is not None:
            streamsx.spl.toolkit.add_toolkit(topo, self.es_toolkit_home)

        s = topo.source([('idx1','{"msg":"This is message number 1"}'), ('idx2','{"msg":"This is message number 2"}')])
        s = s.map(lambda x : x, schema=schema)
        es.bulk_insert_dynamic(s, index_name_attribute='indexName', message_attribute='document', credentials=get_credentials(), ssl_trust_all_certificates=True)
        # build only
        self._build_only(name, topo)

class TestCloud(TestES):
    def setUp(self):
        self.es_toolkit_home = os.environ["ELASTICSEARCH_TOOLKIT_HOME"]
        Tester.setup_streaming_analytics(self, force_remote_build=False)

    @classmethod
    def setUpClass(self):
        # start streams service
        connection = sr.StreamingAnalyticsConnection()
        service = connection.get_streaming_analytics()
        result = service.start_instance()

class TestCloudRemote(TestCloud):
    def setUp(self):
        Tester.setup_streaming_analytics(self, force_remote_build=True)
        self.es_toolkit_home = os.environ["ELASTICSEARCH_TOOLKIT_HOME"]

    @classmethod
    def setUpClass(self):
        super().setUpClass()


class TestICPRemote(TestES):
    def setUp(self):
        Tester.setup_distributed(self)
        self.es_toolkit_home = None
        # setup test config
        self.test_config = {}
        job_config = streamsx.topology.context.JobConfig(tracing='info')
        job_config.add(self.test_config)
        self.test_config[streamsx.topology.context.ConfigParams.SSL_VERIFY] = False 

    @classmethod
    def setUpClass(self):
        super().setUpClass()

