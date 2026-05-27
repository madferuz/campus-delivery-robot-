# VoiceCommand.msg
# Published by the voice node every time a valid voice command is
# recognized. Mission control subscribes and acts on this message.

Header header

# Recognized command keyword. Supported values:
#   "deliver", "stop", "return_home", "open_box", "status".
string command

# Optional target name when the command is "deliver" (e.g. "library").
string target

# Confidence of the recognition in [0.0, 1.0].
float32 confidence
