# coding: utf8
from setuptools import setup

setup(
    name="builtin_redis",
    install_requires=[
    ],
    extras_require={
        'dev':[
            "pytest",
            "pytest-asyncio",
            "redis-py"
        ]
    },
)
