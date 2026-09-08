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

BG = '#000000'
CARD_BG = '#111318'
TEXT_LIGHT = '#f5f5f5'
MUTED = '#7d8590'
ACCENT = '#2f6fed'


def _darken(hex_color, factor=0.82):
    """Return a slightly darker shade of hex_color, for button press feedback."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f'#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}'


class PIDTuningApp(Node):
    MULT_DEFAULTS = {'Kp': 0.03, 'Ki': 0.008, 'Kd': 0.6}

    def __init__(self, root):
        super().__init__('drone_pid_tuner')
        self.throttle_pub = self.create_publisher(PIDTune, "/throttle_pid", 10)
        self.pitch_pub = self.create_publisher(PIDTune, "/pitch_pid", 10)
        self.roll_pub = self.create_publisher(PIDTune, "/roll_pid", 10)

        self.root = root
        self.root.title('PID Tuning - Quadcopter')
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.entries = {}
        self.step_entries = {}
        self.multiplier_entries = {}
        self.computed_labels = {}
        # Keep the entries' StringVars alive: nothing else references them once
        # _create_pid_row/_create_section return, so without this they get
        # garbage-collected and silently drop their write traces.
        self._value_vars = {}
        self._mult_vars = {}
        self._saved_values = self._load_saved_values()

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
        pid_msg.kp = float(int(self.entries[value + "_Kp"].get()) * self._get_multiplier(value, "Kp"))
        pid_msg.ki = float(int(self.entries[value + "_Ki"].get()) * self._get_multiplier(value, "Ki"))
        pid_msg.kd = float(int(self.entries[value + "_Kd"].get()) * self._get_multiplier(value, "Kd"))
        return pid_msg

    def _load_icons(self):
        """Load and set the icons."""
        package_dir = get_package_share_directory('pid_tune')
        self.left_icon_image = Image.open(os.path.join(package_dir, 'resources', 'e.png'))
        self.right_icon_image = Image.open(os.path.join(package_dir, 'resources', 'drone.webp'))
        self.success_image = Image.open(os.path.join(package_dir, 'resources', 'success.webp'))

        self.left_icon_image = self.left_icon_image.resize((30, 30), Image.LANCZOS)
        self.left_icon_photo = ImageTk.PhotoImage(self.left_icon_image)

        self.right_icon_image = self.right_icon_image.resize((44, 44), Image.LANCZOS)
        self.right_icon_photo = ImageTk.PhotoImage(self.right_icon_image)

        self.success_image = self.success_image.resize((18, 18), Image.LANCZOS)
        self.success_photo = ImageTk.PhotoImage(self.success_image)

    def _create_widgets(self):
        """Create and place all widgets."""
        self.body = tk.Frame(self.root, bg=BG)
        self.body.pack(fill='both', expand=True)

        self._create_header()
        self._create_sections()
        self._create_buttons()

    def _create_header(self):
        """Create the header row with icons and title."""
        header = tk.Frame(self.body, bg=BG)
        header.pack(fill='x', pady=(10, 8))
        tk.Label(header, image=self.left_icon_photo, bg=BG).pack(side='left', padx=(14, 0))
        tk.Label(header, text="Swift Pico PID Tuner", font=('Arial', 13, 'bold'), bg=BG, fg=TEXT_LIGHT).pack(
            side='left', expand=True)
        tk.Label(header, image=self.right_icon_photo, bg=BG).pack(side='right', padx=(0, 14))

    def _create_sections(self):
        """Create the PID tuning sections for Throttle, Pitch, and Roll."""
        self._create_section('Throttle', 'throttle')
        self._create_section('Pitch', 'pitch')
        self._create_section('Roll', 'roll')

    def _create_section(self, title, prefix):
        """Create a section card with its own Scale row and Kp/Ki/Kd rows."""
        card = tk.Frame(self.body, bg=CARD_BG, bd=0)
        card.pack(fill='x', padx=14, pady=(0, 10))

        tk.Label(card, text=f'● {title.upper()}', bg=CARD_BG, fg=ACCENT, font=('Arial', 11, 'bold')).grid(
            row=0, column=0, columnspan=7, padx=12, pady=(8, 2), sticky='w')

        tk.Label(card, text='SCALE', bg=CARD_BG, fg=MUTED, font=('Arial', 7, 'bold')).grid(
            row=1, column=0, columnspan=7, padx=12, sticky='w')

        for i, key in enumerate(('Kp', 'Ki', 'Kd')):
            col = i * 2
            tk.Label(card, text=f'{key} ×', bg=CARD_BG, fg=TEXT_LIGHT, font=('Arial', 9, 'bold')).grid(
                row=2, column=col, padx=(12 if i == 0 else 8, 3), pady=(0, 6), sticky='e')
            mult_var = tk.StringVar(value=str(self.MULT_DEFAULTS[key]))
            mult_entry = tk.Entry(card, textvariable=mult_var, width=6, bg=BG, fg=TEXT_LIGHT, justify='center',
                                   relief='flat', bd=2, highlightthickness=1, highlightbackground=MUTED,
                                   insertbackground=TEXT_LIGHT, font=('Arial', 9))
            mult_entry.grid(row=2, column=col + 1, padx=(0, 6), pady=(0, 6), sticky='w')
            self.multiplier_entries[f'{prefix}_{key}'] = mult_entry
            self._mult_vars[f'{prefix}_{key}'] = mult_var
            mult_var.trace_add('write', lambda *_, p=prefix, k=key: self._refresh_computed(p, k))

        self._create_pid_row(card, 'Kp', 3, prefix)
        self._create_pid_row(card, 'Ki', 4, prefix)
        self._create_pid_row(card, 'Kd', 5, prefix)
        tk.Frame(card, bg=CARD_BG, height=4).grid(row=6, column=0, columnspan=7)

        for key in ('Kp', 'Ki', 'Kd'):
            self._refresh_computed(prefix, key)

    def _create_pid_row(self, parent, label_text, row, prefix):
        """Create a PID row with Kp, Ki, or Kd controls plus the live computed (scaled) value."""
        tk.Label(parent, text=label_text, bg=CARD_BG, fg=TEXT_LIGHT, font=('Arial', 10, 'bold')).grid(
            row=row, column=0, padx=(12, 4), pady=3, sticky='w')

        tk.Button(parent, text='−', width=2, font=('Arial', 9, 'bold'),
                  command=lambda: self._decrease_value(self.entries[f"{prefix}_{label_text}"],
                                                        self.step_entries[f"{prefix}_{label_text}_step"], prefix),
                  bg=ACCENT, fg=TEXT_LIGHT, relief='flat', bd=0,
                  activebackground=_darken(ACCENT), activeforeground=TEXT_LIGHT).grid(row=row, column=1, padx=3)

        value_var = tk.StringVar(value=self._initial_value(prefix, label_text))
        entry = tk.Entry(parent, textvariable=value_var, width=4, bg=BG, fg=TEXT_LIGHT, justify='center',
                          relief='flat', bd=2, highlightthickness=1, highlightbackground=MUTED,
                          insertbackground=TEXT_LIGHT, font=('Arial', 10))
        entry.grid(row=row, column=2, padx=3)
        entry.bind('<Return>', lambda event, p=prefix: self.pid_publish(p))
        self.entries[f"{prefix}_{label_text}"] = entry
        self._value_vars[f"{prefix}_{label_text}"] = value_var
        value_var.trace_add('write', lambda *_, p=prefix, k=label_text: self._refresh_computed(p, k))

        tk.Button(parent, text='+', width=2, font=('Arial', 9, 'bold'),
                  command=lambda: self._increase_value(entry, self.step_entries[f"{prefix}_{label_text}_step"],
                                                        prefix),
                  bg=ACCENT, fg=TEXT_LIGHT, relief='flat', bd=0,
                  activebackground=_darken(ACCENT), activeforeground=TEXT_LIGHT).grid(row=row, column=3, padx=3)

        computed_label = tk.Label(parent, text='= 0.000', bg=CARD_BG, fg=ACCENT, font=('Courier', 10, 'bold'),
                                   width=8, anchor='w')
        computed_label.grid(row=row, column=4, padx=(8, 8))
        self.computed_labels[f'{prefix}_{label_text}'] = computed_label

        tk.Label(parent, text='Step', bg=CARD_BG, fg=MUTED, font=('Arial', 7)).grid(
            row=row, column=5, padx=(0, 3))

        step_entry = tk.Entry(parent, width=3, bg=BG, fg=TEXT_LIGHT, justify='center', relief='flat', bd=2,
                               highlightthickness=1, highlightbackground=MUTED, insertbackground=TEXT_LIGHT,
                               font=('Arial', 9))
        step_entry.grid(row=row, column=6, padx=(0, 12))
        step_entry.insert(0, "1")
        self.step_entries[f"{prefix}_{label_text}_step"] = step_entry

    def _refresh_computed(self, prefix, key):
        """Update the live '= scaled value' label for one Kp/Ki/Kd row."""
        label = self.computed_labels.get(f'{prefix}_{key}')
        if label is None:
            return
        try:
            raw = int(self.entries[f'{prefix}_{key}'].get())
            mult = float(self.multiplier_entries[f'{prefix}_{key}'].get())
        except ValueError:
            label.config(text='= —')
            return
        label.config(text=f'= {raw * mult:.3f}')

    def _create_buttons(self):
        """Create the Save button and success icon."""
        button_frame = tk.Frame(self.body, bg=BG)
        button_frame.pack(pady=(2, 14))

        tk.Button(button_frame, text='Save Values', font=('Arial', 10, 'bold'), command=self._save_values,
                  bg=ACCENT, fg=TEXT_LIGHT, relief='flat', bd=0, padx=14, pady=6,
                  activebackground=_darken(ACCENT), activeforeground=TEXT_LIGHT).grid(row=0, column=0, padx=(0, 8))

        self.success_label = tk.Label(button_frame, image=self.success_photo, bg=BG)
        self.success_label.grid(row=0, column=1, padx=(8, 0))
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

    def _find_scripts_dir(self):
        """Locate src/controller_tuner/pid_tune/scripts by walking up from this file.

        This node runs from the built install/ copy, so __file__'s own directory
        isn't the source tree. Fall back to it if the workspace src/ can't be found
        (e.g. package installed without a sibling src/ checkout).
        """
        current = os.path.dirname(os.path.abspath(__file__))
        while True:
            # candidate = os.path.join(current, 'src', 'controller_tuner', 'pid_tune', 'scripts')
            candidate = os.path.join(current, 'src', 'swift_pico', 'src') # for Swift Pico package and pico_ws workspace
            if os.path.isdir(candidate):
                return candidate
            parent = os.path.dirname(current)
            if parent == current:
                return os.path.dirname(os.path.abspath(__file__))
            current = parent

    def _load_saved_values(self):
        """Load previously saved PID values from pid_values.yaml, if it exists."""
        yaml_path = os.path.join(self._find_scripts_dir(), 'pid_values.yaml')
        if not os.path.isfile(yaml_path):
            return {}
        try:
            with open(yaml_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
        except (yaml.YAMLError, OSError):
            return {}
        return data if isinstance(data, dict) else {}

    def _initial_value(self, prefix, key):
        """Resume from the last saved (scaled) value for prefix/key, or '0' if none was saved."""
        section = self._saved_values.get(f'{prefix}_pid', {})
        saved_scaled = section.get('ros__parameters', {}).get(key) if isinstance(section, dict) else None
        if saved_scaled is None:
            return "0"
        mult = float(self._mult_vars[f'{prefix}_{key}'].get())
        if mult <= 0:
            return "0"
        return str(round(saved_scaled / mult))

    def _get_multiplier(self, prefix, key):
        """Read and validate a section's save-multiplier entry for Kp/Ki/Kd."""
        raw = self.multiplier_entries[f'{prefix}_{key}'].get()
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"{prefix.title()} {key} multiplier must be a number.")
        if value <= 0:
            raise ValueError(f"{prefix.title()} {key} multiplier must be positive.")
        return value

    def _scaled_section_values(self, prefix):
        """Read a section's raw Kp/Ki/Kd entries and scale them by that section's multipliers."""
        values = {}
        for key in ('Kp', 'Ki', 'Kd'):
            raw = int(self.entries[f"{prefix}_{key}"].get())
            if raw < 0:
                raise ValueError("Values must be positive integers.")
            values[key] = raw * self._get_multiplier(prefix, key)
        return values

    def _save_values(self):
        """Save PID values (scaled by each section's multipliers) to a file."""
        try:
            throttle_values = self._scaled_section_values('throttle')
            pitch_values = self._scaled_section_values('pitch')
            roll_values = self._scaled_section_values('roll')

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

            # Write the YAML data to the source scripts dir (not the install copy this runs from),
            # so it survives rebuilds and is easy to find in the workspace.
            yaml_path = os.path.join(self._find_scripts_dir(), 'pid_values.yaml')
            with open(yaml_path, 'w') as yaml_file:
                yaml.dump(yaml_data, yaml_file, default_flow_style=False, sort_keys=False)

            self.get_logger().info(f"Saved PID values to {yaml_path}")
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
