
import { tool } from "ai";
import { uploadFileToSubmissionDataSchema } from "./aitm.schema.ts";
import { uploadFileToSubmission, UploadFileToSubmissionData } from "..";

export default tool({
  description: `
  Upload a file
Upload a file to attach to a submission comment

See the {file:file_uploads.html File
Upload Documentation} for details on the file upload workflow.

The final step of the file upload
workflow will return the attachment data,
including the new file id. The caller can then PUT the
file_id to the
submission API to attach it to a comment
    `,
  parameters: uploadFileToSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<UploadFileToSubmissionData, "url"> ) => {
    try {
      const { data } = await uploadFileToSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    