from distutils.core import setup

setup(
    name='Flex2Pdf',
    version='0.0.0',
    author='Alain Bangoula',
    author_email='alain@come-n-see.fr',
    packages=['flex2pdf', 'flex2pdf.test'],
    url='http://pypi.python.org/pypi/Flex2Pdf/',
    license='LICENSE.txt',
    description='Building pdf using CSS3 Flex Box Model',
    long_description=open('README.txt').read(),
    install_requires=[
        "Reportlab >= 2.5",
        "PIL == 1.1.7",
    ],
    setup_requires=[
    "Reportlab >= 2.5",
        "PIL == 1.1.7",
    ],
)
