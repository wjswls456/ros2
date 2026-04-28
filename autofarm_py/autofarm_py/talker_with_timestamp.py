"""
Taler with Timestamp - Day 1
 - 100Hz 메시지 publish
 - 메시지엣 시퀀스 번호 + 송신 시각(나노초) 보냄
 - 수신측에서 latency 계산 가능
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TimestampTalker(Node): # Node를 상속(부모) Node가 가진 모든 기능(publish 가능, 토픽 관리 등)을 물려받음
    def __init__(self):
        super().__init__('timestamp_talker') 
        #Qos depth 10 = 큐에 최대 10개 메시지 대기
        self.publisher_ = self.create_publisher(String,'chatter_with_ts',10)
        self.timeer = self.create_timer(0.01,self.publish_message)
        self.count = 0
        self.get_logger().info('TimestampTalker started - publishing at 100Hz')

    def publish_message(self):
        msg = String()
        # 송신 시각을 나노초로 가져옴
        sent_ns = self.get_clock().now().nanoseconds
        # '시컨스번호, 타임스탬프' 형식으로 인코딩
        msg.data = f'{self.count},{sent_ns}'
        self.publisher_.publish(msg)
        self.count +=1
        if self.count % 100 == 0:
            self.get_logger().info(f'Published {self.count} messages')

def main():
    rclpy.init()
    node=TimestampTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Stopped by user')
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
