bl_info = {
    "name": "CodeStat",
    "author": "Howie Duhzit",
    "version": (1, 0, 0),
    "blender": (3, 50, 0),
    "location": "Viewport",
    "description": "CodeStat Addon for tracking Blender XP",
    "warning": "",
    "wiki_url": "",
    "category": "Development",
}

import bpy
import requests
import json
import time
import math

PULSE_ENDPOINT = "https://codestats.net/api/my/pulses"
PROFILE_ENDPOINT = "https://codestats.net/api/users/"

def get_level(xp):
    LEVEL_FACTOR = 0.025
    return int(math.floor(LEVEL_FACTOR * math.sqrt(xp)))

def CodeStatsPulse():
    preferences = bpy.context.preferences.addons[__name__].preferences
    api_key = preferences.api_key
    if api_key:
        try:
            print("Sending pulse...")
            pulse_data = {
                "coded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "xps": [{"language": "Blender", "xp": 5}]  # Add the languages and accumulated XP here
            }

            headers = {"X-API-Token": api_key, "Content-Type": "application/json"}
            response = requests.post(PULSE_ENDPOINT, headers=headers, data=json.dumps(pulse_data))

            if response.status_code == 201:
                print("Pulse sent successfully!")
            else:
                print("Failed to send pulse. Please check your API key and username.")

        except Exception as e:
            print("An error occurred while sending the pulse.")

    else:
        print("Please enter your API key in the plugin settings.")

    return 300.0

class CodeStatsPluginSettings(bpy.types.AddonPreferences):
    bl_idname = __name__

    api_key: bpy.props.StringProperty(name="API Key", description="Enter your CodeStats API Key", default="", subtype="PASSWORD")
    username: bpy.props.StringProperty(name="username", description="Enter your CodeStats Username", default="")

    def draw(self, context):
        layout = self.layout
        layout.label(text="CodeStats API Key:")
        layout.prop(self, "api_key")
        layout.label(text="CodeStats Username:")
        layout.prop(self, "username")
        
class CodeStatsPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_code_stats_panel"
    bl_label = "Code::Stats"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Info"

    def draw(self, context):
        layout = self.layout
        
        preferences = bpy.context.preferences.addons[__name__].preferences
        api_key = preferences.api_key
        username = preferences.username
        
        if api_key and username:
            try:
                profile_url = PROFILE_ENDPOINT + username
                headers = {"X-API-Token": api_key}
                response = requests.get(profile_url, headers=headers)
                
                if response.status_code == 200:
                    data = json.loads(response.text)
                    user = data["user"]
                    total_xp = data["total_xp"]
                    new_xp = data["new_xp"]
                    level = get_level(total_xp)
                    languages = data["languages"]
                    blender_language = languages["Blender"]
                    blender_xp = blender_language["xps"]
                    blender_level = get_level(blender_xp)

                    row = layout.row()
                    row.label(text=f"***** {user} *****")
                    row = layout.row()
                    row.label(text=f"Level {level} - {total_xp} XP")
                    row = layout.row()
                    row.label(text=f"Blender Level {blender_level} - {blender_xp} XP")

                else:
                    row = layout.row()
                    row.label(text="Failed to fetch profile info. Please check your API key and username.")

            except Exception as e:
                row = layout.row()
                row.label(text="An error occurred while fetching profile info.")

        else:
            row = layout.row()
            row.label(text="Please enter your API key and username in the add-on preferences.")

classes = (
    CodeStatsPluginSettings,
    CodeStatsPanel
)

def register():
    bpy.utils.register_class(CodeStatsPluginSettings)
    bpy.utils.register_class(CodeStatsPanel)
    bpy.app.timers.register(CodeStatsPulse, first_interval=0, persistent=True)

def unregister():
    bpy.utils.unregister_class(CodeStatsPluginSettings)
    bpy.utils.unregister_class(CodeStatsPanel)
    bpy.app.timers.unregister(CodeStatsPulse)
    
if __name__ == "__main__":
    register()
