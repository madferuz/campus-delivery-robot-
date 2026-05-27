#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
voice_command_node.py
=====================
Owner: Member 5 (Voice & Remote interface).

ROS function #1 for Member 5: a Publisher (and conditional Subscriber)
that turns spoken commands into VoiceCommand messages.

Two input modes are supported via the ~mode parameter:

  mode = "mic"  (default)
      Use the SpeechRecognition library to listen on the default
      microphone, run Google's free recognizer, and publish recognized
      commands.

  mode = "text"
      Subscribe to /delivery/voice/text_in (std_msgs/String) so the
      CLI tool or pytest can inject simulated voice commands. Useful
      when the demo machine has no microphone and for unit testing.

A small keyword grammar is applied to map free-form sentences into one
of the supported command keywords:
    "deliver", "stop", "return_home", "open_box", "status".

Topics:
    Subscribes : /delivery/voice/text_in        (std_msgs/String, text mode)
    Publishes  : /delivery/voice/commands       (delivery_msgs/VoiceCommand)
"""

import re

import rospy
from std_msgs.msg import String

from delivery_msgs.msg import VoiceCommand


# Each rule is (compiled regex, command, optional target group name).
# The first match wins.
GRAMMAR_RULES = [
    (re.compile(r"\b(deliver|take|bring|send)\b.*\bto\b\s+(?P<target>[a-z_ ]+)",
                re.IGNORECASE), "deliver", "target"),
    (re.compile(r"\bstop\b|\bhalt\b|\bbrake\b", re.IGNORECASE), "stop", None),
    (re.compile(r"\b(return|go)\s+home\b|\bcome\s+back\b",
                re.IGNORECASE), "return_home", None),
    (re.compile(r"\bopen\b.*\bbox\b|\bopen\b.*\bdelivery\b",
                re.IGNORECASE), "open_box", None),
    (re.compile(r"\bstatus\b|\breport\b|\bhow\s+are\s+you\b",
                re.IGNORECASE), "status", None),
]


def parse_utterance(text):
    """Return (command, target, confidence) or (None, "", 0.0)."""
    if not text:
        return None, "", 0.0
    for pattern, cmd, target_group in GRAMMAR_RULES:
        match = pattern.search(text)
        if match:
            target = ""
            if target_group:
                target = match.group(target_group).strip().lower()
                # Normalise (e.g. "the library" -> "library").
                target = re.sub(r"\bthe\s+", "", target).strip()
                target = target.replace(" ", "_")
            return cmd, target, 0.9
    return None, "", 0.0


class VoiceCommandNode:

    def __init__(self):
        self.mode = rospy.get_param("~mode", "text")
        self.cmd_pub = rospy.Publisher("/delivery/voice/commands",
                                       VoiceCommand, queue_size=10)

        if self.mode == "text":
            self.text_sub = rospy.Subscriber(
                "/delivery/voice/text_in", String, self._on_text)
            rospy.loginfo("[voice_command_node] text mode. publish strings on "
                          "/delivery/voice/text_in")
        elif self.mode == "mic":
            self._start_microphone_loop()
        else:
            rospy.logerr("[voice_command_node] unknown mode '%s'", self.mode)

    # ------------------------------------------------------------------
    # Text mode
    # ------------------------------------------------------------------
    def _on_text(self, msg):
        self._publish_from_text(msg.data)

    # ------------------------------------------------------------------
    # Microphone mode
    # ------------------------------------------------------------------
    def _start_microphone_loop(self):
        try:
            # Imported lazily so that text-mode users do not need the
            # SpeechRecognition / PyAudio system libraries.
            import speech_recognition as sr
        except ImportError:
            rospy.logerr("[voice_command_node] SpeechRecognition not "
                         "installed - falling back to text mode")
            self.mode = "text"
            self.text_sub = rospy.Subscriber(
                "/delivery/voice/text_in", String, self._on_text)
            return

        recognizer = sr.Recognizer()
        try:
            microphone = sr.Microphone()
        except OSError as exc:
            rospy.logerr("[voice_command_node] microphone init failed: %s",
                         exc)
            self.mode = "text"
            self.text_sub = rospy.Subscriber(
                "/delivery/voice/text_in", String, self._on_text)
            return

        rospy.loginfo("[voice_command_node] microphone mode - listening...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

        while not rospy.is_shutdown():
            try:
                with microphone as source:
                    audio = recognizer.listen(source, phrase_time_limit=4)
                text = recognizer.recognize_google(audio)
                rospy.loginfo("[voice_command_node] heard: %r", text)
                self._publish_from_text(text)
            except sr.UnknownValueError:
                # Silence or unintelligible audio. Keep listening.
                continue
            except sr.RequestError as exc:
                rospy.logwarn_throttle(
                    10.0, "[voice_command_node] recognizer error: %s", exc)

    # ------------------------------------------------------------------
    # Common publish path
    # ------------------------------------------------------------------
    def _publish_from_text(self, text):
        cmd, target, conf = parse_utterance(text)
        if cmd is None:
            rospy.loginfo("[voice_command_node] ignored utterance: %r", text)
            return
        msg = VoiceCommand()
        msg.header.stamp = rospy.Time.now()
        msg.command = cmd
        msg.target = target
        msg.confidence = conf
        self.cmd_pub.publish(msg)
        rospy.loginfo("[voice_command_node] published %s target=%r",
                      cmd, target)


def main():
    rospy.init_node("voice_command_node", anonymous=False)
    VoiceCommandNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
