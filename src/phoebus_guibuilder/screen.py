import phoebusgen.screen as Screen
import phoebusgen.widget as Widget


class TechUIScreens:
    def __init__(
        self, screen_name: str, Prefix: list[str], Suffix: list[str], ui_map: list[str]
    ):
        widgets = []

        self.P: str = "P"
        self.M: str = "M"

        screen = Screen.Screen(screen_name)
        for order, ui in enumerate(ui_map):
            widgets.append(
                Widget.EmbeddedDisplay(
                    "MOTOR", ui, (10 + 2 * order), (10 + 2 * order), 700, 700
                )
            )
            widgets[order].macro(self.P, Prefix[order])
            widgets[order].macro(self.M, Suffix[order])

            screen.add_widget(widgets[order])

        screen.write_screen("first_screen.bob")

    def create_screen(self, screen: str):
        Screen.Screen(screen)


TechUIScreens("Motor", ["BL01T-MO-STAGE-01"], ["X"], ["./techui-support/bob/MOTOR.bob"])
