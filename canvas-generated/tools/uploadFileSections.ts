
import { tool } from "ai";
import { uploadFileSectionsDataSchema } from "./aitm.schema.ts";
import { uploadFileSections, UploadFileSectionsData } from "..";

export default tool({
  description: `
  Upload a file
Upload a file to a submission.

This API endpoint is the first step in uploading a
file to a submission as a student.
See the {file:file_uploads.html File Upload Documentation} for
details on the file upload workflow.

The final step of the file upload workflow will return the
attachment data,
including the new file id. The caller can then POST to submit the
+online_upload+
assignment with these file ids.
    `,
  parameters: uploadFileSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UploadFileSectionsData, "url"> ) => {
    try {
      const { data } = await uploadFileSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    