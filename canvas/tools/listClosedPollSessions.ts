
import { tool } from "ai";
import { listClosedPollSessionsDataSchema } from "./aitm.schema.ts";
import { listClosedPollSessions, ListClosedPollSessionsData } from "..";

export default tool({
  description: `
  List closed poll sessions
A paginated list of all closed poll sessions available to the current
user.
    `,
  parameters: listClosedPollSessionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListClosedPollSessionsData, "url"> ) => {
    try {
      const { data } = await listClosedPollSessions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    