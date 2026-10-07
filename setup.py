from setuptools import setup,find_packages

with open('req.txt') as f:
    req=f.read().splitlines()

setup(
    author="Durga Charan",
    name="RAG PROJECT LIB",
    packages=find_packages(),
    install_requires=req
)