
import { tool } from "ai";
import { deletePollSessionDataSchema } from "./aitm.schema.ts";
import { deletePollSession, DeletePollSessionData } from "..";

export default tool({
  description: `
  Delete a poll session
<b>204 No Content</b> response code is returned if the deletion was
successful.
    `,
  parameters: deletePollSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePollSessionData, "url"> ) => {
    try {
      const { data } = await deletePollSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    