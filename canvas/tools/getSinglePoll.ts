
import { tool } from "ai";
import { getSinglePollDataSchema } from "./aitm.schema.ts";
import { getSinglePoll, GetSinglePollData } from "..";

export default tool({
  description: `
  Get a single poll
Returns the poll with the given id
    `,
  parameters: getSinglePollDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSinglePollData, "url"> ) => {
    try {
      const { data } = await getSinglePoll(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    