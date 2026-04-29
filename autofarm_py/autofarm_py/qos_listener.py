

import csv
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String

class QosLatencyListener(Node):
    def __init__(self):
        super().__init__('qos_latency_listener')
    # talker와 동일하게 파라미터로 QoS를 받는다
    # 중요: Pub/Sub QoS가 호환되지 않으면 메시지 자체가 안 옴 (Q5 참조)

        self.declare_parameter('reliability', 'reliable')
        self.declare_parameter('depth', 10)

        self.reliability_str = self.get_parameter('reliability').value
        self.depth = self.get_parameter('depth').value
        
        if self.reliability_str == 'best_effort':
            reliability = ReliabilityPolicy.BEST_EFFORT
        else:
            reliability = ReliabilityPolicy.RELIABLE

        qos = QoSProfile(
            reliability=reliability,
            history=HistoryPolicy.KEEP_LAST,
            depth=self.depth,
        )

        self.subscription = self.create_subscription(
            String, 'chatter_with_ts', self.callback, qos
        )

                # 통계용 상태들
        self.latencies_us = []   # 모든 latency 샘플 (마이크로초)
        self.last_seq = -1       # 직전에 받은 seq (-1 = 아직 못 받음)
        self.first_seq = -1      # 처음 받은 seq (drop rate 계산의 기준점)
        self.dropped = 0         # 누적 drop 개수
        self.received = 0        # 실제 받은 메시지 수

        self.get_logger().info(
            f'QosLatencyListener started — reliability={self.reliability_str}, depth={self.depth}'
        )

    def callback(self,msg):
        recv_ns = self.get_clock().now().nanoseconds

        try:
            seq_str,sent_ns_str =msg.data.split(',')
            seq = int(seq_str)
            sent_ns = int(sent_ns_str)
        except ValueError:
            return
        

        latency_us = (recv_ns - sent_ns) / 1000.0
        self.latencies_us.append(latency_us)
        self.received += 1

         # ─── Day 2의 핵심: drop 검출 ───
        # talker가 0,1,2,3,...로 연속된 seq를 보냈는데
        # 중간에 빠지면 listener에서 받는 seq 사이에 갭이 생긴다.
        # 예: last_seq=5, 이번 seq=8 → 6,7 두 개가 dropped
        if self.last_seq >= 0:
            gap = seq - self.last_seq - 1
            if gap > 0:
                self.dropped += gap
        else:
            # 첫 메시지 — drop rate 계산 기준점으로 저장
            self.first_seq = seq
        self.last_seq = seq

        # 50개마다 누적 통계 출력 (실시간 모니터링용)
        if self.received % 50 == 0:
            self._print_status()
    def _print_status(self):
        if not self.latencies_us:
            return
        # latency 분포 — 평균만 보면 outlier에 흐려지니까 percentile로 본다
        sorted_lat = sorted(self.latencies_us)
        n = len(sorted_lat)
        p50 = sorted_lat[n // 2]
        p95 = sorted_lat[min(int(n * 0.95), n - 1)]
        p99 = sorted_lat[min(int(n * 0.99), n - 1)]
        avg = sum(sorted_lat) / n

        # drop rate = 누락 / (보냈어야 할 총량) × 100
        # "보냈어야 할 총량"은 첫 수신 seq부터 마지막 수신 seq까지의 범위
        # (시작 전·종료 후 빠진 건 어차피 셀 수 없음)
        expected = self.last_seq - self.first_seq + 1
        drop_rate = (self.dropped / expected * 100.0) if expected > 0 else 0.0

        self.get_logger().info(
            f'recv={self.received} dropped={self.dropped} '
            f'drop_rate={drop_rate:.2f}% | '
            f'avg={avg:.1f}us p50={p50:.1f} p95={p95:.1f} p99={p99:.1f}'
        )

    def save_csv(self):
        # 파일명에 QoS 정보를 박아서 4개 조합 결과가 안 섞이게 한다
        # 예: /tmp/day2_best_effort_d1.csv
        path = f'/tmp/day2_{self.reliability_str}_d{self.depth}.csv'
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            # 메타데이터는 첫 두 줄에 주석으로 (pandas로 읽을 때 skiprows=2)
            w.writerow([f'# reliability={self.reliability_str}, depth={self.depth}'])
            w.writerow([f'# received={self.received}, dropped={self.dropped}'])
            w.writerow(['index', 'latency_us'])
            for i, lat in enumerate(self.latencies_us):
                w.writerow([i, f'{lat:.3f}'])
        self.get_logger().info(f'Saved CSV to {path}')


def main():
    rclpy.init()
    node = QosLatencyListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('=== Final Statistics ===')
        if node.latencies_us:
            node._print_status()
            node.save_csv()
        else:
            # 메시지가 하나도 안 잡힌 경우 → QoS 매칭 실패 가능성이 가장 큼
            node.get_logger().warn(
                'No messages received. QoS 호환성 확인 필요 '
                '(Pub=BestEffort, Sub=Reliable이면 매칭 안 됨)'
            )
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()