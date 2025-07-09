
import { tool } from "ai";
import { uploadFileToFolderDataSchema } from "./aitm.schema.ts";
import { uploadFileToFolder, UploadFileToFolderData } from "..";

export default tool({
  description: `
  Upload a file
Upload a file to a folder.

This API endpoint is the first step in uploading a
file.
See the {file:file_uploads.html File Upload Documentation} for details on
the file upload
workflow.

Only those with the "Manage Files" permission on a course or group can
upload files to a
folder in that course or group.
    `,
  parameters: uploadFileToFolderDataSchema.omit({ url: true }),
  execute: async (args : Omit<UploadFileToFolderData, "url"> ) => {
    try {
      const { data } = await uploadFileToFolder(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    