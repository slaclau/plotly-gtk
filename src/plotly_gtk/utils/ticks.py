import logging
import numbers

import numpy as np

logger = logging.getLogger(__name__)


class Ticks:
    ROUND_SET = {
        10: [2, 5, 10],
        "LOG1": [-0.046, 0, 0.301, 0.477, 0.602, 0.699, 0.778, 0.845, 0.903, 0.954, 1],
        "LOG2": [-0.301, 0, 0.301, 0.699, 1],
    }

    def __init__(self, layout, axis, length):
        logger.debug(
            f"Ticks.__init__(layout: {layout}, axis: {axis}, length: {length})"
        )
        self.layout = layout
        self.axis = axis
        self.axis_layout = self.layout[axis]
        self.axis_layout["_range"][0] = self.axis_layout["_range"][0]
        self.axis_layout["_range"][-1] = self.axis_layout["_range"][-1]
        self.length = length

    def tick_first(self):
        logger.debug("Calling Ticks.tick_first")
        axrev = self.axis_layout["_range"][-1] < self.axis_layout["_range"][0]
        round_func = np.floor if axrev else np.ceil
        logger.debug(f"_dtick: {self.axis_layout["_dtick"]}")
        if isinstance(self.axis_layout["_dtick"], numbers.Number):
            tmin = (
                round_func(
                    (self.axis_layout["_range"][0] - self.axis_layout["_tick0"])
                    / self.axis_layout["_dtick"]
                )
                * self.axis_layout["_dtick"]
                + self.axis_layout["_tick0"]
            )
        else:
            ttype = self.axis_layout["_dtick"][0]
            dtnum = int(self.axis_layout["_dtick"][1:])
            if ttype == "M":
                # TODO: Implement M type ticks
                raise NotImplementedError("M type ticks not implemented yet")
            elif ttype == "L":
                tmin = np.log10(
                    round_func(
                        (
                            np.power(10, self.axis_layout["_range"][0])
                            - self.axis_layout["_tick0"]
                        )
                        / dtnum
                    )
                    * dtnum
                    + self.axis_layout["_tick0"]
                )
            elif ttype == "D":
                # TODO: Finish
                tickset = (
                    self.ROUND_SET["LOG2"] if dtnum == 2 else self.ROUND_SET["LOG1"]
                )
                tickset = self.ROUND_SET[
                    "LOG2"
                ]  # FIXME: temp fix - demo log_1 is returning wrong dtnum
                frac = self.round_up(self.axis_layout["_range"][0] % 1, tickset, axrev)
                tmin = np.floor(self.axis_layout["_range"][0]) + np.log(
                    np.round(np.power(10, frac), 1)
                ) / np.log(10)
            else:
                raise ValueError(f"Unknown dtick: {self.axis_layout['_dtick']}")
        logger.debug(f"Returning {tmin} from Ticks.tick_first")
        return tmin

    def tick_increment(self, x: float, dtick: str, rev: bool) -> float:
        logger.debug(
            f"Calling Ticks.tick_increment(x: {x}, dtick: {dtick}, rev: {rev})"
        )
        sign = -1 if rev else 1
        ttype = dtick[0]
        dtnum = int(dtick[1:])
        # TODO: Do this: dtsigned = sign * dtnum

        if ttype == "M":
            raise NotImplementedError
        elif ttype == "L":
            raise NotImplementedError
        elif ttype == "D":
            tickset = self.ROUND_SET["LOG2"] if dtnum == 2 else self.ROUND_SET["LOG1"]
            tickset = self.ROUND_SET[
                "LOG2"
            ]  # FIXME: temp fix - demo log_1 is returning wrong dtnum
            x2 = x + sign * 0.01
            frac = self.round_up(x2 % 1, tickset, rev)
            inc = np.floor(x2) + np.log(np.round(np.power(10, frac), 1)) / np.log(10)
        else:
            raise ValueError(f"Unknown dtick: {self.axis_layout['_dtick']}")
        logger.debug(f"Returning {inc} from Ticks.tick_increment")
        assert isinstance(inc, float)
        return inc

    def calculate(self):
        rev = self.axis_layout["_range"][0] >= self.axis_layout["_range"][-1]
        self.prepare()

        if "tickmode" in self.axis_layout and self.axis_layout["tickmode"] == "array":
            return self.array_ticks()

        if isinstance(self.axis_layout["_dtick"], numbers.Number):
            logger.debug("Numeric dtick")
            self.axis_layout["_tickvals"] = np.arange(
                self.tick_first(),
                self.axis_layout["_range"][-1],
                self.axis_layout["_dtick"],
            )
        else:
            logger.debug("Text dtick")
            x = self.tick_first()
            _tickvals = np.array([x])
            logger.debug(f"_range: {self.axis_layout["_range"]}")
            while True:
                x = self.tick_increment(x, self.axis_layout["_dtick"], rev)
                if x >= (
                    self.axis_layout["_range"][-1]
                    if not rev
                    else self.axis_layout["_range"][0]
                ):
                    break
                _tickvals = np.append(_tickvals, [x])
            logger.debug(f"Original _tickvals: {_tickvals}")
            self.axis_layout["_tickvals"] = np.power(10, _tickvals)
            logger.debug(f"Corrected _tickvals: {self.axis_layout["_tickvals"]}")
        if isinstance(self.axis_layout["_dtick"], numbers.Number):
            self.axis_layout["_ticktext"] = np.char.mod(
                "%g", self.axis_layout["_tickvals"]
            )
        else:
            _text = []
            for _tick in self.axis_layout["_tickvals"]:
                logval = np.log10(_tick)
                if logval == np.floor(logval):
                    _text.append(f"{_tick:g}")
                else:
                    _text.append(
                        f"<sup>{_tick / np.power(10, np.floor(logval)):g}</sup>"
                    )
            self.axis_layout["_ticktext"] = _text

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
            self.auto_ticks(
                (self.axis_layout["_range"][-1] - self.axis_layout["_range"][0]) / nt
            )

    @staticmethod
    def round_up(
        value: float, rounding_set: list[float], rev: bool = False
    ) -> float | int:
        # TODO: rev
        if value <= np.max(rounding_set):
            rtn = rounding_set[np.argwhere(np.array(rounding_set) > value)[0][0]]
            assert isinstance(rtn, float) or isinstance(rtn, int)
            return rtn
        return max(rounding_set)

    @staticmethod
    def round_dtick(rough_dtick, base, rounding_set):
        rounded_val = Ticks.round_up(rough_dtick / base, rounding_set)
        return base * rounded_val

    def auto_ticks(self, rough_dtick):
        def get_base(v):
            return np.power(v, np.floor(np.log(rough_dtick) / np.log(10)))

        if self.axis_layout["_type"] == "log":
            self.axis_layout["_tick0"] = 0
            # FIXME: make this work
            if False:  # rough_dtick > 0.7:
                self.axis_layout["_dtick"] = np.ceil(rough_dtick)
            elif (
                np.abs(self.axis_layout["_range"][-1] - self.axis_layout["_range"][0])
                < 1
            ):
                nt = (
                    1.5
                    * np.abs(
                        self.axis_layout["_range"][-1] - self.axis_layout["_range"][0]
                    )
                    / rough_dtick
                )
                rough_dtick = (
                    np.abs(
                        np.power(10, self.axis_layout["_range"][-1])
                        - np.power(10, self.axis_layout["_range"][0])
                    )
                    / nt
                )
                base = get_base(10)
                self.axis_layout["_dtick"] = "L" + str(
                    self.round_dtick(rough_dtick, base, self.ROUND_SET[10])
                )
            else:
                self.axis_layout["_dtick"] = "D2" if rough_dtick > 0.3 else "D1"
        else:
            self.axis_layout["_tick0"] = 0
            base = get_base(10)
            self.axis_layout["_dtick"] = self.round_dtick(
                rough_dtick, base, self.ROUND_SET[10]
            )

    def array_ticks(self):
        vals = self.axis_layout["tickvals"]
        if self.axis_layout["_type"] == "log":
            vals = np.log(vals)
        range = self.axis_layout["_range"]
        idx_min = np.argwhere(vals >= range[0])[0][0]
        idx_max = np.argwhere(vals <= range[1])[-1][0]
        idx_slice = slice(idx_min, idx_max + 1)

        self.axis_layout["_tickvals"] = self.axis_layout["tickvals"][idx_slice]
        self.axis_layout["_ticktext"] = self.axis_layout["ticktext"][idx_slice]
        return self.axis_layout["_tickvals"]
