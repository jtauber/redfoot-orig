
from distutils.core import setup

setup(
    name = 'medusa',
    version = "0.5.2-rf1",
    description = "A framework for implementing asynchronous servers.",
    author = "Sam Rushing",
    author_email = "rushing@nightmare.com",
    maintainer = "A.M. Kuchling",
    maintainer_email = "akuchlin@mems-exchange.org",
    url = "http://www.amk.ca/python/code/medusa.html",

    packages = ['medusa'],
    package_dir = {'medusa':'.'},
    )
