from setuptools import setup

setup(
    name='pykachu',
    version='0.1.1',
    packages=['pykachu'],
    url='https://github.com/sievetech/pykachu',
    license='3-BSD',
    author='Sieve',
    author_email='sievetech@sieve.com.br',
    description='Monitoramento simples de tarefas em background usando Redis como backend ',
    install_requires=["redis"]
)
