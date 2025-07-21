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
        self.root.geometry("320x250")

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

class TunePidDrone(Node):
	def __init__(self):
		super().__init__('tune_pid_drone')

		pitch_ui = self.get_parameter_or('~ppid_ui_enable', Parameter('~ppid_ui_enable', Parameter.Type.BOOL, True))
		roll_ui = self.get_parameter_or('~rpid_ui_enable', Parameter('~rpid_ui_enable', Parameter.Type.BOOL, True))
		yaw_ui = self.get_parameter_or('~ypid_ui_enable', Parameter('~ypid_ui_enable', Parameter.Type.BOOL, True))
		throttle_ui = self.get_parameter_or('~tpid_ui_enable', Parameter('~tpid_ui_enable', Parameter.Type.BOOL, True))

		if pitch_ui and roll_ui and yaw_ui and throttle_ui :
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.ppid.root.mainloop()

		elif pitch_ui and roll_ui and yaw_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.ppid.root.mainloop()

		elif pitch_ui and roll_ui and throttle_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.ppid.root.mainloop()

		elif pitch_ui and yaw_ui and throttle_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.ppid.root.mainloop()

		elif roll_ui and yaw_ui and throttle_ui:
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)#Title of the ui, topic name of the publisher, queue size
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.rpid.root.mainloop()

		elif pitch_ui and roll_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.ppid.root.mainloop()

		elif pitch_ui and yaw_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.ppid.root.mainloop()

		elif pitch_ui and yaw_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.ppid.root.mainloop()

		elif roll_ui and yaw_ui:
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.rpid.root.mainloop()

		elif roll_ui and throttle_ui:
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.rpid.root.mainloop()

		elif yaw_ui and throttle_ui:
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.ypid.root.mainloop()

		elif pitch_ui:
			self.ppid = Pid_dim(self, "Pitch","pid_tuning_pitch",1000) #Title of the ui, topic name of the publisher, queue size
			self.ppid.root.mainloop()

		elif roll_ui:
			self.rpid = Pid_dim(self, "Roll","pid_tuning_roll",1000)
			self.rpid.root.mainloop()

		elif yaw_ui:
			self.ypid = Pid_dim(self, "Yaw","pid_tuning_yaw",1000)
			self.ypid.root.mainloop()

		elif throttle_ui:
			self.tpid = Pid_dim(self, "Throttle","pid_tuning_altitude",1000)
			self.tpid.root.mainloop()

		else:
			self.get_logger().info("UI DISABLED")

	
def main(args=None):
    rclpy.init(args=args)
    node = TunePidDrone()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
