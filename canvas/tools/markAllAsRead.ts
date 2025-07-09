
import { tool } from "ai";
import { markAllAsReadDataSchema } from "./aitm.schema.ts";
import { markAllAsRead, MarkAllAsReadData } from "..";

export default tool({
  description: `
  Mark all as read
Mark all conversations as read.
    `,
  parameters: markAllAsReadDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkAllAsReadData, "url"> ) => {
    try {
      const { data } = await markAllAsRead(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    