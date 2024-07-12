import numpy as np


class Ticks:
    ROUND_SET = {10: [2, 5, 10]}

    def __init__(self, layout, axis, length):
        self.layout = layout
        self.axis = axis
        self.axis_layout = self.layout[axis]
        self.min = self.axis_layout["_range"][0]
        self.max = self.axis_layout["_range"][-1]
        self.length = length

    def update_length(self, length):
        self.length = length

    def tick_first(self):
        tmin = (
            np.ceil(
                (self.min - self.axis_layout["_tick0"]) / self.axis_layout["_dtick"]
            )
            * self.axis_layout["_dtick"]
            + self.axis_layout["_tick0"]
        )
        return tmin

    def calculate(self):
        self.prepare()

        if "tickmode" in self.axis_layout and self.axis_layout["tickmode"] == "array":
            return self.array_ticks()

        self.axis_layout["_tickvals"] = np.arange(
            self.tick_first(),
            self.max,
            self.axis_layout["_dtick"],
        )
        self.axis_layout["_ticktext"] = np.char.mod("%g", self.axis_layout["_tickvals"])
        return self.axis_layout["_tickvals"]

    def prepare(self):
        if (
            "tickmode" in self.axis_layout and self.axis_layout["tickmode"] == "auto"
        ) or "dtick" not in self.axis_layout:
            nt = self.axis_layout["nticks"]

            if nt == 0:
                min_px = 40 if self.axis.startswith("y") else 80
                nt = round(self.length / min_px)
                nt = min(10, max(5, nt))
            self.auto_ticks((self.max - self.min) / nt)

    @staticmethod
    def round_up(value, rounding_set):
        if value <= np.max(rounding_set):
            return rounding_set[np.argwhere(np.array(rounding_set) > value)[0][0]]
        return max(rounding_set)

    @staticmethod
    def round_dtick(rough_dtick, base, rounding_set):
        rounded_val = Ticks.round_up(rough_dtick / base, rounding_set)
        return base * rounded_val

    def auto_ticks(self, rough_dtick):
        def get_base(v):
            return np.power(v, np.floor(np.log(rough_dtick) / np.log(10)))

        self.axis_layout["_tick0"] = 0
        base = get_base(10)
        self.axis_layout["_dtick"] = self.round_dtick(
            rough_dtick, base, self.ROUND_SET[10]
        )

    def array_ticks(self):
        vals = self.axis_layout["tickvals"]
        if "type" in self.axis_layout and self.axis_layout["type"] == "log":
            vals = np.log(vals)
        range = self.axis_layout["_range"]
        idx_min = np.argwhere(vals >= range[0])[0][0]
        idx_max = np.argwhere(vals <= range[1])[-1][0]
        idx_slice = slice(idx_min, idx_max + 1)

        self.axis_layout["_tickvals"] = self.axis_layout["tickvals"][idx_slice]
        self.axis_layout["_ticktext"] = self.axis_layout["ticktext"][idx_slice]
        return self.axis_layout["_tickvals"]
