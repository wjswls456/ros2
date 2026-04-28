# AutoFarm — ROS2 Portfolio

> 농업 자율주행 회사 지원을 준비하며 진행하는 12일 ROS2 학습 포트폴리오.
> 5년 전 MQTT IoT 프로젝트를 ROS2로 재구성하며 Zero-Copy IPC, SROS2 보안,
> Latency 측정을 직접 실험합니다.

## 진행 상황

- [x] Day 1 — Python rclpy Pub/Sub + Latency 측정 (코드 작성 완료)
- [ ] Day 2 — Custom msg + Service + Action
- [ ] Day 3 — Composable Nodes (intra-process)
- [ ] Day 4 — C++ 입문
- [ ] Day 5 — Loaned Messages + Shared Memory
- [ ] Day 6 — iceoryx + 4 시나리오 측정 ⭐
- [ ] Day 7 — MQTT 브리지
- [ ] Day 8 — SROS2 보안 ⭐
- [ ] Day 9 — Lifecycle + Parameters
- [ ] Day 10 — FastAPI 대시보드 + Prometheus
- [ ] Day 11 — ros2_tracing
- [ ] Day 12 — README + 영상 + 블로그

## 환경

- Ubuntu 24.04 (WSL2)
- ROS2 Jazzy
- Python 3.12

## 빌드 & 실행

\`\`\`bash
cd ~/autofarm_ws
colcon build --packages-select autofarm_py
source install/setup.bash

# Terminal 1 — Talker (100Hz publish with timestamp)
ros2 run autofarm_py talker_ts

# Terminal 2 — Listener (latency measurement)
ros2 run autofarm_py listener_lat
\`\`\`

## 자격요건 매칭

| 자격요건 | 충족 Day |
|---|---|
| ROS2 시스템 설계 | Day 1~3, 9 |
| Python rclpy | Day 1, 2, 7 |
| C++ rclcpp | Day 4, 5 |
| Pub/Sub 통신 | Day 1, 7 |
| MQTT | Day 7 |
| Zero-Copy IPC / iceoryx | Day 5, 6 ⭐ |
| 보안 통신 (SROS2) | Day 8 ⭐ |
| Latency 최적화 | Day 1, 5, 6, 11 |

## License
Apache-2.0