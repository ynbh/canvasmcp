
import { tool } from "ai";
import { createSinglePollDataSchema } from "./aitm.schema.ts";
import { createSinglePoll, CreateSinglePollData } from "..";

export default tool({
  description: `
  Create a single poll
Create a new poll for the current user
    `,
  parameters: createSinglePollDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSinglePollData, "url"> ) => {
    try {
      const { data } = await createSinglePoll(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    