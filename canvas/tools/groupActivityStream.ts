
import { tool } from "ai";
import { groupActivityStreamDataSchema } from "./aitm.schema.ts";
import { groupActivityStream, GroupActivityStreamData } from "..";

export default tool({
  description: `
  Group activity stream
Returns the current user's group-specific activity stream, paginated.

For
full documentation, see the API documentation for the user activity
stream, in the user api.
    `,
  parameters: groupActivityStreamDataSchema.omit({ url: true }),
  execute: async (args : Omit<GroupActivityStreamData, "url"> ) => {
    try {
      const { data } = await groupActivityStream(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    