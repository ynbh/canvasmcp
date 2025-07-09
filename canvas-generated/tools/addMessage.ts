
import { tool } from "ai";
import { addMessageDataSchema } from "./aitm.schema.ts";
import { addMessage, AddMessageData } from "..";

export default tool({
  description: `
  Add a message
Add a message to an existing conversation. Response is similar to the
GET/show action,
except that only includes the
latest message (i.e. what we just sent)

An array of user ids.
Defaults to all of the current conversation
recipients. To explicitly send a message to no other
recipients,
this array should consist of the logged-in user id.

An array of message ids from this
conversation to send to recipients
of the new message. Recipients who already had a copy of
included
messages will not be affected.
    `,
  parameters: addMessageDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddMessageData, "url"> ) => {
    try {
      const { data } = await addMessage(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    