
import { tool } from "ai";
import { listPollChoicesInPollDataSchema } from "./aitm.schema.ts";
import { listPollChoicesInPoll, ListPollChoicesInPollData } from "..";

export default tool({
  description: `
  List poll choices in a poll
Returns the paginated list of PollChoices in this poll.
    `,
  parameters: listPollChoicesInPollDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPollChoicesInPollData, "url"> ) => {
    try {
      const { data } = await listPollChoicesInPoll(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    