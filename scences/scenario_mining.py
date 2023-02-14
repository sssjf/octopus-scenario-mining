class ScenarioMining:
    scenario_id = 0
    classification_id = 0

    def __init__(self):
        return

    @staticmethod
    def enter_check(*args):
        # check the scenes start
        return True

    @staticmethod
    def exit_check(*args):
        # check the scenes end
        return True

    @staticmethod
    def second_check(*args):
        return True

    def get_segs(self, *args):
        # get the segment of the object scenes
        return

    def cal_scaled(self, *args):
        # transform and save the scales of the window scope
        return

    def judge_scenes(self, *args):
        # judge the scene if it is right for the requirement
        return

    @staticmethod
    def window_start_check(*args):
        # the condition of the scene start
        return

    @staticmethod
    def window_end_check(point_list, start, end, obj_freq):
        # find the end frame of the same object
        window_start = start
        window_end = len(point_list) - 1
        for temp in range(start, window_end):
            if point_list[temp + 1].frame_no - point_list[temp].frame_no > obj_freq:
                return window_start, temp
        return window_start, window_end

    def refind_segs(self, segs):
        # merge the coincide segments
        segs = sorted(segs, key=lambda r: r["start_time"])
        final_segs = []
        if len(segs) > 0:
            temp_start = segs[0]["start_time"]
            temp_end = segs[0]["end_time"]
            for i in range(1, len(segs)):
                if segs[i]["start_time"] > temp_end:
                    final_segs.append({"scenario_id": self.scenario_id, "start_time": temp_start, "end_time": temp_end})
                    temp_start = segs[i]["start_time"]
                    temp_end = segs[i]["end_time"]
                elif segs[i]["end_time"] > temp_end:
                    temp_end = segs[i]["end_time"]
            final_segs.append({"scenario_id": self.scenario_id, "start_time": temp_start, "end_time": temp_end})
        return final_segs

    def check(self, *args):
        # check the scene
        return


