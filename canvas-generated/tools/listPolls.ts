
import { tool } from "ai";
import { listPollsDataSchema } from "./aitm.schema.ts";
import { listPolls, ListPollsData } from "..";

export default tool({
  description: `
  List polls
Returns the paginated list of polls for the current user.
    `,
  parameters: listPollsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPollsData, "url"> ) => {
    try {
      const { data } = await listPolls(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    