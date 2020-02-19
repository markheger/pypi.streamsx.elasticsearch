# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

import datetime

import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring
import streamsx.topology.composite
from urllib.parse import urlparse
from streamsx.toolkits import download_toolkit

_TOOLKIT_NAME = 'com.ibm.streamsx.elasticsearch'


def _add_file(topology, path):
    filename = os.path.basename(path)
    topology.add_file_dependency(path, 'opt')
    return 'opt/'+filename

def download_toolkit(url=None, target_dir=None):
    r"""Downloads the latest Elasticsearch toolkit from GitHub.

    Example for updating the Elasticsearch toolkit for your topology with the latest toolkit from GitHub::

        import streamsx.elasticsearch as es
        # download Elasticsearch toolkit from GitHub
        elasticsearch_toolkit_location = es.download_toolkit()
        # add the toolkit to topology
        streamsx.spl.toolkit.add_toolkit(topology, elasticsearch_toolkit_location)

    Example for updating the topology with a specific version of the Elasticsearch toolkit using a URL::

        import streamsx.elasticsearch as es
        url221 = 'https://github.com/IBMStreams/streamsx.elasticsearch/releases/download/v2.1.1/streamsx.elasticsearch.toolkits-2.1.1-20181204-0909.tgz'
        elasticsearch_toolkit_location = es.download_toolkit(url=url221)
        streamsx.spl.toolkit.add_toolkit(topology, elasticsearch_toolkit_location)

    Args:
        url(str): Link to toolkit archive (\*.tgz) to be downloaded. Use this parameter to 
            download a specific version of the toolkit.
        target_dir(str): the directory where the toolkit is unpacked to. If a relative path is given,
            the path is appended to the system temporary directory, for example to /tmp on Unix/Linux systems.
            If target_dir is ``None`` a location relative to the system temporary directory is chosen.

    Returns:
        str: the location of the downloaded Elasticsearch toolkit

    .. note:: This function requires an outgoing Internet connection
    .. versionadded:: 1.2
    """
    _toolkit_location = streamsx.toolkits.download_toolkit (toolkit_name=_TOOLKIT_NAME, url=url, target_dir=target_dir)
    return _toolkit_location


