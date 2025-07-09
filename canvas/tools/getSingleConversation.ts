
import { tool } from "ai";
import { getSingleConversationDataSchema } from "./aitm.schema.ts";
import { getSingleConversation, GetSingleConversationData } from "..";

export default tool({
  description: `
  Get a single conversation
Returns information for a single conversation for the current user.
Response includes all
fields that are present in the list/index action as well as messages
and
extended participant information.
    `,
  parameters: getSingleConversationDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleConversationData, "url"> ) => {
    try {
      const { data } = await getSingleConversation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    