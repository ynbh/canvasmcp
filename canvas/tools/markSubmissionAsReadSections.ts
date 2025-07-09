
import { tool } from "ai";
import { markSubmissionAsReadSectionsDataSchema } from "./aitm.schema.ts";
import { markSubmissionAsReadSections, MarkSubmissionAsReadSectionsData } from "..";

export default tool({
  description: `
  Mark submission as read
No request fields are necessary.

On success, the response will be 204 No
Content with an empty body.
    `,
  parameters: markSubmissionAsReadSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkSubmissionAsReadSectionsData, "url"> ) => {
    try {
      const { data } = await markSubmissionAsReadSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    