class Insert(streamsx.topology.composite.ForEach):
    """Stores JSON documents in a specified index of an Elasticsearch database.

    Example writing string messages to an index with credentials stored in application configuration with the name 'elasticsearch'::

        import streamsx.elasticsearch as es
        from streamsx.topology.topology import Topology

        topo = Topology()
        s = topo.source(['Hello', 'World!']).as_string()
        s.for_each(es.Insert(credentials='elasticsearch', index_name='sample-index-cloud'))

    Example with specifying connection string as credentials and additional parameters as kwargs::

        connection_string = 'https:https://ibm_cloud_USER:PASSWORD@XXXX.databases.appdomain.cloud:30735'
        config = {
            'ssl_trust_all_certificates': True
        }
        s.for_each(es.Insert(credentials=connection_string, index_name='sample-index-cloud', **config))

    Example with dynamic index name (part of the stream)::

        s = topo.source([('idx1','{"msg":"This is message number 1"}'), ('idx2','{"msg":"This is message number 2"}')])
        schema = StreamSchema('tuple<rstring indexName, rstring document>')
        s = s.map(lambda x : x, schema=schema)
        config = {
            'ssl_trust_all_certificates': True,
            'index_name_attribute': 'indexName',
            'message_attribute': 'document'
        }
        s.for_each(es.Insert(credentials=connection_string, index_name=None, **config))

    .. versionadded:: 1.3

    Attributes
    ----------
    credentials : str
        Name of the application configuration containing the credentials as properties or the connection string for your Elasticsearch database. When set to ``None``, the application configuration name ``es`` is used.
    index_name: str
        Name of the Elasticsearch index, the documents will be inserted to. If the index does not exist in the Elasticsearch server, it will be created by the server. However, you should create and configure indices by yourself before using them, to avoid automatic creation with properties that do not match the use case. For example unsuitable mapping or number of shards or replicas. 
    bulk_size: int
        Size of the bulk to submit to Elasticsearch. The default value is 1.
    options : kwargs
        The additional optional parameters as variable keyword arguments.
    """

    def __init__(self, credentials, index_name, bulk_size=1, **options):
        self.credentials = credentials
        self.index_name = index_name
        self.bulk_size = bulk_size
        
        self.vm_arg = None
        self.index_name_attribute = None
        self.message_attribute = None
        self.ssl_trust_all_certificates = None
        self.ssl_debug = None
        self.ssl_trust_store = None
        self.ssl_trust_store_password = None
        self.ssl_verify_hostname = None
        self.read_timeout = None
        self.reconnection_policy_count = None
        self.connection_timeout = None
        if 'index_name_attribute' in options:
            self.index_name_attribute = options.get('index_name_attribute')
        if 'message_attribute' in options:
            self.message_attribute = options.get('message_attribute')
        if 'ssl_trust_all_certificates' in options:
            self.ssl_trust_all_certificates = options.get('ssl_trust_all_certificates')
        if 'ssl_debug' in options:
            self.ssl_debug = options.get('ssl_debug')
        if 'ssl_trust_store' in options:
            self.ssl_trust_store = options.get('ssl_trust_store')
        if 'ssl_trust_store_password' in options:
            self.ssl_trust_store_password = options.get('ssl_trust_store_password')
        if 'ssl_verify_hostname' in options:
            self.ssl_verify_hostname = options.get('ssl_verify_hostname')
        if 'read_timeout' in options:
            self.read_timeout = options.get('read_timeout')
        if 'reconnection_policy_count' in options:
            self.reconnection_policy_count = options.get('reconnection_policy_count')
        if 'connection_timeout' in options:
            self.connection_timeout = options.get('connection_timeout')

    @property
    def vm_arg(self):
        """
            str: Arbitrary JVM arguments can be passed to the Streams operator
        """
        return self._vm_arg

    @vm_arg.setter
    def vm_arg(self, value):
        self._vm_arg = value

    @property
    def index_name_attribute(self):
        """
            str: Name of the input stream attribute containing the Elasticsearch index, the documents will be inserted to.
        """
        return self._index_name_attribute

    @index_name_attribute.setter
    def index_name_attribute(self, value):
        self._index_name_attribute = value

    @property
    def message_attribute(self):
        """
            str: Name of the input stream attribute containing the JSON document. Parameter is not required when input stream schema is ``CommonSchema.Json``.
        """
        return self._message_attribute

    @message_attribute.setter
    def message_attribute(self, value):
        self._message_attribute = value

    @property
    def ssl_trust_all_certificates(self):
        """
            bool: If set to 'True', the SSL/TLS layer will not verify the server certificate chain. The default is 'False'. This parameter can be overwritten by the application configuration.
        """
        return self._ssl_trust_all_certificates

    @ssl_trust_all_certificates.setter
    def ssl_trust_all_certificates(self, value):
        self._ssl_trust_all_certificates = value

    @property
    def ssl_debug(self):
        """
            bool: If set to 'True', SSL/TLS protocol debugging is enabled, all protocol data and information is logged to the console. The default is 'False'.
        """
        return self._ssl_debug

    @ssl_debug.setter
    def ssl_debug(self, value):
        self._ssl_debug = value

    @property
    def ssl_trust_store(self):
        """
            str: Specifies the name of a file containing trusted certificates. This file is added to the application directory.
        """
        return self._ssl_trust_store

    @ssl_trust_store.setter
    def ssl_trust_store(self, value):
        self._ssl_trust_store = value

    @property
    def ssl_trust_store_password(self):
        """
            str: Specify the password used to access the Truststore file.
        """
        return self._ssl_trust_store_password

    @ssl_trust_store_password.setter
    def ssl_trust_store_password(self, value):
        self._ssl_trust_store_password = value

    @property
    def ssl_verify_hostname(self):
        """
            bool: If set to False, the SSL/TLS layer will not verify the hostname in the server certificate against the actual name of the server host. WARNING: this is unsecure and should only be used for debugging purposes. The default is True.
        """
        return self._ssl_verify_hostname

    @ssl_verify_hostname.setter
    def ssl_verify_hostname(self, value):
        self._ssl_verify_hostname = value

    @property
    def read_timeout(self):
        """
            int: The timeout for waiting for a REST response from the server node. Specified in milliseconds. The default value is 5000 (5 seconds).
        """
        return self._read_timeout

    @read_timeout.setter
    def read_timeout(self, value):
        self._read_timeout = value

    @property
    def reconnection_policy_count(self):
        """
            int: Specifies the number of reconnection attemps to th Elasticsearch server, upon disconnection.
        """
        return self._reconnection_policy_count

    @reconnection_policy_count.setter
    def reconnection_policy_count(self, value):
        self._reconnection_policy_count = value

    @property
    def connection_timeout(self):
        """
            int: The timeout for waiting on establishment of the TCP connection to the server node. Specified in milliseconds. The default value is 20000 (20 seconds).
        """
        return self._connection_timeout

    @connection_timeout.setter
    def connection_timeout(self, value):
        self._connection_timeout = value


    def populate(self, topology, stream, name, **options) -> streamsx.topology.topology.Sink:
        if stream.oport.schema == CommonSchema.Json:
            self.message_attribute = 'jsonString'     

        _op = _ElasticsearchIndex(stream, indexName=self.index_name, bulkSize=self.bulk_size, name=name)
        if self.message_attribute is not None:
           _op.params['documentAttribute'] = _op.attribute(stream, self.message_attribute)
        if self.index_name_attribute is not None:
           _op.params['indexNameAttribute'] = _op.attribute(stream, self.index_name_attribute)

        # check credentials - either app config name or connection string
        if self.credentials is None:
            self.credentials = 'es'
        creds = urlparse(self.credentials)
        if not creds.netloc:
            _op.params['appConfigName'] = self.credentials
            if self.ssl_trust_all_certificates == True:
                _op.params['sslTrustAllCertificates'] = _op.expression('true')
            else:
                _op.params['sslTrustAllCertificates'] = _op.expression('false')
        else:
           _op.params['userName'] = creds.username
           _op.params['password'] = creds.password
           _op.params['nodeList'] = creds.hostname+':'+str(creds.port)
           if creds.scheme == 'https':
               _op.params['sslEnabled'] = _op.expression('true')
               if self.ssl_trust_all_certificates == True:
                   _op.params['sslTrustAllCertificates'] = _op.expression('true')
               else:
                   _op.params['sslTrustAllCertificates'] = _op.expression('false')

        if self.ssl_debug is not None:
            if self.ssl_debug == True:
                _op.params['sslDebug'] = _op.expression('true')
        if self.ssl_trust_store is not None:
            _op.params['sslTrustStore'] = _add_file(topology, self.ssl_trust_store)
        if self.ssl_trust_store_password is not None:
            _op.params['sslTrustStorePassword'] = self.ssl_trust_store_password
        if self.ssl_verify_hostname is not None:
            if self.ssl_verify_hostname == True:
                _op.params['sslVerifyHostname'] = _op.expression('true')
        if self.read_timeout is not None:
            _op.params['readTimeout'] = streamsx.spl.types.int32(self.read_timeout)
        if self.reconnection_policy_count is not None:
            _op.params['reconnectionPolicyCount'] = streamsx.spl.types.int32(self.reconnection_policy_count)
        if self.connection_timeout is not None:
            _op.params['connectionTimeout'] = streamsx.spl.types.int32(self.connection_timeout)

        return streamsx.topology.topology.Sink(_op)



