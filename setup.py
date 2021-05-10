from setuptools import setup

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="lexicons_builder",
    version="0.1.2",
    packages=[
        "lexicons_builder",
        "lexicons_builder.graphs",
        "lexicons_builder.scrappers",
        "lexicons_builder.wordnet_explorer",
        "lexicons_builder.nlp_model_explorer",
    ],
    url="https://lexicons-builder.readthedocs.io",
    license="MIT",
    author="GLNB",
    author_email="glnb@gmail.com",
    description="lexicons_builder, a tool to create lexicons",
    long_description=long_description,
    install_requires=["gensim", "languagecodes", "banal", "nltk", "rdflib"],
    project_urls={
        'Documentation': 'https://lexicons-builder.readthedocs.io',
        'Source': 'https://github.com/GuillaumeLNB/lexicons_builder',
    }
)
