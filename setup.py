from setuptools import setup

setup(
    name="lexicons_builder",
    version="0.1.0",
    packages=[
        "lexicons_builder",
        "lexicons_builder.graphs",
        "lexicons_builder.scrappers",
        "lexicons_builder.wordnet_explorer",
        "lexicons_builder.nlp_model_explorer",
    ],
    url="",
    license="MIT",
    author="GLNB",
    author_email="glnb@gmail.com",
    description="lexicons_builder, a tool to create lexicons",
    install_requires=["gensim"],
)
