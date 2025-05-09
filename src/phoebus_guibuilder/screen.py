import warnings
from pathlib import Path
from pprint import PrettyPrinter

import phoebusgen.screen as Screen
import phoebusgen.widget as Widget
from lxml import etree, objectify

from phoebus_guibuilder.datatypes import Entry

# from phoebus_guibuilder.guibuilder import Guibuilder

pp = PrettyPrinter()


class TechUIScreens:
    def __init__(self, screen_components: list[Entry], screen: dict):
        self.screen_components = screen_components
        self.screen_ = Screen.Screen(self.screen_components[0].DESC)
        widgets = []

        self.P: str = "P"
        self.M: str = "M"

        for order, ui in enumerate(self.screen_components):
            if ui.M is not None:
                name = ui.M
            else:
                name = ui.type

            widgets.append(
                Widget.EmbeddedDisplay(
                    name,
                    "./techui-support/bob/" + screen[ui.type]["file"],
                    (10 + 2 * order),
                    (10 + 2 * order),
                    700,
                    700,
                )
            )
            widgets[order].macro(self.P, ui.P)
            widgets[order].macro(self.M, ui.M)

            self.screen_.add_widget(widgets[order])

        self.screen_.write_screen(self.screen_components[0].DESC + ".bob")


class BobScreens:
    def __init__(self, bob_path: str | Path):
        bob_path = bob_path if isinstance(bob_path, Path) else Path(bob_path)

        assert bob_path.exists(), warnings.warn(
            f"Bob file {bob_path} can't be found. Does it exist?", stacklevel=1
        )

        self.path = bob_path

    def read_bob(self) -> None:
        parser = etree.XMLParser()
        # Read the bob file
        self.tree: etree._ElementTree = objectify.parse(self.path, parser)

        # Find the root tag (in this case: <display version="2.0.0">)
        self.root = self.tree.getroot()

    def autofill_bob(self, gui):
        # Get names from component list
        comp_names = [comp.name for comp in gui.components]

        # Loop over objects in the xml
        # i.e. every tag below <display version="2.0.0">
        # but not any nested tags below them
        for child in self.root:
            # For type hinting
            assert isinstance(child, etree._Element)  # noqa: SLF001

            # If widget is a symbol (i.e. a component)
            if child.tag == "widget" and child.get("type", default=None) == "symbol":
                # Extract it's name
                symbol_name = child.find("name", namespaces=None).text

                # If the name exists in the component list
                if symbol_name in comp_names:
                    # Get first copy of component (should only be one)
                    comp = next(
                        (comp for comp in gui.components if comp.name == symbol_name),
                    )

                    # Extract it's current pv_name, or if empty set to {prefix}
                    pv_name: str = (
                        child.find("pv_name", namespaces=None).text or "{prefix}"
                    )

                    # Replace instance of {prefix} with the component's prefix
                    pv_name = pv_name.replace("{prefix}", comp.prefix)

                    # Set component's pv_name to the autofilled pv_name
                    child.find("pv_name", namespaces=None).text = pv_name

    def write_bob(self):
        self.tree.write(
            "BL23B.bob",
            pretty_print=True,  # type: ignore
            encoding="utf-8",  # type: ignore
            xml_declaration=True,  # type: ignore
        )
