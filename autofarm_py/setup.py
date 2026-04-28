from setuptools import find_packages, setup

package_name = 'autofarm_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kimjaewon',
    maintainer_email='wjswls45645697@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'talker_ts = autofarm_py.talker_with_timestamp:main' ,
            'listener_lat = autofarm_py.listener_with_latency:main'
        ],
    },
)
