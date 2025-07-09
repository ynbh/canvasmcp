
import { tool } from "ai";
import { markSubmissionAsUnreadSectionsDataSchema } from "./aitm.schema.ts";
import { markSubmissionAsUnreadSections, MarkSubmissionAsUnreadSectionsData } from "..";

export default tool({
  description: `
  Mark submission as unread
No request fields are necessary.

On success, the response will be 204 No
Content with an empty body.
    `,
  parameters: markSubmissionAsUnreadSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkSubmissionAsUnreadSectionsData, "url"> ) => {
    try {
      const { data } = await markSubmissionAsUnreadSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    