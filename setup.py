import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "aws-scripts",
    version = "0.1.16",
    author = "Marcos Martinez",
    author_email = "frommelmak@gmail.com",
    description = "Some useful AWS scripts I use from time to time",
    license = "MIT",
    keywords = "aws amazon-web-services ec2-instance google-calendar-synchronization amazon mongodb backup",
    url = "http://github.com/frommelmak/aws-scripts",
    install_requires=['boto3>=1.18.60',
                      'argparse',
                      'fabric>=2.7.1',
                      'google-api-python-client>=1.7.3',
                      'oauth2client>=4.1.2',
                      'boto>=2.38.0',
                      'sshutil>=0.9.7',
                      'botocore>=1.21.60',
                      'rich>=12.5.1',
                      ],
    extras_require={
        "mongodb": ['pymongo>=2.9,< 3.0'],
    },
    python_requires='>=2.7',
    packages=find_packages(exclude=['docs', 'tests*']),
    scripts = ['aws-scripts/ec2-instances.py',
               'aws-scripts/ec2-instance-state.py',
               'aws-scripts/ec2-reserved.py',
               'aws-scripts/ec2-elb.py',
               'aws-scripts/ec2-ebs.py',
               'aws-scripts/ec2-snap-mgmt.py',
               'aws-scripts/mongodb-backup.py',
               'aws-scripts/rds-instances.py',
               'aws-scripts/route53-set-hostname.py',
               'aws-scripts/route53-del-hostname.py',
               'aws-scripts/s3-download-file.py',
               'aws-scripts/lifecycle-hook-worker.py',
               'aws-scripts/ec2-sg.py',
               'aws-scripts/ec2-tg.py',
               'aws-scripts/role.py'
              ],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
