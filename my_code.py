"""The OpenExVis visualizer.

Transfers the visualization data it receives from an OpenExVis translator into
visualization commands used by the UI to show the visualization. OpenExVis user
interfaces should inherit the visualizer.

"""

# TODO: Is inheritance the correct solution?

import time

import oevt_python

class OevVisualizer:
    """Translate OpenExVis visualization data to commands to the UI."""

    def __init__(self):
        # The speed of visualization. When False, we are paused. Higher values
        # mean faster visualization.
        self.speed = False
        # The translator we use to create visualization data.
        # We feed this visualizer to the oevt constructor to tell it to send
        # the data back to us.
        self.translator = oevt_python.OevTranslator(self)

    def vis_step(self, visdata):
        """Create commands for one visualization step.

        The translator calls this function giving the visualization data as an
        argument. The data is used for making the visualization. For now, we
        simply split it to a list without converting it to commands.

        """
        viscommands = visdata.split(';')
        self.draw_step(viscommands, self.speed)
        return True

    def visualize(self, code):
        """Visualize execution of code.

        Code as a string is given as an argument and fed to the translator
        associated with this visualizer.

        """
        self.translator.translate(code)
        return True

    def set_speed(self, speed):
        """Set the speed of visualization."""
        self.speed = speed

    def draw_step(self, visinfo):
        """Draw a visualization step."""
        # User interfaces should implement this to draw the visualization.
        pass
