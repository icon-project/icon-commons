# ICON Commons

ICON Commons is a utility project which is used for running T-Bears and ICON Service.
This project provides some utility classes for setting configuration data and logging.

## Building from Source
After checking out the source code, create a virtual environment and run the build script in the source directory as follows.
```
$ virtualenv -p python3 venv  # create a virtual environment
$ source venv/bin/activate    # switch to the virtual environment
(venv) $ ./build.sh           # run the build script
(venv) $ ls dist/             # check the generated wheel file
iconcommons-1.1.3-py3-none-any.whl
```

## Installation

Basically you can install ICON Commons package by using `pip3` command on your local environment.

### Requirements

ICON Commons package requires the following environments.

- OS: MacOS, Linux
  - Windows is not supported
- Python
  - Make a virtualenv for Python 3.6.5+ (3.7 is also supported)
  - Check your Python version
    ```bash
    $ python3 -V
    Python 3.6.7
    ```
  - IDE: PyCharm is recommended.

### Installing on MacOS / Linux

```bash
(venv) $ pip3 install iconcommons
```

## Reference

## License

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.
