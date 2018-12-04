from setuptools import setup

setup(
        name='Duality2',
        version='0.0.1',
        author='luren',
        author_email='lurenwang@gmail.com',
        description='Prototype bilateral generative password manager',
        entry_points={
            'console_scripts': ['duality2 = duality2.__main__:main']
        },
        install_requires=['GitPython==2.1.11',
            'pyperclip==1.6.4'],
        keywords='generative password manager',
        packages=['duality2'],
        python_requires='>3.5.2',
        license='MIT'
)
