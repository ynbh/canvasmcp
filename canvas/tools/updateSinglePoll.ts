
import { tool } from "ai";
import { updateSinglePollDataSchema } from "./aitm.schema.ts";
import { updateSinglePoll, UpdateSinglePollData } from "..";

export default tool({
  description: `
  Update a single poll
Update an existing poll belonging to the current user
    `,
  parameters: updateSinglePollDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateSinglePollData, "url"> ) => {
    try {
      const { data } = await updateSinglePoll(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    