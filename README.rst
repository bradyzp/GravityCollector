

Gravity Collection Protocol
---------------------------

1. Device (Sensor Data Logger) pings server to check if it is registered and if
    the configuration matches its current config.
    e.g. GET /sensor/at1m-15

    RESPONSE 200  Content-Type: application/json
        { SensorID: 2, ConfigID: 31, ConfigHash: <sha256 hash> }

2. If device is not registered in system it must CREATE the Sensor & Configuration entities::

    e.g. POST /sensor/at1m-15?type=at1m&config=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad&g0=10000.0&gravcal=20005.123


3. After sensor is created/validated data can be sent::

    e.g. POST /data/at1m-15
    Content-Type application/json
    {
        gravity: 10010.351
    }


Installation with uWSGI and NGINX on CentOS7
--------------------------------------------

1. GravityRepo is packaged as a wheel using setup.py::

    python setup.py bdist_wheel

2. On the deployment target ensure Python 3.6 or greater is installed::

    sudo yum install https://centos7.iuscommunity.org/ius-release.rpm
    sudo yum install python36u python36u-devel python36u-libs
    sudo yum install uwsgi

2a. uwsgi can alternatively be installed via pip but requires a c-compiler e.g. glibc

3. Create a directory and venv where the application will reside e.g. in /opt::

    mkdir /opt/gravityrepo && cd /opt/gravityrepo
    python3.6 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install GravityRepo-x.x-py3-none-any.whl

4. Create the requisite uwsgi.ini and wsgi.py files in the application directory, e.g. /opt/gravityrepo
    - uwsgi.ini follows uwsgi conventions for specifying configuration parameters,
      this file alleviates the need to specify the options on the command line
    - wsgi.py simply imports the Flask app (and creates an instance if a factory is utilized),
      the instance is referenced in the uwsgi.ini module directive

5. Create the systemd unit service file (see gravityrepo.service) and install it in /etc/systemd/system/<name>.service
    - Note that the example unit file utilizes an environment variables file
    - The RuntimeDirectory=uwsgi directive creates a directory named uwsgi in /run on launch, this is where the socket file will be created
    - Note that the nginx user must have sufficient permissions to read/write the socket file