def bulk_insert(stream, index_name, bulk_size=1, message_attribute=None, credentials='es', ssl_trust_all_certificates=False, name=None):
    """Stores JSON documents in a specified index of an Elasticsearch database.

    Ingests tuples and stores them in Elasticsearch as documents when bulk size is reached.
    If input is ``streamsx.topology.schema.StreamSchema``, then each attribute in the input schema will become an document attribute, the name of the JSON attribute will be the name of the Stream tuple attribute, the value will be taken from the attributes value. 
    Writes JSON documents without conversion, when input stream is ``CommonSchema.Json``.

    Args:
        stream(streamsx.topology.topology.Stream): Stream of tuples stored in Elasticsearch as documents. Supports ``CommonSchema.Json`` in the input stream to store the JSON messages in Elasticsearch. Otherwise each attribute in the input schema will become an document attribute, the name of the JSON attribute will be the name of the Streams tuple attribute, the value will be taken from the attributes value.
        index_name(str): Name of the Elasticsearch index, the documents will be inserted to. If the index does not exist in the Elasticsearch server, it will be created by the server. However, you should create and configure indices by yourself before using them, to avoid automatic creation with properties that do not match the use case. For example unsuitable mapping or number of shards or replicas. 
        bulk_size(int): Size of the bulk to submit to Elasticsearch. The default value is 1.      
        message_attribute(str): Name of the input stream attribute containing the JSON document. Parameter is not required when input stream schema is ``CommonSchema.Json``.                     
        credentials(str): Name of the application configuration containing the credentials as properties or the connection string for your Elasticsearch database. When not set, the application configuration name ``es`` is used.
        ssl_trust_all_certificates(bool): If set to 'True', the SSL/TLS layer will not verify the server certificate chain. The default is 'False'. This parameter can be overwritten by the application configuration.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        :py:class:`topology_ref:streamsx.topology.topology.Sink`: Stream termination.

    .. deprecated:: 1.3.0
        Use the :py:class:`~Insert`.
    """
    if stream.oport.schema == CommonSchema.Json:
        message_attribute = 'jsonString'     

    _op = _ElasticsearchIndex(stream, indexName=index_name, bulkSize=bulk_size, name=name)
    if message_attribute is not None:
       _op.params['documentAttribute'] = _op.attribute(stream, message_attribute)
    # check credentials - either app config name or connection string
    creds = urlparse(credentials)
    if not creds.netloc:
        _op.params['appConfigName'] = credentials
        if ssl_trust_all_certificates == True:
            _op.params['sslTrustAllCertificates'] = _op.expression('true')
        else:
            _op.params['sslTrustAllCertificates'] = _op.expression('false')
    else:
       _op.params['userName'] = creds.username
       _op.params['password'] = creds.password
       _op.params['nodeList'] = creds.hostname+':'+str(creds.port)
       if creds.scheme == 'https':
           _op.params['sslEnabled'] = _op.expression('true')
           if ssl_trust_all_certificates == True:
               _op.params['sslTrustAllCertificates'] = _op.expression('true')
           else:
               _op.params['sslTrustAllCertificates'] = _op.expression('false')

    return streamsx.topology.topology.Sink(_op)

    
