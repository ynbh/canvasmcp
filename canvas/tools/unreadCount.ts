
import { tool } from "ai";
import { unreadCountDataSchema } from "./aitm.schema.ts";
import { unreadCount, UnreadCountData } from "..";

export default tool({
  description: `
  Unread count
Get the number of unread conversations for the current user
    `,
  parameters: unreadCountDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnreadCountData, "url"> ) => {
    try {
      const { data } = await unreadCount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    