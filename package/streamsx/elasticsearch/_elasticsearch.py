# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2018

import datetime

import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring
from urllib.parse import urlparse
from streamsx.toolkits import download_toolkit

_TOOLKIT_NAME = 'com.ibm.streamsx.elasticsearch'


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


def bulk_insert(stream, index_name, bulk_size=1, message_attribute=None, credentials='es', ssl_trust_all_certificates=False, name=None):
    """Stores JSON documents in a specified index of an Elasticsearch database.

    Ingests tuples and stores them in Elasticsearch as documents when bulk size is reached.
    If input is ``streamsx.topology.schema.StreamSchema``, then each attribute in the input schema will become an document attribute, the name of the JSON attribute will be the name of the Streams tuple attribute, the value will be taken from the attributes value. 
    Writes JSON documents without conversion, when input stream is ``CommonSchema.Json``.

    Args:
        stream(Stream): Stream of tuples stored in Elasticsearch as documents. Supports ``CommonSchema.Json`` in the input stream to store the JSON messages in Elasticsearch. Otherwise each attribute in the input schema will become an document attribute, the name of the JSON attribute will be the name of the Streams tuple attribute, the value will be taken from the attributes value.
        index_name(str): Name of the Elasticsearch index, the documents will be inserted to. If the index does not exist in the Elasticsearch server, it will be created by the server. However, you should create and configure indices by yourself before using them, to avoid automatic creation with properties that do not match the use case. For example unsuitable mapping or number of shards or replicas. 
        bulk_size(int): Size of the bulk to submit to Elasticsearch. The default value is 1.      
        message_attribute(str): Name of the input stream attribute containing the JSON document. Parameter is not required when input stream schema is ``CommonSchema.Json``.                     
        credentials(str): Name of the application configuration containing the credentials as properties or the connection string for your Elasticsearch database. When not set, the application configuration name ``es`` is used.
        ssl_trust_all_certificates(bool): If set to 'True', the SSL/TLS layer will not verify the server certificate chain. The default is 'False'. This parameter can be overwritten by the application configuration.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        streamsx.topology.topology.Sink: Stream termination.
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
        stream(Stream): Stream of tuples stored in Elasticsearch as documents. Requires ``streamsx.topology.schema.StreamSchema`` (schema for a structured stream) as input.
        index_name_attribute(str): Name of the input stream attribute containing the Elasticsearch index, the documents will be inserted to.
        message_attribute(str): Name of the input stream attribute containing the JSON document.                    
        bulk_size(int): Size of the bulk to submit to Elasticsearch. The default value is 1.      
        credentials(str): Name of the application configuration containing the credentials as properties or the connection string for your Elasticsearch database. When not set, the application configuration name ``es`` is used.
        ssl_trust_all_certificates(bool): If set to 'True', the SSL/TLS layer will not verify the server certificate chain. The default is 'False'. This parameter can be overwritten by the application configuration.
        name(str): Sink name in the Streams context, defaults to a generated name.

    Returns:
        streamsx.topology.topology.Sink: Stream termination.
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



