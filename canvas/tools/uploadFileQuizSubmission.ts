
import { tool } from "ai";
import { uploadFileQuizSubmissionDataSchema } from "./aitm.schema.ts";
import { uploadFileQuizSubmission, UploadFileQuizSubmissionData } from "..";

export default tool({
  description: `
  Upload a file
Associate a new quiz submission file

This API endpoint is the first step in uploading
a quiz submission file.
See the {file:file_uploads.html File Upload Documentation} for details
on
the file upload workflow as these parameters are interpreted as per the
documentation there.
    `,
  parameters: uploadFileQuizSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<UploadFileQuizSubmissionData, "url"> ) => {
    try {
      const { data } = await uploadFileQuizSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    