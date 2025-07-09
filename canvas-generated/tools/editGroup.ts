
import { tool } from "ai";
import { editGroupDataSchema } from "./aitm.schema.ts";
import { editGroup, EditGroupData } from "..";

export default tool({
  description: `
  Edit a group
Modifies an existing group.  Note that to set an avatar image for the
group, you must
first upload the image file to the group, and the use the
id in the response as the argument to this
function.  See the
{file:file_uploads.html File Upload Documentation} for details on the file
upload
workflow.
    `,
  parameters: editGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditGroupData, "url"> ) => {
    try {
      const { data } = await editGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    