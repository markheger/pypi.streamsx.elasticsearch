# Python streamsx.elasticsearch package

This exposes SPL operators in the `com.ibm.streamsx.elasticsearch` toolkit as Python methods.

Package is organized using standard packaging to upload to PyPi.

The package is uploaded to PyPi in the standard way:
```
cd package
python setup.py sdist bdist_wheel upload -r pypi
```
Note: This is done using the `ibmstreams` account at pypi.org and requires `.pypirc` file containing the credentials in your home directory.

Package details: https://pypi.python.org/pypi/streamsx.elasticsearch

Documentation is using Sphinx and can be built locally using:
```
cd package/docs
make html
```
and viewed using
```
firefox package/docs/build/html/index.html
```

The documentation is also setup at `readthedocs.io`.

Documentation links:
* http://streamsxelasticsearch.readthedocs.io

## Version update

To change the version information of the Python package, edit following files:

- ./package/docs/source/conf.py
- ./package/streamsx/elasticsearch/\_\_init\_\_.py

When the development status changes, edit the *classifiers* in

- ./package/setup.py

When the documented sample must be changed, change it here:

- ./package/streamsx/elasticsearch/\_\_init\_\_.py
- ./package/DESC.txt

## Test

Package can be tested with TopologyTester using the [Streaming Analytics](https://www.ibm.com/cloud/streaming-analytics) service and [Compose for Elasticsearch](https://www.ibm.com/cloud/compose/elasticsearch) service on IBM Cloud.

Store connection parameters in application configuration, default name is 'es', or set the environment variable `ELASTICSEARCH_CONNECTION` with the connection string of the Elasticsearch cloud service.

### Test with local Streams installation in distributed mode

```
export ELASTICSEARCH_TOOLKIT_HOME=<toolkit_location>
cd package
python3 -u -m unittest streamsx.elasticsearch.tests.test_elasticsearch.TestES
```

or

```
ant test
```

### Test with Streaming Analytics service

```
export ELASTICSEARCH_TOOLKIT_HOME=<toolkit_location>
cd package
python3 -u -m unittest streamsx.elasticsearch.tests.test_elasticsearch.TestCloud
```

or 

```
ant test-sas
```
