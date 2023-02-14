from __future__ import absolute_import

from scences import K_LOG, analyzers, READER_MAP


def get_episode_topics_and_files(bag_path):
    topics = []
    files = []
    return topics, files


def read_data(file):
    reader = READER_MAP[','.join([file.format, file.topic.name])]
    return reader(file)


def upload_rst(objects):
    pass


def run_main():
    bag = {}
    topics, files = get_episode_topics_and_files(bag)
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
        upload_rst(objects)
    except Exception as error:
        K_LOG.exception(error)
        raise error


if __name__ == "__main__":
    run_main()
