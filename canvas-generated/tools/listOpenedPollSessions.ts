
import { tool } from "ai";
import { listOpenedPollSessionsDataSchema } from "./aitm.schema.ts";
import { listOpenedPollSessions, ListOpenedPollSessionsData } from "..";

export default tool({
  description: `
  List opened poll sessions
A paginated list of all opened poll sessions available to the current
user.
    `,
  parameters: listOpenedPollSessionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListOpenedPollSessionsData, "url"> ) => {
    try {
      const { data } = await listOpenedPollSessions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    