import json
import time
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


class Timer:
    """
    cached_timers format:
    {"guid_1": {"isSuccess": True, "trace_start": xx, "trace_end": xx, "ready_time": []},
     "guid_2": {...}, ...}
    """

    try:
        update_cnt = 0
        with open("cached_timers.json", "r") as f:
            cached_timers = json.load(f)
    except Exception as e:
        cached_timers = {}
        update_cnt = 0
        logger.warn("no cached timer is found, build from scratch")
        # traceback.print_exc()

    @staticmethod
    def save_cache():
        with open("cached_timers.json", "w") as f:
            json.dump(Timer.cached_timers, f, indent=2)
            logger.info("Timer cached in cached_timers.json")

    def __init__(self, ubt, google=True, **kwargs):
        self.isSuccess = False
        self.fmt = "%Y-%m-%d %H:%M:%S"
        self.trace_start, self.trace_end = None, None
        self.ready_time = []
        self.network_trace = dict()
        self.google = google
        # self.state = [
        #     "battery_charged_off",
        #     "battery_charged_on",
        #     "battery_low",
        #     "battery_okay",
        #     "phone_off",
        #     "phone_on",
        #     "screen_off",
        #     "screen_on",
        #     "screen_unlock",
        # ]

        self.min_battery_level = kwargs.get("min_battery_level", 50)

        # get marched ubt from user_behavior_tiny by uid
        self.ubt = ubt

        if ubt == None:  # no user trace will be used
            self.isSuccess = True
            self.model = None
            return

        self.model = ubt["model"]
        self.guid = ubt["guid"]

        # build from cache and no need to update the cache
        if Timer.cached_timers is not None:
            if self.guid in Timer.cached_timers:
                self.isSuccess = Timer.cached_timers[self.guid]["isSuccess"]
                self.trace_start = Timer.cached_timers[self.guid]["trace_start"]
                self.trace_end = Timer.cached_timers[self.guid]["trace_end"]
                self.ready_time = Timer.cached_timers[self.guid]["ready_time"]
                self.network_trace = Timer.cached_timers[self.guid]["network_trace"]
                return

        # build from scrach and update cache
        Timer.update_cnt += 1
        # ### get ready time list ###
        start_charge, end_charge, okay, low = None, None, None, None
        message = self.ubt["messages"].split("\n")
        ready_time = []
        # for s in self.state:
        # message = message.replace(s, "\t" + s + "\n")
        # message = message.replace('\x00', '').strip().split("\n")
        # get ready time

        # ### get trace start time and trace end time ###
        for mes in message:
            try:
                t = mes.strip().split("\t")[0].strip()
                if t == "":
                    continue
                if not self.trace_start:
                    self.refer_time = t
                    self.refer_second = time.mktime(
                        datetime.strptime(self.refer_time, self.fmt).timetuple()
                    )
                    self.trace_start = 0
                sec = (
                        time.mktime(datetime.strptime(t, self.fmt).timetuple())
                        - self.refer_second
                )
                self.trace_end = sec
            except ValueError:
                logger.debug("invalid trace for uid: {}".format(self.ubt["guid"]))
                # traceback.print_exc()
                # assert False
                Timer.cached_timers[self.guid] = {}
                Timer.cached_timers[self.guid]["isSuccess"] = self.isSuccess
                Timer.cached_timers[self.guid]["trace_start"] = self.trace_start
                Timer.cached_timers[self.guid]["trace_end"] = self.trace_end
                Timer.cached_timers[self.guid]["ready_time"] = self.ready_time
                Timer.cached_timers[self.guid]["network_trace"] = self.network_trace
                if Timer.update_cnt % 100 == 0:
                    Timer.save_cache()
                return

        idle = False  # define: idle = locked
        screen_off = False
        locked = False
        wifi = False
        charged = False
        mobile_net = False
        net = None
        battery_level = 0.0
        st = None  # ready start time
        ed = None  # ready end time
        for mes in message:
            if mes.strip() == "":
                continue
            try:
                t, s = mes.strip().split("\t")
                t = t.strip()
                s = s.strip()
                s = s.lower()
                if s == "battery_charged_on":
                    charged = True
                elif s == "battery_charged_off":
                    charged = False
                elif s == "wifi":
                    wifi = True
                    net = "fix"
                elif s == "unknown" or s == "4g" or s == "3g" or s == "2g" or s == "5g":
                    wifi = False
                    mobile_net = False
                    if s == "4g" or s == "5g":
                        net = "mobile"
                        mobile_net = True
                elif s == "screen_on":
                    screen_off = False
                elif s == "screen_off":
                    screen_off = True
                elif s == "screen_lock":
                    locked = True
                elif s == "screen_unlock":
                    locked = False
                elif s[-1] == "%":
                    battery_level = float(s[:-1])
                else:
                    logger.error("invalid trace state: {}".format(s))
                    idle = False  # define: idle = locked
                    screen_off = False
                    locked = False
                    wifi = False
                    charged = False
                    battery_level = 0.0
                    assert False

                # you can define your own 'idle' state
                idle = locked or screen_off
                if (
                        idle
                        and (wifi or mobile_net)
                        and (charged or battery_level > self.min_battery_level)
                        and st == None
                ):
                    st = (
                            time.mktime(datetime.strptime(t, self.fmt).timetuple())
                            - self.refer_second
                    )
                    self.network_trace[st] = net
                if (st != None) and not (idle and wifi and charged):
                    ed = (
                            time.mktime(datetime.strptime(t, self.fmt).timetuple())
                            - self.refer_second
                    )
                    ready_time.append([st, ed])
                    st, ed = None, None
                    self.network_trace[ed] = net

                """
                if s == 'battery_charged_on' and not start_charge:
                    start_charge = time.mktime(datetime.strptime(t, self.fmt).timetuple()) - \
                                   time.mktime(datetime.strptime(self.refer_time, self.fmt).timetuple())
                elif s == 'battery_charged_off' and start_charge:
                    end_charge = time.mktime(datetime.strptime(t, self.fmt).timetuple()) - \
                                 time.mktime(datetime.strptime(self.refer_time, self.fmt).timetuple())
                    ready_time.append([start_charge, end_charge])
                    start_charge, end_charge = None, None
                if not self.google:
                    if s == 'battery_okay' and not okay:
                        okay = time.mktime(datetime.strptime(t, self.fmt).timetuple()) - \
                               time.mktime(datetime.strptime(self.refer_time, self.fmt).timetuple())
                    elif s == 'battery_low' and okay:
                        low = time.mktime(datetime.strptime(t, self.fmt).timetuple()) - \
                              time.mktime(datetime.strptime(self.refer_time, self.fmt).timetuple())
                        ready_time.append([okay, low])
                        okay, low = None, None
                """
            except ValueError as e:
                logger.debug("invalid trace for uid: {}".format(self.ubt["guid"]))
                # traceback.print_exc()
                # assert False
                Timer.cached_timers[self.guid] = {}
                Timer.cached_timers[self.guid]["isSuccess"] = self.isSuccess
                Timer.cached_timers[self.guid]["trace_start"] = self.trace_start
                Timer.cached_timers[self.guid]["trace_end"] = self.trace_end
                Timer.cached_timers[self.guid]["ready_time"] = self.ready_time
                Timer.cached_timers[self.guid]["network_trace"] = self.network_trace
                if Timer.update_cnt % 500 == 0:
                    Timer.save_cache()
                return

        # merge ready time
        try:
            ready_time = sorted(ready_time, key=lambda x: x[0])
            now = ready_time[0]
            for a in ready_time:
                if now[1] >= a[0]:
                    now = [now[0], max(a[1], now[1])]
                else:
                    self.ready_time.append(now)
                    now = a
            self.ready_time.append(now)
        except (ValueError, IndexError):
            logger.debug(
                "merge ready time error! invalid trace for uid: {}".format(
                    self.ubt["guid"]
                )
            )
            # traceback.print_exc()
            # assert False
            Timer.cached_timers[self.guid] = {}
            Timer.cached_timers[self.guid]["isSuccess"] = self.isSuccess
            Timer.cached_timers[self.guid]["trace_start"] = self.trace_start
            Timer.cached_timers[self.guid]["trace_end"] = self.trace_end
            Timer.cached_timers[self.guid]["ready_time"] = self.ready_time
            Timer.cached_timers[self.guid]["network_trace"] = self.network_trace
            if Timer.update_cnt % 100 == 0:
                Timer.save_cache()
            return

        if int(self.trace_end - self.trace_start) == 0:
            logger.info("find an invalid trace where trace_end = trace_start")
            logger.debug("invalid trace for uid: {}".format(self.ubt["guid"]))
            Timer.cached_timers[self.guid] = {}
            Timer.cached_timers[self.guid]["isSuccess"] = self.isSuccess
            Timer.cached_timers[self.guid]["trace_start"] = self.trace_start
            Timer.cached_timers[self.guid]["trace_end"] = self.trace_end
            Timer.cached_timers[self.guid]["ready_time"] = self.ready_time
            Timer.cached_timers[self.guid]["network_trace"] = self.network_trace
            if Timer.update_cnt % 100 == 0:
                Timer.save_cache()
            return

        logger.debug("user {} ready list: {}".format(self.ubt["guid"], self.ready_time))
        self.isSuccess = True
        Timer.cached_timers[self.guid] = {}
        Timer.cached_timers[self.guid]["isSuccess"] = self.isSuccess
        Timer.cached_timers[self.guid]["trace_start"] = self.trace_start
        Timer.cached_timers[self.guid]["trace_end"] = self.trace_end
        Timer.cached_timers[self.guid]["ready_time"] = self.ready_time
        Timer.cached_timers[self.guid]["network_trace"] = self.network_trace
        if Timer.update_cnt % 100 == 0:
            Timer.save_cache()

    def ready(self, round_start, reference=True):  # time_window, reference=True
        """
        if client is ready at time: round_start + time_window
        Args:
            round_start (int): round start time (reference time)
        Return: True if ready at round_start
        """
        if self.ubt == None:
            return True

        if self.isSuccess == False:
            return False

        if reference:
            round_start = round_start % self.trace_end

        for item in self.ready_time:
            if item[0] <= round_start <= item[1]:
                return True
        return False

    def will_finish(self, round_start, computation_time, reference=True):
        """
        If client will finish the local computation
        started at round_start.
        Args:
            round_start (int): round start time
            time_window (int): execute time
        Return: True if ready at round_start and at round_start + computation_time
        """
        if self.ubt == None:
            return True

        if self.isSuccess == False:
            return False

        if reference:
            round_start = round_start % self.trace_end

        for item in self.ready_time:
            if item[0] <= round_start <= item[1]:
                if (round_start + computation_time <= item[1]) or (
                        reference
                        and (round_start + computation_time) % self.trace_end <= item[1]
                ):
                    return True
                return False
        return False

    def get_net(self, time, reference=True):
        if reference:
            time = time % self.trace_end
        return self.network_trace.get(time)