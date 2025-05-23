import os
import re

import yaml

from phoebus_guibuilder.datatypes import Beamline, Component, Entry
from phoebus_guibuilder.screen import TechUIScreens as Screen


class Guibuilder:
    """
    This class provides the functionality to process the required
    create_gui.yaml file into screens mapped from ioc.yaml and
    gui_map.yaml files.

    """

    def __init__(self, create_gui_yaml: str):
        self.components: list[Component] = []

        self.beamline: Beamline

        self.valid_entities: list[Entry] = []

        self.create_gui: str = create_gui_yaml

        self.extract_from_create_gui()

    def extract_from_create_gui(
        self,
    ):
        """
        Extracts from the create_gui.yaml file to generate
        the required Beamline and components structures.
        """

        with open(self.create_gui) as f:
            conf = yaml.safe_load(f)
            bl: dict[str, str] = conf["beamline"]
            comps: dict[str, dict[str, str]] = conf["components"]

            self.beamline = Beamline(**bl)

            for key, comp in comps.items():
                self.components.append(Component(key, **comp))

    def find_services_folders(
        self,
    ):
        """
        Finds the related folders in the services directory
        and extracts the related entites with the matching prefixes
        """

        services_directory = (
            "./example/" + self.beamline.dom + "-services/services"
        )  # TODO: rm hardcoding, map to services.
        path = f"{services_directory}"
        files = os.listdir(path)

        # Attempting to match the prefix to the files in the services directory
        pattern = "^(.*)-(.*)-(.*)"

        for component in self.components:
            domain: re.Match[str] | None = re.match(pattern, component.P)
            assert domain is not None, "Empty Prefix Field"

            for file in files:
                match = re.match(pattern, file)
                if match:
                    if match.group(1) == domain.group(1).lower():
                        if os.path.exists(f"{path}/{file}/config/ioc.yaml"):
                            self.extract_valid_entities(
                                ioc_yaml=f"{path}/{file}/config/ioc.yaml",
                                component=component,
                            )
                        else:
                            print(f"No ioc.yaml file for service: {file}")

    def extract_valid_entities(self, ioc_yaml: str, component: Component):
        """
        Extracts the entities in ioc.yaml matching the defined prefix
        """

        entities: list[dict[str, str]] = []
        component_match = f"{component.P}:{component.R}"

        with open(ioc_yaml) as ioc:
            conf = yaml.safe_load(ioc)
            entities = conf["entities"]
            for entity in entities:
                if (
                    "P" in entity.keys() and entity["P"] == component_match
                ):  # the suffix could be M, could be R
                    self.valid_entities.append(
                        Entry(
                            type=entity["type"],
                            DESC=component.name,
                            P=entity["P"],
                            M=None,
                            R=None,
                        )
                    )
                    if "M" in entity.keys():
                        self.valid_entities[-1].M = entity["M"]

    def gui_map(self):
        """
        Maps the valid entities from the ioc.yaml file
        to the required screen in gui_map.yaml
        """

        gui_map = "./techui-support/gui_map.yaml"

        with open(gui_map) as map:
            conf = yaml.safe_load(map)
            print(self.valid_entities)
            Screen(self.valid_entities, conf)
            # for entry in self.valid_entities:
            #     if conf[entry.type]:
            #         print(
            #             conf[entry.type]["file"]
            #         )  # Find correct .bob file, and injet macros

            # else:
            #     print("No BOB available")

    def choose_tech_support(self, branch: str):
        """
        Method which helps pull the required branch
        of the tech-support submodule
        """
        checkout_branch = "cd  ./techui_support ;\
            git checkout -b {branch};\
            cd -"

        os.system(checkout_branch)
