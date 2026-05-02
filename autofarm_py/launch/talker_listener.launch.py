"""
가장 단순한 launch 파일 - day 5

- latency_talker와 latency_listener를 동시에 실행
- 파라미터는 default 값 사용(reliable , depth = 10)
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

#  "launch 파일은 왜 일반 Python처럼 안 쓰나요?"
#  ROS2 launch는 "실행 시점"이 아니라 "구성 시점"에 동작해요. 즉, launch 파일이 한 번 실행될 때 모든 동적 값을 미리 결정해놓고 그 다음 노드를 띄우는 구조.


def generate_launch_description():

    """
    Node(...) 인자 4개

    package: 어느 패키지의 실행파일인가
    executable: setup.py의 entry_points에 등록된 이름 (latency_talker)
    name: ROS2 노드 이름. 보통 executable과 같음
    output='screen': 노드의 로그를 터미널에 보이게. 이거 빠뜨리면 노드는 도는데 화면이 조용함
    parameters : 노드에 전달하는 파라미터
    """

    # 1단계 : launch 인자 선언

    """
    DeclareLaunchArgument

    'reliability': 인자 이름. CLI에서 reliability:=...로 받음
    default_value='reliable': 인자 안 주면 이 값
    description=...: --show-args로 도움말 표시 시 보임
    """

    reliability_arg = DeclareLaunchArgument('reliability',default_value='reliable',description='Qos reliability: reliable or best_effor')
    depth_arg=DeclareLaunchArgument('depth',default_value='10',description='Qos history depth (queue size)')

    # 2단계 : 노드에서 인자 사용(LaunchConfiguration으로 wrap)

    talker = Node(package='autofarm_py',executable='latency_talker',name='latency_talker',output='screen',parameters=[{
        'reliability':LaunchConfiguration('reliability'),'depth':LaunchConfiguration('depth')}])

    listener = Node(package='autofarm_py',executable='latency_listener',name='latency_listener',output='screen',parameters=[{
        'reliability':LaunchConfiguration('reliability'),'depth':LaunchConfiguration('depth')}])
    return LaunchDescription([
        reliability_arg,
        depth_arg,
        talker,
        listener,
    ])