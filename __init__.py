'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy


bl_info = {
    "name":        "Rigify Gamerig Extension",
    "description": "Gamerig extension for rigify",
    "author":      "cgtinker",
    "version":     (0, 0, 1),
    "blender":     (2, 90, 0),
    "location":    "Object > Data Properties",
    "wiki_url":    "https://github.com/cgtinker/rigify_gamerig_extension",
    "tracker_url": "https://github.com/cgtinker/rigify_gamerig_extension/issues",
    "support":     "COMMUNITY",
    "category":    "Development"
}


class PG_CGT_Rigify_Extension_Properties(bpy.types.PropertyGroup):
    def is_armature(self, object):
        if object.type == 'ARMATURE':
            if 'rig_id' in object.data:
                return False
            return True
        return False

    selected_metarig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        description="Select a metarig as future gamerig.",
        name="Armature",
        poll=is_armature)

    frame_start: bpy.props.IntProperty(default=1)
    frame_end: bpy.props.IntProperty(default=120)
    bake_name: bpy.props.StringProperty(default="New Action")


class OBJECT_PT_RigifyExtensionUI(bpy.types.Panel):
    bl_label = "Rigify Gamerig Extension"
    bl_options = {'DEFAULT_CLOSED'}
    bl_idname = "OBJECT_PT_CGT_Rigify_Extension"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(self, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE' and context.active_object.data.get("rig_id") is not None

    def draw(self, context):
        user = context.scene.cgtinker_rigify_extension  # noqa
        layout = self.layout
        row = layout.row(align=True)
        row.prop_search(data=user, property="selected_metarig", search_data=bpy.data,
                        search_property="objects", text="Meta-Rig", icon="ARMATURE_DATA")

        if user.selected_metarig:
            layout.row(align=True).operator("button.ot_cgt_link_generated_to_metarig", text="Link Meta-Rig", icon='ANIM')

            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=True)
            col = flow.row(align=True)
            col.row(align=True).prop(data=user, property="frame_start", text="Frame Start")
            col.row(align=True).prop(data=user, property="frame_end", text="Frame End")
            flow.row(align=True).prop(data=user, property="bake_name", text="")
            flow.row(align=True).operator("button.ot_cgt_bake_metarig", text="Bake Meta-Rig", icon='ACTION')

            layout.row(align=True).operator("button.ot_cgt_unlink_metarig", text="Unlink Meta-Rig", icon='REMOVE')


class OT_CGT_LinkGenerated2MetaRig(bpy.types.Operator):
    bl_label = "Link to Meta-Rig"
    bl_idname = "button.ot_cgt_link_generated_to_metarig"
    bl_description = "Link rigify metarig to generated rig."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = bpy.context.scene.cgtinker_rigify_extension
        metarig = user.selected_metarig
        rig = context.object

        # guards
        d = {}
        if metarig is None:
            logging.warning("No rig to transfer to selected.")
            return {'CANCELLED'}

        if rig is None:
            logging.warning("No rig to transfer from selected.")
            return {'CANCELLED'}

        for bone in metarig.data.bones:
            d[bone.name] = ''

        # get bone references (atm locations at layer 29)
        rig = bpy.data.objects['rig']
        for bone in rig.data.bones:
            if bone.layers[29] or bone.use_deform:
                name = bone.name
                if name.startswith('DEF-'):
                    name = name.replace('DEF-', '')
                if name not in d:
                    d[name] = None
                else:
                    d[name] = bone.name

        # add constraints
        for key, value in d.items():
            if value != None:
                constraint = metarig.pose.bones[key].constraints.new('COPY_TRANSFORMS')
                constraint.target = rig
                constraint.subtarget = value
                constraint.influence = 1

        return {'FINISHED'}


class OT_CGT_BakeMetaRig(bpy.types.Operator):
    bl_label = "Unlink Meta-Rig"
    bl_idname = "button.ot_cgt_bake_metarig"
    bl_description = "Bake metarig animation to rna strip."

    @staticmethod
    def stash(obj, action, track_name, start_frame):
        # https://blender.stackexchange.com/questions/254615/how-can-i-push-all-actions-into-nla-trough-blender-headless-with-python
        tracks = obj.animation_data.nla_tracks
        new_track = tracks.new(prev=None)
        new_track.name = track_name
        strip = new_track.strips.new(action.name, start_frame, action)
        new_track.lock = True
        new_track.mute = True
        obj.animation_data.action = None

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = bpy.context.scene.cgtinker_rigify_extension

        # selection
        generated_rig = bpy.context.selected_objects[0]
        metarig = user.selected_metarig
        bpy.ops.object.select_all(action='DESELECT')
        metarig.select_set(True)

        # bake
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.nla.bake(frame_start=user.frame_start, frame_end=user.frame_end, only_selected=False, visual_keying=True, clear_constraints=False, bake_types={'POSE'})
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        metarig.select_set(True)

        # stashing
        metarig.animation_data.action.name = user.bake_name
        self.stash(metarig, metarig.animation_data.action, user.bake_name, user.frame_start)
        bpy.ops.object.select_all(action='DESELECT')

        generated_rig.select_set(True)

        return {'FINISHED'}


class OT_CGT_UnlinkMetaRig(bpy.types.Operator):
    bl_label = "Unlink Meta-Rig"
    bl_idname = "button.ot_cgt_unlink_metarig"
    bl_description = "Unlink rigify metarig from generated rig."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = bpy.context.scene.cgtinker_rigify_extension
        metarig = user.selected_metarig

        # remove constraints
        d = {}
        for pb in metarig.pose.bones:
            d[pb] = pb.constraints

        for bone, constraints in d.items():
            for c in constraints:
                bone.constraints.remove(c)

        return {'FINISHED'}


classes = [
    OT_CGT_LinkGenerated2MetaRig,
    OT_CGT_UnlinkMetaRig,
    OT_CGT_BakeMetaRig,
    PG_CGT_Rigify_Extension_Properties,
    OBJECT_PT_RigifyExtensionUI,
]



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgtinker_rigify_extension = bpy.props.PointerProperty(type=PG_CGT_Rigify_Extension_Properties)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cgtinker_rigify_extension


if __name__ == '__main__':
    try:
        unregister()
    except RuntimeError:
        pass

    register()
