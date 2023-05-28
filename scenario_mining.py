from __future__ import absolute_import

import os

import rosbag

from scenes import K_LOG, analyzers, READER_MAP


def read_data(file):
    reader = READER_MAP[','.join([file.format, file.topic.name])]
    return reader(file)


def upload_result(objects):
    with open(os.path.join(os.getenv("output_dir"), "segments.csv"), "w") as f:
        f.write("tag_name, start, end, folder\n")
        for segment_object in objects:
            f.write(f"{segment_object.scenario_name},{segment_object.start_time},{segment_object.end_time},vehicle")


def merge_segments(segment_results, scenario_name_1, scenario_name_2):
    segments_1 = [segment for segment in segment_results if segment["scenario_name"] == scenario_name_1]
    segments_2 = [segment for segment in segment_results if segment["scenario_name"] == scenario_name_2]
    segments_1 = sorted(segments_1, key=lambda r: r["start_time"])
    segments_2 = sorted(segments_2, key=lambda r: r["start_time"])
    if len(segments_1) == 0 or len(segments_2) == 0:
        return
    new_scenario_name = scenario_name_1 + "_" + scenario_name_2
    index = 0
    start_time = segments_2[index]["start_time"]
    end_time = segments_2[index]["end_time"]
    for segment_info in segments_1:
        if segment_info["start_time"] < start_time < segment_info["end_time"]:
            segment_results.append({"scenario_name": new_scenario_name,
                                    "start_time": segment_info["start_time"],
                                    "end_time": max(segment_info["end_time"], end_time)})
            index += 1
            if index == len(segments_2):
                return
            start_time = segments_2[index]["start_time"]
            end_time = segments_2[index]["end_time"]
        elif segment_info["start_time"] > start_time:
            index += 1
            if index == len(segments_2):
                return
            start_time = segments_2[index]["start_time"]
            end_time = segments_2[index]["end_time"]


def run_main():
    bag = rosbag.Bag(os.getenv("rosbag_path"), "r")
    topics = bag.get_type_and_topic_info()
    topic_data = {}
    objects = []
    try:
        for analyzer in analyzers:
            K_LOG.info("start analyzer: " + type(analyzer).__name__)
            if not set(analyzer.need_topics()).issubset(topics):
                K_LOG.warning("Lack topics to do analyze.")
                continue
            try:
                for topic in analyzer.need_topics():
                    if topic not in topic_data:
                        topic_data[topic] = read_data(bag[topic])
                segments = analyzer.check(topic_data)
                if len(segments) > 0:
                    for segment in segments:
                        objects.append(segment)
            except Exception as error:
                K_LOG.exception(error)
        upload_result(objects)
    except Exception as error:
        K_LOG.exception(error)
        raise error


if __name__ == "__main__":
    run_main()
