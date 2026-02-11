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
        self.prev_state = STATE_EMPTY

        self.prev_smoothed_area = None
        self.exit_counter = 0

        self.last_exit_frame = None   # آخرین فریم معتبرِ حضور
        self.exit_emitted = False     # جلوگیری از EXIT تکراری

    def update(self, smoothed_area, frame=None):
        if self.prev_smoothed_area is None:
            trend = 0
        else:
            trend = smoothed_area - self.prev_smoothed_area

        self.prev_smoothed_area = smoothed_area
        self.prev_state = self.state

        event_type = None

        if self.state == STATE_EMPTY:
            self.exit_emitted = False
            if smoothed_area > ENTER_AREA and trend > ENTER_TREND:
                self.state = STATE_ENTERING
                event_type = "ENTER"

        elif self.state == STATE_ENTERING:
            if smoothed_area > INSIDE_AREA and abs(trend) < TREND_STABLE:
                self.state = STATE_INSIDE
                event_type = "INSIDE"

        elif self.state == STATE_INSIDE:
            # همیشه آخرین فریم حضور را نگه دار
            if frame is not None:
                self.last_exit_frame = frame.copy()

            if trend < EXIT_TREND and smoothed_area < INSIDE_AREA * 0.85:
                self.state = STATE_EXITING
                self.exit_counter = 0

        elif self.state == STATE_EXITING:
            if smoothed_area >= EXIT_AREA:
                if frame is not None:
                    self.last_exit_frame = frame.copy()

            if smoothed_area < EXIT_AREA:
                self.exit_counter += 1
            else:
                self.exit_counter = 0

            if (
                self.exit_counter >= EXIT_FRAMES_REQUIRED
                and not self.exit_emitted
            ):
                event_type = "EXIT"
                self.exit_emitted = True

            if self.exit_emitted and smoothed_area < EXIT_AREA:
                self.state = STATE_EMPTY
                self.exit_counter = 0

        return event_type, self.state, self.exit_counter, self.last_exit_frame