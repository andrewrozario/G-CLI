from setuptools import setup, find_packages

setup(
    name="gcli-ai",
    version="3.0.0",
    packages=find_packages(),
    py_modules=["gcli"],
    include_package_data=True,
    install_requires=[
        "typer",
        "rich",
        "requests",
        "openai",
        "google-generativeai",
        "python-dotenv",
        "watchdog",
        "psutil",
        "pydantic>=2.9.0",
        "anthropic",
        "langchain-core"
    ],
    entry_points={
        "console_scripts": [
            "g=gcli:app",
            "G=gcli:app",
        ],
    },
)
