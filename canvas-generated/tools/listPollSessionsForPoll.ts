
import { tool } from "ai";
import { listPollSessionsForPollDataSchema } from "./aitm.schema.ts";
import { listPollSessionsForPoll, ListPollSessionsForPollData } from "..";

export default tool({
  description: `
  List poll sessions for a poll
Returns the paginated list of PollSessions in this poll.
    `,
  parameters: listPollSessionsForPollDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPollSessionsForPollData, "url"> ) => {
    try {
      const { data } = await listPollSessionsForPoll(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    