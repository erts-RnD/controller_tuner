#!/usr/bin/env python3

import tkinter as tk
from tkinter import Scale

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from controller_msg.msg import PIDTune


class Pid_dim():

    def __init__(self, node, title, topic_name, queue_size):
        self.pub_pid = node.create_publisher(PIDTune, topic_name, queue_size)
        self.pid_params = PIDTune()

        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes("-topmost", True)
        self.root.geometry("250x210")

        self.scale = Scale(
            self.root,
            orient="horizontal",
            from_=0,
            to=5000,
            command=self.set_value,
            label="Kp",
            width="20",
            length="300",
            troughcolor="red",
            sliderlength="15",
        )
        self.scale1 = Scale(
            self.root,
            orient="horizontal",
            from_=0,
            to=1000,
            command=self.set_value,
            label="Ki",
            width="20",
            length="300",
            troughcolor="green",
            sliderlength="15",
        )
        self.scale2 = Scale(
            self.root,
            orient="horizontal",
            from_=0,
            to=5000,
            command=self.set_value,
            label="Kd",
            width="20",
            length="300",
            troughcolor="blue",
            sliderlength="15",
        )

        self.scale.pack()
        self.scale1.pack()
        self.scale2.pack()

    def set_value(self, event):

        self.pid_params.kp = self.scale.get()
        self.pid_params.ki = self.scale1.get()
        self.pid_params.kd = self.scale2.get()
        self.pub_pid.publish(self.pid_params)

class TunePidDifferential(Node):
	def __init__(self):
		super().__init__('tune_pid_differential')

		lwheel_ui = self.get_parameter_or('~lpid_ui_enable', Parameter('~lpid_ui_enable', Parameter.Type.BOOL, True))
		rwheel_ui = self.get_parameter_or('~rpid_ui_enable', Parameter('~rpid_ui_enable', Parameter.Type.BOOL, True))

		if lwheel_ui and rwheel_ui:
			self.lpid = Pid_dim(self, "Left_wheel", "lpid_params", 1000)
			self.rpid = Pid_dim(self, "Right_wheel", "rpid_params", 1000)
			self.lpid.root.mainloop()
			self.rpid.root.mainloop()
		elif lwheel_ui:
			self.lpid = Pid_dim(self, "Left_wheel", "lpid_params", 1000)
			self.lpid.root.mainloop()
		elif rwheel_ui:
			self.rpid = Pid_dim(self, "Right_wheel", "rpid_params", 1000)
			self.rpid.root.mainloop()
		else:
			self.get_logger().info("UI DISABLED")

	
def main(args=None):
    rclpy.init(args=args)
    node = TunePidDifferential()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
