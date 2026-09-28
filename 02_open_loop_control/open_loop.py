#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from math import pi

class Turtlebot(Node):
    def __init__(self):
        super().__init__("turtlebot_move")
        self.get_logger().info("Turtlebot 開ループ正方形軌道制御が開始されました。Ctrl + C で終了できます")
        self.vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # 制御指令の配信周期: 10 Hz (1周期あたり 0.1 秒)
        self.rate = 10
        self.timer = self.create_timer(1.0 / self.rate, self.run)

        # 速度パラメータの設定 (スリップや慣性による誤差を低減するため、穏やかな速度を推奨)
        self.linear_speed = 0.2    # 前進時の並進速度 (m/s)
        self.angular_speed = 0.2   # その場での左旋回角速度 (rad/s)

        # 理論時間の計算:
        # 1. 4m 直進に必要な時間 (s)
        self.forward_time = 4.0 / self.linear_speed           # 4.0 / 0.2 = 20.0 秒
        # 2. その場で 90度 (pi/2 rad) 左旋回に必要な時間 (s)
        self.turn_time = (pi / 2.0) / self.angular_speed     # ~7.854 秒

        # 10Hz におけるタイマーステップ数への換算 (step)
        # ヒント：Gazebo 内で摩擦や慣性により回転角や移動距離に過不足が生じる場合は、このカウント値を微調整してください
        self.forward_count = 470
        self.turn_count = 152

        # ステートマシン管理
        self.side = 0           # 現在の辺の番号 (0, 1, 2, 3: 計4辺)
        self.state = "FORWARD"  # 現在の動作状態: "FORWARD"(直進) または "TURN"(旋回)
        self.step = 0           # 現在の動作のステップカウンタ

    def run(self):
        vel = Twist()

        # 4辺すべての走行が完了した場合、ロボットを停止させてタイマーを破棄
        if self.side >= 4:
            vel.linear.x = 0.0
            vel.angular.z = 0.0
            self.vel_pub.publish(vel)
            self.get_logger().info("【完了】正方形軌道を周回し、原点 [0, 0] 付近に復帰しました。走行を停止します。")
            self.timer.cancel()
            return

        if self.state == "FORWARD":
            if self.step < self.forward_count:
                vel.linear.x = self.linear_speed
                vel.angular.z = 0.0
                self.step += 1
            else:
                # 1辺の直進が完了、旋回状態へ遷移
                self.get_logger().info(f"第 {self.side + 1} 辺の 4m 直進が完了しました。その場で左に 90度 旋回を開始します...")
                self.state = "TURN"
                self.step = 0

        elif self.state == "TURN":
            if self.step < self.turn_count:
                vel.linear.x = 0.0
                vel.angular.z = self.angular_speed
                self.step += 1
            else:
                # 旋回完了、次の辺の直進へ遷移
                self.side += 1
                self.state = "FORWARD"
                self.step = 0
                if self.side < 4:
                    self.get_logger().info(f"第 {self.side} 回目の旋回が完了しました。第 {self.side + 1} 辺の走行を開始します...")

        # 速度指令をパブリッシュ
        self.vel_pub.publish(vel)


def main(args=None):
    rclpy.init(args=args)
    turtlebot = Turtlebot()

    try:
        rclpy.spin(turtlebot)
    except KeyboardInterrupt:
        print("\nCtrl + C が検出されました。プログラムを終了します...")
    finally:
        turtlebot.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

