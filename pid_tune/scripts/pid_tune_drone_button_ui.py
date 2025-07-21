#!/usr/bin/env python3

import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import rclpy
from rclpy.node import Node
from controller_msg.msg import PIDTune
import yaml
import os
from ament_index_python.packages import get_package_share_directory

class PIDTuningApp(Node):
    def __init__(self, root):
        super().__init__('drone_pid_tuner')
        self.throttle_pub = self.create_publisher(PIDTune, "/throttle_pid", 10)
        self.pitch_pub = self.create_publisher(PIDTune, "/pitch_pid", 10)
        self.roll_pub = self.create_publisher(PIDTune, "/roll_pid", 10)

        self.root = root
        self.root.title('PID Tuning - Quadcopter')
        self.root.attributes("-topmost", True)
        self.root.geometry("523x880")
        self.root.resizable(False, False)
        self.root.configure(bg='#dfa363')

        self.entries = {}
        self.step_entries = {}

        self._load_icons()
        self._create_widgets()

    def pid_publish(self, section):
        """Publish the PID values to the corresponding ROS2 topic based on the section."""
        if section == "throttle":
            self.throttle_pub.publish(self.pid_values(section))
        elif section == "pitch":
            self.pitch_pub.publish(self.pid_values(section))
        elif section == "roll":
            self.roll_pub.publish(self.pid_values(section))

    def pid_values(self, value):
        pid_msg = PIDTune()
        # Get values from the PIDTuningApp instance
        pid_msg.kp = int(self.entries[value + "_Kp"].get())
        pid_msg.ki = int(self.entries[value + "_Ki"].get())
        pid_msg.kd = int(self.entries[value + "_Kd"].get())
        return pid_msg
    
    def _load_icons(self):
        """Load and set the icons."""
        package_dir = get_package_share_directory('pid_tune')
        self.left_icon_image = Image.open(os.path.join(package_dir, 'resources', 'e.png'))
        self.right_icon_image = Image.open(os.path.join(package_dir, 'resources', 'drone.webp'))
        self.success_image = Image.open(os.path.join(package_dir, 'resources', 'success.webp'))

        self.left_icon_image = self.left_icon_image.resize((40, 40), Image.LANCZOS)
        self.left_icon_photo = ImageTk.PhotoImage(self.left_icon_image)
      
        self.right_icon_image = self.right_icon_image.resize((60, 60), Image.LANCZOS)
        self.right_icon_photo = ImageTk.PhotoImage(self.right_icon_image)

        self.success_image = self.success_image.resize((24, 24), Image.LANCZOS)
        self.success_photo = ImageTk.PhotoImage(self.success_image)

    def _create_widgets(self):
        """Create and place all widgets."""
        self._create_icons()
        self._create_sections()
        self._create_buttons()

    def _create_icons(self):
        """Create and place the left and right icons."""
        tk.Label(self.root, image=self.left_icon_photo, bg='#dfa363').grid(row=0, column=0, padx=(30, 0), pady=(20, 0), sticky='nw')
        tk.Label(self.root, text="Swift Pico", font=('Arial', 18, 'bold'), bg='#dfa363', fg='black').grid(row=0, column=1, columnspan=4, pady=(20, 0), sticky='n')
        tk.Label(self.root, image=self.right_icon_photo, bg='#dfa363').grid(row=0, column=5, padx=(0, 30), pady=(20, 0), sticky='ne')

    def _create_sections(self):
        """Create the PID tuning sections for Throttle, Pitch, and Roll."""
        self._create_section('Throttle', 1, 'throttle')
        self._create_section('Pitch', 8, 'pitch')
        self._create_section('Roll', 15, 'roll')

    def _create_section(self, title, start_row, prefix):
        """Create a section for a given title and prefix."""
        section_frame = tk.Frame(self.root, bg='#feedba', bd=3, relief='groove')
        section_frame.grid(row=start_row, column=0, columnspan=6, padx=20, pady=(10, 5), sticky='we')
        tk.Label(section_frame, text=title, font=('Arial', 14, 'bold'), bg='#feedba', fg='#10396f').grid(row=0, column=0, columnspan=6, pady=(5, 10), sticky='n')

        self._create_pid_row(section_frame, 'Kp', 1, prefix)
        self._create_pid_row(section_frame, 'Ki', 2, prefix)
        self._create_pid_row(section_frame, 'Kd', 3, prefix)
        tk.Label(section_frame, bg='#feedba').grid(row=4, column=0, columnspan=6, pady=(10, 0))

    def _create_pid_row(self, parent, label_text, row, prefix):
        """Create a PID row with Kp, Ki, or Kd controls."""
        tk.Label(parent, text=label_text, bg='#feedba', font=('Arial', 12, 'bold'), fg='#10396f').grid(row=row, column=0, padx=(20, 5), pady=(10, 5), sticky='w')

        tk.Button(parent, text='-', width=2, command=lambda: self._decrease_value(self.entries[f"{prefix}_{label_text}"], self.step_entries[f"{prefix}_{label_text}_step"], prefix), bg='#286372', fg='white', relief='raised', bd=3).grid(row=row, column=1, padx=5)
        
        entry = tk.Entry(parent, width=5, bg='#e6dbc1', justify='center', relief='sunken', bd=3)
        entry.grid(row=row, column=2, padx=5)
        entry.insert(0, "0")
        entry.bind('<Return>', lambda event, p=prefix: self.pid_publish(p))
        self.entries[f"{prefix}_{label_text}"] = entry
        
        tk.Button(parent, text='+', width=2, command=lambda: self._increase_value(entry, self.step_entries[f"{prefix}_{label_text}_step"], prefix), bg='#286372', fg='white', relief='raised', bd=3).grid(row=row, column=3, padx=5)
        
        tk.Label(parent, text='Step Size', bg='#feedba', font=('Arial', 10)).grid(row=row, column=4, padx=(20, 5))
        
        step_entry = tk.Entry(parent, width=5, bg='#e6dbc1', justify='center', relief='sunken', bd=3)
        step_entry.grid(row=row, column=5, padx=(5, 20))
        step_entry.insert(0, "1")
        self.step_entries[f"{prefix}_{label_text}_step"] = step_entry

    def _create_buttons(self):
        """Create the Save button and success icon."""
        button_frame = tk.Frame(self.root, bg='#dfa363')
        button_frame.grid(row=22, column=0, columnspan=6, pady=(20, 20))

        tk.Button(button_frame, text='Save Values', font=('Arial', 11, 'bold'), command=self._save_values, bg='white', fg='#f38a51', relief='raised', bd=3).grid(row=0, column=0, padx=(0, 10))

        self.success_label = tk.Label(button_frame, image=self.success_photo, bg='#dfa363')
        self.success_label.grid(row=0, column=1, padx=(10, 0))
        self.success_label.grid_remove()

    def _validate_integer(self, value):
        """Check if the value is a positive integer."""
        try:
            int_value = int(value)
            if int_value < 0:
                return False
            return True
        except ValueError:
            return False

    def _increase_value(self, entry, step_entry, section):
        """Increase the value in the entry widget and publish the PID values."""
        entry_value = entry.get()
        step_value = step_entry.get()

        if not self._validate_integer(entry_value):
            messagebox.showerror("Invalid Input", "Please enter a positive integer for the value.")
            return
        
        if not self._validate_integer(step_value):
            messagebox.showerror("Invalid Input", "Please enter a positive integer for the step size.")
            return

        current_value = int(entry_value)
        step_size = int(step_value)
        entry.delete(0, tk.END)
        entry.insert(0, str(current_value + step_size))

        # Publish the updated values
        self.pid_publish(section)

    def _decrease_value(self, entry, step_entry, section):
        """Decrease the value in the entry widget and publish the PID values."""
        entry_value = entry.get()
        step_value = step_entry.get()

        if not self._validate_integer(entry_value):
            messagebox.showerror("Invalid Input", "Please enter a positive integer for the value.")
            return
        
        if not self._validate_integer(step_value):
            messagebox.showerror("Invalid Input", "Please enter a positive integer for the step size.")
            return

        current_value = int(entry_value)
        step_size = int(step_value)
        new_value = current_value - step_size
        if new_value < 0:
            new_value = 0
        entry.delete(0, tk.END)
        entry.insert(0, str(new_value))

        # Publish the updated values
        self.pid_publish(section)

    def _save_values(self):
        """Save PID values to a file."""
        try:
            throttle_values = {
                "Kp": int(self.entries["throttle_Kp"].get()),
                "Ki": int(self.entries["throttle_Ki"].get()),
                "Kd": int(self.entries["throttle_Kd"].get())
            }
            pitch_values = {
                "Kp": int(self.entries["pitch_Kp"].get()),
                "Ki": int(self.entries["pitch_Ki"].get()),
                "Kd": int(self.entries["pitch_Kd"].get())
            }
            roll_values = {
                "Kp": int(self.entries["roll_Kp"].get()),
                "Ki": int(self.entries["roll_Ki"].get()),
                "Kd": int(self.entries["roll_Kd"].get())
            }

            if any(v < 0 for v in throttle_values.values()) or \
               any(v < 0 for v in pitch_values.values()) or \
               any(v < 0 for v in roll_values.values()):
                raise ValueError("Values must be positive integers.")

            # Structure the data to match a typical ROS 2 parameter YAML file format
            yaml_data = {
                'throttle_pid': {
                    'ros__parameters': throttle_values
                },
                'pitch_pid': {
                    'ros__parameters': pitch_values
                },
                'roll_pid': {
                    'ros__parameters': roll_values
                }
            }

            # Write the YAML data to a file
            with open('pid_values.yaml', 'w') as yaml_file:
                yaml.dump(yaml_data, yaml_file, default_flow_style=False)

            self.success_label.grid()  # Show the success icon
            self.root.after(2000, self._hide_success_icon)  # Hide the success icon after 2 seconds

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def _hide_success_icon(self):
        """Hide the success icon."""
        self.success_label.grid_remove()


def main(args=None):
    rclpy.init(args=args)
    root = tk.Tk()
    app = PIDTuningApp(root)
    root.mainloop()
    app.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
