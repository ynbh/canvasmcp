
import { tool } from "ai";
import { deletePollDataSchema } from "./aitm.schema.ts";
import { deletePoll, DeletePollData } from "..";

export default tool({
  description: `
  Delete a poll
<b>204 No Content</b> response code is returned if the deletion was successful.
    `,
  parameters: deletePollDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePollData, "url"> ) => {
    try {
      const { data } = await deletePoll(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    