
import { tool } from "ai";
import { deletePollChoiceDataSchema } from "./aitm.schema.ts";
import { deletePollChoice, DeletePollChoiceData } from "..";

export default tool({
  description: `
  Delete a poll choice
<b>204 No Content</b> response code is returned if the deletion was successful.
    `,
  parameters: deletePollChoiceDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePollChoiceData, "url"> ) => {
    try {
      const { data } = await deletePollChoice(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    