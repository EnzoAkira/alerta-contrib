
from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="alerta-messagebird",
    version=version,
    description='Alerta plugin for Messagebird',
    url='',
    license='GoContact',
    author='Bruno Cruz',
    author_email='bcruz@gocontact.pt',
    packages=find_packages(),
    py_modules=['alerta_messagebird'],
    install_requires=[
        'messagebird'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'messagebird = alerta_messagebird:MessageBird'
        ]
    }
)
