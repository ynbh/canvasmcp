
import { tool } from "ai";
import { uploadFileToUsersFilesDataSchema } from "./aitm.schema.ts";
import { uploadFileToUsersFiles, UploadFileToUsersFilesData } from "..";

export default tool({
  description: `
  Upload a file
Upload a file to the user's personal files section. This API endpoint is the first
step in uploading a file to a user's files. See the {file:file_uploads.html File Upload
Documentation} for details on the file upload workflow. Note that typically users will only be able
to upload files to their own files section. Passing a user_id of +self+ is an easy shortcut to
specify the current user.
    `,
  parameters: uploadFileToUsersFilesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UploadFileToUsersFilesData, "url"> ) => {
    try {
      const { data } = await uploadFileToUsersFiles(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    