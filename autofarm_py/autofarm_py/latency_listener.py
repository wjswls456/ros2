"""

Latency Listener - Day 4
- Day2의 qos_listener를 custom msg(LatencyMsg)로 리팩토링
- String 파싱 제거 -> 메시지 필드에서 직접 추출
- drop 검출, p50/p95/p99 통계, csv 저장은 기존 로직 그대로
"""

import os
import rclpy
import csv
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from autofarm_interfaces.msg import LatencyMsg


class LatencyListener(Node):
    def __init__(self):
        super().__init__('latency_listener')

        self.declare_parameter('output_dir', '/home/wjswls/autofarm_ws/ros2_logs')
        self.output_dir = self.get_parameter('output_dir').value

        self.declare_parameter('reliability','reliable')
        self.declare_parameter('depth',10)

        self.reliability_str= self.get_parameter('reliability').value
        self.depth=self.get_parameter('depth').value

        if self.reliability_str =='best_effort':
            reliability =ReliabilityPolicy.BEST_EFFORT
        else:
            reliability = ReliabilityPolicy.RELIABLE

        qos = QoSProfile(reliability=reliability,history=HistoryPolicy.KEEP_LAST,depth=self.depth)
        self.subscription=self.create_subscription(LatencyMsg,'latency_topic',self.callback,qos)


        self.latencies_us =[]
        self.last_seq = -1
        self.first_seq = -1
        self.dropped =0
        self.received = 0

        self.get_logger().info( f'LatencyListener started — reliability={self.reliability_str}, depth={self.depth}')

        self.declare_parameter('duration_sec', 0.0)
        duration=self.get_parameter('duration_sec').value

        # ─── Day 5 추가: 자동 종료 기능 ───
        if duration is not None and duration > 0:
            self.shutdown_timer = self.create_timer(duration, self._shutdown)
            self.get_logger().info(f'Auto-shutdown after {duration}s')

    def callback(self,msg):
        recv_ns = self.get_clock().now().nanoseconds

        # ─── Day 4의 핵심 변경 ───
        # Day 2: msg.data.split(',') 파싱 + try/except ValueError
        # Day 4: 메시지 필드에서 직접 추출 → 파싱·예외처리 불필요

        seq = msg.seq
        sent_us = msg.stamp.sec * 1_000_000_000 + msg.stamp.nanosec
        latencies_us = (recv_ns - sent_us) / 1000.0
        self.latencies_us.append(latencies_us)
        self.received +=1

        if self.last_seq >=0:
            gap = seq - self.last_seq -1
            if gap > 0:
                self.dropped += gap
        else:
            self.first_seq = seq
        self.last_seq =seq

        if self.received % 50 ==0:
            self._print_status()

    def _print_status(self):
        if not self.latencies_us:
            return
        sorted_lat = sorted(self.latencies_us)
        n = len(sorted_lat)
        p50 = sorted_lat[n // 2]
        p95 = sorted_lat[min(int(n * 0.95), n - 1)]
        p99 = sorted_lat[min(int(n * 0.99), n - 1)]
        avg = sum(sorted_lat) / n
        expected = self.last_seq - self.first_seq + 1
        drop_rate = (self.dropped / expected * 100.0) if expected > 0 else 0.0

        self.get_logger().info(
            f'recv={self.received} dropped={self.dropped} '
            f'drop_rate={drop_rate:.2f}% | '
            f'avg={avg:.1f}us p50={p50:.1f} p95={p95:.1f} p99={p99:.1f}'
        )

    def save_csv(self):
        os.makedirs(self.output_dir, exist_ok=True)
        path = f'{self.output_dir}/day5_{self.reliability_str}_d{self.depth}.csv'
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow([f'# reliability={self.reliability_str}, depth={self.depth}'])
            w.writerow([f'# received={self.received}, dropped={self.dropped}'])
            w.writerow(['index', 'latency_us'])
            for i, lat in enumerate(self.latencies_us):
                w.writerow([i, f'{lat:.3f}'])
        self.get_logger().info(f'Saved CSV to {path}')

    def _shutdown(self):
        """duration_sec 도달 시 호출. 통계 + CSV 저장 + 종료."""
        self.get_logger().info('=== Final Statistics (auto-shutdown) ===')
        if self.latencies_us:
            self._print_status()
            self.save_csv()
        else:
            self.get_logger().warn('No messages received during measurement')
        rclpy.shutdown()


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
            node.get_logger().warn('No messages received. Qos 호환성 또는 토픽 이름 확인 필요')
    node.destroy_node()
    try:
        rclpy.shutdown()
    except Exception:
        pass


if __name__ == "__main__":
    main()