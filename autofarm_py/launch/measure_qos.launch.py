"""
4가지 QoS 조합 자동 순회 - Day 5 Step 4
- 각 조합을 25초씩 측정 (30초 간격으로 시작)
- 총 약 2분 후 전체 자동 종료
- CSV는 day5_<reliability>_d<depth>.csv 형태로 저장됨
"""

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


# 조합 정의: (reliability, depth)
COMBOS = [
    ('reliable',    10),
    ('best_effort', 10),
    ('reliable',    1),
    ('best_effort', 1),
]

DURATION = 25.0      # 각 조합 측정 시간 (초)
INTERVAL = 30.0      # 다음 조합 시작 간격 (5초 여유)
OUTPUT_DIR = '/home/wjswls/autofarm_ws/ros2_logs'


def generate_launch_description():
    actions = []

    for i, (reliability, depth) in enumerate(COMBOS):
        # i번째 조합은 i*30초 후 시작
        start_time = i * INTERVAL

        talker = Node(
            package='autofarm_py',
            executable='latency_talker',
            name=f'latency_talker_{i}',  # 노드 이름 충돌 방지
            output='screen',
            parameters=[{
                'reliability': reliability,
                'depth': depth,
                'duration_sec': DURATION,
            }],
        )

        listener = Node(
            package='autofarm_py',
            executable='latency_listener',
            name=f'latency_listener_{i}',
            output='screen',
            parameters=[{
                'reliability': reliability,
                'depth': depth,
                'duration_sec': DURATION,
                'output_dir': OUTPUT_DIR,
            }],
        )

        # i번째 조합은 start_time 초 후에 시작
        actions.append(TimerAction(period=start_time, actions=[talker, listener]))

    return LaunchDescription(actions)