def bulk_insert_dynamic(stream, index_name_attribute, message_attribute, bulk_size=1, credentials='es', ssl_trust_all_certificates=False, name=None):
    """Stores JSON documents in a specified index of an Elasticsearch database. The index name is part of the input stream.

    Ingests tuples and stores them in Elasticsearch as documents when bulk size is reached.
    The index name can change per tuple. 

    Example with dynamic index name passed with input stream attribute, where the input stream "sample_stream" is of type "sample_schema"::

        import streamsx.elasticsearch as es
        
        sample_schema = StreamSchema('tuple<rstring indexName, rstring document>')
        ...
        es.bulk_insert_dynamic(sample_stream, index_name_attribute='indexName', message_attribute='document')

    Args:
        stream(streamsx.topology.topology.Stream): Stream of tuples stored in Elasticsearch as documents. Requires ``streamsx.topology.schema.StreamSchema`` (schema for a structured stream) as input.
        index_name_attribute(str): Name of the input stream attribute containing the Elasticsearch index, the documents will be inserted to.
        message_attribute(str): Name of the input stream attribute containing the JSON document.                    
        bulk_size(int): Size of the bulk to submit to Elasticsearch. The default value is 1.      
        credentials(str): Name of the application configuration containing the credentials as properties or the connection string for your Elasticsearch database. When not set, the application configuration name ``es`` is used.
        ssl_trust_all_certificates(bool): If set to 'True', the SSL/TLS layer will not verify the server certificate chain. The default is 'False'. This parameter can be overwritten by the application configuration.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        :py:class:`topology_ref:streamsx.topology.topology.Sink`: Stream termination.

    .. deprecated:: 1.3.0
        Use the :py:class:`~Insert`.
    """

    _op = _ElasticsearchIndex(stream, bulkSize=bulk_size, name=name)
    _op.params['documentAttribute'] = _op.attribute(stream, message_attribute)
    _op.params['indexNameAttribute'] = _op.attribute(stream, index_name_attribute)
    # check credentials - either app config name or connection string
    creds = urlparse(credentials)
    if not creds.netloc:
        _op.params['appConfigName'] = credentials
        if ssl_trust_all_certificates == True:
            _op.params['sslTrustAllCertificates'] = _op.expression('true')
        else:
            _op.params['sslTrustAllCertificates'] = _op.expression('false')
    else:
       _op.params['userName'] = creds.username
       _op.params['password'] = creds.password
       _op.params['nodeList'] = creds.hostname+':'+str(creds.port)
       if creds.scheme == 'https':
           _op.params['sslEnabled'] = _op.expression('true')
           if ssl_trust_all_certificates == True:
               _op.params['sslTrustAllCertificates'] = _op.expression('true')
           else:
               _op.params['sslTrustAllCertificates'] = _op.expression('false')

    return streamsx.topology.topology.Sink(_op)


