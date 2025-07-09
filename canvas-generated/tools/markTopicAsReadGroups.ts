
import { tool } from "ai";
import { markTopicAsReadGroupsDataSchema } from "./aitm.schema.ts";
import { markTopicAsReadGroups, MarkTopicAsReadGroupsData } from "..";

export default tool({
  description: `
  Mark topic as read
Mark the initial text of the discussion topic as read.

No request fields are
necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markTopicAsReadGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkTopicAsReadGroupsData, "url"> ) => {
    try {
      const { data } = await markTopicAsReadGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    