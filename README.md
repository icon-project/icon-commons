# ICON Commons

ICON Commons is a utility project which is used for running T-Bears and ICON Service. this project provides configuration data setting and log setting.  

## Building source code
 First, clone this project. Then go to the project folder and create a user environment and run build script.
```
$ virtualenv -p python3 venv  # Create a virtual environment.
$ source venv/bin/activate    # Enter the virtual environment.
(venv)$ ./build.sh            # run build script
(venv)$ ls dist/              # check result wheel file
iconcommons-1.0.1-py3-none-any.whl
```

## Installation

This chapter will explain how to install ICON Commons on your T-Bears or ICON Service. 

### Requirements

ICON Commons development and execution requires following environments.

- OS: MacOS, Linux
  - Windows are not supported yet.
- Python
  - Version: python 3.6.x
  - IDE: Pycharm is recommended.

### Setup on MacOS / Linux

```bash
# Install the ICON Commons
$ pip install iconcommons
```

## Reference

## License

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.
