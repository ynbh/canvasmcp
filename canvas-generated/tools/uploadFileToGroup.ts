
import { tool } from "ai";
import { uploadFileToGroupDataSchema } from "./aitm.schema.ts";
import { uploadFileToGroup, UploadFileToGroupData } from "..";

export default tool({
  description: `
  Upload a file
Upload a file to the group.

This API endpoint is the first step in uploading a file
to a group.
See the {file:file_uploads.html File Upload Documentation} for details on
the file
upload workflow.

Only those with the "Manage Files" permission on a group can upload files
to the
group. By default, this is anybody participating in the
group, or any admin over the group.
    `,
  parameters: uploadFileToGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<UploadFileToGroupData, "url"> ) => {
    try {
      const { data } = await uploadFileToGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    