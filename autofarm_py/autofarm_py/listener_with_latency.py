"""
Listener with Latency Measurement — Day 1
- talker가 보낸 메시지의 송신 시각과 현재 시각 차이로 latency 계산
- 50개마다 누적 통계(p50/p95/p99) 출력
- Ctrl+C 종료 시 최종 통계 + CSV 저장
"""
import csv
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LatencyListener(Node):
    def __init__(self):
        super().__init__('latency_listener')
        self.subscription =self.create_subscription(String,'chatter_with_ts',self.callback,10)
        self.latencies_us = []
        self.get_logger().info('LatencyListener started — waiting for messages')
    def callback(self,msg):
        recv_ns = self.get_clock().now().nanoseconds
        try:
            seq_str,sent_ns_str = msg.data.split(',')
            sent_ns = int(sent_ns_str)
        except ValueError:
            return
        latency_us = (recv_ns - sent_ns) / 1000.0
        self.latencies_us.append(latency_us)

        # 50개마다 누적 통계 출력
        if len(self.latencies_us) % 50 ==0:
            self._print_status()
        
    def _print_status(self):
        sorted_lat = sorted(self.latencies_us)
        n = len(sorted_lat)
        p50 = sorted_lat[n//2]
        p95 = sorted_lat[int(n*0.95)]
        p99 = sorted_lat[int(n*0.99)]
        avg = sum(sorted_lat) / n
        self.get_logger().info(
            f'count={n} avg={avg:.1f}us p50={p50:.1f} p95={p95:.1f} p99={p99:.1f}'
        )
    def save_csv(self, path='/tmp/day1_latency.csv'):
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['index', 'latency_us'])
            for i, lat in enumerate(self.latencies_us):
                w.writerow([i, f'{lat:.3f}'])
        self.get_logger().info(f'Saved CSV to {path}')

def main():
    rclpy.init()
    node = LatencyListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('=== Final Statistics ===')
        if node.latencies_us:
            node._print_status()
            node.save_csv()
        else:
            print('No messages received.')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()