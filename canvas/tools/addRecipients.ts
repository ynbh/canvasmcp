
import { tool } from "ai";
import { addRecipientsDataSchema } from "./aitm.schema.ts";
import { addRecipients, AddRecipientsData } from "..";

export default tool({
  description: `
  Add recipients
Add recipients to an existing group conversation. Response is similar to
the GET/show
action, except that only includes the
latest message (e.g. "joe was added to the conversation by
bob")
    `,
  parameters: addRecipientsDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddRecipientsData, "url"> ) => {
    try {
      const { data } = await addRecipients(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    