from config import (
    ENTER_AREA,
    INSIDE_AREA,
    EXIT_AREA,
    ENTER_TREND,
    EXIT_TREND,
    TREND_STABLE,
    EXIT_FRAMES_REQUIRED
)
STATE_EMPTY    = 0
STATE_ENTERING = 1
STATE_INSIDE   = 2
STATE_EXITING  = 3

class FSM:
    def __init__(self):
        self.state = STATE_EMPTY
        self.prev_smoothed_area = None
        self.exit_counter = 0
        self.last_presence_frame = None  # فریم آخر حضور
        self.exit_emitted = False       # جلوگیری از چندبار ثبت EXIT

    def update(self, smoothed_area, raw_frame=None):
        # ---------- trend ----------
        if self.prev_smoothed_area is None:
            trend = 0
        else:
            trend = smoothed_area - self.prev_smoothed_area
        self.prev_smoothed_area = smoothed_area

        event_type = None

        if self.state == STATE_EMPTY:
            self.exit_emitted = False
            self.last_presence_frame = None
            if smoothed_area > ENTER_AREA and trend > ENTER_TREND:
                self.state = STATE_ENTERING
                event_type = "ENTER"

        elif self.state == STATE_ENTERING:
            if smoothed_area > INSIDE_AREA and abs(trend) < TREND_STABLE:
                self.state = STATE_INSIDE
                event_type = "INSIDE"

        elif self.state == STATE_INSIDE:
            # آخرین فریم معتبر حضور را نگه داریم
            if raw_frame is not None:
                self.last_presence_frame = raw_frame.copy()

            if trend < EXIT_TREND and smoothed_area < INSIDE_AREA * 0.9:
                self.state = STATE_EXITING
                self.exit_counter = 0

        elif self.state == STATE_EXITING:
            # هنوز داخل ناحیه است → فریم حضور را نگه داریم
            if smoothed_area >= EXIT_AREA:
                if raw_frame is not None:
                    self.last_presence_frame = raw_frame.copy()
                self.exit_counter = 0
            else:
                self.exit_counter += 1

            if self.exit_counter >= EXIT_FRAMES_REQUIRED and not self.exit_emitted:
                event_type = "EXIT"
                self.exit_emitted = True

            if self.exit_emitted and smoothed_area < EXIT_AREA:
                self.state = STATE_EMPTY
                self.exit_counter = 0

        return event_type, self.state, self.exit_counter, self.last_presence_frame