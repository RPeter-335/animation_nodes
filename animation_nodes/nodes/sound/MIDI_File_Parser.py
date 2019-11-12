import os
import bpy
from ... base_types import AnimationNode
from ... utils.midi import MIDI_ParseFile

# path : last modification, content
cache = {}

class MIDIFile(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiFileParserNode"
    bl_label = "MIDI File Parser"
    bl_width_default = 180
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Text", "Path", "path", showFileChooser = True)
        self.newOutput("MIDITrackList", "Tracks", "tracks")

    def draw(self, layout):
        if self.inputs[0].isUnlinked:
            name = os.path.basename(self.inputs[0].value)
            if name != "":
                layout.label(text = name, icon = "FILE_TEXT")

    def drawAdvanced(self, layout):
        self.invokeFunction(layout, "clearCache", text = "Clear Cache")

    def clearCache(self):
        cache.clear()

    def execute(self, path):
        if not os.path.exists(path):
            self.raiseErrorMessage("Path does not exist")

        key = path
        lastModification = os.stat(path).st_mtime

        loadFile = False
        if key not in cache:
            loadFile = True
        else:
            oldLastModification = cache[key][0]
            if lastModification > oldLastModification:
                loadFile = True

        if loadFile:
            try:
                tracks = MIDI_ParseFile(path)
                cache[key] = (lastModification, tracks)
            except LookupError:
                self.raiseErrorMessage("Invalid Encoding")
        else:
            tracks = None

        return cache.get(key)[1]
