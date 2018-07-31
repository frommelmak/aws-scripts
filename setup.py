import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "aws-scripts",
    version = "0.0.1",
    author = "Marcos Martínez",
    author_email = "frommelmak@gmail.com",
    description = ("Some useful AWS scripts I use from time to time"),
    license = "MIT",
    keywords = "aws amazon-web-services ec2-instance google-calendar-synchronization amazon",
    url = "http://packages.python.org/aws-scripts",
    install_requires=['boto3>=1.6.3',
                      'argparse>=',
                      'paramiko>=1.15.2',
                      'google-api-python-client>=1.7.3',
                      'oauth2client>=4.1.2',
                      'boto>=2.38.0',
                      'sshutil>=0.9.7',
                      'botocore>=1.9.3',
                      ],
    packages=['aws-scripts', 'tests'],
    scripts = ['ec2-instances.py',
               'ec2-reserved.py',
               'ec2-elb.py',
               'ec2-snap-mgmt.py',
               's3-mongodump.py',
               'rds-instances.py',
               'route53-set-hostname.py',
               'route53-del-hostname.py',
               's3-download-file.py',
               'lifecycle-hook-worker.py',
              ],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
