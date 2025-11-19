from setuptools import setup, find_packages

setup(
    name='DeepPack3D',
    version='0.1.0',
    author='ckt.tomchung',
    author_email='ckt.tomchung@gmail.com',
    description='Reinforcement learning-based optimizer for 3D bin packing problem',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zgtcktom/Reinforcement-Learning-for-Online-3D-Bin-Packing',
    packages=find_packages(),
    install_requires=[
        'numpy==1.26.4',
        'matplotlib==3.9.0',
        'tensorflow==2.10.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='==3.10',
)