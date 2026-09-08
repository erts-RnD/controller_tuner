from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import OpaqueFunction
from launch import LaunchContext

def evaluate_spawn(context, *args, **kwargs):
    node_name = LaunchConfiguration('node_name').perform(context)
    print("node_name:", node_name)
    
    nodes = []

    if node_name == "button_ui":
        button_ui = Node(
            package='pid_tune',
            executable='pid_tune_drone_button_ui.py',
            name='drone_pid_tuner'
        )
        nodes.append(button_ui)

    # elif node_name == "slider_ui":
    #     slider_ui = Node(
    #         package='pid_tune',
    #         executable='pid_tune_drone_slider_ui.py',
    #         name='tune_pid_drone',
    #         parameters=[
    #             {'ppid_ui_enable': True},
    #             {'rpid_ui_enable': True},
    #             {'ypid_ui_enable': False},
    #             {'tpid_ui_enable': True},
    #         ]
    #     )
    #     nodes.append(slider_ui)

    return nodes

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'node_name',
            default_value='button_ui',
            description='Name of the node to launch'
        ),
        OpaqueFunction(function=evaluate_spawn)
    ])
