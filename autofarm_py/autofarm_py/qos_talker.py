"""
Talker with Configurable QoS - Day 2
- 100Hz 메시지 publish 
- 파라미터로 reliability(reliable/best_effort)와 depth 받음
- 메시지에 시퀀스 번호 + 송신 시각(나노초) 포함
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

class QosTalker(Node):
    def __init__(self):
        super().__init__('qos_talker')

        # 파라미터 선언  reliable + depth 10
        # CLI에서 --ros-args -p reliability:=best_effort 식으로 주입한다

        self.declare_parameter('reliability','reliable')
        self.declare_parameter('depth',10)

        
        reliability_str = self.get_parameter('reliability').value
        depth = self.get_parameter('depth').value

        # 문자열로 받은 파라미터를 ROS2 enum으로 매핑
        # ros2 launch 파일에서도 똑같이 'reliable'/'best_effort' 문자열로 넘길 수 있어서 편함
        if reliability_str == 'best_effort':
            reliability = ReliabilityPolicy.BEST_EFFORT
        else:
            reliability = ReliabilityPolicy.RELIABLE

        # QoS 프로파일 — 비교할 두 축(reliability, depth)을 여기 모은다
        # history는 KEEP_LAST 고정. KEEP_ALL을 쓰면 depth가 무의미해지고 메모리 위험 ↑

        qos = QoSProfile(
            reliability=reliability,
            history=HistoryPolicy.KEEP_LAST,
            depth=depth,
        )

        # publisher 생성 시 정수(10) 대신 QoSProfile 객체를 넘긴다
        # 그냥 10을 넘겨서 reliability=reliable이 묵시적으로 적용됐던 것

        self.publisher_= self.create_publisher(String,'chatter_with_ts',qos)
        self.timer = self.create_timer(0.01,self.publish_message)
        self.count = 0
        

    def publish_message(self):
        msg = String()
        sent_ns = self.get_clock().now().nanoseconds
        msg.data = f'{self.count},{sent_ns}'
        self.publisher_.publish(msg)
        self.count += 1
        if self.count % 100 ==0:
            self.get_logger().info(f'Published {self.count} messages')

def main():
    rclpy.init()
    node = QosTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f'Stopped by user (sent total: {node.count})')

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
