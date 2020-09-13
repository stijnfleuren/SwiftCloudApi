<img src="https://www.swiftmobility.eu/swiftmobility.png" width="500"/>

# Swift Mobility Cloud API

## Introduction
This library provides a pure Python interface for the [Swift Mobility Cloud API](https://www.swiftmobility.eu/services). It works with Python versions 3.7 and above.

[Swift Mobility](https://www.swiftmobility.eu/>) provides services for fully automated optimization of fixed-time schedules (traffic light schedules) in a matter of seconds, even for the most complex intersections. [Swift Mobility](https://www.swiftmobility.eu/>) exposes a rest APIs and this library is intended to make it even easier for Python programmers to use.

## Installing
You can install the [Swift Mobility Cloud API](https://www.swiftmobility.eu/services) using:

```sh
$ pip install swift_cloud_py
```
## Getting the code

The code is hosted at https://github.com/stijnfleuren/swift_cloud_api

Check out the latest development version anonymously with:

    $ git clone git://github.com/stijnfleuren/swift_cloud_api.git
    $ cd swift_cloud_api

To install dependencies using pip, run:

    $ pip install -Ur requirements.txt
    
To install dependencies using pipenv, run:

    $ pipenv install

## Getting started

### Credentials
To be able to connect to the Swift Mobility Cloud API you need credentials.
To this end, set the following two environment variables:
 - smc_api_key: this is the Swift Mobility Cloud API KEY
 - smc_secret_key: this is the Swift Mobility Cloud API Secret Key.

If you do not yet have these credentials, you can send a mail to cloud_api@swiftmobility.eu.

### Examples
In the folder \examples you can find several examples to get you started.

## License
MIT licence