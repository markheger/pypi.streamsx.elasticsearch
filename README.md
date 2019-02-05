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

## Test

Package can be tested with TopologyTester using the [Streaming Analytics](https://www.ibm.com/cloud/streaming-analytics) service and [Compose for Elasticsearch](https://www.ibm.com/cloud/compose/elasticsearch) service on IBM Cloud.

Store connection parameters in application configuration, default name is 'es', or set the environment variable `ELASTICSEARCH_CONNECTION` with the connection string of the Elasticsearch cloud service.

```
export ELASTICSEARCH_TOOLKIT_HOME=<toolkit_location>
cd package
python3 -u -m unittest streamsx.elasticsearch.tests.test_elasticsearch.TestES
```
