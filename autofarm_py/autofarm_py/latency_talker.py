"""
Latency Talker - Day 4
- Day 2의 qos_talker를 custom msg(LatencyMsg)로 리팩토링
- std_msgs/String 인코딩(seq,timestamp) 제거
- 메시지 객체에 seq, stamp 필드로 직접 할당 -> 더 깔끔하고 타입 안전
- rqt_plot으로 stamp.sec,stamp.nanosec 같은 숫자 필드 plot 가능
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from autofarm_interfaces.msg import LatencyMsg


class LatencyTalker(Node):
    def __init__(self):
        super().__init__('latency_talker')

        self.declare_parameter('reliability','reliable')
        self.declare_parameter('depth',10)

        reliability_str = self.get_parameter('reliability').value
        depth = self.get_parameter('depth').value

        if reliability_str == 'best_effort':
            reliability = ReliabilityPolicy.BEST_EFFORT
        else:
            reliability = ReliabilityPolicy.RELIABLE

        qos = QoSProfile(reliability=reliability,history= HistoryPolicy.KEEP_LAST,depth=depth)


        self.publisher_ = self.create_publisher(LatencyMsg,'latency_topic',qos)
        self.time = self.create_timer(0.01,self.publish_mssage)
        self.count =0
        self.get_logger().info(f'LatencyTalker started — reliability={reliability_str}, depth={depth}, rate=100Hz')
        
    def publish_mssage(self):
        msg = LatencyMsg()

        msg.seq = self.count

        msg.stamp = self.get_clock().now().to_msg()

        self.publisher_.publish(msg)
        self.count +=1
        if self.count % 100 ==0:
            self.get_logger().info(f'Published {self.count} messages')




def main():
    rclpy.init()
    node = LatencyTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f'Stopped by user (sent total: {node.count})')

if __name__ == '__main__':
    main()