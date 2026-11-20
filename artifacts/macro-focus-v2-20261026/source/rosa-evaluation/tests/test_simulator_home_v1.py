import re
import unittest
import xml.etree.ElementTree as ET
from rosa_reliability.ros_arm import HOME_POSE
from experiments.simulator_home_v1 import INSTALLED, MARKER, home_description, verify_home


class SpawnHomeTests(unittest.TestCase):
    def test_only_change_is_initial_positions_not_geometry_or_controllers(self):
        original = INSTALLED.read_text()
        generated = home_description(original)
        self.assertEqual(re.sub(r'\n    initial_positions="[^"\n]*"', '', generated), original)
        root = ET.fromstring(generated)
        control = root.find('{http://wiki.ros.org/xacro}ur_ros2_control')
        expression = control.attrib['initial_positions']
        for key, value in HOME_POSE.items():
            self.assertIn(key + '=' + repr(value), expression)

    def test_unexpected_template_and_nonhome_state_fail_closed(self):
        for template in ('no known macro', MARKER + MARKER):
            with self.assertRaises(RuntimeError):
                home_description(template)
        verify_home(HOME_POSE)
        nonhome = dict(HOME_POSE, elbow_joint=0.)
        with self.assertRaises(RuntimeError):
            verify_home(nonhome)
        with self.assertRaises(RuntimeError):
            verify_home({})