class _ElasticsearchIndex(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema=None, vmArg=None, appConfigName=None, bulkSize=None, connectionTimeout=None, documentAttribute=None, hostName=None, hostPort=None, idName=None, idNameAttribute=None, indexName=None, indexNameAttribute=None, maxConnectionIdleTime=None, nodeList=None, password=None, readTimeout=None, reconnectionPolicyCount=None, sslDebug=None, sslEnabled=None, sslTrustAllCertificates=None, sslTrustStore=None, sslTrustStorePassword=None, sslVerifyHostname=None, storeTimestamps=None, timestampName=None, timestampValueAttribute=None, userName=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.elasticsearch::ElasticsearchIndex"
        inputs=stream
        schemas=schema
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if bulkSize is not None:
            params['bulkSize'] = bulkSize
        if connectionTimeout is not None:
            params['connectionTimeout'] = connectionTimeout
        if documentAttribute is not None:
            params['documentAttribute'] = documentAttribute
        if hostName is not None:
            params['hostName'] = hostName
        if hostPort is not None:
            params['hostPort'] = hostPort
        if idName is not None:
            params['idName'] = idName
        if idNameAttribute is not None:
            params['idNameAttribute'] = idNameAttribute
        if indexName is not None:
            params['indexName'] = indexName
        if indexNameAttribute is not None:
            params['indexNameAttribute'] = indexNameAttribute
        if maxConnectionIdleTime is not None:
            params['maxConnectionIdleTime'] = maxConnectionIdleTime
        if nodeList is not None:
            params['nodeList'] = nodeList
        if password is not None:
            params['password'] = password
        if readTimeout is not None:
            params['readTimeout'] = readTimeout
        if reconnectionPolicyCount is not None:
            params['reconnectionPolicyCount'] = reconnectionPolicyCount
        if sslDebug is not None:
            params['sslDebug'] = sslDebug
        if sslEnabled is not None:
            params['sslEnabled'] = sslEnabled
        if sslTrustAllCertificates is not None:
            params['sslTrustAllCertificates'] = sslTrustAllCertificates
        if sslTrustStore is not None:
            params['sslTrustStore'] = sslTrustStore
        if sslTrustStorePassword is not None:
            params['sslTrustStorePassword'] = sslTrustStorePassword
        if sslVerifyHostname is not None:
            params['sslVerifyHostname'] = sslVerifyHostname
        if storeTimestamps is not None:
            params['storeTimestamps'] = storeTimestamps
        if timestampName is not None:
            params['timestampName'] = timestampName
        if timestampValueAttribute is not None:
            params['timestampValueAttribute'] = timestampValueAttribute
        if userName is not None:
            params['userName'] = userName

        super(_ElasticsearchIndex, self).__init__(topology,kind,inputs,schema,params,name)



