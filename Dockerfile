FROM ros:noetic

COPY scenes /root/scenes
COPY scenario_mining.py /root/scenario_mining.py
ENV PYTHONPATH=/opt/ros/noetic/lib/python3/dist-packages

WORKDIR /root
