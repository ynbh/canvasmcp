
import { tool } from "ai";
import { submitAssignmentSectionsDataSchema } from "./aitm.schema.ts";
import { submitAssignmentSections, SubmitAssignmentSectionsData } from "..";

export default tool({
  description: `
  Submit an assignment
Make a submission for an assignment. You must be enrolled as a student in
the
course/section to do this.

All online turn-in submission types are supported in this API.
However,
there are a few things that are not yet supported:

* Files can be submitted based on a
file ID of a user or group file. However, there is no API yet for listing the user and group files,
or uploading new files via the API. A file upload API is coming soon.
* Media comments can be
submitted, however, there is no API yet for creating a media comment to submit.
* Integration with
Google Docs is not yet supported.
    `,
  parameters: submitAssignmentSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SubmitAssignmentSectionsData, "url"> ) => {
    try {
      const { data } = await submitAssignmentSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    