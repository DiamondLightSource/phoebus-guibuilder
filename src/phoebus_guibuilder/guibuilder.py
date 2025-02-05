import pprint
import re
from dataclasses import dataclass
from warnings import warn

import yaml

pp = pprint.PrettyPrinter()


@dataclass
class Beamline:
    dom: str
    desc: str


@dataclass
class Component:
    name: str
    desc: str
    prefix: str
    filename: str | None = None

    def __post_init__(self):
        self._extract_p_and_r()

    def __repr__(self) -> str:
        return f"Component(name={self.name}, desc={self.desc}, prefix={self.P}, \
            suffix={self.R}, filename={self.filename})"

    def _extract_p_and_r(self):
        pattern = re.compile(
            r"""
            ^           # start of string
            (?=         # lookahead to ensure the following pattern matches
                [A-Za-z0-9-]{14,16} # match 14 to 16 alphanumeric characters or hyphens
                [:A-Za-z0-9]* # match zero or more colons or alphanumeric characters
                [.A-Za-z0-9]  # match a dot or alphanumeric character
            )
            (?!.*--)    # negative lookahead to ensure no double hyphens
            (?!.*:\..)  # negative lookahead to ensure no colon followed by a dot
            (           # start of capture group 1
                (?:[A-Za-z0-9]{2,5}-){3} # match 2 to 5 alphanumeric characters followed
                                    # by a hyphen, repeated 3 times
                [\d]*   # match zero or more digits
                [^:]?   # match zero or one non-colon character
            )
            (?::([a-zA-Z0-9:]*))? # match zero or one colon followed by zero or more
                                # alphanumeric characters or colons (capture group 2)
            (?:\.([a-zA-Z0-9]+))? # match zero or one dot followed by one or more
                                # alphanumeric characters (capture group 3)
            $           # end of string
        """,
            re.VERBOSE,
        )

        match = re.match(pattern, self.prefix)
        if match:
            self.P: str = match.group(1)
            self.R: str = match.group(2)
            # TODO: Is this needed?
            self.attribute: str | None = match.group(3)
        else:
            warn(f"No valid PV prefix found for {self.name}.", stacklevel=1)
            exit()


components: list[Component] = []

with open("create_gui.yaml") as f:
    conf = yaml.safe_load(f)

    bl: dict[str, str] = conf["beamline"]
    comps: dict[str, dict[str, str]] = conf["components"]

    beamline = Beamline(**bl)

    for key, comp in comps.items():
        components.append(Component(key, **comp))

print("BEAMLINE:")
pp.pprint(beamline)

print("")
print("COMPONENTS")
pp.pprint(components)
